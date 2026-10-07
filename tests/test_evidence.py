from deceptionguard.evidence import (
    Severity,
    detect_all,
    detect_attachment_risks,
    detect_auth_failures,
    detect_sender_mismatch,
    detect_url_risks,
)
from deceptionguard.ingestion.email_record import EmailRecord


def create_mock_record(**kwargs):
    default = {
        "sender": "John <john@example.com>",
        "reply_to": None,
        "return_path": None,
        "message_id": None,
        "subject": "Test",
        "date": "Today",
        "body_text": "Hello",
        "hidden_text": "",
        "has_bidi_controls": False,
        "has_zero_width": False,
        "received_chain": [],
        "auth_results": {},
        "links": [],
        "attachments": []
    }
    default.update(kwargs)
    return EmailRecord(**default)

def test_sender_mismatch():
    # Negative case
    rec = create_mock_record(sender="Support <support@company.com>")
    assert len(detect_sender_mismatch(rec)) == 0

    # Positive case: Display name domain spoofing
    rec2 = create_mock_record(sender="paypal.com <admin@scam.com>")
    evs = detect_sender_mismatch(rec2)
    assert len(evs) >= 1
    assert any(e.evidence_type == "DISPLAY_NAME_DOMAIN_MISMATCH" for e in evs)

    # Positive case: Reply-To mismatch
    rec3 = create_mock_record(sender="admin@company.com", reply_to="hacker@evil.com")
    evs = detect_sender_mismatch(rec3)
    assert len(evs) == 1
    assert evs[0].evidence_type == "REPLY_TO_MISMATCH"

def test_brand_lookalike():
    # The detector is inside detect_sender_mismatch (DISPLAY_NAME_BRAND_MISMATCH) and detect_url_risks
    rec = create_mock_record(sender="PayPal Support <admin@scam.com>")
    evs = detect_sender_mismatch(rec)
    assert len(evs) == 1
    assert evs[0].evidence_type == "DISPLAY_NAME_BRAND_MISMATCH"
    assert evs[0].severity == Severity.CRITICAL

def test_url_risks():
    rec = create_mock_record(
        links=[
            ("Click here", "http://192.168.1.1/login"),  # IP literal
            ("Login", "http://bit.ly/123"), # Shortener
            ("https://paypal.com", "http://paypa1.com"), # Anchor mismatch + Brand typosquatting
            ("Safe", "https://example.com") # Benign
        ]
    )
    evs = detect_url_risks(rec)
    types = [e.evidence_type for e in evs]
    assert "URL_IP_LITERAL" in types
    assert "URL_SHORTENER" in types
    assert "URL_ANCHOR_MISMATCH" in types
    assert "BRAND_TYPOSQUATTING" in types

def test_auth_failures():
    rec = create_mock_record(auth_results={"spf": "fail", "dkim": "pass", "dmarc": "softfail"})
    evs = detect_auth_failures(rec)
    types = [e.evidence_type for e in evs]
    assert "AUTH_SPF_FAILURE" in types
    assert "AUTH_DMARC_FAILURE" in types
    assert "AUTH_DKIM_FAILURE" not in types

def test_attachment_risks():
    rec = create_mock_record(attachments=[
        {"filename": "invoice.pdf.exe", "mime_type": "application/x-msdownload", "size": 1000, "double_extension": True, "extension_mismatch": False},
        {"filename": "doc.pdf", "mime_type": "application/x-msdownload", "size": 1000, "double_extension": False, "extension_mismatch": True}
    ])
    evs = detect_attachment_risks(rec)
    types = [e.evidence_type for e in evs]
    assert "ATTACHMENT_EXECUTABLE" in types
    assert "ATTACHMENT_DOUBLE_EXTENSION" in types
    assert "ATTACHMENT_EXTENSION_MISMATCH" in types

def test_detect_all():
    rec = create_mock_record(
        sender="paypal.com <admin@scam.com>",
        has_zero_width=True,
        hidden_text="Hidden"
    )
    evs = detect_all(rec)
    types = [e.evidence_type for e in evs]
    assert "DISPLAY_NAME_DOMAIN_MISMATCH" in types
    assert "TEXT_OBFUSCATION" in types
    assert "HTML_HIDDEN_TEXT" in types

    # Check serialization
    js = evs[0].to_dict()
    assert isinstance(js["severity"], str)
