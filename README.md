# Isagawa Kernel

**Governance that an AI agent builds for itself, and then cannot quietly skip.**

Drop it into a repo. The agent reads your codebase, writes its own protocol, wires its own
enforcement hooks, and from then on the rules it wrote are checked mechanically on every
tool call — not remembered, not reread, not hoped for.

No runtime. No dependencies beyond Python and bash. Markdown and JSON all the way down.

---

## The problem

Agents drift. Not dramatically — quietly. Fifty actions into a session an agent has stopped
re-reading the conventions it was given, is repeating a mistake it already fixed once, and is
reporting success it did not verify. Prompting harder does not fix this, because a prompt is
advice and advice is exactly what drifts.

The usual fixes make it worse. A longer system prompt gets skimmed. A checklist gets
summarized. A style guide gets paraphrased into something adjacent to what it said.

The kernel's answer is to stop relying on the agent remembering anything.

---

## How it works

Rules live in files. Compliance is checked by hooks that run before and after tool calls, in a
separate process, reading state off disk. When a gate is unsatisfied the tool call is blocked
and the agent is handed the exact command that unblocks it.

```
session-start → anchor → WORK ─────────────────→ complete
                   ↑        ↓                        ↑
                   └─ every N actions ←──────────────┘
                            ↓
                  failure? → fix → learn
```

Five gates guard every Write, Edit and Bash:

| # | Gate | Blocks when |
|---|------|-------------|
| 1 | Session started | The session never ran `session-start` |
| 2 | Lesson recorded | A test failed and no lesson was written |
| 3 | Anchored | The protocol has not been re-read |
| 4 | Action budget | N actions have passed since the last anchor |
| 5 | Anchor token | The agent flipped `anchored` without doing the anchor |

Gate 5 is the interesting one. When gate 4 trips it mints a random token. A real anchor reads
that token from state and confirms it. An agent that skips the ceremony and just sets
`anchored: true` never sees the token, so it blocks again — the shortcut is closed by
construction rather than by instruction.

Read-only commands (`ls`, `git status`, `grep`, …) skip the gates but still count. Writes into
`.claude/` skip both, so the agent can always record state.

**Honest scope:** this is enforcement at the tool-call layer, and it holds against drift and
shortcuts, which is what actually goes wrong. It is not a security boundary and does not claim
to be unbypassable — an agent determined to circumvent it can. What the kernel gives you is
that circumvention becomes a visible, recorded event instead of an invisible one.

---

## Quick start

```bash
git clone https://github.com/isagawa-co/isagawa-kernel.git

# copy the kernel into your project
cp -r isagawa-kernel/.claude    your-project/.claude
cp -r isagawa-kernel/lib        your-project/lib
cp    isagawa-kernel/CLAUDE.md  your-project/CLAUDE.md
cp    isagawa-kernel/run-task.sh your-project/run-task.sh
```

1. Open `your-project` in Claude Code and give the agent any task.
2. It finds no domain, so it runs `/kernel/domain-setup`: scans the repo, writes
   `.claude/protocols/<domain>-protocol.md`, instantiates a domain gate hook, and registers
   every hook in `.claude/settings.local.json`.
3. It asks you to restart. **This is required** — Claude Code loads hooks at startup, so
   until you restart, nothing is enforced.
4. Say "continue". The agent anchors and resumes, now governed.

Copying only `.claude/` is not enough: `/kernel/learn` imports `lib/skill_extraction.py`, and
`run-task.sh` sources `lib/common.sh`.

---

## Architecture

Everything at the top level is **core** and active. Everything under `extensions/` is
**opt-in** and inert until you copy it into `.claude/` yourself.

```
.claude/commands/kernel/    7 core commands
.claude/hooks/              4 hooks + 1 template
.claude/skills/             2 core skills
lib/                        common.sh, skill_extraction.py
run-task.sh                 headless task runner
tests/                      5 suites, core only
extensions/                 opt-in, inactive by default
```

The line matters because the kernel is **frozen**. Core will not grow — see
[docs/kernel-feature-freeze-policy.md](docs/kernel-feature-freeze-policy.md). Anything built on
top of the kernel goes in `extensions/` or in your own project, never into core.

### Core commands

| Command | What it does |
|---------|--------------|
| `session-start` | Check state, resume where the last session stopped |
| `domain-setup` | Scan the repo, write the protocol, wire the hooks |
| `anchor` | Re-read the protocol, then audit every action since the last anchor |
| `learn` | Record a lesson after a failure — this is what clears a gate-2 block |
| `fix` | Impact assessment before changing anything |
| `complete` | Final gate before a task is allowed to be called done |
| `reset` | Clear agent-created state for a clean test run |

