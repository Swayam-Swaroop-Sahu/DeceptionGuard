from deceptionguard.evidence.schema import Evidence, Severity
from deceptionguard.risk_engine.scorer import FactorContribution, RiskResult, score_email


def test_score_phishing_graph_only():
    """Test scoring a phishing-like graph without evidence."""
    graph = {
        "urgency_pressure": True,     # 20
        "financial_request": True,    # 15
        "trust_abuse": "impersonating security", # 15
        "action_requested": "verify account",    # 10
        "deception_tone": "fear"      # 10
    }

    result = score_email(graph)
    assert isinstance(result, RiskResult)
    assert result.total_score == 70
    assert len(result.factors) == 5

def test_score_evidence_only():
    """Test scoring just evidence (empty graph)."""
    graph = {}
    evidence_list = [
        Evidence(evidence_type="DISPLAY_NAME_DOMAIN_MISMATCH", severity=Severity.HIGH, explanation="test"), # 30
        Evidence(evidence_type="URL_IP_LITERAL", severity=Severity.CRITICAL, explanation="test"), # 35
    ]

    result = score_email(graph, evidence_list)
    assert result.total_score == 65
    # 5 intent factors (all 0) + 2 evidence factors = 7 factors total
    assert len(result.factors) == 7

    factor_dict = {f.name: f.contribution for f in result.factors}
    assert factor_dict["DISPLAY_NAME_DOMAIN_MISMATCH"] == 30
    assert factor_dict["URL_IP_LITERAL"] == 35

def test_score_combined_caps_at_100():
    """Test combined scoring caps at 100."""
    graph = {
        "urgency_pressure": True,     # 20
        "financial_request": True,    # 15
        "trust_abuse": "impersonating security", # 15
        "action_requested": "verify account",    # 10
        "deception_tone": "fear"      # 10
    } # 70 from intent

    evidence_list = [
        Evidence(evidence_type="ATTACHMENT_EXECUTABLE", severity=Severity.CRITICAL, explanation="test"), # 50
    ]

    result = score_email(graph, evidence_list)
    assert result.total_score == 100 # (70 + 50) capped at 100

def test_factor_contribution_dataclass():
    """Test FactorContribution dataclass."""
    fc = FactorContribution(name="test", weight=10, contribution=5, category="intent")
    assert fc.name == "test"
    assert fc.weight == 10
    assert fc.contribution == 5
    assert fc.category == "intent"

def test_risk_result_dataclass():
    """Test RiskResult dataclass."""
    factors = [
        FactorContribution(name="test1", weight=10, contribution=5, category="intent"),
        FactorContribution(name="test2", weight=20, contribution=10, category="evidence")
    ]
    rr = RiskResult(total_score=15, factors=factors)
    assert rr.total_score == 15
    assert len(rr.factors) == 2
