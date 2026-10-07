"""Evaluation metrics for DeceptionGuard.

Computes standard ML metrics, calibration (ECE), ROC/PR AUC,
bootstrap confidence intervals, and McNemar tests.
Requires scikit-learn and numpy (part of [dev] extras).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_HAS_METRICS = False
try:
    import numpy as np
    from sklearn.metrics import (
        average_precision_score,
        precision_recall_fscore_support,
        roc_auc_score,
        roc_curve,
    )
    _HAS_METRICS = True
except ImportError:
    pass


def _require_metrics() -> None:
    if not _HAS_METRICS:
        raise ImportError(
            "scikit-learn and numpy are required for advanced metrics. "
            "Install with: pip install deceptionguard[dev]"
        )


def calculate_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Calculate Expected Calibration Error (ECE)."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    binids = np.digitize(y_prob, bins) - 1

    ece = 0.0
    for i in range(n_bins):
        bin_mask = binids == i
        if np.any(bin_mask):
            bin_acc = np.mean(y_true[bin_mask])
            bin_conf = np.mean(y_prob[bin_mask])
            bin_count = np.sum(bin_mask)
            ece += (bin_count / len(y_true)) * np.abs(bin_acc - bin_conf)

    return float(ece)


def calculate_fpr_at_tpr(y_true: np.ndarray, y_prob: np.ndarray, target_tpr: float = 0.95) -> float:
    """Calculate FPR at a given TPR (e.g., 95%)."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    # Find the index of the first TPR that is >= target_tpr
    idx = np.where(tpr >= target_tpr)[0]
    if len(idx) == 0:
        return 1.0
    return float(fpr[idx[0]])


def compute_all_metrics(y_true: list[int], y_prob: list[float], threshold: float = 0.5) -> dict[str, float]:
    """Compute all required metrics."""
    _require_metrics()

    y_true_arr = np.array(y_true)
    y_prob_arr = np.array(y_prob)
    y_pred = (y_prob_arr >= threshold).astype(int)

    if len(np.unique(y_true_arr)) < 2:
        return {"error": "Need both classes to compute AUC."}

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true_arr, y_pred, average="binary", zero_division=0
    )

    roc_auc = roc_auc_score(y_true_arr, y_prob_arr)
    pr_auc = average_precision_score(y_true_arr, y_prob_arr)
    fpr_95 = calculate_fpr_at_tpr(y_true_arr, y_prob_arr, 0.95)
    ece = calculate_ece(y_true_arr, y_prob_arr)

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "fpr_at_95_tpr": float(fpr_95),
        "ece": float(ece)
    }


def bootstrap_ci(
    y_true: list[int],
    y_prob: list[float],
    n_iterations: int = 1000,
    seed: int = 42
) -> dict[str, dict[str, float]]:
    """Compute 95% bootstrap confidence intervals for all metrics."""
    _require_metrics()

    rng = np.random.default_rng(seed)
    n_samples = len(y_true)

    y_true_arr = np.array(y_true)
    y_prob_arr = np.array(y_prob)

    metrics_dist = {
        "precision": [], "recall": [], "f1": [],
        "roc_auc": [], "pr_auc": [], "fpr_at_95_tpr": [], "ece": []
    }

    for _ in range(n_iterations):
        indices = rng.choice(n_samples, size=n_samples, replace=True)
        yt = y_true_arr[indices]
        yp = y_prob_arr[indices]

        if len(np.unique(yt)) < 2:
            continue

        m = compute_all_metrics(yt.tolist(), yp.tolist())
        if "error" not in m:
            for k, v in m.items():
                metrics_dist[k].append(v)

    results = {}
    for k, v in metrics_dist.items():
        if v:
            results[k] = {
                "mean": float(np.mean(v)),
                "ci_lower": float(np.percentile(v, 2.5)),
                "ci_upper": float(np.percentile(v, 97.5))
            }

    return results


def mcnemar_test(y_true: list[int], y_pred1: list[int], y_pred2: list[int]) -> float:
    """Perform McNemar's test between two systems.

    Returns the p-value.
    """
    _require_metrics()

    # Create contingency table
    # n00: both correct
    # n01: sys1 correct, sys2 wrong
    # n10: sys1 wrong, sys2 correct
    # n11: both wrong
    n01 = 0
    n10 = 0

    for t, p1, p2 in zip(y_true, y_pred1, y_pred2):
        c1 = (t == p1)
        c2 = (t == p2)
        if c1 and not c2:
            n01 += 1
        elif not c1 and c2:
            n10 += 1

    from scipy.stats import chi2

    b = n01
    c = n10

    if b + c == 0:
        return 1.0

    statistic = ((abs(b - c) - 1) ** 2) / (b + c)
    p_value = 1.0 - chi2.cdf(statistic, 1)

    return float(p_value)
