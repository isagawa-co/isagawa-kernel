# Step 1: Scan Commands

Verify all commands are properly registered and consistent.

## Process

1. **List actual command files:**
   - Glob `.claude/commands/kernel/*.md`
   - Note each filename

2. **Read CLAUDE.md command tree:**
   - Find the `Commands` section
   - Extract the listed commands

3. **Cross-reference:**
   - Every file in the directory should appear in CLAUDE.md
   - Every entry in CLAUDE.md should have a matching file
   - Flag mismatches

4. **Check command content:**
   - Each command should reference a skill (if complex) or have inline instructions
   - Each command should have `## Instructions` and `## When to Invoke`

## Output

```
Commands: [N found]
Gaps:
- [command] exists but not in CLAUDE.md
- [command] in CLAUDE.md but file missing
- [command] missing ## Instructions section
Clean: [list of commands with no issues]
```
