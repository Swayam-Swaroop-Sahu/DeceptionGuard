import pytest
from src.intent_graph.schema import validate_graph, INTENT_GRAPH_SCHEMA
from src.intent_graph.extractor import extract_intent_graph, _fallback_extract
from src.ingestion.email_record import EmailRecord


def test_validate_graph_valid():
    """Test validation of a valid intent graph."""
    graph = {
        "claimed_identity": "Security Team",
        "requested_action": "Verify account",
        "urgency_signals": ["urgent", "immediate"],
        "authority_signals": ["security", "department"],
        "payload_targets": ["https://malicious-site.com/login"]
    }
    assert validate_graph(graph) is True


def test_validate_graph_none_values():
    """Test validation with None values."""
    graph = {
        "claimed_identity": None,
        "requested_action": None,
        "urgency_signals": [],
        "authority_signals": [],
        "payload_targets": []
    }
    assert validate_graph(graph) is True


def test_validate_graph_missing_key():
    """Test validation fails with missing key."""
    graph = {
        "claimed_identity": "Test",
        "requested_action": "Test",
        "urgency_signals": [],
        "authority_signals": [],
        # missing payload_targets
    }
    assert validate_graph(graph) is False


def test_validate_graph_wrong_type():
    """Test validation fails with wrong type."""
    graph = {
        "claimed_identity": "Test",
        "requested_action": "Test",
        "urgency_signals": "not a list",  # should be list
        "authority_signals": [],
        "payload_targets": []
    }
    assert validate_graph(graph) is False


def test_fallback_extract_phishing():
    """Test fallback extraction detects phishing signals."""
    record = EmailRecord(
        sender="security@payroll-services.xyz",
        reply_to="verify@malicious-domain.com",
        return_path="bounce@spammer.net",
        subject="URGENT: Your Account Has Been Compromised!",
        date=None,
        body_text="URGENT SECURITY ALERT! Your account has been compromised! Immediate action required. Click the link below to verify your identity and secure your account: https://verify-account-now.malicious-site.com/login?token=abc123",
        links=["https://verify-account-now.malicious-site.com/login?token=abc123"],
        attachments=[]
    )

    graph = _fallback_extract(record)

    # Should detect urgency signals (case-insensitive)
    urgency_lower = [s.lower() for s in graph["urgency_signals"]]
    assert "urgent" in urgency_lower
    assert "immediate" in urgency_lower or "action required" in urgency_lower

    # Should detect authority signals
    authority_lower = [s.lower() for s in graph["authority_signals"]]
    assert "security" in authority_lower

    # Should have links as payload targets
    assert "https://verify-account-now.malicious-site.com/login?token=abc123" in graph["payload_targets"]

    # Should have valid schema
    assert validate_graph(graph) is True


def test_fallback_extract_legitimate():
    """Test fallback extraction on legitimate email."""
    record = EmailRecord(
        sender="john.doe@company.com",
        reply_to=None,
        return_path=None,
        subject="Quarterly Report Attached",
        date=None,
        body_text="Dear team, please find attached the quarterly report for your review.",
        links=[],
        attachments=[]
    )

    graph = _fallback_extract(record)

    # Should have empty urgency/authority for normal email
    assert len(graph["urgency_signals"]) == 0
    assert len(graph["authority_signals"]) == 0
    assert validate_graph(graph) is True


def test_extract_intent_graph_with_fallback():
    """Test extract_intent_graph returns fallback graph when no API available."""
    record = EmailRecord(
        sender="security@payroll-services.xyz",
        reply_to="verify@malicious-domain.com",
        return_path=None,
        subject="URGENT: Verify Your Account",
        date=None,
        body_text="URGENT: Your account has been compromised! Click here to verify immediately: https://malicious-site.com/verify",
        links=["https://malicious-site.com/verify"],
        attachments=[]
    )

    graph = extract_intent_graph(record)

    # Should return a valid graph (via fallback)
    assert validate_graph(graph) is True
    
    # Check urgency signals (case-insensitive)
    urgency_lower = [s.lower() for s in graph["urgency_signals"]]
    assert "urgent" in urgency_lower
    assert "https://malicious-site.com/verify" in graph["payload_targets"]


def test_extract_intent_graph_empty_email():
    """Test extract_intent_graph with minimal email."""
    record = EmailRecord(
        sender="test@example.com",
        reply_to=None,
        return_path=None,
        subject="Test",
        date=None,
        body_text="This is a test email.",
        links=[],
        attachments=[]
    )

    graph = extract_intent_graph(record)

    # Should return valid graph structure (may be empty via fallback)
    assert validate_graph(graph) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])