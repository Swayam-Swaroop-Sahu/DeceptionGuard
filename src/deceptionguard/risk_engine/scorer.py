"""Risk engine scorer — deterministic factor-based scoring.

Loads factor weights from TOML (stdlib tomllib) and computes a
risk score from an intent graph.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import DEFAULT_FACTOR_WEIGHTS


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
    """Load factor weights from weights.toml or return defaults.

    Args:
        path: Optional explicit path to a TOML file with a [factor_weights] section.
              If None, loads from the bundled weights.toml next to this file.

    Returns:
        Dict mapping factor names to integer weights.
    """
    if path is None:
        path = Path(__file__).parent / "weights.toml"

    path = Path(path)
    if path.is_file():
        with open(path, "rb") as f:
            data = tomllib.load(f)
        if "factor_weights" in data:
            return data["factor_weights"]

    return dict(DEFAULT_FACTOR_WEIGHTS)


def _check_identity_mismatch(graph: dict[str, Any]) -> bool:
    """Check if claimed identity doesn't match sender domain."""
    claimed = graph.get("claimed_identity")
    if not claimed:
        return False

    # Simple check: if claimed identity mentions known brands but sender is suspicious
    suspicious_keywords = ["security", "support", "admin", "billing", "verify", "account"]
    claimed_lower = claimed.lower()
    return any(kw in claimed_lower for kw in suspicious_keywords)


def _check_urgency_high(graph: dict[str, Any]) -> bool:
    """Check for high urgency signals."""
    urgency_signals = graph.get("urgency_signals", [])
    high_urgency_keywords = [
        "urgent", "immediate", "now", "asap", "emergency", "critical",
        "24 hours", "24h", "hours", "deadline", "expire", "suspend",
        "closure", "terminate", "act now", "hurry", "limited time",
    ]

    for signal in urgency_signals:
        signal_lower = signal.lower()
        if any(kw in signal_lower for kw in high_urgency_keywords):
            return True
    return False


def _check_authority_spoof(graph: dict[str, Any]) -> bool:
    """Check for authority spoofing signals."""
    authority_signals = graph.get("authority_signals", [])
    authority_keywords = [
        "security team", "it department", "help desk", "support team",
        "admin", "administrator", "bank", "irs", "government",
        "microsoft", "apple", "google", "amazon", "paypal", "linkedin",
        "facebook", "instagram", "twitter", "github", "gitlab",
        "security", "compliance", "legal", "hr", "human resources",
    ]

    for signal in authority_signals:
        signal_lower = signal.lower()
        if any(kw in signal_lower for kw in authority_keywords):
            return True
    return False


def _check_payload_links(graph: dict[str, Any]) -> bool:
    """Check for suspicious payload links."""
    payload_targets = graph.get("payload_targets", [])

    if not payload_targets:
        return False

    # Check for suspicious patterns in links
    suspicious_patterns = [
        "verify", "login", "signin", "account", "secure", "update",
        "confirm", "validate", "authenticate", "reset", "recover",
        "unlock", "restore", "activate", "verify-account", "secure-",
    ]

    for target in payload_targets:
        target_lower = target.lower()
        if any(pattern in target_lower for pattern in suspicious_patterns):
            return True
    return False


def _check_action_request(graph: dict[str, Any]) -> bool:
    """Check for explicit action requests."""
    requested_action = graph.get("requested_action")
    if not requested_action:
        return False

    action_keywords = [
        "click", "verify", "confirm", "update", "provide", "enter",
        "submit", "login", "sign in", "download", "open", "visit",
        "go to", "follow", "access", "reset", "change", "confirm",
    ]

    action_lower = requested_action.lower()
    return any(kw in action_lower for kw in action_keywords)


def score_graph(graph: dict[str, Any], weights_path: Path | str | None = None) -> RiskResult:
    """Compute risk score from intent graph.

    Args:
        graph: Intent graph dict with the standard schema keys.
        weights_path: Optional path to weights TOML file.

    Returns:
        RiskResult with deterministic score 0-100 and factor breakdown.
    """
    weights = load_weights(weights_path)
    factors: list[FactorContribution] = []

    # Factor 1: Claimed Identity Mismatch
    identity_mismatch = _check_identity_mismatch(graph)
    identity_weight = weights.get("claimed_identity_mismatch", 25)
    identity_contribution = identity_weight if identity_mismatch else 0
    factors.append(FactorContribution(
        name="claimed_identity_mismatch",
        weight=identity_weight,
        contribution=identity_contribution,
    ))

    # Factor 2: Urgency High
    urgency_high = _check_urgency_high(graph)
    urgency_weight = weights.get("urgency_high", 30)
    urgency_contribution = urgency_weight if urgency_high else 0
    factors.append(FactorContribution(
        name="urgency_high",
        weight=urgency_weight,
        contribution=urgency_contribution,
    ))

    # Factor 3: Authority Spoof
    authority_spoof = _check_authority_spoof(graph)
    authority_weight = weights.get("authority_spoof", 20)
    authority_contribution = authority_weight if authority_spoof else 0
    factors.append(FactorContribution(
        name="authority_spoof",
        weight=authority_weight,
        contribution=authority_contribution,
    ))

    # Factor 4: Payload Links
    payload_links = _check_payload_links(graph)
    payload_weight = weights.get("payload_links", 15)
    payload_contribution = payload_weight if payload_links else 0
    factors.append(FactorContribution(
        name="payload_links",
        weight=payload_weight,
        contribution=payload_contribution,
    ))

    # Factor 5: Action Request
    action_request = _check_action_request(graph)
    action_weight = weights.get("action_request", 10)
    action_contribution = action_weight if action_request else 0
    factors.append(FactorContribution(
        name="action_request",
        weight=action_weight,
        contribution=action_contribution,
    ))

    total_score = sum(f.contribution for f in factors)

    return RiskResult(
        total_score=min(total_score, 100),  # Cap at 100
        factors=factors,
    )
