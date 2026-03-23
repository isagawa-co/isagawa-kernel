# Step 5: Write Task Files

Create the task folder and write all task files.

## Process

1. **Create the project folder:**
   ```
   tasks/[project-name]/
   ```

2. **Write the index file (000-index.md):**

   ```markdown
   # [Project Name] — Task Index

   ## Goal
   [One-line goal from step 1]

   ## Tasks

   | # | Task | Dependencies | Status |
   |---|------|-------------|--------|
   | 001 | [[001-tag-verb-object]] | none | pending |
   | 002 | [[002-tag-verb-object]] | 001 | pending |
   | 003 | [[003-tag-verb-object]] | 001, 002 | pending |
   | ... | ... | ... | ... |

   ## Deliverables
   - [What exists when all tasks complete]
   ```

3. **Write each task file:**

   Follow this template exactly:

   ```markdown
   # [Task Title]

   ## Context
   [Why this task exists. What it produces. How it fits the project.]

   ## Dependencies
   - [List prior tasks that must be complete, or "None"]

   ## Phase Gate
   - [ ] [Artifact from dependency exists — file path, state value, repo condition]
   - [ ] [Any prerequisite state that must be true before starting]
   (Omit this section if Dependencies is "None")

   ## Requirements
   - [Specific requirement 1]
   - [Specific requirement 2]
   - [Include file paths, command names, exact values where applicable]

   ## Acceptance Criteria
   - [ ] [Mechanically verifiable criterion 1]
   - [ ] [Mechanically verifiable criterion 2]
   - [ ] [Include verification method: file exists, grep matches, test passes]

   ## Completion Signal
   When ALL acceptance criteria are met, invoke `/kernel/complete`.
   ```

   **Phase Gate vs Acceptance Criteria:**
   - Phase Gate = what must exist BEFORE you start (inputs)
   - Acceptance Criteria = what must exist AFTER you finish (outputs)
   - Agent checks Phase Gate first. If any gate fails, stop and report — don't start implementing.

4. **Verify all files written:**
   - Glob `tasks/[project-name]/*.md` — count matches expected total
   - Read 000-index.md — verify all tasks listed
   - Spot-check one task file — verify template followed

## Rules

- **Self-contained tasks** — each task has enough context to implement alone
- **No forward references** — task 002 can reference 001's output, not 003's
- **HUMAN REQUIRED** label — add to any task needing user decisions
- **Naming convention** — `NNN-[tag]-verb-object.md`
- **Completion signal** — every task ends with the `/kernel/complete` instruction
