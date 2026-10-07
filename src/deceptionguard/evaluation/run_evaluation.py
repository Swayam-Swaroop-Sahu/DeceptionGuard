"""Evaluation harness — compare baseline vs full pipeline.

Core evaluation functions use only stdlib. Baseline comparison requires
scikit-learn (optional [dev] dependency).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

# Guard optional imports
_HAS_SKLEARN = False
try:
    from sklearn.metrics import precision_recall_fscore_support

    _HAS_SKLEARN = True
except ImportError:
    pass

from ..ingestion.email_record import EmailRecord
from ..intent_graph.extractor import extract_intent_graph


def load_dataset(path: str) -> list[dict[str, Any]]:
    """Load labeled dataset from CSV with columns: text, label, [subtype].

    Args:
        path: Path to CSV file.

    Returns:
        List of dicts with 'text', 'label', and optionally 'subtype' keys.
    """
    records: list[dict[str, Any]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record: dict[str, Any] = {
                "text": row["text"],
                "label": int(row["label"]),
            }
            if "subtype" in row:
                record["subtype"] = row["subtype"]
            records.append(record)
    return records


def _precision_recall_f1(
    true_labels: list[int],
    pred_labels: list[int],
) -> dict[str, float]:
    """Compute precision, recall, F1 for binary classification (stdlib only).

    Args:
        true_labels: Ground truth labels (0 or 1).
        pred_labels: Predicted labels (0 or 1).

    Returns:
        Dict with precision, recall, and f1 keys.
    """
    tp = sum(1 for t, p in zip(true_labels, pred_labels) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(true_labels, pred_labels) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(true_labels, pred_labels) if t == 1 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {"precision": precision, "recall": recall, "f1": f1}


def evaluate_baseline(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate baseline classifier on dataset.

    Requires scikit-learn (optional [dev] dependency).
    """
    if not _HAS_SKLEARN:
        raise ImportError(
            "scikit-learn is required for baseline evaluation. "
            "Install with: pip install deceptionguard[dev]"
        )

    from ..baseline.classifier import BaselineClassifier

    # Load train data
    train_path = Path(__file__).parent.parent / "data" / "processed" / "placeholder_train.csv"
    if train_path.exists():
        train_data = load_dataset(str(train_path))
    else:
        # Fallback: use 70% of test data for training
        import random

        rng = random.Random(42)
        shuffled = list(data)
        rng.shuffle(shuffled)
        split_idx = int(len(shuffled) * 0.7)
        train_data = shuffled[:split_idx]

    classifier = BaselineClassifier()
    classifier.train(
        [d["text"] for d in train_data],
        [d["label"] for d in train_data],
    )

    # Predict on test set
    texts = [d["text"] for d in data]
    true_labels = [d["label"] for d in data]
    predictions = classifier.predict(texts)
    pred_labels = [1 if p > 0.5 else 0 for p in predictions]

    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, pred_labels, average="binary"
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "predictions": predictions,
        "pred_labels": pred_labels,
    }


