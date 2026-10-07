"""Intent graph extractor — LLM-based and heuristic extraction.

Uses urllib (stdlib) to call any OpenAI-compatible endpoint.
Falls back to heuristic keyword-based extraction when no LLM is configured.
No openai SDK dependency.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from typing import Any

from ..config import LLMConfig, load_config
from ..ingestion.email_record import EmailRecord
from .schema import INTENT_GRAPH_SCHEMA, validate_graph

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Heuristic (offline) extraction
# ---------------------------------------------------------------------------

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

    # Authority keywords
    authority_keywords = [
        "security team", "it department", "help desk", "support team",
        "admin", "administrator", "bank", "irs", "government",
        "microsoft", "apple", "google", "amazon", "paypal", "linkedin",
        "facebook", "instagram", "twitter", "github", "gitlab",
        "security", "compliance", "legal", "hr", "human resources",
        "verification", "account team", "billing", "fraud prevention",
    ]

    # Action keywords
    action_keywords = [
        "click", "verify", "confirm", "update", "provide", "enter",
        "submit", "login", "sign in", "download", "open", "visit",
        "go to", "follow", "access", "reset", "change", "validate",
        "authenticate", "unlock", "restore", "activate",
    ]

    # Identity patterns
    identity_patterns = [
        "security team", "support team", "admin team", "it team",
        "help desk", "customer service", "verification team",
        "fraud team", "compliance team", "billing department",
    ]

    urgency_signals = [kw for kw in urgency_keywords if kw in text]
    authority_signals = [kw for kw in authority_keywords if kw in text]

    # Find claimed identity
    claimed_identity: str | None = None
    for pattern in identity_patterns:
        if pattern in text:
            claimed_identity = pattern.title()
            break

    # Find requested action
    requested_action: str | None = None
    for kw in action_keywords:
        if kw in text:
            idx = text.find(kw)
            context = text[max(0, idx - 20) : idx + 50].strip()
            requested_action = context
            break

    # Payload targets are the links
    payload_targets = list(record.links) if record.links else []

    return {
        "claimed_identity": claimed_identity,
        "requested_action": requested_action,
        "urgency_signals": urgency_signals,
        "authority_signals": authority_signals,
        "payload_targets": payload_targets,
    }


# ---------------------------------------------------------------------------
# LLM extraction via urllib (OpenAI-compatible API)
# ---------------------------------------------------------------------------

def _call_llm(
    prompt: str,
    llm_config: LLMConfig,
) -> str | None:
    """Call an OpenAI-compatible LLM endpoint using urllib.

    Args:
        prompt: The prompt to send to the LLM.
        llm_config: LLM configuration with endpoint details.

    Returns:
        LLM response content as string, or None if unavailable.
    """
    if not llm_config.is_configured:
        return None

    url = f"{llm_config.base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {llm_config.api_key}",
    }
    payload = json.dumps({
        "model": llm_config.model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": 2048,
        "stream": False,
    }).encode("utf-8")

    for attempt in range(llm_config.max_retries):
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=llm_config.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]

        except (urllib.error.URLError, urllib.error.HTTPError, OSError, KeyError) as e:
            logger.warning(
                "LLM call failed (attempt %d/%d): %s",
                attempt + 1,
                llm_config.max_retries,
                e,
            )
            if attempt < llm_config.max_retries - 1:
                time.sleep(2**attempt)  # Exponential backoff

    logger.error("LLM call failed after %d attempts", llm_config.max_retries)
    return None


def _build_prompt(record: EmailRecord) -> str:
    """Build the prompt for intent extraction."""
    return f"""Analyze this email and extract the intent graph as JSON.

Email:
From: {record.sender}
Reply-To: {record.reply_to or 'N/A'}
Return-Path: {record.return_path or 'N/A'}
Subject: {record.subject or 'N/A'}
Date: {record.date or 'N/A'}

Body:
{record.body_text}

Links found: {record.links}

Extract the following as JSON:
- claimed_identity: Who the sender claims to be (organization, role, etc.) or null
- requested_action: What action the sender wants the recipient to take, or null
- urgency_signals: List of phrases indicating urgency (e.g., "urgent", "immediate", "24 hours")
- authority_signals: List of phrases indicating authority (e.g., "security team", "IRS", "bank")
- payload_targets: List of URLs, domains, or actions that are the payload target

Return ONLY valid JSON matching this schema:
{json.dumps(INTENT_GRAPH_SCHEMA, indent=2)}"""


def extract_intent_graph(
    record: EmailRecord,
    llm_config: LLMConfig | None = None,
) -> dict[str, Any]:
    """Extract intent graph from an email record.

    Priority:
    1. LLM extraction (if configured)
    2. Heuristic fallback (always available)

    Args:
        record: Parsed email record.
        llm_config: LLM configuration. If None, loads from config.

    Returns:
        Validated intent graph dict.
    """
    empty_graph: dict[str, Any] = {
        "claimed_identity": None,
        "requested_action": None,
        "urgency_signals": [],
        "authority_signals": [],
        "payload_targets": [],
    }

    # Resolve LLM config
    if llm_config is None:
        try:
            cfg = load_config(load_env=False)
            llm_config = cfg.llm
        except Exception:
            llm_config = LLMConfig()

    # If no API key configured, skip LLM entirely and use fallback
    if not llm_config.is_configured:
        logger.info("No LLM API key configured, using heuristic fallback")
        fallback_graph = _fallback_extract(record)
        if validate_graph(fallback_graph):
            return fallback_graph
        logger.warning("All extraction methods failed, returning empty graph")
        return empty_graph

    # Build prompt
    prompt = _build_prompt(record)

    # Try LLM
    response = _call_llm(prompt, llm_config)

    if response:
        try:
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]

            graph = json.loads(cleaned_response.strip())

            if validate_graph(graph):
                logger.info("Successfully extracted intent graph via LLM")
                return graph
            else:
                logger.warning("LLM returned invalid graph schema: %s", graph)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse LLM response as JSON: %s", e)
        except Exception as e:
            logger.warning("Unexpected error processing LLM response: %s", e)

    # Fallback to heuristic extraction
    logger.info("Falling back to heuristic-based extraction")
    fallback_graph = _fallback_extract(record)

    if validate_graph(fallback_graph):
        return fallback_graph

    logger.warning("All extraction methods failed, returning empty graph")
    return empty_graph
