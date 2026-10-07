from unittest.mock import MagicMock

from deceptionguard.config import LLMConfig
from deceptionguard.ingestion.email_record import EmailRecord
from deceptionguard.intent_graph.extractor import _fallback_extract, extract_intent_graph
from deceptionguard.intent_graph.schema import validate_graph


def test_validate_graph_valid():
    """Test validation of a valid intent graph."""
    graph = {
        "urgency_pressure": True,
        "financial_request": False,
        "action_requested": "Click here",
        "deception_tone": "fear",
        "trust_abuse": "impersonating security"
    }
    assert validate_graph(graph) is True

def test_validate_graph_none_values():
    """Test validation with None values."""
    graph = {
        "urgency_pressure": False,
        "financial_request": False,
        "action_requested": None,
        "deception_tone": None,
        "trust_abuse": None
    }
    assert validate_graph(graph) is True

    # Pydantic fills defaults for missing keys, so we test something that can't be cast.
    graph = {
        "urgency_pressure": "this is not a bool and can't be cast to one",
    }
    assert validate_graph(graph) is False

def test_validate_graph_wrong_type():
    """Test validation fails with wrong type."""
    graph = {
        "urgency_pressure": [1, 2, 3], # wrong type
        "financial_request": False,
        "action_requested": None,
        "deception_tone": None,
        "trust_abuse": None
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
        body_text="URGENT SECURITY TEAM ALERT! Please pay the invoice immediately.",
        links=[],
        attachments=[]
    )
    graph = _fallback_extract(record)

    assert graph["urgency_pressure"] is True
    assert graph["financial_request"] is True
    assert graph["deception_tone"] == "fear"
    assert "security team" in (graph["trust_abuse"] or "")
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

    assert graph["urgency_pressure"] is False
    assert graph["financial_request"] is False
    assert graph["deception_tone"] == "curiosity" # "attached"
    assert validate_graph(graph) is True

from unittest.mock import patch


def test_extract_intent_graph_llm():
    """Test extract_intent_graph uses urllib.request."""
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

    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"choices": [{"message": {"content": "{\\"urgency_pressure\\": true, \\"financial_request\\": false, \\"action_requested\\": \\"click\\", \\"deception_tone\\": \\"neutral\\", \\"trust_abuse\\": null}"}}]}'

    config = LLMConfig(api_key="sk-test", model="gpt-4o-mini")

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        graph = extract_intent_graph(record, llm_config=config)

    assert graph["urgency_pressure"] is True
    assert graph["action_requested"] == "click"
    mock_urlopen.assert_called_once()

def test_extract_intent_graph_llm_failure():
    """Test extract_intent_graph falls back when LLM fails."""
    record = EmailRecord(
        sender="test@example.com",
        reply_to=None,
        return_path=None,
        subject="URGENT",
        date=None,
        body_text="Please wire the money.",
        links=[],
        attachments=[]
    )

    config = LLMConfig(api_key="sk-test", model="gpt-4o-mini")

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = Exception("API Error")
        graph = extract_intent_graph(record, llm_config=config)

    # Should fall back to heuristic
    assert graph["urgency_pressure"] is True
    assert graph["financial_request"] is True
