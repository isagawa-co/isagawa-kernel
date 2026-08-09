# Step 2: Scan Skills

Verify all skills are properly structured and referenced.

## Process

1. **List actual skill directories:**
   - Glob `.claude/skills/*/SKILL.md`
   - Note each skill name

2. **Check each skill structure:**
   - Has `SKILL.md` with step table
   - Has `references/` directory (if steps reference it)
   - Every step referenced in SKILL.md has a matching file in references/
   - No orphan files in references/ not listed in SKILL.md

3. **Cross-reference with CLAUDE.md:**
   - Every skill directory should be mentioned in CLAUDE.md Skills section
   - Flag unlisted skills

4. **Cross-reference with protocol:**
   - Read protocol index
   - Every skill should appear in the protocol's Kernel references table
   - Flag unlisted skills

## Output

```
Skills: [N found]
Gaps:
- [skill] missing from CLAUDE.md
- [skill] missing from protocol
- [skill]/references/step-XX.md referenced in SKILL.md but file missing
- [skill]/references/orphan.md exists but not in SKILL.md step table
Clean: [list of skills with no issues]
```
