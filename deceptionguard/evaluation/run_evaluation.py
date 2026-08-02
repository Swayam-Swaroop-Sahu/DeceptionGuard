import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
from sklearn.metrics import precision_recall_fscore_support
from deceptionguard.baseline.classifier import BaselineClassifier
from deceptionguard.ingestion.parser import parse_eml
from deceptionguard.intent_graph.extractor import extract_intent_graph
from deceptionguard.risk_engine.scorer import score_graph


def load_dataset(path: str) -> pd.DataFrame:
    """Load labeled dataset with columns: text, label, subtype."""
    return pd.read_csv(path)


def _get_text_from_record(record) -> str:
    """Combine subject and body text for classification."""
    parts = []
    if record.subject:
        parts.append(record.subject)
    parts.append(record.body_text)
    return " ".join(parts)


def evaluate_baseline(df: pd.DataFrame) -> Dict:
    """Evaluate baseline classifier on dataset."""
    # Load train data to train the classifier
    train_path = Path(__file__).parent.parent / "data" / "processed" / "placeholder_train.csv"
    if train_path.exists():
        train_df = pd.read_csv(train_path)
    else:
        # Fallback: use part of test data for training
        train_df = df.sample(frac=0.7, random_state=42)
    
    classifier = BaselineClassifier()
    classifier.train(train_df["text"].tolist(), train_df["label"].tolist())
    
    # Predict on test set
    predictions = classifier.predict(df["text"].tolist())
    pred_labels = [1 if p > 0.5 else 0 for p in predictions]
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        df["label"].tolist(), pred_labels, average="binary"
    )
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "predictions": predictions,
        "pred_labels": pred_labels
    }


def evaluate_full_pipeline(df: pd.DataFrame) -> Dict:
    """Evaluate full DeceptionGuard pipeline on dataset."""
    # For the full pipeline, we need actual email files
    # Since we only have text data, we'll simulate by creating EmailRecords
    # In practice, this would parse actual .eml files
    
    predictions = []
    pred_labels = []
    
    for _, row in df.iterrows():
        # Create a minimal EmailRecord from text
        from deceptionguard.ingestion.email_record import EmailRecord
        record = EmailRecord(
            sender="unknown@example.com",
            reply_to=None,
            return_path=None,
            subject="",
            date=None,
            body_text=row["text"],
            links=[],
            attachments=[]
        )
        
        # Extract intent graph (will return empty without API key)
        graph = extract_intent_graph(record)
        
        # Score the graph
        result = score_graph(graph)
        
        # Use risk score as probability (normalized to 0-1)
        prob = result.total_score / 100.0
        predictions.append(prob)
        pred_labels.append(1 if prob > 0.5 else 0)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        df["label"].tolist(), pred_labels, average="binary", zero_division=0
    )
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "predictions": predictions,
        "pred_labels": pred_labels
    }


def evaluate_by_subtype(df: pd.DataFrame, pred_labels: list) -> Dict:
    """Evaluate performance by subtype if available."""
    if "subtype" not in df.columns:
        return {}
    
    results = {}
    for subtype in df["subtype"].unique():
        mask = df["subtype"] == subtype
        sub_true = df.loc[mask, "label"].tolist()
        sub_pred = [pred_labels[i] for i in range(len(pred_labels)) if mask.iloc[i]]
        
        if len(set(sub_true)) < 2:
            # Skip if only one class present
            continue
            
        precision, recall, f1, _ = precision_recall_fscore_support(
            sub_true, sub_pred, average="binary", zero_division=0
        )
        
        results[subtype] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": len(sub_true)
        }
    
    return results


def generate_report(baseline_metrics: Dict, system_metrics: Dict, 
                    subtype_results: Dict) -> str:
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
            "|---------|-----------|--------|-----|---------|"
        ])
        
        for subtype, metrics in subtype_results.items():
            lines.append(
                f"| {subtype} | {metrics['precision']:.4f} | "
                f"{metrics['recall']:.4f} | {metrics['f1']:.4f} | {metrics['support']} |"
            )
        
        lines.append("")
    
    lines.extend([
        "---",
        "*Report generated by DeceptionGuard Evaluation Harness*"
    ])
    
    return "\n".join(lines)


def main():
    # Load test dataset
    test_path = Path(__file__).parent.parent / "data" / "processed" / "placeholder_test.csv"
    
    if not test_path.exists():
        print(f"Test dataset not found at {test_path}")
        print("Run baseline/train_baseline.py first to generate placeholder data")
        return
    
    df = load_dataset(str(test_path))
    print(f"Loaded {len(df)} test samples")
    
    # Evaluate baseline
    print("Evaluating baseline classifier...")
    baseline_metrics = evaluate_baseline(df)
    print(f"Baseline F1: {baseline_metrics['f1']:.4f}")
    
    # Evaluate full pipeline
    print("Evaluating full pipeline...")
    system_metrics = evaluate_full_pipeline(df)
    print(f"System F1: {system_metrics['f1']:.4f}")
    
    # Evaluate by subtype
    subtype_results = evaluate_by_subtype(df, system_metrics["pred_labels"])
    
    # Generate report
    report = generate_report(baseline_metrics, system_metrics, subtype_results)
    
    # Write report
    report_path = Path(__file__).parent / "report.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\nReport written to {report_path}")
    print("\n" + report)


if __name__ == "__main__":
    main()