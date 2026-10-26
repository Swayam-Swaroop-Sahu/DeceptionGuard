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


import re

def _fallback_extract(record: EmailRecord) -> dict[str, Any]:
    """Fallback extraction using keyword-based heuristics.

    Used when LLM API is unavailable or not configured.
    """
    body_lower = record.body_text.lower()
    subject_lower = (record.subject or "").lower()
    text = f"{subject_lower} {body_lower}"

    # Urgency keywords
    urgency_keywords = [
        "urgent", "immediate", "immediately", "asap", "emergency", "critical",
        "24 hours", "24h", "hours left", "deadline", "expire", "expires", "expired",
        "suspend", "suspended", "closure", "terminate", "act now", "hurry",
        "limited time", "expires today", "final notice", "last chance",
        "now", "important", "lose access", "compromised", "deactivated",
        "unauthorized", "suspicious", "security alert", "notice", "action required",
        "warning", "attention", "locked", "legal action", "promptly", "reschedule",
        "vulnerability", "patch required", "update now", "claim now", "security"
    ]

    # Exclude standard benign business timing when no high-risk urgency hooks exist
    is_benign_timing = any(
        phrase in text for phrase in [
            "payment due within 30 days", "due within 30 days",
            "within 3-5 business days", "respond within 24 hours", "due by end of month"
        ]
    )
    has_high_risk_urgency = any(
        kw in text for kw in [
            "urgent", "immediately", "compromised", "lose access", "deactivated",
            "suspended", "unauthorized", "security alert", "action required", "legal action"
        ]
    )

    urgency_pressure = (
        any(kw in text for kw in urgency_keywords)
        and (not is_benign_timing or has_high_risk_urgency)
    )

    # Financial keywords
    financial_keywords = [
        "invoice", "payment", "wire", "transfer", "bank", "banking", "account",
        "credit card", "billing", "receipt", "overdue", "fund", "funds",
        "deposit", "salary", "bonus", "payroll", "crypto", "bitcoin",
        "tax", "taxes", "fee", "cost", "subscription", "gift card",
        "reward", "cash", "prize", "refund", "$", "dollar", "off", "pay"
    ]

    # Action keywords
    action_keywords = [
        "click", "verify", "confirm", "update", "provide", "enter",
        "submit", "login", "sign in", "download", "open", "visit",
        "go to", "follow", "access", "reset", "change", "validate",
        "authenticate", "unlock", "restore", "activate", "reply",
        "review", "reschedule", "claim", "apply", "upgrade", "cancel",
        "secure", "resolve", "fix", "take action"
    ]

    # Identity patterns for trust abuse
    identity_patterns = [
        "security team", "support team", "admin team", "it team",
        "help desk", "customer service", "verification team",
        "fraud team", "compliance team", "billing department", "security alert",
        "irs", "internal revenue service", "government", "microsoft", "apple",
        "google", "paypal", "amazon", "netflix", "bank of america", "chase",
        "wells fargo", "facebook", "twitter", "linkedin", "dhl", "fedex",
        "ups", "usps", "slack", "trello", "zoom", "github", "atlassian",
        "dropbox", "adobe"
    ]

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
    fear_triggers = [
        "compromised", "unauthorized", "access", "legal", "deactivated",
        "suspended", "locked", "failed", "vulnerability", "alert", "patch",
        "funds", "secure", "activity", "closure"
    ]
    if urgency_pressure and (financial_request or any(w in text for w in fear_triggers)):
        deception_tone = "fear"
    elif any(
        re.search(r"\b" + re.escape(w) + r"\b", text)
        for w in ["win", "won", "prize", "reward", "gift card", "off", "free", "claim"]
    ):
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

    # Configure provider based on the config
    import os
    api_key = llm_config.api_key or os.environ.get("OPENAI_API_KEY", "")
    api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = llm_config.model

    if not api_key and not os.environ.get("LLM_NO_KEY_REQUIRED"):
        logger.warning("LLM API key missing and not marked as unrequired, using heuristic fallback")
        fallback_graph = _fallback_extract(record)
        if validate_graph(fallback_graph):
            return fallback_graph
        return empty_graph

    try:
        import urllib.error
        import urllib.parse
        import urllib.request

        url = f"{api_base.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=llm_config.timeout) as response:
            resp_body = response.read().decode("utf-8")
            resp_data = json.loads(resp_body)
            content = resp_data["choices"][0]["message"]["content"]

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
