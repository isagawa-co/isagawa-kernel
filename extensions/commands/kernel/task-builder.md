# /kernel/task-builder

Decompose a goal into tasks and execute them autonomously.

## Usage

```
/kernel/task-builder Build the RAGA eval spec using DeepEval as template
/kernel/task-builder Create run-task-batch.sh for batch task execution
```

## Instructions

This command uses a skill-based approach with 8 steps.

### Load Skill

Read and follow: `.claude/skills/task-builder/SKILL.md`

### Quick Reference

| Step | Action |
|------|--------|
| 1 | Parse goal |
| 2 | Research context |
| 3 | Resolve template |
| 4 | Decompose into main tasks |
| 5 | Expand to atomic subtasks |
| 6 | Write task files |
| 7 | Execute (start cycling) |
| 8 | Structural audit |

### Key Principles

- **Goal → Main Tasks → Atomic Subtasks** — three-tier decomposition
- **Template resolution** — platform builds read the template repo, produce `_context/` files
- **Path provenance** — every BUILD path traces to `_context/path-mapping.json`
- **Index file** — 000-index.md links all tasks
- **Self-contained tasks** — each task implementable alone
- **Testable criteria** — every acceptance criterion is mechanical
- **Structural audit** — post-execution diff against template before shipping
- **Auto-execute** — don't ask, just build and cycle
