"""Intent graph extractor — LLM-based and heuristic extraction.

Uses litellm to call standard endpoints.
Falls back to heuristic keyword-based extraction when no LLM is configured.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..config import LLMConfig, load_config
from ..ingestion.email_record import EmailRecord
from .schema import validate_graph

logger = logging.getLogger(__name__)


def _fallback_extract(record: EmailRecord) -> dict[str, Any]:
    """Fallback extraction using keyword-based heuristics.

    Used when LLM API is unavailable or not configured.
    """
    body_lower = record.body_text.lower()
    subject_lower = (record.subject or "").lower()
    text = f"{subject_lower} {body_lower}"

    # Urgency keywords
    urgency_keywords = [
        "urgent", "immediate", "asap", "emergency", "critical",
        "24 hours", "24h", "hours left", "deadline", "expire",
        "suspend", "closure", "terminate", "act now", "hurry",
        "limited time", "expires today", "final notice", "last chance",
    ]

    # Financial keywords
    financial_keywords = [
        "invoice", "payment", "wire", "transfer", "bank", "account",
        "credit card", "billing", "receipt", "overdue", "fund",
        "deposit", "salary", "bonus", "payroll", "crypto", "bitcoin",
    ]

    # Action keywords
    action_keywords = [
        "click", "verify", "confirm", "update", "provide", "enter",
        "submit", "login", "sign in", "download", "open", "visit",
        "go to", "follow", "access", "reset", "change", "validate",
        "authenticate", "unlock", "restore", "activate", "reply"
    ]

    # Identity patterns for trust abuse
    identity_patterns = [
        "security team", "support team", "admin team", "it team",
        "help desk", "customer service", "verification team",
        "fraud team", "compliance team", "billing department",
        "irs", "government", "microsoft", "apple", "google", "paypal",
    ]

    urgency_pressure = any(kw in text for kw in urgency_keywords)
    financial_request = any(kw in text for kw in financial_keywords)

    # Find requested action
    requested_action = None
    for kw in action_keywords:
        if kw in text:
            idx = text.find(kw)
            context = text[max(0, idx - 10) : idx + 30].strip()
            requested_action = context
            break

    # Determine trust abuse
    trust_abuse = None
    for pattern in identity_patterns:
        if pattern in text:
            trust_abuse = f"impersonating {pattern}"
            break

    # Determine tone heuristically
    deception_tone = None
    if urgency_pressure and financial_request:
        deception_tone = "fear"
    elif "win" in text or "prize" in text or "reward" in text:
        deception_tone = "greed"
    elif "attached" in text or "document" in text:
        deception_tone = "curiosity"

    return {
        "urgency_pressure": urgency_pressure,
        "financial_request": financial_request,
        "action_requested": requested_action,
        "deception_tone": deception_tone,
        "trust_abuse": trust_abuse,
    }


def _build_prompt(record: EmailRecord) -> str:
    """Build the prompt for intent extraction."""
    return f"""Analyze this email and extract the intent graph as JSON.

Email:
From: {record.sender}
Subject: {record.subject or 'N/A'}
Body:
{record.body_text}

Extract the following as JSON:
- urgency_pressure: boolean (True if urgency or pressure is applied)
- financial_request: boolean (True if asking for money, payment, or financial info)
- action_requested: string or null (e.g. 'click link', 'download', 'reply')
- deception_tone: string or null (e.g. 'fear', 'greed', 'curiosity')
- trust_abuse: string or null (e.g. 'impersonating authority', 'fake colleague')

Return ONLY valid JSON.
"""


def extract_intent_graph(
    record: EmailRecord,
    llm_config: LLMConfig | None = None,
) -> dict[str, Any]:
    """Extract intent graph from an email record using litellm.

    Priority:
    1. LLM extraction via litellm (if configured)
    2. Heuristic fallback
    """
    empty_graph: dict[str, Any] = {
        "urgency_pressure": False,
        "financial_request": False,
        "action_requested": None,
        "deception_tone": None,
        "trust_abuse": None,
    }

    if llm_config is None:
        try:
            cfg = load_config(load_env=False)
            llm_config = cfg.llm
        except Exception:
            llm_config = LLMConfig()

    if not llm_config.is_configured:
        logger.info("No LLM API key configured, using heuristic fallback")
        fallback_graph = _fallback_extract(record)
        if validate_graph(fallback_graph):
            return fallback_graph
        return empty_graph

    prompt = _build_prompt(record)

    # Configure litellm based on the config
    import os
    if llm_config.api_key:
        os.environ["OPENAI_API_KEY"] = llm_config.api_key

    # In a real setup, we might set api_base for standard openai compatible endpoints
    # For now, litellm handles "gpt-4o-mini" gracefully if OPENAI_API_KEY is set.

    try:
        import litellm
        response = litellm.completion(
            model=llm_config.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=llm_config.timeout,
            num_retries=llm_config.max_retries
        )

        content = response.choices[0].message.content
        if content:
            graph = json.loads(content.strip())
            if validate_graph(graph):
                return graph
            else:
                logger.warning("LLM returned invalid schema: %s", graph)
    except Exception as e:
        logger.warning("LLM call failed: %s", e)

    # Fallback
    logger.info("Falling back to heuristic-based extraction")
    fallback_graph = _fallback_extract(record)
    if validate_graph(fallback_graph):
        return fallback_graph

    return empty_graph
