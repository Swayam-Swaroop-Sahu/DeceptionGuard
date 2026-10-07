"""Baseline classifier — TF-IDF + Logistic Regression.

Requires scikit-learn (optional [dev] dependency).
This module is NOT part of the core pipeline; it is used for
comparison baselines only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

_HAS_SKLEARN = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    _HAS_SKLEARN = True
except ImportError:
    pass


def _require_sklearn() -> None:
    """Raise an informative error if scikit-learn is not installed."""
    if not _HAS_SKLEARN:
        raise ImportError(
            "scikit-learn is required for the baseline classifier. "
            "Install with: pip install deceptionguard[dev]"
        )


class BaselineClassifier:
    """TF-IDF + Logistic Regression baseline for phishing detection.

    Requires scikit-learn to be installed (part of [dev] extras).
    """

    def __init__(self) -> None:
        _require_sklearn()
        self.pipeline: Any = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=1000)),
            ("clf", LogisticRegression(random_state=42)),
        ])

    def train(self, records: list[str], labels: list[int]) -> None:
        """Train the classifier on text records and labels."""
        _require_sklearn()
        self.pipeline.fit(records, labels)

    def predict(self, records: list[str]) -> list[float]:
        """Return phishing probability scores (0-1)."""
        _require_sklearn()
        return self.pipeline.predict_proba(records)[:, 1].tolist()
