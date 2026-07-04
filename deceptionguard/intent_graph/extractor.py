import json
import logging
from typing import Dict, Optional
from ..ingestion.email_record import EmailRecord
from .schema import validate_graph, INTENT_GRAPH_SCHEMA

logger = logging.getLogger(__name__)

# Placeholder for LLM provider - can be swapped
def _call_llm(prompt: str, model: str = "gpt-4") -> Optional[str]:
    """
    Placeholder for LLM API call.
    
    TODO: Implement actual LLM call (OpenAI, Anthropic, local model, etc.)
    Requires API key in environment variable.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name to use
        
    Returns:
        LLM response as string, or None if unavailable
    """
    # Check if API key is available
    import os
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("No LLM API key found in environment. Returning empty graph.")
        return None
    
    # TODO: Implement actual LLM call here
    # Example:
    # import openai
    # response = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": prompt}])
    # return response.choices[0].message.content
    
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
    Extract intent graph from an email record using LLM.
    
    On failure, returns empty graph with all fields null/empty.
    """
    # Default empty graph
    empty_graph = {
        "claimed_identity": None,
        "requested_action": None,
        "urgency_signals": [],
        "authority_signals": [],
        "payload_targets": []
    }
    
    # Build prompt
    prompt = _build_prompt(record)
    
    # Try LLM call with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = _call_llm(prompt)
            if response:
                # Parse JSON from response
                # Handle potential markdown code blocks
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0]
                
                graph = json.loads(response.strip())
                
                # Validate against schema
                if validate_graph(graph):
                    return graph
                else:
                    logger.warning(f"LLM returned invalid graph schema: {graph}")
            else:
                logger.warning("LLM returned empty response")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON (attempt {attempt + 1}): {e}")
        except Exception as e:
            logger.warning(f"LLM call failed (attempt {attempt + 1}): {e}")
    
    # Return empty graph on any failure
    logger.info("Returning empty intent graph due to LLM failure or unavailable")
    return empty_graph