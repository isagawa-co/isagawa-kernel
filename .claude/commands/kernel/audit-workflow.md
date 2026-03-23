# /kernel/audit-workflow

Scan kernel infrastructure for gaps, then auto-fix.

## Usage

```
/kernel/audit-workflow
```

## Instructions

This command uses a skill-based approach with 6 steps.

### Load Skill

Read and follow: `.claude/skills/audit-workflow/SKILL.md`

### Quick Reference

| Step | Action |
|------|--------|
| 1 | Scan commands |
| 2 | Scan skills |
| 3 | Scan hooks + settings |
| 4 | Scan protocol + CLAUDE.md |
| 5 | Scan state + lessons |
| 6 | Report + generate fix tasks + auto-cycle |

### Key Principles

- **Read every file** — don't assume anything is wired correctly
- **Cross-reference** — commands ↔ CLAUDE.md ↔ protocol ↔ skills ↔ hooks
- **Audit first, fix second** — report findings before generating tasks
- **Verify fixes** — re-run audit after remediation to confirm clean
