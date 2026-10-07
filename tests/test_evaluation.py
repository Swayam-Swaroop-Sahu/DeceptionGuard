from pathlib import Path

import pytest

from deceptionguard.evaluation.run_evaluation import (
    evaluate_baseline,
    evaluate_by_subtype,
    evaluate_full_pipeline,
    generate_report,
    load_dataset,
)


def test_load_dataset():
    """Test loading a dataset."""
    import csv

    # Create a temporary CSV for testing
    test_data = [
        {"text": "test email 1", "label": 0, "subtype": "legit"},
        {"text": "test email 2", "label": 1, "subtype": "phishing"}
    ]
    test_path = Path(__file__).parent / "test_temp.csv"
    with open(test_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "subtype"])
        writer.writeheader()
        writer.writerows(test_data)

    loaded = load_dataset(str(test_path))
    assert len(loaded) == 2
    assert "text" in loaded[0]
    assert "label" in loaded[0]
    assert "subtype" in loaded[0]

    # Cleanup
    test_path.unlink()


def test_evaluate_baseline():
    """Test baseline evaluation."""
    test_data = [
        {"text": "Dear team, please review the quarterly report.", "label": 0},
        {"text": "URGENT: Your account compromised! Click here!", "label": 1},
        {"text": "Meeting reminder for tomorrow at 10 AM.", "label": 0},
        {"text": "Verify your banking info now or lose access.", "label": 1},
    ]

    metrics = evaluate_baseline(test_data)

    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "predictions" in metrics
    assert "pred_labels" in metrics
    assert len(metrics["predictions"]) == 4
    assert len(metrics["pred_labels"]) == 4


def test_evaluate_full_pipeline():
    """Test full pipeline evaluation."""
    test_data = [
        {"text": "Dear team, please review the quarterly report.", "label": 0},
        {"text": "URGENT: Your account compromised! Click here!", "label": 1},
    ]

    metrics = evaluate_full_pipeline(test_data)

    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "predictions" in metrics
    assert "pred_labels" in metrics
    assert len(metrics["predictions"]) == 2
    assert len(metrics["pred_labels"]) == 2


def test_evaluate_by_subtype():
    """Test subtype evaluation."""
    test_data = [
        {"text": "test1", "label": 0, "subtype": "legit"},
        {"text": "test2", "label": 1, "subtype": "legit"},
        {"text": "test3", "label": 0, "subtype": "phishing"},
        {"text": "test4", "label": 1, "subtype": "phishing"},
        {"text": "test5", "label": 0, "subtype": "phishing"},
        {"text": "test6", "label": 1, "subtype": "phishing"}
    ]
    pred_labels = [0, 1, 0, 1, 0, 1]  # Perfect predictions

    results = evaluate_by_subtype(test_data, pred_labels)

    assert "legit" in results
    assert "phishing" in results
    assert results["legit"]["f1"] == 1.0
    assert results["phishing"]["f1"] == 1.0


def test_evaluate_by_subtype_no_subtype_column():
    """Test subtype evaluation without subtype column."""
    test_data = [
        {"text": "test1", "label": 0},
        {"text": "test2", "label": 1}
    ]
    pred_labels = [0, 1]

    results = evaluate_by_subtype(test_data, pred_labels)

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
