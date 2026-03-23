# /kernel/task-builder

Decompose a goal into tasks and execute them autonomously.

## Usage

```
/kernel/task-builder Build the RAGA eval spec using DeepEval as template
/kernel/task-builder Create run-task-batch.sh for batch task execution
```

## Instructions

This command uses a skill-based approach with 6 steps.

### Load Skill

Read and follow: `.claude/skills/task-builder/SKILL.md`

### Quick Reference

| Step | Action |
|------|--------|
| 1 | Parse goal |
| 2 | Research context |
| 3 | Decompose into main tasks |
| 4 | Expand to atomic subtasks |
| 5 | Write task files |
| 6 | Execute (start cycling) |

### Key Principles

- **Goal → Main Tasks → Atomic Subtasks** — three-tier decomposition
- **Index file** — 000-index.md links all tasks
- **Self-contained tasks** — each task implementable alone
- **Testable criteria** — every acceptance criterion is mechanical
- **Auto-execute** — don't ask, just build and cycle
