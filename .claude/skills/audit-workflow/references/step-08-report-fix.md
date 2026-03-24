# Step 6: Report + Fix

Aggregate all findings and auto-remediate.

## Process

1. **Aggregate findings from steps 1-5:**

   ```
   AUDIT REPORT

   Commands: [N clean, M gaps]
   Skills: [N clean, M gaps]
   Hooks: [N clean, M gaps]
   Protocol + CLAUDE.md: [N clean, M gaps]
   State + Lessons: [N clean, M gaps]

   Total gaps: [sum]

   Findings:
   1. [gap description]
   2. [gap description]
   ...
   ```

2. **If zero gaps:** Report "AUDIT CLEAN — no gaps found." and stop.

3. **If gaps found — generate fix tasks:**
   - Create `tasks/audit-fixes/` folder
   - Write one task per gap (or group related gaps)
   - Follow task template: Context, Dependencies, Phase Gate, Requirements, Acceptance Criteria, Completion Signal
   - Name: `NNN-audit-fix-[description].md`

4. **Write index:**
   - Create `tasks/audit-fixes/000-index.md` with wikilinks to all fix tasks

5. **Start cycling:**
   - Invoke `/kernel/autonomous-cycle audit-fixes`
   - Agent fixes each gap autonomously

## Rules

- **Don't fix during audit** — audit first, fix second. Keeps findings clean.
- **One task per gap** — unless gaps are tightly related (e.g., "add X to both CLAUDE.md and protocol")
- **Acceptance criteria must verify the fix** — not just "edit the file" but "grep confirms the entry exists"
- **Re-run audit after fixes** — verify gaps are closed (invoke `/kernel/audit-workflow` again)
