# Kernel Feature Freeze Policy

## Policy

The Isagawa Kernel is frozen. No new commands, hooks, or skills will be added to this repo.

## Core List (Frozen)

### Commands (7)
1. `session-start.md` — Check state, resume
2. `domain-setup.md` — Build protocol + hooks
3. `anchor.md` — Re-read protocol, audit work
4. `learn.md` — Record lessons after failures
5. `fix.md` — Impact assessment before fixes
6. `complete.md` — Final quality gate
7. `reset.md` — Fresh state for testing

### Hooks (4)
1. `universal-gate-enforcer.py` — Anchor counter, learn blocks, state gates
2. `actions-log-appender.py` — Action tracking
3. `auto-approve-claude-writes.py` — Auto-approve state writes
4. `test-failure-detector.py` — Test failure detection

### Skills (2)
1. `kernel-domain-setup/` — Self-building protocol creation
2. `autonomous-cycling/` — Autonomous task loop

## Where Extensions Go

Extensions (task-builder, execute-pipeline, audit-workflow, prod-test, backlog, attestation, etc.) are workspace-level additions. They live in the consuming project's `.claude/` directory, not in the kernel repo.

```
your-project/
├── .claude/
│   ├── commands/kernel/          ← kernel commands (from this repo)
│   ├── commands/kernel/          ← extension commands (added by workspace)
│   ├── skills/kernel-domain-setup/  ← kernel skill
│   ├── skills/autonomous-cycling/   ← kernel skill
│   ├── skills/task-builder/         ← extension skill (workspace adds this)
│   └── hooks/                       ← kernel hooks + domain hooks
```

## Rationale

The kernel is a minimal governance layer, not an application framework. Keeping it small ensures:

1. **Portability** — Drop into any repo without bloat
2. **Stability** — Core loop doesn't change, so domain specs don't break
3. **Clarity** — 7 commands, 4 hooks, 2 skills. That's the whole system.
4. **Separation** — Governance (kernel) vs. capabilities (extensions) are distinct concerns

Bug fixes and improvements to existing commands/hooks/skills are allowed. New additions are not.
