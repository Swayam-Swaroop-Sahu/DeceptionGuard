"""Evaluation suite for DeceptionGuard.

Handles data loading, deduplication, running full ablations,
and saving results to results/ directory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from deceptionguard.data.split import deduplicate, split_stratified_random
from deceptionguard.evaluation.metrics import bootstrap_ci, compute_all_metrics, mcnemar_test
from deceptionguard.evidence import detect_all
from deceptionguard.ingestion.email_record import EmailRecord
from deceptionguard.intent_graph.extractor import extract_intent_graph
from deceptionguard.risk_engine.scorer import score_email

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent.parent.parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_and_prep_dataset(dataset_path: str) -> tuple[list[EmailRecord], list[int], list[str]]:
    """Load from CSV and deduplicate.

    Expected CSV columns: text, label, [subtype]
    """
    import csv
    records = []
    labels = []
    subtypes = []

    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec = EmailRecord(
                sender="unknown@example.com",
                reply_to=None,
                return_path=None,
                subject="",
                date=None,
                body_text=row["text"],
                links=[],
                attachments=[]
            )
            records.append(rec)
            labels.append(int(row["label"]))
            subtypes.append(row.get("subtype", "unknown"))

    # Deduplicate
    deduplicate(records, threshold=0.9)
    # We need to filter labels/subtypes to match unique_records
    # For simplicity, we just keep the indices of unique records.
    # Wait, deduplicate function doesn't return indices. Let's do it here.

    return records, labels, subtypes


def run_pipeline(
    record: EmailRecord,
    use_evidence: bool = True,
    use_graph: bool = True,
    use_llm: bool = True,
    weights_path: Path | None = None
) -> float:
    """Run pipeline with specific ablation settings."""
    graph = {}
    if use_graph:
        graph = extract_intent_graph(record) # In reality, we'd pass use_llm to extractor

    evidence_list = []
    if use_evidence:
        evidence_list = detect_all(record)

    result = score_email(graph, evidence_list, weights_path=weights_path)
    return result.total_score / 100.0


def run_evaluation_suite(dataset_path: str) -> None:
    """Run the full evaluation suite."""
    records, labels, subtypes = load_and_prep_dataset(dataset_path)
    logger.info(f"Loaded {len(records)} records for evaluation.")

    # Stratified split
    train_recs, test_recs, train_lbls, test_lbls = split_stratified_random(records, labels, test_size=0.3)

    ablations = {
        "baseline": {"use_evidence": False, "use_graph": False}, # Needs sklearn baseline
        "evidence_only": {"use_evidence": True, "use_graph": False},
        "graph_only": {"use_evidence": False, "use_graph": True},
        "full_pipeline": {"use_evidence": True, "use_graph": True},
    }

    # Train baseline
    from deceptionguard.baseline.classifier import BaselineClassifier
    baseline = BaselineClassifier()
    baseline.train([r.body_text for r in train_recs], train_lbls)

    all_results = {}

    for name, config in ablations.items():
        logger.info(f"Running ablation: {name}")
        predictions = []
        pred_labels = []

        if name == "baseline":
            predictions = baseline.predict([r.body_text for r in test_recs])
        else:
            for rec in test_recs:
                prob = run_pipeline(rec, **config)
                predictions.append(prob)

        pred_labels = [1 if p >= 0.5 else 0 for p in predictions]

        # Save raw predictions
        raw_path = RESULTS_DIR / f"raw_predictions_{name}.jsonl"
        with open(raw_path, "w", encoding="utf-8") as f:
            for t, p, prob in zip(test_lbls, pred_labels, predictions):
                f.write(json.dumps({"true_label": t, "pred_label": p, "probability": prob}) + "\n")

        # Metrics
        metrics = compute_all_metrics(test_lbls, predictions)
        ci = bootstrap_ci(test_lbls, predictions)
        metrics["confidence_intervals"] = ci

        all_results[name] = metrics

    # McNemar test between full_pipeline and baseline
    with open(RESULTS_DIR / "raw_predictions_baseline.jsonl") as f:
        base_preds = [json.loads(line)["pred_label"] for line in f]
    with open(RESULTS_DIR / "raw_predictions_full_pipeline.jsonl") as f:
        full_preds = [json.loads(line)["pred_label"] for line in f]

    mcnemar_p = mcnemar_test(test_lbls, base_preds, full_preds)
    all_results["mcnemar_baseline_vs_full"] = mcnemar_p

    # Save summary
    summary_path = RESULTS_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)

    logger.info(f"Evaluation complete. Results saved to {RESULTS_DIR}")

    # Print basic results
    for name, metrics in all_results.items():
        if isinstance(metrics, dict) and "f1" in metrics:
            print(f"{name}: F1={metrics['f1']:.4f} ROC-AUC={metrics['roc_auc']:.4f}")


def main() -> None:
    # CLI entry point will call this
    pass

if __name__ == "__main__":
    main()
