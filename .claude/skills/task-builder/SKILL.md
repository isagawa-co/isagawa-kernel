# Task Builder — Skill

**Type:** Prescriptive
**Style:** Indexed — SKILL.md + references/

## What

Takes a user-provided goal and autonomously decomposes it into a structured task set, then executes it. The user provides the "what" — the agent figures out the "how" by breaking it into main tasks with atomic subtasks.

## Steps

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Parse goal | → `references/step-01-parse-goal.md` |
| 2 | Research context | → `references/step-02-research.md` |
| 3 | Decompose into main tasks | → `references/step-03-decompose.md` |
| 4 | Expand to atomic subtasks | → `references/step-04-atomize.md` |
| 5 | Write task files | → `references/step-05-write-tasks.md` |
| 6 | Execute | → `references/step-06-execute.md` |

## Execution

1. **Check for resume state:**
   - Read `.claude/state/session_state.json`
   - If `resume_step` exists for task-builder, skip to that step
   - If task folder already has files, resume cycling (skip to step 6)

2. **Execute steps sequentially:**
   - Read each reference file before executing that step
   - Each step produces output the next step consumes

## Task Structure

```
tasks/[project-name]/
├── 000-index.md              ← main task index (wikilinks to all tasks)
├── 001-[main-task-1].md      ← main task with atomic subtask checklist
├── 002-[main-task-2].md
├── ...
└── NNN-[final-task].md
```

## Key Principles

- **Goal → Main Tasks → Atomic Subtasks** — three-tier decomposition
- **Index file** — 000-index.md links to all tasks, shows dependencies
- **Each task is self-contained** — enough context to implement without reading other tasks
- **Acceptance criteria are testable** — specific, mechanical, verifiable
- **Completion signal** — every task ends with "invoke `/kernel/complete`"
- **Protocol = Index** — 000-index.md points to tasks, tasks point to subtasks inline

## Outcome

After completion:
- Task folder created at `tasks/[project-name]/`
- All tasks written with requirements + acceptance criteria
- Autonomous cycling started on the folder
- Work delivered
