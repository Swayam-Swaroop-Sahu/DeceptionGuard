from deceptionguard.risk_engine.scorer import FactorContribution, RiskResult, score_graph


def test_score_phishing_graph():
    """Test scoring a phishing-like graph."""
    graph = {
        "urgency_pressure": True,
        "financial_request": True,
        "trust_abuse": "impersonating security",
        "action_requested": "verify account",
        "deception_tone": "fear"
    }

    result = score_graph(graph)

    assert isinstance(result, RiskResult)
    assert result.total_score == 100
    assert len(result.factors) == 5

    for factor in result.factors:
        assert factor.contribution > 0
        assert factor.contribution == factor.weight

def test_score_legitimate_graph():
    """Test scoring a legitimate graph."""
    graph = {
        "urgency_pressure": False,
        "financial_request": False,
        "trust_abuse": None,
        "action_requested": None,
        "deception_tone": "neutral"
    }

    result = score_graph(graph)

    assert isinstance(result, RiskResult)
    assert result.total_score == 0

    for factor in result.factors:
        assert factor.contribution == 0

def test_score_empty_graph():
    """Test scoring an empty graph."""
    graph = {}
    result = score_graph(graph)
    assert result.total_score == 0

def test_score_partial_graph():
    """Test scoring a graph with only some signals."""
    graph = {
        "urgency_pressure": True,
        "financial_request": False,
        "trust_abuse": "impersonating boss",
        "action_requested": None,
        "deception_tone": "neutral"
    }

    result = score_graph(graph)

    assert isinstance(result, RiskResult)
    assert result.total_score == 50  # urgency(30) + trust_abuse(20)

    factor_dict = {f.name: f.contribution for f in result.factors}
    assert factor_dict["urgency_pressure"] == 30
    assert factor_dict["financial_request"] == 0
    assert factor_dict["trust_abuse"] == 20
    assert factor_dict["action_requested"] == 0
    assert factor_dict["deception_tone_high_risk"] == 0

def test_factor_contribution_dataclass():
    """Test FactorContribution dataclass."""
    fc = FactorContribution(name="test", weight=10, contribution=5)
    assert fc.name == "test"
    assert fc.weight == 10
    assert fc.contribution == 5

def test_risk_result_dataclass():
    """Test RiskResult dataclass."""
    factors = [
        FactorContribution(name="test1", weight=10, contribution=5),
        FactorContribution(name="test2", weight=20, contribution=10)
    ]
    rr = RiskResult(total_score=15, factors=factors)
    assert rr.total_score == 15
    assert len(rr.factors) == 2
