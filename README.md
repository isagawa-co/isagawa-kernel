# Isagawa Kernel

**The self-improving harness for AI coding agents.**

Drop-in agent harness that makes AI agents govern themselves. The agent builds its own rules, enforces them mechanically, and gets better every time it fails. No framework. No runtime. Just structure that actually sticks.

---

## The Problem

AI agents drift. The longer the task, the worse it gets.

- They ignore system prompts after a few thousand tokens
- They skip steps when the work gets complex
- They make the same mistake twice because nothing enforces learning
- They produce inconsistent output across sessions
- Memory and RAG give them context — but no obligation to use it

Every existing solution is **advisory**. Give the agent instructions, context, or memory — and hope it follows them. It doesn't. Not reliably. Not on long tasks. Not under pressure.

## The Solution

The Isagawa Kernel introduces **Spec-Driven Development (SDD)** — a framework where the agent builds, enforces, and improves its own governance from a domain spec. The agent internalizes the spec, builds its own protocol and enforcement, and hooks then block violations by default at the tool-call level.

By default the agent is blocked from skipping a quality check, ignoring a failure, or proceeding without recording what it learned (default-blocking, not tamper-proof — see the FAQ). It's not "please follow this spec" — it's "you are blocked until you do."

```
You (drop kernel in) → Agent scans repo → Builds own protocol
                                         → Builds own enforcement
                                         → Builds own task queue
                                         → Starts working (governed)
                                         → Fails? Learns. Gets harder to break.
```

**You don't write the rules. The agent does — and the hooks block breaking them by default.**

### What is Spec-Driven Development?

SDD flips the traditional relationship between developer and agent:

| Traditional | SDD + Kernel |
|-------------|------------------------|
| You write the spec and hope | Agent internalizes the spec and enforces it |
| You enforce quality | Agent enforces its own quality |
| You update after failures | Agent updates itself after failures |
| Agent follows instructions (sometimes) | Agent follows its own rules (hook-enforced by default) |
| Quality depends on prompt engineering | Quality compounds automatically over time |

The kernel is the runtime that makes SDD possible. Domain specs are the knowledge that makes it domain-aware.

---

## How It's Different

| Approach | What happens when the agent drifts |
|----------|-----------------------------------|
| System prompts | Agent ignores them after 10K tokens |
| RAG / memory | Agent has context but no obligation to use it |
| Static specs | Agent skips steps when they're hard |
| Fine-tuning | Expensive, brittle, doesn't generalize |
| **Isagawa Kernel** | **Agent is blocked. Cannot proceed until compliant.** |

Other tools help agents remember. This one makes them behave.

---

## What You Get

**Without a domain spec** (kernel only):
- Drop the kernel into any repo
- Agent scans your codebase, builds a protocol from what it finds
- Governance loop enforces the protocol as the agent works
- Every failure becomes a permanent lesson
- Cross-session persistence — the agent picks up where it left off

**With a domain spec** (kernel + spec):
- Same as above, plus domain-specific knowledge
- Agent builds to your industry's patterns, conventions, and quality gates
- Specs are portable — drop one into any project with the kernel installed

```
Session 1:    Agent sets up. Builds protocol. Learns the codebase.
Session 5:    Agent catches its own mistakes. Protocol is tightening.
Session 20:   Governance is battle-tested. Same patterns, every time.
Session 50+:  One-shot quality. The system has seen every failure mode.
```

### Example: Kernel + QA Spec on a Real Project

You have a web app. You want governed test automation. Here's what happens:

```bash
# 1. Clone a release repo (kernel + Playwright spec bundled)
git clone https://github.com/isagawa-qa/platform-playwright.git my-qa-project
```

2. Open `my-qa-project` in VS Code → open the Claude Code panel
3. Invoke `/qa-workflow` — the spec's slash command that starts governed test codegen

**What the agent does (governed, not guessing):**

