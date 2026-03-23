# Step 3: Decompose into Main Tasks

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
   - Too big? (more than ~20 actions to complete) → split
   - Too small? (1-2 actions) → merge with adjacent task
   - Sweet spot: 5-15 actions per main task

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
- Keep the task count reasonable — 3-10 main tasks, not 40
