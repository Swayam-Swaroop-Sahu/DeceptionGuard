import pytest
from deceptionguard.intent_graph.schema import validate_graph, INTENT_GRAPH_SCHEMA
from deceptionguard.intent_graph.extractor import extract_intent_graph
from deceptionguard.ingestion.email_record import EmailRecord


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


def test_extract_intent_graph_placeholder():
    """Test extract_intent_graph returns empty graph when no API key."""
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
    
    # Should return empty graph structure
    assert graph == {
        "claimed_identity": None,
        "requested_action": None,
        "urgency_signals": [],
        "authority_signals": [],
        "payload_targets": []
    }
    # Should be valid according to schema
    assert validate_graph(graph) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])