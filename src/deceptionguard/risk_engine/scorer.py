"""Risk engine scorer — deterministic factor-based scoring.

Loads factor weights from TOML (stdlib tomllib) and computes a
risk score from an intent graph.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FactorContribution:
    """A single factor's contribution to the risk score."""
    name: str
    weight: int
    contribution: int


@dataclass
class RiskResult:
    """Result of risk scoring: total score and per-factor breakdown."""
    total_score: int
    factors: list[FactorContribution]


def load_weights(path: Path | str | None = None) -> dict[str, int]:
    if path is None:
        path = Path(__file__).parent / "weights.toml"

    path = Path(path)
    if path.is_file():
        with open(path, "rb") as f:
            data = tomllib.load(f)
        if "factor_weights" in data:
            return data["factor_weights"]

    return {
        "urgency_pressure": 30,
        "financial_request": 25,
        "trust_abuse": 20,
        "action_requested": 10,
        "deception_tone_high_risk": 15
    }


def score_graph(graph: dict[str, Any], weights_path: Path | str | None = None) -> RiskResult:
    """Compute risk score from new intent graph schema."""
    weights = load_weights(weights_path)
    factors: list[FactorContribution] = []

    # 1. Urgency Pressure
    val = graph.get("urgency_pressure", False)
    w = weights.get("urgency_pressure", 30)
    factors.append(FactorContribution("urgency_pressure", w, w if val else 0))

    # 2. Financial Request
    val = graph.get("financial_request", False)
    w = weights.get("financial_request", 25)
    factors.append(FactorContribution("financial_request", w, w if val else 0))

    # 3. Trust Abuse
    val = bool(graph.get("trust_abuse"))
    w = weights.get("trust_abuse", 20)
    factors.append(FactorContribution("trust_abuse", w, w if val else 0))

    # 4. Action Requested
    val = bool(graph.get("action_requested"))
    w = weights.get("action_requested", 10)
    factors.append(FactorContribution("action_requested", w, w if val else 0))

    # 5. Deception Tone
    tone = graph.get("deception_tone")
    val = tone in ["fear", "greed"]
    w = weights.get("deception_tone_high_risk", 15)
    factors.append(FactorContribution("deception_tone_high_risk", w, w if val else 0))

    total_score = sum(f.contribution for f in factors)
    return RiskResult(total_score=min(total_score, 100), factors=factors)
