import pytest
from src.risk_engine.scorer import score_graph, FactorContribution, RiskResult


def test_score_phishing_graph():
    """Test scoring a phishing-like graph."""
    graph = {
        "claimed_identity": "Security Team",
        "requested_action": "Click here to verify your account",
        "urgency_signals": ["urgent", "immediate action required", "24 hours"],
        "authority_signals": ["security department", "automated message"],
        "payload_targets": ["https://verify-account-now.malicious-site.com/login"]
    }
    
    result = score_graph(graph)
    
    assert isinstance(result, RiskResult)
    assert result.total_score == 100
    assert len(result.factors) == 5
    
    # All factors should have positive contribution
    for factor in result.factors:
        assert factor.contribution > 0
        assert factor.contribution == factor.weight


def test_score_legitimate_graph():
    """Test scoring a legitimate graph."""
    graph = {
        "claimed_identity": "John Doe, Senior Analyst",
        "requested_action": "Please review the attached report",
        "urgency_signals": [],
        "authority_signals": [],
        "payload_targets": ["https://company.com/reports/q4-2023"]
    }
    
    result = score_graph(graph)
    
    assert isinstance(result, RiskResult)
    assert result.total_score == 0
    
    # All factors should have zero contribution
    for factor in result.factors:
        assert factor.contribution == 0


def test_score_empty_graph():
    """Test scoring an empty graph."""
    graph = {
        "claimed_identity": None,
        "requested_action": None,
        "urgency_signals": [],
        "authority_signals": [],
        "payload_targets": []
    }
    
    result = score_graph(graph)
    
    assert isinstance(result, RiskResult)
    assert result.total_score == 0


def test_score_partial_graph():
    """Test scoring a graph with only some signals."""
    graph = {
        "claimed_identity": "Security Team",
        "requested_action": None,
        "urgency_signals": ["urgent"],
        "authority_signals": [],
        "payload_targets": []
    }
    
    result = score_graph(graph)
    
    assert isinstance(result, RiskResult)
    # Should have identity mismatch (25) + urgency (30) = 55
    assert result.total_score == 55
    
    # Check specific factors
    factor_dict = {f.name: f.contribution for f in result.factors}
    assert factor_dict["claimed_identity_mismatch"] == 25
    assert factor_dict["urgency_high"] == 30
    assert factor_dict["authority_spoof"] == 0
    assert factor_dict["payload_links"] == 0
    assert factor_dict["action_request"] == 0


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])