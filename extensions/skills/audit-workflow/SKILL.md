# Audit Workflow — Skill

**Type:** Prescriptive
**Style:** Indexed — SKILL.md + references/

## What

Scans all kernel infrastructure for gaps, stale references, broken connections, and missing wiring. Reports findings, generates fix tasks, and auto-executes them. Combines audit + remediation in one pass.

## Steps

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Scan commands | → `references/step-01-scan-commands.md` |
| 2 | Scan skills | → `references/step-02-scan-skills.md` |
| 3 | Scan hooks + settings | → `references/step-03-scan-hooks.md` |
| 4 | Scan protocol + CLAUDE.md | → `references/step-04-scan-protocol.md` |
| 5 | Scan state + lessons | → `references/step-05-scan-state.md` |
| 6 | Scan testing completeness | → `references/step-06-scan-testing.md` |
| 7 | Scan task atomicity | → `references/step-07-scan-atomicity.md` |
| 8 | Report + fix | → `references/step-08-report-fix.md` |

## Execution

1. **Execute steps 1-7 sequentially:**
   - Read each reference file before executing that step
   - Each step produces a list of findings (or "clean")

2. **Step 8 aggregates and acts:**
   - If findings exist → generate fix tasks → cycle through them
   - If clean → report and done

## What Gets Checked

| Category | Checks |
|----------|--------|
| Commands | All commands referenced in CLAUDE.md? Naming consistent? |
| Skills | All skills referenced in CLAUDE.md + protocol? SKILL.md present? |
| Hooks | All hooks wired in settings.local.json? Files exist? |
| Protocol | References valid? Date current? All skills/hooks listed? |
| CLAUDE.md | Command tree matches actual files? Skills section complete? |
| State | Workflow state consistent? No stale values? |
| Lessons | Index matches lesson files? No orphan files? |
| Testing | Task sets have Level 3 prod tests? Gate contracts? Kernel integration test? |
| Atomicity | Each task = one action? No bundled multi-file writes or multi-command tasks? |

## Key Principles

- **Read every file** — don't assume, verify (Rule Zero)
- **Cross-reference** — every command/skill/hook must be referenced in at least CLAUDE.md or protocol
- **Report before fixing** — show findings first, then generate tasks
- **Idempotent** — running twice produces same result if nothing changed
