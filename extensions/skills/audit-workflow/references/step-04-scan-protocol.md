# Step 4: Scan Protocol + CLAUDE.md

Verify the protocol index and CLAUDE.md are complete and current.

## Process

1. **Read protocol:**
   - `.claude/protocols/[domain]-protocol.md`
   - Extract all file references from tables

2. **Verify each reference exists:**
   - Every file listed in the protocol should exist on disk
   - Flag missing files

3. **Read CLAUDE.md:**
   - Extract command tree listing
   - Extract skills section entries

4. **Cross-reference CLAUDE.md with actual files:**
   - Every command in `.claude/commands/kernel/` should be in the tree
   - Every skill in `.claude/skills/` should be in the skills section
   - Flag mismatches in either direction

5. **Check freshness:**
   - Protocol `Updated` date — is it recent?
   - Do recent changes (new commands, skills, hooks) appear in both files?

## Output

```
Protocol references: [N total]
CLAUDE.md commands: [N listed] vs [N actual]
CLAUDE.md skills: [N listed] vs [N actual]
Gaps:
- [file] referenced in protocol but doesn't exist
- [command] exists but not in CLAUDE.md command tree
- [skill] exists but not in CLAUDE.md skills section
- Protocol date stale (last updated: [date])
Clean: [what's consistent]
```
