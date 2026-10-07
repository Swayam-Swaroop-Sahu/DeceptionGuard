from pathlib import Path

import pytest

from deceptionguard.ingestion.email_record import EmailRecord
from deceptionguard.ingestion.parser import ParseError, parse_eml, parse_eml_string, parse_mbox

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
    assert any(href == "https://company.com/reports/q4-2023" for _, href in record.links)
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
    assert any(href == "https://verify-account-now.malicious-site.com/login?token=abc123" for _, href in record.links)
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


class TestParseEmlString:
    """Tests for parse_eml_string function."""

    def test_parse_eml_string_normal(self):
        """Test parsing a normal email from string."""
        raw = """From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Date: Mon, 1 Jan 2024 12:00:00 +0000

Hello world, this is a test email.
"""
        record = parse_eml_string(raw)

        assert isinstance(record, EmailRecord)
        assert record.sender == "sender@example.com"
        assert record.subject == "Test Subject"
        assert "test email" in record.body_text.lower()
        assert record.links == []
        assert record.attachments == []

    def test_parse_eml_string_with_links(self):
        """Test parsing email with links in body."""
        raw = """From: sender@example.com
Subject: Check this out

Visit https://example.com and https://test.com/page
"""
        record = parse_eml_string(raw)

        assert len(record.links) == 2
        assert any(href == "https://example.com" for _, href in record.links)
        assert any(href == "https://test.com/page" for _, href in record.links)

    def test_parse_eml_string_no_body(self):
        """Test parsing email with no body text."""
        raw = """From: sender@example.com
Subject: Empty body

"""
        record = parse_eml_string(raw)

        assert isinstance(record, EmailRecord)
        assert record.sender == "sender@example.com"
        assert record.subject == "Empty body"
        assert record.body_text == ""
        assert record.links == []

    def test_parse_eml_string_missing_from_raises(self):
        """Test that missing From header raises ParseError."""
        raw = """Subject: No sender

Body text here.
"""
        with pytest.raises(ParseError, match="Missing required 'From' header"):
            parse_eml_string(raw)

    def test_parse_eml_string_empty_input_raises(self):
        """Test that empty input raises ParseError."""
        with pytest.raises(ParseError, match="Empty input"):
            parse_eml_string("")

        with pytest.raises(ParseError, match="Empty input"):
            parse_eml_string("   \n\t  ")

    def test_parse_eml_string_malformed_raises(self):
        """Test that completely malformed input raises ParseError."""
        # This is not a valid email format at all
        raw = "This is not an email at all, just random text"
        # message_from_string is lenient, but we should still get a record
        # with empty sender, which should raise
        with pytest.raises(ParseError):
            parse_eml_string(raw)

    def test_parse_eml_string_multipart(self):
        """Test parsing a multipart email string."""
        raw = """From: sender@example.com
To: recipient@example.com
Subject: Multipart Test
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=utf-8

Plain text body.
--boundary123
Content-Type: text/html; charset=utf-8

<html><body><p>HTML body.</p></body></html>
--boundary123--
"""
        record = parse_eml_string(raw)

        assert isinstance(record, EmailRecord)
        assert record.sender == "sender@example.com"
        assert record.subject == "Multipart Test"
        assert "Plain text body" in record.body_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
