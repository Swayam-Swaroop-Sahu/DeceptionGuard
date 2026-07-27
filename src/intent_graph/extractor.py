import json
import logging
import os
import time
from typing import Dict, Optional
from ..ingestion.email_record import EmailRecord
from .schema import validate_graph, INTENT_GRAPH_SCHEMA

logger = logging.getLogger(__name__)

# NVIDIA API Configuration
NVIDIA_API_KEY = os.environ.get(
    "NVIDIA_API_KEY",
    "<YOUR_NVIDIA_API_KEY>"
)
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "openai/gpt-oss-20b"


# Fallback: Local heuristic-based extraction (no API needed)
def _fallback_extract(record: EmailRecord) -> Dict:
    """
    Fallback extraction using keyword-based heuristics.
    Used when LLM API is unavailable or fails.
    """
    body_lower = record.body_text.lower()
    subject_lower = (record.subject or "").lower()
    text = f"{subject_lower} {body_lower}"

    # Urgency keywords
    urgency_keywords = [
        "urgent", "immediate", "asap", "emergency", "critical",
        "24 hours", "24h", "hours left", "deadline", "expire",
        "suspend", "closure", "terminate", "act now", "hurry",
        "limited time", "expires today", "final notice", "last chance"
    ]

    # Authority keywords
    authority_keywords = [
        "security team", "it department", "help desk", "support team",
        "admin", "administrator", "bank", "irs", "government",
        "microsoft", "apple", "google", "amazon", "paypal", "linkedin",
        "facebook", "instagram", "twitter", "github", "gitlab",
        "security", "compliance", "legal", "hr", "human resources",
        "verification", "account team", "billing", "fraud prevention"
    ]

    # Action keywords
    action_keywords = [
        "click", "verify", "confirm", "update", "provide", "enter",
        "submit", "login", "sign in", "download", "open", "visit",
        "go to", "follow", "access", "reset", "change", "validate",
        "authenticate", "unlock", "restore", "activate"
    ]

    # Identity patterns
    identity_patterns = [
        "security team", "support team", "admin team", "it team",
        "help desk", "customer service", "verification team",
        "fraud team", "compliance team", "billing department"
    ]

    urgency_signals = [kw for kw in urgency_keywords if kw in text]
    authority_signals = [kw for kw in authority_keywords if kw in text]

    # Find claimed identity
    claimed_identity = None
    for pattern in identity_patterns:
        if pattern in text:
            claimed_identity = pattern.title()
            break

    # Find requested action
    requested_action = None
    for kw in action_keywords:
        if kw in text:
            idx = text.find(kw)
            context = text[max(0, idx - 20):idx + 50].strip()
            requested_action = context
            break

    # Payload targets are the links
    payload_targets = record.links if record.links else []

    return {
        "claimed_identity": claimed_identity,
        "requested_action": requested_action,
        "urgency_signals": urgency_signals,
        "authority_signals": authority_signals,
        "payload_targets": payload_targets
    }


def _call_nvidia_llm(prompt: str, max_retries: int = 3, timeout: int = 30) -> Optional[str]:
    """
    Call NVIDIA hosted LLM API with retry logic and timeout.

    Args:
        prompt: The prompt to send to the LLM
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds

    Returns:
        LLM response as string, or None if unavailable
    """
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package not installed. Install with: pip install openai")
        return None

    if not NVIDIA_API_KEY:
        logger.warning("No NVIDIA_API_KEY configured.")
        return None

    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY
    )

    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=NVIDIA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                top_p=0.9,
                max_tokens=2048,
                stream=False
            )

            message = completion.choices[0].message
            reasoning = getattr(message, "reasoning_content", None)
            if reasoning:
                logger.debug(f"LLM reasoning: {reasoning[:200]}...")

            return message.content

        except Exception as e:
            logger.warning(
                f"NVIDIA LLM call failed (attempt {attempt + 1}/{max_retries}): {e}"
            )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

    logger.error(f"NVIDIA LLM call failed after {max_retries} attempts")
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


def extract_intent_graph(record: EmailRecord) -> Dict:
    """
    Extract intent graph from an email record using LLM with fallback.

    Priority:
    1. NVIDIA hosted LLM (gpt-oss-20b)
    2. Local heuristic fallback

    Returns validated intent graph matching schema.
    """
    empty_graph = {
        "claimed_identity": None,
        "requested_action": None,
        "urgency_signals": [],
        "authority_signals": [],
        "payload_targets": []
    }

    # Build prompt
    prompt = _build_prompt(record)

    # Try NVIDIA LLM
    response = _call_nvidia_llm(prompt)

    if response:
        try:
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]

            graph = json.loads(cleaned_response.strip())

            if validate_graph(graph):
                logger.info("Successfully extracted intent graph via NVIDIA LLM")
                return graph
            else:
                logger.warning(f"LLM returned invalid graph schema: {graph}")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error processing LLM response: {e}")

    # Fallback to heuristic extraction
    logger.info("Falling back to heuristic-based extraction")
    fallback_graph = _fallback_extract(record)

    if validate_graph(fallback_graph):
        return fallback_graph

    logger.warning("All extraction methods failed, returning empty graph")
    return empty_graph