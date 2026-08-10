# Extensions

Everything in this directory is **opt-in and inactive by default**.

The kernel is frozen (see [`../docs/kernel-feature-freeze-policy.md`](../docs/kernel-feature-freeze-policy.md)).
Core is 7 commands, 5 hooks, 2 skills — nothing more gets added to it. Anything built
on top of the kernel lives here, outside `.claude/`, so Claude Code does not discover
or load it until you deliberately install it.

Nothing here is required for the kernel to work. Core has no dependency on any of it.

---

## Installing an extension

Copy the pieces you want into your project's `.claude/` (and `lib/`), then restart
Claude Code so the command is discovered:

```bash
# a command
cp extensions/commands/kernel/task-builder.md .claude/commands/kernel/

# its skill
cp -r extensions/skills/task-builder .claude/skills/

# a python package
cp -r extensions/lib/validators lib/
```

Uninstalling is deleting what you copied. Core is unaffected either way.

---

## What is here

### Commands

| Command | Requires | What it does |
|---------|----------|--------------|
| `task-builder.md` | `skills/task-builder/` | Decompose a goal into atomic tasks with gate contracts, then execute them |
| `audit-workflow.md` | `skills/audit-workflow/` | Scan kernel infrastructure for gaps and generate fix tasks |
| `autonomous-cycle.md` | core `skills/autonomous-cycling/` | Loop through numbered tasks unattended |
| `backlog.md` | `task-builder` | Write a backlog item in the standard format |

`autonomous-cycle.md` is the only one whose skill is already in core — the
`autonomous-cycling/` behaviour spec ships active, but the command that drives it
does not.

### Skills

| Skill | Files |
|-------|-------|
| `skills/task-builder/` | `SKILL.md` + 11 step/reference files |
| `skills/audit-workflow/` | `SKILL.md` + 8 scan step files |

### Libraries

| Package | What it is |
|---------|-----------|
| `lib/validators/` | Code-quality, state and bash validators. The domain gate enforcer picks these up automatically when `lib/validators/` exists at your repo root, upgrading it from the always-on bash safety check to full Write/Edit validation. See [`lib/validators/EXTENSIBILITY.md`](lib/validators/EXTENSIBILITY.md). |
| `lib/attestation/` | Signing, intent chains and transparency-log helpers. Standalone — no core command calls into it. |

`lib/validators` is the one extension core actively looks for. `.claude/hooks/domain-gate-enforcer.template.py`
resolves it at import time and reports on stderr when it is absent, so the reduced
enforcement scope is always stated rather than silently assumed.

---

## Support

These ship as-is. They are not covered by the kernel's test suites in `../tests/`,
which exercise core only.