def evaluate_full_pipeline(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate full DeceptionGuard pipeline on dataset (stdlib only)."""
    predictions: list[float] = []
    pred_labels: list[int] = []
    true_labels = [d["label"] for d in data]

    for item in data:
        # Create a minimal EmailRecord from text
        record = EmailRecord(
            sender="unknown@example.com",
            reply_to=None,
            return_path=None,
            subject="",
            date=None,
            body_text=item["text"],
            links=[],
            attachments=[],
        )

        # Extract intent graph (will use heuristic without API key)
        graph = extract_intent_graph(record)

        # Detect evidence
        from ..evidence import detect_all
        evidence_list = detect_all(record)

        # Score the graph and evidence
        from ..risk_engine.scorer import score_email
        result = score_email(graph, evidence_list)

        # Use risk score as probability (normalized to 0-1)
        prob = result.total_score / 100.0
        predictions.append(prob)
        pred_labels.append(1 if prob > 0.5 else 0)

    metrics = _precision_recall_f1(true_labels, pred_labels)
    metrics["predictions"] = predictions
    metrics["pred_labels"] = pred_labels

    return metrics


def evaluate_by_subtype(
    data: list[dict[str, Any]],
    pred_labels: list[int],
) -> dict[str, dict[str, Any]]:
    """Evaluate performance by subtype if available."""
    # Check if subtype is present
    if not any("subtype" in d for d in data):
        return {}

    # Group by subtype
    subtypes: dict[str, tuple[list[int], list[int]]] = {}
    for i, item in enumerate(data):
        subtype = item.get("subtype", "unknown")
        if subtype not in subtypes:
            subtypes[subtype] = ([], [])
        subtypes[subtype][0].append(item["label"])
        subtypes[subtype][1].append(pred_labels[i])

    results: dict[str, dict[str, Any]] = {}
    for subtype, (sub_true, sub_pred) in sorted(subtypes.items()):
        if len(set(sub_true)) < 2:
            continue  # Skip if only one class present

        metrics = _precision_recall_f1(sub_true, sub_pred)
        metrics["support"] = len(sub_true)
        results[subtype] = metrics

    return results


def generate_report(
    baseline_metrics: dict[str, Any],
    system_metrics: dict[str, Any],
    subtype_results: dict[str, dict[str, Any]],
) -> str:
    """Generate markdown report from evaluation results."""
    lines = [
        "# DeceptionGuard Evaluation Report",
        "",
        "## Baseline Classifier (TF-IDF + LogisticRegression)",
        f"- **Precision**: {baseline_metrics['precision']:.4f}",
        f"- **Recall**: {baseline_metrics['recall']:.4f}",
        f"- **F1 Score**: {baseline_metrics['f1']:.4f}",
        "",
        "## Full Pipeline (Intent Graph + Risk Engine)",
        f"- **Precision**: {system_metrics['precision']:.4f}",
        f"- **Recall**: {system_metrics['recall']:.4f}",
        f"- **F1 Score**: {system_metrics['f1']:.4f}",
        "",
    ]

    if subtype_results:
        lines.extend([
            "## Subtype Breakdown",
            "",
            "| Subtype | Precision | Recall | F1 | Support |",
            "|---------|-----------|--------|-----|---------|",
        ])

        for subtype, metrics in sorted(subtype_results.items()):
            lines.append(
                f"| {subtype} | {metrics['precision']:.4f} | "
                f"{metrics['recall']:.4f} | {metrics['f1']:.4f} | {metrics['support']} |"
            )

        lines.append("")

    lines.extend([
        "---",
        "*Report generated by DeceptionGuard Evaluation Harness*",
    ])

    return "\n".join(lines)


def main() -> None:
    """Run evaluation and generate report."""
    # Load test dataset
    test_path = Path(__file__).parent.parent / "data" / "processed" / "placeholder_test.csv"

    if not test_path.exists():
        print(f"Test dataset not found at {test_path}")
        print("Run `dg train-baseline` first to generate placeholder data")
        return

    data = load_dataset(str(test_path))
    print(f"Loaded {len(data)} test samples")

    # Evaluate full pipeline (stdlib only)
    print("Evaluating full pipeline...")
    system_metrics = evaluate_full_pipeline(data)
    print(f"System F1: {system_metrics['f1']:.4f}")

    # Evaluate baseline (requires sklearn)
    baseline_metrics: dict[str, Any] = {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    if _HAS_SKLEARN:
        print("Evaluating baseline classifier...")
        baseline_metrics = evaluate_baseline(data)
        print(f"Baseline F1: {baseline_metrics['f1']:.4f}")
    else:
        print("Skipping baseline evaluation (scikit-learn not installed)")

    # Evaluate by subtype
    subtype_results = evaluate_by_subtype(data, system_metrics["pred_labels"])

    # Generate report
    report = generate_report(baseline_metrics, system_metrics, subtype_results)

    # Write report
    report_path = Path(__file__).parent / "report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport written to {report_path}")
    print("\n" + report)


if __name__ == "__main__":
    main()