### Hooks

| Hook | Role |
|------|------|
| `universal-gate-enforcer.py` | The five gates, plus the auto-incrementing action counter |
| `actions-log-appender.py` | Appends every Write, Edit and Bash to an audit log |
| `test-failure-detector.py` | Flags `needs_learn` when a test command exits non-zero |
| `auto-approve-claude-writes.py` | Auto-approves the agent's own `.claude/` state writes |
| `domain-gate-enforcer.template.py` | Template — `domain-setup` instantiates it per domain |

The domain gate has two tiers. Its bash safety check is inlined with no imports, so it enforces
in a bare install. Code-quality and state validation come from an optional `lib/validators`
package (shipped in `extensions/`); when it is absent the hook still enforces the bash check and
says so on stderr. It never exits silently pretending to have run checks it did not run.

### Core skills

| Skill | Purpose |
|-------|---------|
| `kernel-domain-setup/` | The 11-step protocol-building procedure `domain-setup` follows |
| `autonomous-cycling/` | Behaviour spec for looping through numbered tasks unattended |

### The headless runner

`run-task.sh` executes numbered task files one at a time through `claude -p`, resuming with
full conversation context on failure and persisting state between iterations.

```bash
./run-task.sh [repo_path] [max_iterations] [task_folder] [backlog_path]
```

It needs the `claude` CLI on your PATH. Core commands reference it by name — `complete` and
`session-start` both describe headless behaviour — which is why it ships here rather than
being left to the consumer to supply.

---

## Extensions

Opt-in, inactive on arrival, and not covered by `tests/`.

| Extension | What it adds |
|-----------|--------------|
| `task-builder` | Decompose a goal into atomic tasks with gate contracts, then execute |
| `audit-workflow` | Scan the kernel infrastructure for gaps and generate fix tasks |
| `autonomous-cycle` | The command that drives the core `autonomous-cycling` spec |
| `backlog` | Write a backlog item in a standard format |
| `lib/validators` | Upgrades the domain gate to full Write/Edit validation |
| `lib/attestation` | Signing, intent chains, transparency-log helpers |

Install by copying into `.claude/` and restarting. See [extensions/README.md](extensions/README.md).

---

## What ships vs what the agent builds

This distinction is the whole design, so it is worth stating plainly.

**Ships in this repo** — the commands, the hooks, the skills, `lib/`, `run-task.sh`, the tests,
and `CLAUDE.md`. All of it generic, none of it about your project.

**Written by the agent, at install time, into your project:**

| File | Written by |
|------|-----------|
| `.claude/protocols/<domain>-protocol.md` | `domain-setup` — derived from *your* repo |
| `.claude/hooks/<domain>-gate-enforcer.py` | `domain-setup`, from the shipped template |
| `.claude/settings.local.json` | `domain-setup` — hook registration |
| `.claude/state/*.json` | the loop, continuously |
| `.claude/lessons/lessons.md` | `learn`, after each failure |

None of those are in this repo, and that is deliberate. A protocol written for someone else's
codebase is exactly the generic advice the kernel exists to replace. The agent writes its own,
about your code, and is then held to it.

---

## Tests

Five suites, run directly:

```bash
bash tests/test_clean_install_bootstrap.sh
```

| Suite | Proves |
|-------|--------|
| `test_clean_install_bootstrap.sh` | A fresh install instantiates the domain gate and it actually **fires** — registration alone is not the property under test |
| `test_domain_gate_template.sh` | The template blocks and allows correctly with no validators present |
| `test_canary_base_modes.sh` | Six deliberately injected runner failures are each caught |
| `test_l2_completion_persistence.sh` | A lost task completion is re-persisted and survives read-back |
| `test_wi03_routed_state_isolation.sh` | Per-agent state writes never touch the parent workflow file |

Every suite works in throwaway `mktemp` sandboxes and never touches real state.

---

## Requirements

- **Claude Code**
- **Python 3** — the hooks
- **Bash** — `run-task.sh` and the tests (Git Bash on Windows)
- **`claude` CLI on PATH** — only for `run-task.sh` headless mode

No install step, no package manager, no build.

---

## Contributing

Fixes to existing commands, hooks and skills are welcome. New ones are not — core is frozen,
and that is a feature. See [CONTRIBUTING.md](CONTRIBUTING.md); the highest-leverage
contribution is a domain spec.

---

## License

[MIT](LICENSE)
