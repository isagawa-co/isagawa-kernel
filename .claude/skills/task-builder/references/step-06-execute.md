# Step 6: Execute

Start autonomous cycling on the task folder.

## Process

1. **Report task plan to user:**

   ```
   TASK BUILDER COMPLETE

   Project: [project-name]
   Tasks created: N
   Folder: tasks/[project-name]/

   Task summary:
   - 001: [title] — [one-line description]
   - 002: [title] — [one-line description]
   - ...

   Starting autonomous cycling.
   ```

2. **Start cycling:**
   - Invoke `/kernel/autonomous-cycle [project-name]`
   - This hands off to the cycling workflow
   - Agent picks first task and begins implementation

## Rules

- Do NOT ask "should I start?" — just start
- The user already requested this work by invoking task-builder
- If any task is marked HUMAN REQUIRED, cycling will handle it (skip or ask)