```
Session Start  → Restores state from last session (or fresh start)
Domain Setup   → Scans your repo + reads the Playwright QA spec
                → Reads reference files: page objects, tasks, roles, test specs
                → Builds protocol: 5-layer architecture, selector priority, interface-first rules
                → Creates enforcement: quality gates for every layer
                → Builds task queue from your request

QA Workflow begins (5-step, gate-enforced):
  Step 1: Input       → Captures URL, persona, test type (UI/API/hybrid)
  Step 2: Pre-flight  → Configures credentials, auth strategy
  Step 3: Processing  → Generates BDD scenarios and expected states
  Step 4: Construction (builds layer by layer, spec-governed):
    → Page Objects    → framework/pages/login/login-page.ts
                        (role-based selectors, BrowserInterface methods, atomic actions)
    → Tasks           → framework/tasks/login/login-tasks.ts
                        (composes page objects, @autologger decorator, void returns)
    → Roles           → framework/roles/login/standard-user-role.ts
                        (composes tasks, multi-step workflows)
    → Tests           → tests/login/test-login.spec.ts
                        (AAA pattern, one role call per test, POM state assertions)
  Step 5: Execution   → npx playwright test --headed
    → Pass? Done.
    → Fail? Agent STOPS. Reports to user. Waits for decision.
      → User picks: AI fix / manual fix / investigate / skip
      → If fix → /kernel/learn records lesson → retry

Failure example:
  Agent uses CSS class selector (.btn-primary) in page object
  → Spec enforces: role-based selectors first (role=button[name="Log in"])
  → Blocked until lesson recorded
  → Learns: "use role selectors, CSS is last resort"
  → Lesson encoded permanently → the same mistake is caught if it recurs
```

**What you did:** Cloned a repo, opened it, said one sentence.

**What you got:** A governed test script built to the spec's 5-layer architecture — page objects, tasks, roles, and test — with every failure captured as a permanent lesson.

### Try It Yourself

The fastest way to see Spec-Driven Development in action:

```bash
git clone https://github.com/isagawa-qa/platform-playwright.git
```

Open `platform-playwright` in VS Code with the Claude Code extension. Tell the agent to build tests for any web app. Watch it set up its own protocol, create enforcement, and start cycling through tasks — governed the entire time. That's the kernel + a domain spec working together.

---

