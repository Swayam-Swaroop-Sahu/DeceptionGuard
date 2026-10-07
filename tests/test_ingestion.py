import pytest
from pathlib import Path
from deceptionguard.ingestion.parser import parse_eml, parse_mbox
from deceptionguard.ingestion.email_record import EmailRecord


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_legit_eml():
    """Test parsing a legitimate email."""
    record = parse_eml(str(FIXTURES_DIR / "legit_email.eml"))
    
    assert isinstance(record, EmailRecord)
    assert "john.doe@company.com" in record.sender
    assert record.reply_to is None
    assert record.return_path is None
    assert record.subject == "Quarterly Report Attached"
    assert "quarterly report" in record.body_text.lower()
    assert "https://company.com/reports/q4-2023" in record.links
    assert len(record.attachments) == 0


def test_parse_phishing_eml():
    """Test parsing a phishing email."""
    record = parse_eml(str(FIXTURES_DIR / "phishing_email.eml"))
    
    assert isinstance(record, EmailRecord)
    assert "security@payroll-services.xyz" in record.sender
    assert record.reply_to == "verify@malicious-domain.com"
    assert record.return_path == "bounce@spammer.net"
    assert record.subject == "URGENT: Your Account Has Been Compromised!"
    assert "compromised" in record.body_text.lower()
    assert "https://verify-account-now.malicious-site.com/login?token=abc123" in record.links
    assert len(record.attachments) == 0


def test_parse_mbox():
    """Test parsing an mbox file with multiple emails."""
    records = parse_mbox(str(FIXTURES_DIR / "mixed_mbox.mbox"))
    
    assert isinstance(records, list)
    assert len(records) == 4
    
    # First email - legitimate
    assert "john.doe@company.com" in records[0].sender
    assert records[0].subject == "Quarterly Report Attached"
    
    # Second email - phishing
    assert "security@payroll-services.xyz" in records[1].sender
    assert records[1].subject == "URGENT: Your Account Has Been Compromised!"
    assert records[1].reply_to == "verify@malicious-domain.com"
    
    # Third email - legitimate
    assert "alice@company.com" in records[2].sender
    assert records[2].subject == "Meeting Reminder: Project Kickoff"
    
    # Fourth email - phishing
    assert "admin@fake-bank.com" in records[3].sender
    assert records[3].subject == "Important: Verify Your Banking Information"
    assert records[3].reply_to == "verify@phishing-site.net"
    
    # Check links are extracted
    assert len(records[0].links) == 1
    assert len(records[1].links) == 1
    assert len(records[2].links) == 1
    assert len(records[3].links) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])