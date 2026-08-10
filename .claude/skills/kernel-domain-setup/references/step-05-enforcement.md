# Step 5: Understand Enforcement

The kernel uses two enforcement layers:

## Layer 1: Universal Hook (automatic)

The universal hook (`.claude/hooks/universal-gate-enforcer.py`) enforces:

| Gate | What It Checks | Blocked Until |
|------|----------------|---------------|
| Session | `session_started = true` | `/kernel/session-start` |
| Learn | `needs_learn = false` | `/kernel/learn` |
| Anchor | `anchored = true` | `/kernel/anchor` |
| Actions | `actions_since_anchor <= limit` | `/kernel/anchor` |

The hook code is universal but **must be registered** in `.claude/settings.local.json` to fire. See step-10 for the registration template. An unregistered hook is dead code.

## Layer 2: Agent Self-Enforcement (via protocol)

Domain-specific rules (architecture, patterns, anti-patterns) are enforced by the agent after reading the protocol during `/kernel/anchor`.

The protocol contains:
- Patterns: What to do
- Anti-patterns: What NOT to do
- Architecture: How layers compose

When agent anchors:
1. Reads protocol
2. Internalizes rules
3. Self-enforces while writing code

## What this means for domain-setup

Rules must be documented clearly in reference files (not protocol) so agent can self-enforce. Verify reference documentation contains:
- Architecture diagram
- Patterns with code examples
- Anti-patterns with examples

The protocol INDEXES these files. Agent reads actual files during anchor.

## Domain Gate Enforcer

A domain-specific hook (`.claude/hooks/{domain}-gate-enforcer.py`) is ALSO instantiated and registered during bootstrap, running alongside — not instead of — the universal hook. See step-10 for the instantiation and registration mechanics.

It has two tiers:

- **Bash safety (always on).** The `cd` check is inlined in the template with no dependencies, so it enforces in a standalone kernel. A hook that registers correctly and then silently does nothing is worse than no hook — it reports safety it is not providing.
- **Code quality and state validation (optional).** These come from the `lib/validators` package, which the kernel does not ship by default. When it is present the hook uses it; when it is absent the hook still enforces the Bash check and reports the reduced scope on stderr. It never exits silently on a missing import.
