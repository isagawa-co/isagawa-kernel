#!/usr/bin/env python3
"""{{DOMAIN}} Gate Enforcer - write-time code-quality and Bash-safety checks.

Instantiated by /kernel/domain-setup as .claude/hooks/{domain}-gate-enforcer.py
and registered as a second PreToolUse hook (matcher: Edit|Write|Bash) alongside
universal-gate-enforcer.py. The universal hook enforces anchor/state gates
generically; this domain hook adds the write-time checks.

Keep it domain-agnostic — any logic tied to a specific workspace extension
(e.g. an intent-chain blocker for /kernel/backlog) belongs with that extension,
NOT in this template.

## Two tiers, by design

The Bash `cd` check is INLINED below, with no dependencies, so a standalone
kernel enforces it out of the box. That guarantee is the whole point: a hook
that registers correctly and then silently does nothing is worse than no hook,
because it reports safety it is not providing.

The richer checks (code quality, state validation) live in the OPTIONAL
`lib/validators` package. When it is present the hook uses it; when it is
absent the hook still enforces the inlined check and says so on stderr. It
never exits silently on a missing import.
"""

import json
import os
import re
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


# ---------------------------------------------------------------------------
# Inlined, dependency-free Bash safety check
# ---------------------------------------------------------------------------

def check_cd(command: str) -> list:
    """Check for a standalone `cd` command in a bash string.

    `cd` shifts the working directory for the rest of the session, which breaks
    hook path resolution (`python .claude/hooks/...` stops resolving) and can
    lock the agent out of Bash entirely. Use absolute paths instead.

    Distinguishes an actual `cd` command (blocks) from `cd` appearing inside a
    string literal, a comment, or a longer word (all allowed).

    Examples:
        >>> check_cd("cd /path && git log")
        ["Bash command uses 'cd' (breaks hook path resolution)"]

        >>> check_cd("git commit -m 'cd implementation'")
        []

        >>> check_cd('echo "the agent\\'s cd choice"')
        []

        >>> check_cd("mkdir /path")
        []

    Known limit: this does not parse escaped quotes or heredocs. It strips
    balanced quoted spans only.
    """
    # Strip quoted spans so `cd` inside a string literal is not a violation.
    # Each quote style is matched against its OWN closing delimiter — a single
    # pattern like ["'].*?["'] will pair a double quote with an apostrophe
    # inside it (e.g. "the agent's cd"), desynchronize, and leave `s cd"`
    # behind, producing a false block on any English possessive.
    cmd_without_quotes = re.sub(r'"[^"]*"|\'[^\']*\'', '', command)

    # Then strip shell comments. Order matters: quotes MUST be removed first,
    # or `echo "a # b"; cd /tmp` would have everything from the quoted `#`
    # onward discarded and the real command would be missed.
    cmd_without_quotes = re.sub(r'(^|\s)#.*$', r'\1', cmd_without_quotes, flags=re.MULTILINE)

    # `cd` as a standalone command: preceded by start/space/;/|/& and followed
    # by space/;/end/|/&.
    if re.search(r'(^|\s|;|\||\&)\bcd\b(\s|;|$|\||&)', cmd_without_quotes):
        return ["Bash command uses 'cd' (breaks hook path resolution)"]

    return []


def block(missing: str, fix: str) -> None:
    """Emit a block message and exit 2 (the PreToolUse deny code)."""
    lines = [f"BLOCKED: {missing}", ""]
    lines.append(f"  {fix}")
    lines.append("")
    print("\n".join(lines), file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Optional shared validators
# ---------------------------------------------------------------------------
# Resolve lib/validators if this repo (or a sibling isagawa-kernel) ships it.
# Absence is NORMAL for a standalone kernel and must not disable the hook.

def _resolve_validators():
    lib_root = ''
    if (_REPO_ROOT / 'lib' / 'validators').is_dir():
        lib_root = str(_REPO_ROOT)
    else:
        search = _HOOK_DIR
        while search != search.parent:
            candidate = search.parent / 'isagawa-kernel'
            if (candidate / 'lib' / 'validators').is_dir():
                lib_root = str(candidate)
                break
            search = search.parent

    if not lib_root:
        return None

    sys.path.insert(0, lib_root)
    try:
        from lib.validators import code_quality, state_validation, bash_validation, common
        return {
            'code_quality': code_quality,
            'state_validation': state_validation,
            'bash_validation': bash_validation,
            'common': common,
        }
    except ImportError as exc:
        # The package is on disk but did not import — a real breakage, not the
        # normal standalone case. Say so; do not pretend the checks ran.
        print(
            f"WARNING: {Path(lib_root) / 'lib' / 'validators'} found but failed to "
            f"import ({exc}). Falling back to the inlined Bash check only; "
            f"code-quality and state validation are NOT running.",
            file=sys.stderr,
        )
        return None


VALIDATORS = _resolve_validators()


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    tool_input = data.get('tool_input', {})

    if tool_name in ('Write', 'Edit'):
        # Write/Edit checks are validator-only. Without the optional package
        # there is nothing to enforce here, so allow.
        if not VALIDATORS:
            sys.exit(0)

        common = VALIDATORS['common']
        file_path = tool_input.get('file_path', '').replace('\\', '/')
        if common.should_skip(file_path):
            sys.exit(0)

        violations = VALIDATORS['state_validation'].check(str(SESSION_STATE))
        if violations:
            common.state_block(violations)

        content = tool_input.get('content', '') or tool_input.get('new_string', '')
        if content:
            # Skip code quality checks for HTML files (naturally contain inline scripts)
            if not file_path.endswith('.html'):
                violations = VALIDATORS['code_quality'].check(file_path, content)
                if violations:
                    common.smart_block(violations, "Code quality")

    elif tool_name == 'Bash':
        command = tool_input.get('command', '')

        # Prefer the shared validator when available (it is the superset), but
        # ALWAYS run the inlined check otherwise — never skip the Bash gate.
        if VALIDATORS:
            violations = VALIDATORS['bash_validation'].check(command)
            if violations:
                VALIDATORS['common'].bash_block(violations)
        else:
            violations = check_cd(command)
            if violations:
                block(
                    "Bash safety violation\n\n  " + "\n  ".join(violations),
                    "Use absolute paths, avoid cd.",
                )

    sys.exit(0)


if __name__ == '__main__':
    main()
