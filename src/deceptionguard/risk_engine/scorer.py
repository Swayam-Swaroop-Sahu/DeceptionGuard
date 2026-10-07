"""Risk engine scorer — deterministic factor-based scoring.

Combines Intent Graph (from LLM) and Evidence layer to compute a final risk score.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..evidence.schema import Evidence


@dataclass
class FactorContribution:
    """A single factor's contribution to the risk score."""
    name: str
    weight: int
    contribution: int
    category: str  # "intent" or "evidence"


@dataclass
class RiskResult:
    """Result of risk scoring: total score and per-factor breakdown."""
    total_score: int
    factors: list[FactorContribution]


def load_weights(path: Path | str | None = None) -> tuple[dict[str, int], dict[str, int]]:
    """Load weights for both intent and evidence.
    Returns (intent_weights, evidence_weights).
    """
    if path is None:
        path = Path(__file__).parent / "weights.toml"

    path = Path(path)
    if path.is_file():
        with open(path, "rb") as f:
            data = tomllib.load(f)
            intent_w = data.get("intent_weights", {})
            evidence_w = data.get("evidence_weights", {})
            if intent_w or evidence_w:
                return intent_w, evidence_w

    # Defaults
    intent_w = {
        "urgency_pressure": 20,
        "financial_request": 15,
        "trust_abuse": 15,
        "action_requested": 10,
        "deception_tone_high_risk": 10
    }
    evidence_w = {
        "DISPLAY_NAME_BRAND_MISMATCH": 40,
        "URL_IP_LITERAL": 35,
        "BRAND_TYPOSQUATTING": 40,
        "ATTACHMENT_EXECUTABLE": 50,
    }
    return intent_w, evidence_w


def score_email(
    graph: dict[str, Any],
    evidence_list: list[Evidence] | None = None,
    weights_path: Path | str | None = None
) -> RiskResult:
    """Compute combined risk score from intent graph and deterministic evidence.

    Args:
        graph: Intent graph dict with the standard schema keys.
        evidence_list: List of deterministic Evidence objects.
        weights_path: Optional path to weights TOML file.

    Returns:
        RiskResult with deterministic score 0-100 and factor breakdown.
    """
    intent_w, evidence_w = load_weights(weights_path)
    factors: list[FactorContribution] = []

    if evidence_list is None:
        evidence_list = []

    # 1. Score Intent
    val = graph.get("urgency_pressure", False)
    w = intent_w.get("urgency_pressure", 20)
    factors.append(FactorContribution("urgency_pressure", w, w if val else 0, "intent"))

    val = graph.get("financial_request", False)
    w = intent_w.get("financial_request", 15)
    factors.append(FactorContribution("financial_request", w, w if val else 0, "intent"))

    val = bool(graph.get("trust_abuse"))
    w = intent_w.get("trust_abuse", 15)
    factors.append(FactorContribution("trust_abuse", w, w if val else 0, "intent"))

    val = bool(graph.get("action_requested"))
    w = intent_w.get("action_requested", 10)
    factors.append(FactorContribution("action_requested", w, w if val else 0, "intent"))

    tone = graph.get("deception_tone")
    val = tone in ["fear", "greed"]
    w = intent_w.get("deception_tone_high_risk", 10)
    factors.append(FactorContribution("deception_tone_high_risk", w, w if val else 0, "intent"))

    # 2. Score Evidence
    # We aggregate evidence by type. If multiple evidences of the same type exist, we apply the weight once.
    seen_evidence_types = {e.evidence_type for e in evidence_list}

    for ev_type in seen_evidence_types:
        w = evidence_w.get(ev_type, 10) # default unknown evidence gets 10
        factors.append(FactorContribution(ev_type, w, w, "evidence"))

    total_score = sum(f.contribution for f in factors)
    return RiskResult(total_score=min(total_score, 100), factors=factors)


# Backwards compatibility alias
def score_graph(graph: dict[str, Any], weights_path: Path | str | None = None) -> RiskResult:
    return score_email(graph, None, weights_path)
