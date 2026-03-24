# /kernel/backlog

Create a new backlog item in the standard format.

## Usage

```
/kernel/backlog Research AI opportunities for Roberts Hawaii — warm contact with VP of HR
/kernel/backlog Build RAGA eval spec using DeepEval as template
/kernel/backlog Fix safe bash counter skip in master kernel
```

## Instructions

1. **Parse the input:**
   - Extract the core idea
   - Determine the tag: `kernel`, `domain`, `market`, `test`, or new tag if needed
   - Determine the verb: `research`, `build`, `fix`, `test`, `add`, `define`
   - Determine scope: BUILD, RESEARCH, TEST, or REFACTOR

2. **Get next number:**
   - Scan `docs/backlog/*.md` for the highest existing number
   - Next number = highest + 1 (skip numbers in `docs/backlog/done/`)

3. **Write the file:**

   Path: `docs/backlog/NNN-[tag]-[verb]-[object].md`

   Template:

   ```markdown
   # [Title]

   ## Status
   Open

   ## Priority
   [High | Medium | Low] — [one-line reason]

   ## Summary
   [2-3 sentences explaining what this is and why it matters]

   ## Requirements
   - [Key requirement or question 1]
   - [Key requirement or question 2]
   - [Key requirement or question 3]

   ## References
   - [Any relevant links, repos, contacts, backlog items]

   ## Task Builder Input
   - **Deliverable:** [What must exist when done]
   - **Scope:** [BUILD | RESEARCH | TEST | REFACTOR]
   - **Constraints:** [Repos, dependencies, human decisions, blockers]
   ```

4. **Report:**
   ```
   BACKLOG ITEM CREATED

   File: docs/backlog/NNN-[tag]-[verb]-[object].md
   Title: [title]
   Priority: [priority]
   Scope: [scope]

   Ready for /kernel/task-builder.
   ```

## Rules

- Ask the user for priority if not obvious from context
- If the user provides detailed requirements, include them all — don't summarize away detail
- The Task Builder Input section is MANDATORY — every backlog item must be task-builder-ready
- Use the naming convention: `NNN-[tag]-verb-object.md`
