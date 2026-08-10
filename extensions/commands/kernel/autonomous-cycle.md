# /kernel/autonomous-cycle

Start autonomous cycling through tasks. User-invoked entry point.

## Usage

```
/kernel/autonomous-cycle              → cycles tasks/
/kernel/autonomous-cycle kernel-test  → cycles tasks/kernel-test/
```

Default task folder: `tasks/`. If a subfolder is specified, cycles `tasks/[subfolder]/` instead.

## Instructions

1. **Resolve task folder:**
   - If argument provided: `tasks/[argument]/`
   - If no argument: `tasks/`
   - Verify the folder exists and has `.md` files

2. **Check gates:**

   | Gate | Required |
   |------|----------|
   | Protocol created | `protocol_created: true` |
   | Anchored | `anchored: true` |
   | Tasks exist | task folder has `.md` files |

3. **Scan tasks:**
   - List all `.md` files in the task folder
   - Exclude files in `completed_tasks` and `skipped_tasks`
   - If no remaining tasks: report "No tasks to cycle through" and STOP

4. **Initialize cycling state:**
   Update `[domain]_workflow.json` (MERGE, don't overwrite):
   ```json
   {
     "cycling": true,
     "task_folder": "tasks/" | "tasks/[subfolder]/",
     "total_tasks": N,
     "current_task": "[lowest-numbered remaining]",
     "attempts_on_current": 0
   }
   ```
   Preserve existing `completed_tasks` and `skipped_tasks` (for resume).

5. **Update session context:**
   Update `session_state.json` context:
   ```json
   {
     "status": "Cycling started — N tasks remaining",
     "current_task": "Implement [first task name]",
     "task_folder": "tasks/" | "tasks/[subfolder]/",
     "cycling": true
   }
   ```

6. **Report:**
   ```
   CYCLING STARTED

   Task folder: [path]
   Total tasks: N
   Already completed: M
   Remaining: K
   First task: [name]

   Starting implementation.
   ```

7. **Begin work:**
   - Read the first task
   - Start implementing
   - `/kernel/complete` handles cycling continuation from here

## When to Invoke

- User says "cycle", "start cycling", "run tasks", or similar
- After domain-setup + anchor when tasks exist
- Called automatically by `/kernel/task-builder` after generating tasks
- NEVER invoke automatically otherwise — this is user-triggered

## Related

- `/kernel/task-builder` — generates tasks from a goal, then invokes this command
