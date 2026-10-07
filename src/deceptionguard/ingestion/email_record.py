"""Email record data model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EmailRecord:
    """Parsed email record with extracted fields.

    All fields are extracted from the raw email message.
    The record is immutable (frozen).
    """

    sender: str
    reply_to: str | None
    return_path: str | None
    subject: str | None
    date: str | None
    body_text: str
    links: list[str] = field(default_factory=list)
    attachments: list[dict[str, str]] = field(default_factory=list)
