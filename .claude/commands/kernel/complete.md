# /kernel/complete

Final gate before marking work done.

## Instructions

1. **Check state:**

   | Gate | Required |
   |------|----------|
   | Protocol created | `protocol_created: true` |
   | Anchored | `anchored: true` |

2. **Verify deliverables (MANDATORY):**

   Before marking complete, actually look at what the task produced. Tool call success is not verification.

   | Deliverable type | How to verify |
   |-----------------|---------------|
   | Files created | Read them — confirm content matches requirements |
   | Files modified | Read the changed sections — confirm the edit is correct |
   | State changed | Read state files — confirm values are what you expect |
   | Tests ran | Read results — confirm pass/fail matches expectations |
   | Repo changes | List files, read key ones — confirm nothing unexpected |
   | Decisions/docs | Read them — confirm they address the requirements |
   | Nothing tangible | State what you verified and why it's sufficient |

   **Report verification in the completion output.** List what you checked and the result.

3. **Determine completion mode:**

   Read `session_state.json` and `[domain]_workflow.json`.
   Check `one_shot` in `session_state.json` FIRST:

   ### Mode A: One-Shot (`one_shot: true`)

   Single task, then exit. Used by `run-task.sh` for headless execution.

   1. Add `current_task` to `completed_tasks` in `[domain]_workflow.json`
      - Use the **exact filename including `.md` extension**
   2. Check if tasks remain:
      - Scan task folder (`task_folder` from workflow state, default `tasks/`) for files NOT in `completed_tasks` or `skipped_tasks`
      - Exclude index files (000-*.md)
      - If none remain: output "ALL_TASKS_COMPLETE"
      - If tasks remain: output "ONE_SHOT_COMPLETE"
   3. Reset state for next fresh invocation:

      `session_state.json`:
      - `session_started: false`
      - `one_shot: false`
      - `context: { "last_completed": "[task name]" }`

      `[domain]_workflow.json`:
      - `anchored: false`
      - `actions_since_anchor: 0`
      - `current_task: null`
      - `attempts_on_current: 0`
      - Preserve `completed_tasks`, `skipped_tasks`, `total_tasks`

   4. Agent stops. No cycling, no next task pick.

   ### Mode B: Cycling (`cycling: true`, NOT one-shot)

   Continuous loop through tasks. Used in interactive sessions and batch mode.

   1. Add `current_task` to `completed_tasks`
   2. Reset `attempts_on_current` to 0
   3. Scan task folder for next incomplete task:
      - List .md files in `task_folder` (from workflow state)
      - Exclude index files (000-*.md)
      - Find lowest-numbered NOT in `completed_tasks` or `skipped_tasks`

   **Dual state update (BOTH files MUST be updated):**

   Update `[domain]_workflow.json`:
   - `completed_tasks`: add current task
   - `current_task`: next task filename (or null if done)
   - `attempts_on_current`: 0

   Update `session_state.json` context:
   - Completion summary for the task just finished
   - Next task name and what it requires
   - Current cycling progress (e.g., "4/7 tasks complete")

   Both files MUST be updated. Workflow tracks cycling state. Session tracks context for compaction recovery.

   - If next task found: announce it, read it, continue working
   - If none remain: announce "All N tasks complete (M skipped)", set `cycling: false`, `cycling_complete: true`

   ### Mode C: Single completion (neither one-shot nor cycling)

   Default behavior — just save context and report done.

4. **Save final conversation context (STRUCTURED):**
   - Update `context` key in `.claude/state/session_state.json` as a JSON object:

   ```json
   {
     "context": {
       "current_task": null,
       "task_folder": "tasks/[folder]/ or null",
       "progress": "N/M tasks complete (K skipped)",
       "last_completed": "task filename",
       "next_step": "next action or 'cycling complete'",
       "notes": "key decisions, open items"
     }
   }
   ```

   - MERGE into existing state, don't overwrite other keys

5. **Update state:**
   ```json
   {
     "complete": true,
     "complete_timestamp": "..."
   }
   ```

6. **Report:**
   ```
   COMPLETE

   Domain: [domain]
   Task: [what was done]
   Files created/modified: [count]
   Lessons learned: [count]

   Verified:
   - [what I checked] → [result]
   - [what I checked] → [result]

   Done.
   ```

## When to Invoke

- ALWAYS before saying "done"
- NEVER skip this gate
