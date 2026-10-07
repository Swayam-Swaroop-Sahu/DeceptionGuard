import mailbox
import re
from email import message_from_bytes, message_from_string
from email.message import EmailMessage
from email.policy import default
from typing import Any

from .email_record import EmailRecord
from .html_parser import parse_html_content
from .normalize import normalize_text


class ParseError(Exception):
    """Raised when email parsing fails due to malformed/incomplete input."""
    pass


def _extract_links_from_text(text: str) -> list[tuple[str, str]]:
    """Extract URLs from plaintext as (url, url) tuples for consistency."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return [(url, url) for url in urls]


def _extract_received_chain(msg: EmailMessage) -> list[str]:
    """Extract all Received headers in order."""
    return [str(v).strip() for v in msg.get_all("Received", [])]


def _extract_auth_results(msg: EmailMessage) -> dict[str, str]:
    """Extract Authentication-Results into a dict of verdicts."""
    auth_header = msg.get("Authentication-Results", "")
    if not auth_header:
        return {}

    results = {}
    auth_str = str(auth_header).lower()

    # Simple regex extraction for spf, dkim, dmarc
    for method in ["spf", "dkim", "dmarc"]:
        match = re.search(fr'{method}=([a-z]+)', auth_str)
        if match:
            results[method] = match.group(1)

    return results


def _get_attachments(msg: EmailMessage) -> list[dict[str, Any]]:
    """Extract detailed attachment info."""
    attachments = []

    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue

        disposition = part.get("Content-Disposition", "")
        if not disposition or "attachment" not in str(disposition).lower():
            # Sometimes attachments don't have disposition but have a filename
            if not part.get_filename():
                continue

        filename = part.get_filename()
        if not filename:
            filename = "unknown_attachment"

        mime_type = part.get_content_type()

        # Calculate size (length of payload)
        payload = part.get_payload(decode=True)
        size = len(payload) if payload else 0

        # Check extensions
        ext_parts = filename.lower().split('.')
        ext = ext_parts[-1] if len(ext_parts) > 1 else ""
        double_ext = len(ext_parts) > 2 and ext in ["exe", "scr", "pif", "cmd", "bat", "js", "vbs"]

        # Simple extension mismatch check (compare mime type to ext)
        ext_mismatch = False
        if ext in ["exe", "dll"] and "application/x-msdownload" not in mime_type and "application/octet-stream" not in mime_type or ext in ["pdf"] and "pdf" not in mime_type and "octet-stream" not in mime_type:
            ext_mismatch = True

        attachments.append({
            "filename": filename,
            "mime_type": mime_type,
            "size": size,
            "extension_mismatch": ext_mismatch,
            "double_extension": double_ext
        })

    return attachments


def _parse_email_message(msg: EmailMessage) -> EmailRecord:
    """Parse an EmailMessage object into an EmailRecord v2."""
    sender = str(msg.get("From", ""))
    if not sender:
        raise ParseError("Missing required 'From' header")

    reply_to = str(msg.get("Reply-To", "")) if msg.get("Reply-To") else None
    return_path = str(msg.get("Return-Path", "")) if msg.get("Return-Path") else None
    message_id = str(msg.get("Message-ID", "")) if msg.get("Message-ID") else None
    subject = str(msg.get("Subject", "")) if msg.get("Subject") else None
    date = str(msg.get("Date", "")) if msg.get("Date") else None

    received_chain = _extract_received_chain(msg)
    auth_results = _extract_auth_results(msg)

    # Body parsing
    body_text_parts = []
    hidden_text_parts = []
    links = []

    # We prioritize HTML. If HTML exists, we parse it. Otherwise, text/plain.
    has_html = False
    html_content = ""
    text_content = ""

    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue

        content_type = part.get_content_type()
        disposition = str(part.get("Content-Disposition", "")).lower()

        if "attachment" in disposition:
            continue

        payload = part.get_payload(decode=True)
        if not payload:
            continue

        text = payload.decode(errors="ignore")

        if content_type == "text/html":
            has_html = True
            html_content += text + " "
        elif content_type == "text/plain":
            text_content += text + " "

    if text_content:
        body_text_parts.append(text_content.strip())
        links.extend(_extract_links_from_text(text_content))

    if has_html:
        visible, hidden, html_links = parse_html_content(html_content)
        body_text_parts.append(visible)
        hidden_text_parts.append(hidden)
        links.extend(html_links)

    raw_body = " ".join(body_text_parts)
    raw_hidden = " ".join(hidden_text_parts)

    # Normalize text
    norm_body, bidi1, zw1 = normalize_text(raw_body)
    norm_hidden, bidi2, zw2 = normalize_text(raw_hidden)

    has_bidi_controls = bidi1 or bidi2
    has_zero_width = zw1 or zw2

    attachments = _get_attachments(msg)

    return EmailRecord(
        sender=sender,
        reply_to=reply_to,
        return_path=return_path,
        message_id=message_id,
        subject=subject,
        date=date,
        body_text=norm_body,
        hidden_text=norm_hidden,
        has_bidi_controls=has_bidi_controls,
        has_zero_width=has_zero_width,
        received_chain=received_chain,
        auth_results=auth_results,
        links=links,
        attachments=attachments
    )


def parse_eml(path: str) -> EmailRecord:
    """Parse a single .eml file."""
    try:
        with open(path, "rb") as f:
            msg = message_from_bytes(f.read(), policy=default)
    except OSError as e:
        raise ParseError(f"Failed to read file: {e}") from e

    return _parse_email_message(msg)


def parse_eml_string(raw_text: str) -> EmailRecord:
    """Parse raw email text."""
    if not raw_text or not raw_text.strip():
        raise ParseError("Empty input: cannot parse email from empty string")

    try:
        msg = message_from_string(raw_text, policy=default)
    except Exception as e:
        raise ParseError(f"Failed to parse email: {e}") from e

    return _parse_email_message(msg)


def parse_mbox(path: str) -> list[EmailRecord]:
    """Parse an mbox file robustly using mailbox streaming."""
    records = []

    # The built-in mailbox module handles streaming implicitly
    # It reads message boundaries without loading everything into memory at once
    # However, list(mbox) would load all, so we iterate
    try:
        mbox = mailbox.mbox(path)
        for msg in mbox:
            try:
                # Convert mailbox.Message to email.message.EmailMessage for modern policy
                # mailbox.mbox yields legacy Messages. We parse it back as bytes.
                msg_bytes = msg.as_bytes()
                modern_msg = message_from_bytes(msg_bytes, policy=default)
                record = _parse_email_message(modern_msg)
                records.append(record)
            except Exception:
                # Skip malformed messages inside mbox
                continue
    except Exception as e:
        print(f"Failed to parse mbox {path}: {e}")

    return records
