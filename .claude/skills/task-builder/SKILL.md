# Task Builder — Skill

**Type:** Prescriptive
**Style:** Indexed — SKILL.md + references/

## What

Takes a user-provided goal and autonomously decomposes it into a structured task set with gate contracts and test fixtures, then executes it — BUILD tasks inline, TEST tasks via spawned sub-agents. Produces a validation report on completion.

## Steps

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Parse goal | → `references/step-01-parse-goal.md` |
| 2 | Research context | → `references/step-02-research.md` |
| 3 | Resolve template | → `references/step-03-resolve-template.md` |
| 4 | Decompose into main tasks | → `references/step-04-decompose.md` |
| 5 | Atomize + gate contract | → `references/step-05-atomize.md` |
| 6 | Write tasks + fixtures | → `references/step-06-write-tasks.md` |
| 7 | Execute (dual mode) | → `references/step-07-execute.md` |
| 8 | Structural audit | → `references/step-08-structural-audit.md` |

## Supporting References

| File | Purpose |
|------|---------|
| `references/template-resolution.md` | Platform schema, path mapping format, banned patterns |
| `references/verification-methods.md` | 3-tier verification + retry decision tree + fixture formats + test data principles |
| `references/production-testing.md` | Level 3 e2e testing — deliverable-specific methods + production test template |
| `references/cross-repo-delegation.md` | Cross-repo agent delegation for factory tasks |

## Execution

1. **Check for resume state:**
   - Read `.claude/state/session_state.json`
   - If `resume_step` exists for task-builder, skip to that step
   - If task folder already has files, resume cycling (skip to step 7)

2. **Execute steps sequentially:**
   - Read each reference file before executing that step
   - Each step produces output the next step consumes

## Task Structure

```
tasks/[project-name]/
├── 000-index.md              ← task index with wikilinks + task types
├── gate-contract.md          ← mechanical test specification (5-column)
├── 001-[build-task].md       ← BUILD: implemented in-session
├── 002-[build-task].md
├── 003-[test-task].md        ← TEST: spawned via run-task.sh
├── ...
├── NNN-[final-task].md
├── _context/                 ← template + path mapping (from step 3)
│   ├── template-file-map.json ← complete file tree of template platform
│   └── path-mapping.json     ← template path → target path mapping
└── _test/
    ├── fixtures/             ← input fixtures for mock_data gates
    │   └── DATA-01-input.json
    ├── expected/             ← expected outputs for mock_data gates
    │   └── DATA-01-expected.json
    └── validation-report.json ← produced after execution completes
```

## Key Principles

- **Goal → Main Tasks → Atomic Subtasks** — three-tier decomposition
- **Gate contract** — mechanical test spec, one check per gate, 5-column format
- **3-tier verification** — structural (file_exists, grep), functional (run_code, run_test, mock_data), semantic (manual)
- **Dual execution** — BUILD tasks cycle in-session, TEST tasks spawn sub-agents via run-task.sh
- **Test fixtures** — input/expected JSON pairs for functional gates, realistic domain data
- **Validation report** — JSON artifact with per-gate pass/fail, produced on completion
- **Retry decision tree** — categorize failure (fixture, task, design, environment), retry at right level
- **Phase Gates** — verify prerequisites before starting each task
- **Index file** — 000-index.md links all tasks, shows types and dependencies
- **Template resolution** — platform builds must read the template repo and produce `_context/` files before decomposing
- **Path provenance** — every BUILD task path traces to `_context/path-mapping.json`, never invented
- **Structural audit** — post-execution diff against template catches drift before shipping
- **Protocol = Index** — point to files, don't duplicate

## Outcome

After completion:
- Task folder created at `tasks/[project-name]/`
- Gate contract with mechanical verification for every deliverable
- Test fixtures for functional gates
- All BUILD tasks implemented via in-session cycling
- All TEST tasks verified via spawned sub-agents
- Validation report produced at `_test/validation-report.json`
- Results presented to user for review
