import pytest
from pathlib import Path
import pandas as pd
from deceptionguard.evaluation.run_evaluation import (
    load_dataset, evaluate_baseline, evaluate_full_pipeline, 
    evaluate_by_subtype, generate_report
)


def test_load_dataset():
    """Test loading a dataset."""
    # Create a temporary CSV for testing
    test_df = pd.DataFrame({
        "text": ["test email 1", "test email 2"],
        "label": [0, 1],
        "subtype": ["legit", "phishing"]
    })
    test_path = Path(__file__).parent / "test_temp.csv"
    test_df.to_csv(test_path, index=False)
    
    loaded = load_dataset(str(test_path))
    assert len(loaded) == 2
    assert list(loaded.columns) == ["text", "label", "subtype"]
    
    # Cleanup
    test_path.unlink()


def test_evaluate_baseline():
    """Test baseline evaluation."""
    test_df = pd.DataFrame({
        "text": [
            "Dear team, please review the quarterly report.",
            "URGENT: Your account compromised! Click here!",
            "Meeting reminder for tomorrow at 10 AM.",
            "Verify your banking info now or lose access.",
        ],
        "label": [0, 1, 0, 1]
    })
    
    metrics = evaluate_baseline(test_df)
    
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "predictions" in metrics
    assert "pred_labels" in metrics
    assert len(metrics["predictions"]) == 4
    assert len(metrics["pred_labels"]) == 4


def test_evaluate_full_pipeline():
    """Test full pipeline evaluation."""
    test_df = pd.DataFrame({
        "text": [
            "Dear team, please review the quarterly report.",
            "URGENT: Your account compromised! Click here!",
        ],
        "label": [0, 1]
    })
    
    metrics = evaluate_full_pipeline(test_df)
    
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "predictions" in metrics
    assert "pred_labels" in metrics
    assert len(metrics["predictions"]) == 2
    assert len(metrics["pred_labels"]) == 2


def test_evaluate_by_subtype():
    """Test subtype evaluation."""
    test_df = pd.DataFrame({
        "text": ["test1", "test2", "test3", "test4", "test5", "test6"],
        "label": [0, 1, 0, 1, 0, 1],
        "subtype": ["legit", "legit", "phishing", "phishing", "phishing", "phishing"]
    })
    pred_labels = [0, 1, 0, 1, 0, 1]  # Perfect predictions
    
    results = evaluate_by_subtype(test_df, pred_labels)
    
    assert "legit" in results
    assert "phishing" in results
    assert results["legit"]["f1"] == 1.0
    assert results["phishing"]["f1"] == 1.0


def test_evaluate_by_subtype_no_subtype_column():
    """Test subtype evaluation without subtype column."""
    test_df = pd.DataFrame({
        "text": ["test1", "test2"],
        "label": [0, 1]
    })
    pred_labels = [0, 1]
    
    results = evaluate_by_subtype(test_df, pred_labels)
    
    assert results == {}


def test_generate_report():
    """Test report generation."""
    baseline = {"precision": 0.8, "recall": 0.7, "f1": 0.75}
    system = {"precision": 0.85, "recall": 0.8, "f1": 0.82}
    subtypes = {
        "phishing": {"precision": 0.9, "recall": 0.85, "f1": 0.87, "support": 10},
        "legit": {"precision": 0.8, "recall": 0.75, "f1": 0.77, "support": 10}
    }
    
    report = generate_report(baseline, system, subtypes)
    
    assert "# DeceptionGuard Evaluation Report" in report
    assert "0.7500" in report  # baseline F1
    assert "0.8200" in report  # system F1
    assert "phishing" in report
    assert "legit" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])