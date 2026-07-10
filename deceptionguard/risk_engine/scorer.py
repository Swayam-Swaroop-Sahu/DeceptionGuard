from dataclasses import dataclass
from typing import List, Tuple, Dict
import yaml
from pathlib import Path


@dataclass
class FactorContribution:
    name: str
    weight: int
    contribution: int


@dataclass
class RiskResult:
    total_score: int
    factors: List[FactorContribution]


def load_weights() -> Dict[str, int]:
    """Load factor weights from weights.yaml."""
    with open(Path(__file__).parent / "weights.yaml") as f:
        return yaml.safe_load(f)["factor_weights"]


def _check_identity_mismatch(graph: Dict) -> bool:
    """Check if claimed identity doesn't match sender domain."""
    claimed = graph.get("claimed_identity")
    if not claimed:
        return False
    
    # Simple check: if claimed identity mentions known brands but sender is suspicious
    suspicious_keywords = ["security", "support", "admin", "billing", "verify", "account"]
    claimed_lower = claimed.lower()
    return any(kw in claimed_lower for kw in suspicious_keywords)


def _check_urgency_high(graph: Dict) -> bool:
    """Check for high urgency signals."""
    urgency_signals = graph.get("urgency_signals", [])
    high_urgency_keywords = [
        "urgent", "immediate", "now", "asap", "emergency", "critical",
        "24 hours", "24h", "hours", "deadline", "expire", "suspend",
        "closure", "terminate", "act now", "hurry", "limited time"
    ]
    
    for signal in urgency_signals:
        signal_lower = signal.lower()
        if any(kw in signal_lower for kw in high_urgency_keywords):
            return True
    return False


def _check_authority_spoof(graph: Dict) -> bool:
    """Check for authority spoofing signals."""
    authority_signals = graph.get("authority_signals", [])
    authority_keywords = [
        "security team", "it department", "help desk", "support team",
        "admin", "administrator", "bank", "irs", "government",
        "microsoft", "apple", "google", "amazon", "paypal", "linkedin",
        "facebook", "instagram", "twitter", "github", "gitlab",
        "security", "compliance", "legal", "hr", "human resources"
    ]
    
    for signal in authority_signals:
        signal_lower = signal.lower()
        if any(kw in signal_lower for kw in authority_keywords):
            return True
    return False


def _check_payload_links(graph: Dict) -> bool:
    """Check for suspicious payload links."""
    payload_targets = graph.get("payload_targets", [])
    
    if not payload_targets:
        return False
    
    # Check for suspicious patterns in links
    suspicious_patterns = [
        "verify", "login", "signin", "account", "secure", "update",
        "confirm", "validate", "authenticate", "reset", "recover",
        "unlock", "restore", "activate", "verify-account", "secure-"
    ]
    
    for target in payload_targets:
        target_lower = target.lower()
        if any(pattern in target_lower for pattern in suspicious_patterns):
            return True
    return False


def _check_action_request(graph: Dict) -> bool:
    """Check for explicit action requests."""
    requested_action = graph.get("requested_action")
    if not requested_action:
        return False
    
    action_keywords = [
        "click", "verify", "confirm", "update", "provide", "enter",
        "submit", "login", "sign in", "download", "open", "visit",
        "go to", "follow", "access", "reset", "change", "confirm"
    ]
    
    action_lower = requested_action.lower()
    return any(kw in action_lower for kw in action_keywords)


def score_graph(graph: Dict) -> RiskResult:
    """
    Compute risk score from intent graph.
    
    Returns deterministic score 0-100 with factor breakdown.
    """
    weights = load_weights()
    factors = []
    
    # Factor 1: Claimed Identity Mismatch
    identity_mismatch = _check_identity_mismatch(graph)
    identity_contribution = weights["claimed_identity_mismatch"] if identity_mismatch else 0
    factors.append(FactorContribution(
        name="claimed_identity_mismatch",
        weight=weights["claimed_identity_mismatch"],
        contribution=identity_contribution
    ))
    
    # Factor 2: Urgency High
    urgency_high = _check_urgency_high(graph)
    urgency_contribution = weights["urgency_high"] if urgency_high else 0
    factors.append(FactorContribution(
        name="urgency_high",
        weight=weights["urgency_high"],
        contribution=urgency_contribution
    ))
    
    # Factor 3: Authority Spoof
    authority_spoof = _check_authority_spoof(graph)
    authority_contribution = weights["authority_spoof"] if authority_spoof else 0
    factors.append(FactorContribution(
        name="authority_spoof",
        weight=weights["authority_spoof"],
        contribution=authority_contribution
    ))
    
    # Factor 4: Payload Links
    payload_links = _check_payload_links(graph)
    payload_contribution = weights["payload_links"] if payload_links else 0
    factors.append(FactorContribution(
        name="payload_links",
        weight=weights["payload_links"],
        contribution=payload_contribution
    ))
    
    # Factor 5: Action Request
    action_request = _check_action_request(graph)
    action_contribution = weights["action_request"] if action_request else 0
    factors.append(FactorContribution(
        name="action_request",
        weight=weights["action_request"],
        contribution=action_contribution
    ))
    
    total_score = sum(f.contribution for f in factors)
    
    return RiskResult(
        total_score=min(total_score, 100),  # Cap at 100
        factors=factors
    )


if __name__ == "__main__":
    # Test with sample graphs
    test_graphs = [
        # Phishing-like graph
        {
            "claimed_identity": "Security Team",
            "requested_action": "Click here to verify your account",
            "urgency_signals": ["urgent", "immediate action required", "24 hours"],
            "authority_signals": ["security department", "automated message"],
            "payload_targets": ["https://verify-account-now.malicious-site.com/login"]
        },
        # Legitimate graph
        {
            "claimed_identity": "John Doe, Senior Analyst",
            "requested_action": "Please review the attached report",
            "urgency_signals": [],
            "authority_signals": [],
            "payload_targets": ["https://company.com/reports/q4-2023"]
        },
        # Empty graph
        {
            "claimed_identity": None,
            "requested_action": None,
            "urgency_signals": [],
            "authority_signals": [],
            "payload_targets": []
        }
    ]
    
    for i, graph in enumerate(test_graphs):
        result = score_graph(graph)
        print(f"\nTest Graph {i + 1}:")
        print(f"  Total Score: {result.total_score}/100")
        for f in result.factors:
            status = "[+]" if f.contribution > 0 else "[-]"
            print(f"  {status} {f.name}: {f.contribution}/{f.weight}")