## Quick Start

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with the [Claude Code extension](https://marketplace.visualstudio.com/items?itemName=anthropics.claude-code)
- Python 3.8+
- That's it. No database, no Docker, no cloud.

### Install

```bash
# Clone the kernel
git clone https://github.com/isagawa-co/isagawa-kernel.git

# Copy into your project
cp -r isagawa-kernel/.claude/ your-project/.claude/
cp isagawa-kernel/CLAUDE.md your-project/CLAUDE.md
```

### First Run

1. Open `your-project` in VS Code
2. Open the Claude Code panel (sidebar or `Ctrl+Shift+P` → "Claude Code")
3. Give the agent any task

The agent will:
1. Detect no domain exists
2. Scan your repo structure, code patterns, and conventions
3. Build its own protocol and enforcement
4. Ask you to restart the extension (enforcement hooks need a reload)
5. Pick up where it left off — fully governed

**That's it.** Five minutes from clone to governed agent.

---

## The Governance Loop

```
session-start → anchor → WORK ─────────────────→ complete
                   ^         |                       ^
                   └─ every N actions ←──────────────┘
                             |
                   failure? → fix → learn (MANDATORY)
```

| Step | What happens |
|------|-------------|
| **Session Start** | Checks state, restores context, resumes from where it left off |
| **Anchor** | Re-reads protocol, audits recent work against it |
| **Work** | Builds — every action tracked automatically |
| **Every N actions** | Forced to stop, re-read protocol, check quality |
| **On failure** | Must diagnose, fix, and record what it learned |
| **Complete** | Final quality gate before marking done |

Skipped a quality check? **Blocked.** Test failed and didn't record the lesson? **Blocked.** Went too long without re-reading the protocol? **Blocked.**

By default the agent can't skip these steps — if it tries, the hook stops it until it complies. (Default-blocking, not tamper-proof; circumvention is logged as a lesson.)

---

## Architecture

Three layers. The kernel governs, the spec teaches, the agent builds everything else.

```
┌─────────────────────────────────────────────┐
│  Agent-Generated                            │
│  Protocol, lessons, enforcement, tasks      │
│  (the agent builds this — you don't)        │
├─────────────────────────────────────────────┤
│  Domain Spec (optional)                     │
│  Industry knowledge for a specific domain   │
├─────────────────────────────────────────────┤
│  Kernel (this repo)                         │
│  Governance loop — always present           │
└─────────────────────────────────────────────┘
```

- **Kernel** governs *how* the agent works. Ships with every project.
- **Domain Spec** teaches *what* to build. Drop one in, or let the agent figure it out from your repo.
- **Agent-Generated** is everything the agent creates — protocols, lessons, task queues. All self-built, all self-improving.

---

## Domain Specs

The kernel governs. Domain specs teach. Together, you get a governed agent that knows your industry.

A domain spec is a portable skill folder — markdown files that encode domain knowledge, patterns, conventions, and quality gates for a specific vertical. Drop one into any project with the kernel installed, and the agent builds to that domain's standards.

### How to Drop In a Domain Spec

```bash
# You already have the kernel installed in your project.
# Now add a domain spec:

# Option 1: Clone a published spec
git clone https://github.com/isagawa-qa/selenium-spec.git
cp -r selenium-spec/ your-project/.claude/skills/selenium-spec/

# Option 2: Already bundled (kernel + spec ship together)
git clone https://github.com/isagawa-qa/platform-selenium.git
# Open platform-selenium in VS Code → open Claude Code panel. Just start.
```

The agent reads the domain spec during setup, merges it with what it discovers in your repo, and builds a protocol that covers both your codebase and your domain's requirements.

**One kernel. Many specs. Each project gets domain-aware governance.**

### Available Specs

| Spec | What the agent builds | Status |
|------|----------------------|--------|
| [QA Platform (Selenium)](https://github.com/isagawa-qa/platform-selenium) | Selenium test automation with Page Object patterns | Live |
| [QA Platform (Playwright)](https://github.com/isagawa-qa/platform-playwright) | Playwright test suites with fixture-based architecture | Live |
| DevOps (CI/CD) | GitHub Actions, GitLab CI, Azure DevOps pipelines | Coming soon |
| Health Insurance | EDI testing, claims processing, benefits configuration | Coming soon |
| Real Estate | Lease-option deal management, buyer matching | Coming soon |

### No Spec? No Problem.

The kernel works without a domain spec. It scans your repo, builds a protocol from what it finds, and governs the agent's work. The spec just makes it domain-aware — it's the difference between a governed agent and a governed agent that knows your industry.

### Build Your Own

Domain specs are just markdown skill folders. No code. No API. No schema to learn.

A spec typically contains:
- **Workflow** — how the agent should approach work in this domain
- **Reference patterns** — conventions, naming, architecture the agent should follow
- **Seeded lessons** — known pitfalls in this domain, pre-loaded so the agent doesn't hit them
- **Task templates** — common work items the agent can cycle through

See the [Selenium spec](https://github.com/isagawa-qa/platform-selenium) for a working example. Build one for your vertical — the kernel handles enforcement.

---

## Capabilities

### Autonomous Cycling

Give the agent a queue of tasks. It picks the next one, implements it, verifies it, marks it complete, and moves to the next — autonomously. No human in the loop between tasks.

The governance loop runs the entire time. Every task gets the same quality enforcement. The agent can cycle through dozens of tasks across multiple sessions, picking up exactly where it left off.

```
Task 001 → implement → verify → complete ✓
Task 002 → implement → verify → complete ✓
Task 003 → implement → fail → fix → learn → verify → complete ✓
Task 004 → implement → verify → complete ✓
...
Task 071 → done. Full project built, governed end to end.
```

### Self-Building Domain Setup

Point the agent at any codebase. It scans the repo — file structure, code patterns, naming conventions, test frameworks, dependencies — and builds its own protocol from scratch. No templates. No configuration. The agent figures out what matters and writes the rules itself.

Add a domain spec and the setup gets smarter — the agent merges domain knowledge with what it discovers in your repo.

### Mandatory Learn Loop

When something breaks, the agent can't just fix it and move on. It must record *what* went wrong, *why* it went wrong, and *what changed* to prevent it. That lesson becomes part of the system permanently.

Session 1 failure → lesson recorded → by session 50 that failure mode is documented and caught fast. The system builds antibodies (recurrences still happen and are tracked).

### Cross-Session Persistence

The agent saves its full context — what it was working on, decisions made, progress through task queues — to state files. Next session, it restores everything and picks up mid-task. No re-explaining. No context loss.

### Periodic Re-Anchoring

Agents drift over long tasks. The kernel forces periodic stops where the agent must re-read its own protocol and audit its recent work against it. If the work doesn't match the protocol, the agent self-corrects before continuing.

This is the difference between "instructions at the top of the conversation" and "instructions enforced continuously throughout."

### Smart Gates

The enforcement knows what's wrong and tells the agent exactly how to fix it. Not just "blocked" — but "blocked because X, do Y to proceed." The agent always has a clear path forward.

---

## Core Principles

- **Self-Building** — The agent internalizes the spec and creates its own protocols and enforcement from it.
- **Self-Improving** — Every failure updates the system, so repeats get caught faster (recurrences are tracked, not made impossible).
- **Safety-First** — Enforcement is mechanical and default-blocking, not advisory. Not tamper-proof — bypasses are a tracked failure mode, not an impossibility.
- **Autonomous** — The agent reports what it did, not asks what to do.
- **Portable** — Markdown and JSON. No build step. No vendor lock-in. Works anywhere Claude Code runs.

---

## Use Cases

**Solo developers** — Give your agent structure it actually follows. Stop re-explaining conventions every session. The kernel remembers and enforces.

**Teams** — Share a kernel + domain spec across the team. Every developer's agent follows the same patterns, conventions, and quality gates. Consistency without code review bottlenecks.

**Consultants / Agencies** — Build domain specs for your clients' verticals. Drop kernel + spec into their repo. Their agent builds to your standards, governed, from day one.

**QA / Test Automation** — Pair with a QA domain spec. Agent builds test suites that follow your framework's patterns. Every test failure becomes a lesson that prevents the next one.

---

## FAQ

**What is SDD?**
Spec-Driven Development. A framework where the agent internalizes a domain spec, builds its own governance from it, and enforces compliance mechanically. The kernel is the runtime that makes SDD work.

**Is this a framework?**
SDD is the framework. The kernel is the implementation. It's a set of markdown files and one enforcement script. No imports, no APIs, no build step. Copy it in, start working.

**Does it work without a domain spec?**
Yes. The kernel scans your repo and builds a protocol from what it finds. The domain spec adds industry-specific knowledge, but the governance loop works either way.

**Does the agent really improve over time?**
Yes. Every failure triggers a mandatory learn cycle, and the lesson gets encoded so the same failure is caught if it recurs. The learn trigger is mechanical; it reduces repeats rather than making them impossible.

**Can the agent bypass the enforcement?**
By default it can't — enforcement operates at the tool-call level, blocking writes, edits, and execution until the agent complies. But it is not tamper-proof: a careless or determined agent can circumvent it (e.g., editing state files), which is why "never bypass" is the top rule and why bypasses are recorded as lessons. Bypass is a tracked failure mode, not an impossibility.

**What AI agents does it work with?**
Currently Claude Code. The architecture is agent-agnostic — any agent runtime that supports tool-call interception can run it.

**How is this different from giving the agent a CLAUDE.md file?**
CLAUDE.md is advisory — the agent reads it once and drifts. The kernel re-reads the protocol every N actions, audits work against it, and blocks non-compliance. Structure that persists, not instructions that decay.

**Can I use my own domain spec with it?**
Yes. Domain specs are just markdown skill folders. Build one for your vertical, drop it into `.claude/skills/`, and the kernel handles the rest. See the [Selenium spec](https://github.com/isagawa-qa/platform-selenium) for the pattern.

**How do domain specs work with teams?**
Everyone clones the same repo with kernel + spec installed. Every developer's agent builds to the same protocol. Same patterns, same quality gates, same enforcement. New team member? Clone and go.

---

## Roadmap

- [x] Core governance loop (session-start, anchor, learn, complete)
- [x] Self-building domain setup (agent creates its own protocol)
- [x] Autonomous task cycling (agent works through task queues)
- [x] Cross-session persistence (state survives restarts)
- [x] Domain spec system (portable, drop-in skill folders)
- [ ] Multi-agent coordination (governed agents working together)
- [ ] Spec marketplace (discover and install community domain specs)
- [ ] Additional agent runtime support

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting domain specs and kernel improvements.

## License

[MIT](LICENSE)
