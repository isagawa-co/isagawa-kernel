#!/usr/bin/env python3
"""
Actions Log Appender — PostToolUse hook that appends to actions_log in session_state.json.

Logs every Edit, Write, and Bash action so anchor Part B has data to review.
Skips .claude/ Write/Edit paths (infrastructure writes don't count as reviewable work).

Entry format:
- Write/Edit: "[tool_name]: [file_path]"
- Bash: "Bash: [first 80 chars of command]"
"""

import json
import sys
from pathlib import Path

_HOOK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _HOOK_DIR.parent.parent
STATE_DIR = _WORKSPACE_ROOT / '.claude' / 'state'
SESSION_STATE = STATE_DIR / 'session_state.json'


def read_state() -> dict:
    if not SESSION_STATE.exists():
        return {}
    try:
        return json.loads(SESSION_STATE.read_text())
    except Exception:
        return {}


def write_state(state: dict):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        SESSION_STATE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    if tool_name not in ('Write', 'Edit', 'Bash'):
        sys.exit(0)

    tool_input = data.get('tool_input', {})

    # Build log entry
    if tool_name in ('Write', 'Edit'):
        file_path = tool_input.get('file_path', '').replace('\\', '/')

        # Skip .claude/ paths — infrastructure, not reviewable work
        if '/.claude/' in file_path or file_path.startswith('.claude/'):
            sys.exit(0)

        # Extract just the filename for brevity
        short_path = file_path.split('/')[-1] if '/' in file_path else file_path
        entry = f"{tool_name}: {short_path}"

    elif tool_name == 'Bash':
        command = tool_input.get('command', '')
        entry = f"Bash: {command[:80]}"

    else:
        sys.exit(0)

    # Append to actions_log
    state = read_state()
    if 'actions_log' not in state:
        state['actions_log'] = []
    state['actions_log'].append(entry)
    write_state(state)

    sys.exit(0)


if __name__ == '__main__':
    main()
