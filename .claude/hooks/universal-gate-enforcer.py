#!/usr/bin/env python3
"""
Universal Gate Enforcer - Smart gate that blocks AND provides fix data.

Tracks: Write, Edit, Bash (unified action counter - AUTO-INCREMENTED)

Gates:
1. session_started = true
2. needs_learn = false (must learn after fix)
3. anchored = true
4. actions_since_anchor <= limit (AUTO-INCREMENTED by hook, not agent)
5. anchor_token_confirmed = true (if pending_anchor_token exists)

Gate 5 prevents quick-anchoring: when the hook blocks at the action limit,
it generates a random token. The anchor command must read this token and
confirm it. If the agent just flips anchored: true without running the
full anchor, the token won't be confirmed and the hook blocks again.

Counter logic:
- ALL Bash commands increment (safe or not)
- Write/Edit to .claude/ paths do NOT increment (infrastructure)
- Write/Edit to project files DO increment

Gate logic:
- Safe Bash commands skip gate checks (never blocked) but still increment
- .claude/ Write/Edit skip everything (no gate, no increment)
- Everything else: gate checks + increment

Learn triggers (set by other mechanisms):
- Test failure (PostToolUse hook on Bash)
- Anchor violation (self-catch via /kernel/anchor Part B)
"""

import json
import os
import sys
import uuid
from pathlib import Path

# Resolve state dir relative to this hook's location (.claude/hooks/)
# so subagents in child workspaces hit their own state, not the parent's.
_HOOK_DIR = Path(__file__).resolve().parent          # .claude/hooks/
_WORKSPACE_ROOT = _HOOK_DIR.parent.parent            # workspace root
STATE_DIR = _WORKSPACE_ROOT / '.claude' / 'state'
SESSION_STATE = STATE_DIR / 'session_state.json'

# Bash commands that are always allowed through gates (read-only / safe)
# NOTE: These still increment the counter — they just don't get blocked.
SAFE_BASH_PREFIXES = (
    'ls', 'cat', 'head', 'tail', 'grep', 'find', 'pwd', 'echo',
    'git status', 'git log', 'git diff', 'git show', 'git branch',
    'node --version', 'npm --version', 'python --version',
    'which', 'where', 'type',
)


def get_domain_state_file(domain: str) -> Path:
    return STATE_DIR / f'{domain}_workflow.json'


def read_state(state_file: Path) -> dict:
    if not state_file.exists():
        return {}
    try:
        return json.loads(state_file.read_text())
    except:
        return {}


def write_state(state_file: Path, state: dict):
    """Write state back to file."""
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except:
        pass  # Best effort - don't block on write failure


def smart_block(missing: str, fix_command: str, fix_description: str):
    message = f"""BLOCKED: {missing}

FIX:
1. Invoke {fix_command}
2. {fix_description}
3. Then retry your command

Command: {fix_command}
"""
    sys.stderr.write(message)
    sys.exit(2)


def is_safe_bash(command: str) -> bool:
    """Check if bash command is read-only/safe."""
    cmd = command.strip().lower()
    for prefix in SAFE_BASH_PREFIXES:
        if cmd.startswith(prefix.lower()):
            return True
    return False


def check_and_increment_counter(session_state: dict, safe_bash: bool) -> int:
    """Check limit THEN increment. Returns new count. Blocks if AT limit (before incrementing).
    When blocking, generates an anchor token that the anchor command must confirm."""
    domain = session_state.get('domain')
    if not domain:
        return 0

    domain_state = read_state(get_domain_state_file(domain))
    if not domain_state:
        return 0

    actions_limit = domain_state.get('actions_limit', 10)
    actions_since = domain_state.get('actions_since_anchor', 0)

    # Check limit BEFORE incrementing — block if AT limit (not after)
    # Safe bash never triggers the block but still increments
    if not safe_bash and actions_since >= actions_limit:
        # Generate anchor token — anchor command must confirm this
        token = str(uuid.uuid4())[:8]
        session_state['pending_anchor_token'] = token
        session_state['anchor_token_confirmed'] = False
        write_state(SESSION_STATE, session_state)

        smart_block(
            missing=f"{actions_limit} actions since last anchor ({actions_since} actions). Token: {token}",
            fix_command="/kernel/anchor",
            fix_description=f"This re-centers on protocol and resets counter. Anchor token: {token}"
        )

    # Increment AFTER check passes (action will proceed)
    actions_since += 1
    domain_state['actions_since_anchor'] = actions_since
    write_state(get_domain_state_file(domain), domain_state)

    return actions_since


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    tool_input = data.get('tool_input', {})

    # Only gate Edit, Write, Bash
    if tool_name not in ('Write', 'Edit', 'Bash'):
        sys.exit(0)

    # For Write/Edit to .claude/ paths: skip everything (no gate, no increment)
    if tool_name in ('Write', 'Edit'):
        file_path = tool_input.get('file_path', '').replace('\\', '/')
        if '/.claude/' in file_path or file_path.startswith('.claude/'):
            sys.exit(0)

    # Determine if this is a safe bash command
    safe_bash = False
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        safe_bash = is_safe_bash(command)

    # Read session state
    session_state = read_state(SESSION_STATE)

    # Gate checks — safe bash skips these (never blocked) but still increments below
    if not safe_bash:
        # Gate 1: Session started?
        if not session_state.get('session_started'):
            smart_block(
                missing="Session not started",
                fix_command="/kernel/session-start",
                fix_description="This initializes the session"
            )

        # Gate 2: Needs learn? (must invoke learn before continuing)
        if session_state.get('needs_learn'):
            reason = session_state.get('needs_learn_reason', 'unknown')
            smart_block(
                missing=f"Lesson not recorded (trigger: {reason})",
                fix_command="/kernel/learn",
                fix_description="Record what you learned from the fix"
            )

        # Gate 3: Anchored?
        domain = session_state.get('domain')
        if domain:
            domain_state = read_state(get_domain_state_file(domain))
            if not domain_state.get('anchored'):
                smart_block(
                    missing="Protocol not anchored",
                    fix_command="/kernel/anchor",
                    fix_description="This reads protocol and updates state"
                )

        # Gate 5: Anchor token confirmed?
        # Prevents quick-anchoring — if a token was issued, anchor must confirm it
        if session_state.get('pending_anchor_token') and not session_state.get('anchor_token_confirmed'):
            token = session_state.get('pending_anchor_token')
            smart_block(
                missing=f"Anchor not completed properly (token {token} not confirmed)",
                fix_command="/kernel/anchor",
                fix_description=f"Run FULL anchor. Read the token '{token}' from session_state.json and confirm it in your anchor output"
            )

    # Gate 4 + AUTO-INCREMENT: check limit then increment
    # Blocks at limit BEFORE incrementing — no off-by-one
    check_and_increment_counter(session_state, safe_bash)

    sys.exit(0)


if __name__ == '__main__':
    main()
