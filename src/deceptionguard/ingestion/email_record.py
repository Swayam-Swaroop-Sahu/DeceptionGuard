"""Email record data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EmailRecord:
    """Parsed email record with extracted fields.

    All fields are extracted from the raw email message.
    The record is immutable (frozen).
    """

    sender: str
    reply_to: str | None = None
    return_path: str | None = None
    message_id: str | None = None
    subject: str | None = None
    date: str | None = None

    # Body text
    body_text: str = ""
    hidden_text: str = ""

    # Normalization flags
    has_bidi_controls: bool = False
    has_zero_width: bool = False

    # Advanced metadata
    received_chain: list[str] = field(default_factory=list)
    auth_results: dict[str, str] = field(default_factory=dict)

    # (anchor_text, href)
    links: list[tuple[str, str]] = field(default_factory=list)

    # Attachments: name, mime_type, size, extension_mismatch, double_extension
    attachments: list[dict[str, Any]] = field(default_factory=list)
