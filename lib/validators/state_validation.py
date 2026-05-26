"""State validation module for Isagawa Kernel.

Checks session state for protocol and ceremony compliance.
Extracted from sr_dev-gate-enforcer.py anchor ceremony validation logic.
"""

import json
from pathlib import Path

REQUIRED_CEREMONY_FIELDS = [
    'protocol_read_timestamp',
    'lessons_read_timestamp',
    'actions_reviewed_count',
    'violations_found',
    'next_action_stated',
    'rules_applied',
    'ceremony_output_generated',
]


def check(session_state_path: str) -> list[str]:
    """Check session state for protocol and ceremony compliance.

    Validates that the anchor ceremony has been fully completed by checking:
    - Presence of anchor_ceremony object
    - All required ceremony fields are populated
    - Field types are correct (timestamps as strings)

    Args:
        session_state_path: Path to .claude/state/session_state.json

    Returns:
        List of violation strings (empty list means compliant)

    Examples:
        >>> check(".claude/state/session_state.json")
        []  # All required fields present

        >>> check(".claude/state/session_state.json")  # Missing anchor_ceremony
        ['Missing anchor_ceremony object in session_state.json', ...]
    """
    violations = []

    try:
        with open(session_state_path, 'r') as f:
            session_state = json.load(f)
    except FileNotFoundError:
        return [f"Session state not found at {session_state_path}"]
    except json.JSONDecodeError as e:
        return [f"Session state JSON invalid: {str(e)}"]
    except Exception as e:
        return [f"Session state error: {str(e)}"]

    # Check if anchor_ceremony object exists
    ceremony = session_state.get('anchor_ceremony', {})
    if not ceremony:
        return [
            'Anchor ceremony incomplete: missing anchor_ceremony object',
            'Cannot proceed without proof of full anchor ceremony completion',
        ]

    # Check each required field
    for field in REQUIRED_CEREMONY_FIELDS:
        if field not in ceremony:
            violations.append(f"Anchor ceremony incomplete: missing required field {field}")
        elif ceremony[field] is None or (isinstance(ceremony[field], str) and not ceremony[field]):
            violations.append(f"Anchor ceremony incomplete: {field} is empty")
        elif field.endswith('_timestamp') and not isinstance(ceremony[field], str):
            violations.append(f"Anchor ceremony incomplete: {field} must be a timestamp string, got {type(ceremony[field]).__name__}")

    return violations
