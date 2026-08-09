#!/usr/bin/env python3
"""
Skill extraction from mature lessons.

When a lesson recurs above a configurable threshold, auto-generates a draft
command markdown file in `.claude/drafts/commands/`. Drafts require user
approval before promotion to `.claude/commands/`.

Usage (from /kernel/learn Step 6):
    from lib.skill_extraction import maybe_extract_skill
    result = maybe_extract_skill(
        issue="Hook bypass via direct state edit",
        root_cause="Agent edited session_state.json directly",
        fix="Added mechanical enforcement in gate-enforcer",
        pattern_key="hook-bypass-direct-edit",
        recurrence_count=3,
        workspace="/path/to/workspace",
    )
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# Default recurrence threshold before skill extraction triggers
DEFAULT_THRESHOLD = 3

# Registry filename (stored in .claude/state/)
PROMOTED_REGISTRY = "promoted_lessons.json"


def _slugify(text: str) -> str:
    """Convert text to a filename-safe slug.

    Args:
        text: Arbitrary string to slugify.

    Returns:
        Lowercase, hyphen-separated slug.

    Examples:
        >>> _slugify("Hook Bypass via Direct Edit")
        'hook-bypass-via-direct-edit'
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _load_registry(workspace: str) -> dict:
    """Load the promoted-lessons registry from workspace state.

    Args:
        workspace: Absolute path to the workspace root.

    Returns:
        Dict mapping pattern_key -> promotion metadata.
    """
    registry_path = os.path.join(workspace, ".claude", "state", PROMOTED_REGISTRY)
    if os.path.isfile(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_registry(workspace: str, registry: dict) -> None:
    """Persist the promoted-lessons registry.

    Args:
        workspace: Absolute path to the workspace root.
        registry: Dict mapping pattern_key -> promotion metadata.
    """
    state_dir = os.path.join(workspace, ".claude", "state")
    os.makedirs(state_dir, exist_ok=True)
    registry_path = os.path.join(state_dir, PROMOTED_REGISTRY)
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


def _generate_draft_command(
    issue: str,
    root_cause: str,
    fix: str,
    pattern_key: str,
    recurrence_count: int,
) -> str:
    """Generate markdown content for a draft command.

    Args:
        issue: What happened.
        root_cause: Why it happened.
        fix: How it was resolved.
        pattern_key: Unique key identifying this lesson pattern.
        recurrence_count: How many times this pattern has recurred.

    Returns:
        Markdown string for the draft command file.
    """
    slug = _slugify(pattern_key)
    title = pattern_key.replace("-", " ").title()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"""# /check/{slug}

> Auto-generated draft from recurring lesson (recurrence: {recurrence_count}).
> Requires user review before promotion to `.claude/commands/`.

## Origin

- **Pattern:** {pattern_key}
- **Issue:** {issue}
- **Root Cause:** {root_cause}
- **Fix:** {fix}
- **Generated:** {now}

## Instructions

1. **Check for this pattern:**
   - Look for signs of: {issue}
   - Verify the fix is in place: {fix}

2. **If violation found:**
   - Flag it with a clear message
   - Apply the known fix

3. **Report:**
   ```
   CHECK: {title}
   Status: [PASS / FAIL]
   Details: [what was found]
   ```

## Promotion

To promote this draft to a live command:
1. Review and edit this file as needed
2. Move to `.claude/commands/check-{slug}.md`
3. The command becomes available as `/check/{slug}`
"""


def maybe_extract_skill(
    issue: str,
    root_cause: str,
    fix: str,
    pattern_key: str,
    recurrence_count: int,
    workspace: str,
    threshold: int = DEFAULT_THRESHOLD,
) -> dict:
    """Conditionally generate a draft command from a recurring lesson.

    Called by /kernel/learn after recurrence detection. If the lesson's
    recurrence_count meets or exceeds the threshold AND the pattern has
    not already been promoted, a draft command is written to the staging
    area.

    Args:
        issue: What happened.
        root_cause: Why it happened.
        fix: How it was resolved.
        pattern_key: Unique key identifying this lesson pattern.
        recurrence_count: How many times this pattern has recurred.
        workspace: Absolute path to the workspace root.
        threshold: Minimum recurrences to trigger extraction (default 3).

    Returns:
        Dict with keys:
            - extracted (bool): Whether a draft was generated.
            - reason (str): Why extraction did or did not happen.
            - draft_path (str | None): Path to the draft file if generated.
    """
    # Below threshold — no extraction
    if recurrence_count < threshold:
        return {
            "extracted": False,
            "reason": f"Below threshold ({recurrence_count}/{threshold})",
            "draft_path": None,
        }

    # Check promotion registry — skip if already promoted
    registry = _load_registry(workspace)
    if pattern_key in registry:
        return {
            "extracted": False,
            "reason": f"Already promoted ({registry[pattern_key].get('promoted_at', 'unknown')})",
            "draft_path": None,
        }

    # Generate draft
    slug = _slugify(pattern_key)
    drafts_dir = os.path.join(workspace, ".claude", "drafts", "commands")
    os.makedirs(drafts_dir, exist_ok=True)

    draft_path = os.path.join(drafts_dir, f"check-{slug}.md")
    content = _generate_draft_command(
        issue=issue,
        root_cause=root_cause,
        fix=fix,
        pattern_key=pattern_key,
        recurrence_count=recurrence_count,
    )

    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Record in registry as drafted (not yet promoted)
    registry[pattern_key] = {
        "status": "drafted",
        "draft_path": draft_path,
        "recurrence_count": recurrence_count,
        "drafted_at": datetime.now(timezone.utc).isoformat(),
        "promoted_at": None,
    }
    _save_registry(workspace, registry)

    return {
        "extracted": True,
        "reason": f"Recurrence {recurrence_count} >= threshold {threshold}",
        "draft_path": draft_path,
    }


def promote_draft(pattern_key: str, workspace: str) -> dict:
    """Promote a drafted command to the live commands directory.

    Called by the user after reviewing a draft. Moves the draft from
    `.claude/drafts/commands/` to `.claude/commands/` and updates the
    registry.

    Args:
        pattern_key: The pattern key of the draft to promote.
        workspace: Absolute path to the workspace root.

    Returns:
        Dict with keys:
            - promoted (bool): Whether promotion succeeded.
            - reason (str): Why promotion did or did not happen.
            - command_path (str | None): Path to the promoted command.
    """
    registry = _load_registry(workspace)

    if pattern_key not in registry:
        return {
            "promoted": False,
            "reason": f"No draft found for pattern '{pattern_key}'",
            "command_path": None,
        }

    entry = registry[pattern_key]
    if entry.get("status") == "promoted":
        return {
            "promoted": False,
            "reason": f"Already promoted at {entry.get('promoted_at', 'unknown')}",
            "command_path": None,
        }

    draft_path = entry.get("draft_path", "")
    if not os.path.isfile(draft_path):
        return {
            "promoted": False,
            "reason": f"Draft file not found: {draft_path}",
            "command_path": None,
        }

    # Move to commands directory
    slug = _slugify(pattern_key)
    commands_dir = os.path.join(workspace, ".claude", "commands")
    os.makedirs(commands_dir, exist_ok=True)
    command_path = os.path.join(commands_dir, f"check-{slug}.md")

    with open(draft_path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(command_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.remove(draft_path)

    # Update registry
    registry[pattern_key]["status"] = "promoted"
    registry[pattern_key]["promoted_at"] = datetime.now(timezone.utc).isoformat()
    registry[pattern_key]["command_path"] = command_path
    _save_registry(workspace, registry)

    return {
        "promoted": True,
        "reason": "Draft promoted to live command",
        "command_path": command_path,
    }
