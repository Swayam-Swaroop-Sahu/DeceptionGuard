from typing import Any

from pydantic import BaseModel, Field


class IntentGraph(BaseModel):
    """Structured intent extracted from an email."""

    urgency_pressure: bool = Field(
        default=False,
        description="True if the email uses language designed to create a sense of urgency or pressure."
    )
    financial_request: bool = Field(
        default=False,
        description="True if the email asks for money, payments, wire transfers, or financial information."
    )
    action_requested: str | None = Field(
        default=None,
        description="The primary action requested of the user (e.g., 'click link', 'download', 'reply'). Null if none."
    )
    deception_tone: str | None = Field(
        default=None,
        description="The primary psychological tone used (e.g., 'fear', 'greed', 'curiosity', 'helpful'). Null if neutral."
    )
    trust_abuse: str | None = Field(
        default=None,
        description="How the email attempts to abuse trust (e.g., 'impersonating authority', 'fake colleague'). Null if no abuse."
    )

def validate_graph(graph: dict[str, Any]) -> bool:
    """Validate that a dict matches the IntentGraph schema."""
    try:
        IntentGraph.model_validate(graph)
        return True
    except Exception:
        return False
