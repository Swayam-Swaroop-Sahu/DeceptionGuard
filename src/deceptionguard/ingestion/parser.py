"""Email parser — parse .eml and .mbox files into EmailRecord objects.

Uses only the Python standard library (email, re, pathlib).
"""

from __future__ import annotations

import re
from email import message_from_bytes, message_from_string
from email.policy import default
from typing import Any

from .email_record import EmailRecord


class ParseError(Exception):
    """Raised when email parsing fails due to malformed/incomplete input."""


def _extract_links(text: str) -> list[str]:
    """Extract URLs from text using regex."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def _get_body_text(msg: Any) -> str:
    """Extract text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore")
            elif content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    # Simple HTML to text conversion
                    html = payload.decode(errors="ignore")
                    # Remove script and style elements
                    html = re.sub(
                        r"<(script|style)[^>]*>.*?</\1>",
                        "",
                        html,
                        flags=re.DOTALL | re.IGNORECASE,
                    )
                    # Replace <br> tags with newlines
                    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
                    # Remove remaining tags
                    html = re.sub(r"<[^>]+>", "", html)
                    return html
        return ""
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore")
        return ""


def _get_attachments(msg: Any) -> list[dict[str, str]]:
    """Extract attachment info from email message."""
    attachments: list[dict[str, str]] = []
    if msg.is_multipart():
        for part in msg.walk():
            disposition = part.get("Content-Disposition", "")
            if "attachment" in disposition:
                filename = part.get_filename()
                mime_type = part.get_content_type()
                if filename:
                    attachments.append({"filename": filename, "mime_type": mime_type})
    return attachments


def _parse_email_message(msg: Any) -> EmailRecord:
    """Internal shared logic: parse an email.message.Message into an EmailRecord."""
    sender = msg.get("From", "")
    if not sender:
        raise ParseError("Missing required 'From' header")

    reply_to = msg.get("Reply-To")
    return_path = msg.get("Return-Path")
    subject = msg.get("Subject")
    date = msg.get("Date")

    body_text = _get_body_text(msg)
    links = _extract_links(body_text)
    attachments = _get_attachments(msg)

    return EmailRecord(
        sender=sender,
        reply_to=reply_to,
        return_path=return_path,
        subject=subject,
        date=date,
        body_text=body_text,
        links=links,
        attachments=attachments,
    )


def parse_eml(path: str) -> EmailRecord:
    """Parse a single .eml file and return an EmailRecord.

    Args:
        path: Path to the .eml file.

    Returns:
        Parsed EmailRecord.

    Raises:
        ParseError: If the file cannot be read or parsed.
    """
    try:
        with open(path, "rb") as f:
            msg = message_from_bytes(f.read(), policy=default)
    except OSError as e:
        raise ParseError(f"Failed to read file: {e}") from e

    return _parse_email_message(msg)


def parse_eml_string(raw_text: str) -> EmailRecord:
    """Parse raw email text (string) and return an EmailRecord.

    Args:
        raw_text: Raw email content as a string (RFC 5322 format).

    Returns:
        EmailRecord with parsed fields.

    Raises:
        ParseError: If the input is malformed or missing required headers.
    """
    if not raw_text or not raw_text.strip():
        raise ParseError("Empty input: cannot parse email from empty string")

    try:
        msg = message_from_string(raw_text, policy=default)
    except Exception as e:
        raise ParseError(f"Failed to parse email: {e}") from e

    return _parse_email_message(msg)


def parse_mbox(path: str) -> list[EmailRecord]:
    """Parse an mbox file and return a list of EmailRecords.

    Args:
        path: Path to the .mbox file.

    Returns:
        List of parsed EmailRecord objects.
    """
    records: list[EmailRecord] = []
    with open(path, "rb") as f:
        content = f.read().decode(errors="ignore")

    # Simple mbox parsing - split by "From " lines
    # Mbox format: each message starts with "From " at beginning of line
    messages = re.split(r"\n(?=From )", content)

    for msg_text in messages:
        if not msg_text.strip():
            continue
        try:
            msg = message_from_string(msg_text, policy=default)

            sender = msg.get("From", "")
            reply_to = msg.get("Reply-To")
            return_path = msg.get("Return-Path")
            subject = msg.get("Subject")
            date = msg.get("Date")

            body_text = _get_body_text(msg)
            links = _extract_links(body_text)
            attachments = _get_attachments(msg)

            records.append(
                EmailRecord(
                    sender=sender,
                    reply_to=reply_to,
                    return_path=return_path,
                    subject=subject,
                    date=date,
                    body_text=body_text,
                    links=links,
                    attachments=attachments,
                )
            )
        except Exception:
            # Skip malformed messages
            continue

    return records
