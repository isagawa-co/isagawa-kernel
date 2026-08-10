# Step 4: Decompose into Main Tasks

Break the goal into 3-10 main tasks that represent major milestones.

## Process

1. **Identify the major phases:**
   - What are the distinct stages of this work?
   - Each phase becomes a main task
   - Order by dependency (what must come first?)

2. **Apply the naming convention:**
   - `NNN-[tag]-verb-object.md`
   - Tags match the project context (e.g., `kernel`, `domain`, `market`)
   - Verbs: research, build, test, deploy, document

3. **Each main task must have:**
   - Clear deliverable (what artifact exists when done)
   - Dependencies (which prior tasks must be complete)
   - Rough scope (is this 1 action or 20?)

4. **Check granularity:**
   - Too big? (more than ~10 actions to complete) → split into multiple tasks
   - Small is GOOD — a task with 1 action is a valid, correct task
   - **NEVER merge tasks for being "too small"** — granularity is the goal
   - Each task = one deliverable action (one file, one command, one config change)

## Phase Boundary Rule (MANDATORY for multi-concern specs)

When a goal has multiple distinct concerns (e.g., "upgrade kernel AND run factory"):

1. **Each concern becomes its own phase** with a named boundary in the index.

2. **Phase boundary tasks** are mandatory between phases:
   - A TEST task that validates the prior phase is complete
   - A RESEARCH task that re-reads the template/context for the next phase (if step 3 produced `_context/` files, this task re-reads them to re-ground)

   This prevents context drift — the agent re-grounds on the template before generating paths for the next phase.

3. **Never mix infrastructure tasks with domain content tasks** in the same dependency chain. Infrastructure tasks (hooks, commands, settings) feed into a boundary gate. Domain tasks (spec files, reference code) start fresh after that gate.

Example:
```
Phase 1: Kernel Sync (tasks 001-023)
   ↓
Phase Boundary: 024-verify-kernel-sync (TEST)
                025-reload-template-context (RESEARCH) ← re-reads _context/ files
   ↓
Phase 2: Factory Build (tasks 026-070)
```

4. **If step 3 produced `_context/path-mapping.json`**, the reload task must read it and confirm all mappings are still valid before the next phase generates any file paths.

## Output

A list of main tasks with order and dependencies:

```
Main tasks:
1. 001-[tag]-research-xxx — research phase, no dependencies
2. 002-[tag]-build-xxx — depends on 001
3. 003-[tag]-build-yyy — depends on 001
4. 004-[tag]-test-xxx — depends on 002, 003
5. 005-[tag]-document-xxx — depends on 004
```

## Rules

- Don't create tasks that require human decisions without marking them `HUMAN REQUIRED`
- Don't create tasks for things that already exist — check first
- Task count is driven by the work, not an arbitrary cap — 80 atomic tasks is correct if the work has 80 actions
- Phase boundaries are non-negotiable for multi-concern specs — the agent WILL drift without them
