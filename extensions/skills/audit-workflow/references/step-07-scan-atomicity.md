# Step 7: Scan Task Atomicity

Verify each task file follows the one-action rule.

## Principle

**One task = one action = one deliverable.**

The unit of atomicity is the **deliverable**, not the content. Ask: "How many distinct things exist after this task that didn't exist before?" If the answer is 1, it's atomic. If the answer is 2+, it's bundled.

## Process

1. **For each active task set** (`tasks/*/` excluding `tasks/completed/`):

2. **For each task file (NNN-*.md), apply the deliverable count test:**

   Read the Requirements and Acceptance Criteria sections. Count deliverables:

   | Question | How to count |
   |----------|-------------|
   | How many files get **created** that didn't exist before? | Each new file = 1 deliverable |
   | How many files get **modified** that weren't modified before? | Each modified file = 1 deliverable |
   | How many commands get **run** whose output matters? | Each command whose exit code or output is checked = 1 deliverable |

   **If deliverable count = 1 → ATOMIC (pass)**
   **If deliverable count > 1 → BUNDLED (flag for splitting)**

   The content, complexity, or number of sections within a single deliverable is irrelevant. A file with 3 sections is still 1 file. A command that produces 50 lines of output is still 1 command.

3. **Cross-check against gate contract:**
   - Each task should map to 1-2 gates
   - If a task satisfies 4+ gates, it's likely bundled — apply the deliverable count test to confirm

4. **Phase Gate checkboxes are NOT deliverables:**
   - `## Phase Gate` checkboxes are prerequisites (inputs), not outputs
   - Do not count them when evaluating atomicity

## Output

```
Atomicity: [N task sets scanned]
Gaps:
- [project]/[task] produces N deliverables (should be N tasks)
- [project]/[task] satisfies 5 gates (likely bundled)
Clean: [list of task sets with no atomicity issues]

Decision log:
- [task]: 1 file created → PASS
- [task]: 2 files created → FAIL (split into 2 tasks)
- [task]: 1 command run → PASS
```
