#!/usr/bin/env python3
"""
Auto-approve ALL writes to .claude/ directory.

Claude Code 2.1+ protects .claude/ from writes even in bypassPermissions mode.
Only .claude/commands/, .claude/agents/, and .claude/skills/ are exempt by default.

The kernel needs full write access to .claude/ for:
- state/          (session-start, anchor, complete, hook counter)
- lessons/        (learn loop)
- protocols/      (domain-setup, learn updates)
- hooks/          (domain-setup, learn updates)
- references/     (domain-setup)
- settings*.json  (domain-setup wires hooks)

This hook auto-approves ALL .claude/ writes via PermissionRequest.
"""

import json
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_name = data.get('tool_name', '')
if tool_name not in ('Write', 'Edit'):
    sys.exit(0)

hook_event = data.get('hook_event_name', '')
tool_input = data.get('tool_input', {})
file_path = tool_input.get('file_path', '').replace('\\', '/')

# Approve any write to .claude/ directory
if '.claude/' in file_path:
    if hook_event == 'PermissionRequest':
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": "allow"
                }
            }
        }
    else:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }
    print(json.dumps(result))
    sys.exit(0)

# Not a .claude/ path — let normal permission flow handle it
sys.exit(0)
