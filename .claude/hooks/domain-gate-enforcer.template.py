#!/usr/bin/env python3
"""{{DOMAIN}} Gate Enforcer - thin orchestrator using shared validators.

Instantiated by /kernel/domain-setup as .claude/hooks/{domain}-gate-enforcer.py
and registered as a second PreToolUse hook (matcher: Edit|Write|Bash) alongside
universal-gate-enforcer.py. The universal hook enforces anchor/state gates
generically; this domain hook adds write-time code-quality and Bash-safety
checks via the kernel's shared lib/validators. Keep it domain-agnostic — any
logic tied to a specific workspace extension (e.g. an intent-chain blocker for
/kernel/backlog) belongs with that extension, NOT in this template.
"""

import json
import os
import sys
from pathlib import Path

_HOOK_DIR = Path(__file__).resolve().parent          # .claude/hooks/
_REPO_ROOT = _HOOK_DIR.parent.parent                 # repo root
STATE_DIR = _REPO_ROOT / '.claude' / 'state'

_agent_id = os.environ.get('KERNEL_AGENT_ID')
if _agent_id:
    SESSION_STATE = STATE_DIR / f'agent-{_agent_id}-session-state.json'
else:
    SESSION_STATE = STATE_DIR / 'session_state.json'

# Resolve the shared validators. Try, in order:
#   (a) {repo_root}/lib          — repos that ship their own copy of lib
#   (b) a sibling isagawa-kernel/lib found by walking up parent directories —
#       repos that sit next to the master kernel (the sr_dev-gate-enforcer.py
#       fallback pattern; also covers git worktrees)
# If neither resolves, fail open (sys.exit(0)) so the hook never hard-blocks a
# repo that simply hasn't wired the validators yet.
_kernel_lib_root = ''
if (_REPO_ROOT / 'lib' / 'validators').is_dir():
    _kernel_lib_root = str(_REPO_ROOT)
else:
    _search = _HOOK_DIR
    while _search != _search.parent:
        _candidate = _search.parent / 'isagawa-kernel'
        if (_candidate / 'lib' / 'validators').is_dir():
            _kernel_lib_root = str(_candidate)
            break
        _search = _search.parent

if not _kernel_lib_root:
    sys.exit(0)
sys.path.insert(0, _kernel_lib_root)

try:
    from lib.validators import code_quality, state_validation, bash_validation, common
except ImportError:
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    tool_input = data.get('tool_input', {})

    if tool_name in ('Write', 'Edit'):
        file_path = tool_input.get('file_path', '').replace('\\', '/')
        if common.should_skip(file_path):
            sys.exit(0)

        violations = state_validation.check(str(SESSION_STATE))
        if violations:
            common.state_block(violations)

        content = tool_input.get('content', '') or tool_input.get('new_string', '')
        if content:
            # Skip code quality checks for HTML files (naturally contain inline scripts)
            if not file_path.endswith('.html'):
                violations = code_quality.check(file_path, content)
                if violations:
                    common.smart_block(violations, "Code quality")

    elif tool_name == 'Bash':
        command = tool_input.get('command', '')
        violations = bash_validation.check(command)
        if violations:
            common.bash_block(violations)

    sys.exit(0)


if __name__ == '__main__':
    main()
