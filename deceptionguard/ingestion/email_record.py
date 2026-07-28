from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class EmailRecord:
    sender: str
    reply_to: Optional[str]
    return_path: Optional[str]
    subject: Optional[str]
    date: Optional[str]
    body_text: str
    links: List[str]
    attachments: List[dict]  # fields: filename, mime_type only