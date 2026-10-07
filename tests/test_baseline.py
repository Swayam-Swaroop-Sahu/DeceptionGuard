import json
import pytest
from pathlib import Path
from deceptionguard.baseline.train_baseline import generate_placeholder_data, main, _HAS_SKLEARN
from deceptionguard.baseline.classifier import BaselineClassifier, _require_sklearn

@pytest.mark.skipif(not _HAS_SKLEARN, reason="scikit-learn not installed")
def test_baseline_classifier(tmp_path):
    train, test = generate_placeholder_data(tmp_path)
    assert len(train) > 0
    assert len(test) > 0
    
    clf = BaselineClassifier()
    texts = [d["text"] for d in train]
    labels = [d["label"] for d in train]
    clf.train(texts, labels)
    
    test_texts = [d["text"] for d in test]
    preds = clf.predict(test_texts)
    assert len(preds) == len(test_texts)
    
    import sys
    from unittest.mock import patch
    with patch("deceptionguard.baseline.train_baseline.__file__", str(tmp_path / "train_baseline.py")):
        main()
        
    metrics_path = tmp_path.parent / "data" / "processed" / "metrics.json"
    assert metrics_path.exists()
    
def test_baseline_no_sklearn():
    if _HAS_SKLEARN:
        return
    with pytest.raises(ImportError):
        _require_sklearn()
        
    with pytest.raises(ImportError):
        generate_placeholder_data()
        
    # main should just print error
    main()
