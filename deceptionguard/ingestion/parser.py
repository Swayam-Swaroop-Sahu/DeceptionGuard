from email import message_from_bytes, message_from_string
from email.policy import default
from typing import List, Optional
import re
from .email_record import EmailRecord


def _extract_links(text: str) -> List[str]:
    """Extract URLs from text using regex."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def _get_body_text(msg) -> str:
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
                    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
                    # Replace <br> tags with newlines
                    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
                    # Remove remaining tags
                    html = re.sub(r'<[^>]+>', '', html)
                    return html
        return ""
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore")
        return ""


def _get_attachments(msg) -> List[dict]:
    """Extract attachment info from email message."""
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            disposition = part.get("Content-Disposition", "")
            if "attachment" in disposition:
                filename = part.get_filename()
                mime_type = part.get_content_type()
                if filename:
                    attachments.append({"filename": filename, "mime_type": mime_type})
    return attachments


def parse_eml(path: str) -> EmailRecord:
    """Parse a single .eml file and return an EmailRecord."""
    with open(path, "rb") as f:
        msg = message_from_bytes(f.read(), policy=default)
    
    sender = msg.get("From", "")
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
        attachments=attachments
    )


def parse_mbox(path: str) -> List[EmailRecord]:
    """Parse an mbox file and return a list of EmailRecords."""
    records = []
    with open(path, "rb") as f:
        content = f.read().decode(errors="ignore")
    
    # Simple mbox parsing - split by "From " lines
    # Mbox format: each message starts with "From " at beginning of line
    messages = re.split(r'\n(?=From )', content)
    
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
            
            records.append(EmailRecord(
                sender=sender,
                reply_to=reply_to,
                return_path=return_path,
                subject=subject,
                date=date,
                body_text=body_text,
                links=links,
                attachments=attachments
            ))
        except Exception:
            # Skip malformed messages
            continue
    
    return records