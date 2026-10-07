from typing import Any


def validate_graph(graph: dict[str, Any]) -> bool:
    """Validate that a dict matches the IntentGraph schema."""
    if not isinstance(graph, dict):
        return False

    expected_types = {
        "urgency_pressure": bool,
        "financial_request": bool,
        "action_requested": (str, type(None)),
        "deception_tone": (str, type(None)),
        "trust_abuse": (str, type(None))
    }

    for key, expected_type in expected_types.items():
        if key not in graph:
            return False
        if not isinstance(graph[key], expected_type):
            return False

    return True
