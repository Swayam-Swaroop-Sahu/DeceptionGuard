import json
from typing import Any, Dict

INTENT_GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "claimed_identity": {"type": ["string", "null"]},
        "requested_action": {"type": ["string", "null"]},
        "urgency_signals": {"type": "array", "items": {"type": "string"}},
        "authority_signals": {"type": "array", "items": {"type": "string"}},
        "payload_targets": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["claimed_identity", "requested_action", "urgency_signals", 
                 "authority_signals", "payload_targets"]
}

def validate_graph(graph: Dict[str, Any]) -> bool:
    """Validate that the graph matches the schema."""
    required_keys = ["claimed_identity", "requested_action", "urgency_signals", 
                     "authority_signals", "payload_targets"]
    
    # Check all required keys exist
    for key in required_keys:
        if key not in graph:
            return False
    
    # Check types
    if not (graph["claimed_identity"] is None or isinstance(graph["claimed_identity"], str)):
        return False
    if not (graph["requested_action"] is None or isinstance(graph["requested_action"], str)):
        return False
    if not isinstance(graph["urgency_signals"], list):
        return False
    if not all(isinstance(s, str) for s in graph["urgency_signals"]):
        return False
    if not isinstance(graph["authority_signals"], list):
        return False
    if not all(isinstance(s, str) for s in graph["authority_signals"]):
        return False
    if not isinstance(graph["payload_targets"], list):
        return False
    if not all(isinstance(s, str) for s in graph["payload_targets"]):
        return False
    
    return True