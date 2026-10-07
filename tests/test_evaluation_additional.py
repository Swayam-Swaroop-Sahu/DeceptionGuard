from deceptionguard.evaluation.run_evaluation import run_evaluation_suite, load_and_prep_dataset
import pytest

def test_load_and_prep_dataset(tmp_path):
    csv_path = tmp_path / "test.csv"
    with open(csv_path, "w") as f:
        f.write("text,label\n")
        f.write("test text,0\n")
        f.write("phishing text,1\n")
        
    records, labels, subtypes = load_and_prep_dataset(str(csv_path))
    assert len(records) == 2
    assert labels == [0, 1]
    
def test_run_evaluation_suite(tmp_path, monkeypatch):
    csv_path = tmp_path / "test.csv"
    with open(csv_path, "w") as f:
        f.write("text,label\n")
        for i in range(10):
            f.write(f"test text {i},0\n")
            f.write(f"phishing text {i},1\n")
        
    import deceptionguard.evaluation.run_evaluation as rev
    monkeypatch.setattr(rev, "RESULTS_DIR", tmp_path)
    
    with monkeypatch.context() as m:
        # Mock baseline classifier and pipeline
        m.setattr(rev, "run_pipeline", lambda rec, **kwargs: 0.9)
        m.setattr(rev, "bootstrap_ci", lambda *args: {})
        import deceptionguard.baseline.classifier as bc
        m.setattr(bc, "BaselineClassifier", type("MockCls", (), {"train": lambda s, x, y: None, "predict": lambda s, x: ([0.1, 0.9] * len(x))[:len(x)]}))
        run_evaluation_suite(str(csv_path))
        
    assert (tmp_path / "summary.json").exists()
