# Step 5: Scan State + Lessons

Verify state files are consistent and lessons index matches actual files.

## Process

1. **Read workflow state:**
   - `.claude/state/[domain]_workflow.json`
   - Check for stale values:
     - `current_task` pointing to a task that doesn't exist
     - `completed_tasks` referencing files not in the task folder
     - `actions_limit` set to unexpected value
     - `cycling: true` but no task folder active

2. **Read session state:**
   - `.claude/state/session_state.json`
   - Check for stale values:
     - `needs_learn: true` with no active issue
     - `needs_restart: true` lingering from old session
     - `context` referencing work from a different task set

3. **Read lessons index:**
   - `.claude/lessons/lessons.md`
   - Extract all topic file references from the table

4. **Verify lesson files exist:**
   - Every file in the lessons table should exist in `.claude/lessons/`
   - Every `.md` file in `.claude/lessons/` (except lessons.md) should be in the table
   - Flag orphans and missing files

## Output

```
State:
- Workflow: [consistent | issues found]
- Session: [consistent | issues found]
Lessons: [N in index] vs [N on disk]
Gaps:
- [issue description]
Clean: [what's consistent]
```
