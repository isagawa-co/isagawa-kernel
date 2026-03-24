# /kernel/session-start

Check state and resume if needed. Always invoke first.

## Instructions

1. **Check for existing state:**
   - Read `.claude/state/session_state.json` if exists
   - If `context` key exists, read and internalize it:
     - If `context` is a JSON object: read `current_task`, `progress`, `last_completed`, `next_step`, `notes`
     - If `context` is a string (legacy): treat as `{ "notes": "the string" }`
   - Report context summary so continuity is established
   - If `needs_restart` is true, handle restart resume (see Step 2)

2. **Handle restart resume:**

   If `needs_restart` is true:

   a. Clear the restart flag:
   ```json
   {
     "needs_restart": false
   }
   ```

   b. Check `resume_step` for skill-based resume:
   - If `resume_step` is set (e.g., `2`), resume `/kernel/domain-setup` at that step
   - Read the skill SKILL.md and continue from indicated step

   c. Otherwise check `resume_after_restart`:
   - If set to "anchor" or "/kernel/anchor", invoke `/kernel/anchor`
   - If set to other command, invoke that command

3. **Check for domain state:**
   - Look for `.claude/state/[domain]_workflow.json`
   - If exists, summarize current progress

4. **Domain persistence rule (CRITICAL):**
   - **If domain exists → USE IT** (never create new)
   - One project = one domain = one protocol
   - New capabilities (API, UI, etc.) extend existing protocol via `/kernel/learn`
   - Only invoke `/kernel/domain-setup` if NO domain exists at all

5. **Update session state (MERGE — read → modify → write):**

   **Merge pattern (MANDATORY):**
   1. Read `session_state.json` into a variable
   2. Modify ONLY these fields: `session_started`, `timestamp`, `resumed_from`
   3. Write the full object back (preserving all other keys)

   **Fields that MUST be preserved (do NOT overwrite):**
   - `context` — prior conversation state for resume
   - `domain` — which domain is active
   - `needs_learn` / `needs_learn_reason` — pending learn obligations
   - `one_shot` — set by run-task.sh for headless mode
   - `actions_log` — populated by PostToolUse hook

   **NEVER write a fresh JSON object.** Always read first, merge, then write.

   ```json
   // Merge these INTO the existing object:
   {
     "session_started": true,
     "timestamp": "...",
     "resumed_from": null | "previous_step"
   }
   ```

6. **Force anchor on fresh start (MERGE — read → modify → write):**

   If NOT resuming from restart (i.e., `needs_restart` was false or missing):

   **Merge pattern (MANDATORY):**
   1. Read `[domain]_workflow.json` into a variable
   2. Set ONLY `anchored: false`
   3. Write the full object back

   **Fields that MUST be preserved (do NOT overwrite):**
   - `completed_tasks` — progress across one-shot invocations
   - `skipped_tasks` — skipped task tracking
   - `cycling` / `task_folder` / `total_tasks` — cycling state
   - `actions_since_anchor` — current counter value

   **NEVER write a fresh JSON object.** Always read first, merge, then write.

7. **Report:**
   ```
   Session started.
   - State: [fresh | resumed from X]
   - Domain: [none | domain name]
   - Prior context: [summary of context key, or "none"]
   - Next: [what to do next]

   Proceeding.
   ```

## Resume Step Support

For skill-based commands like `/kernel/domain-setup`:

| State Field | Purpose |
|-------------|---------|
| `resume_step` | Step number to resume from (e.g., `2`) |
| `resume_after_restart` | Command to invoke (e.g., `"/kernel/anchor"`) |

When `resume_step` is set:
1. Invoke the relevant skill command
2. Skip to the indicated step
3. Continue from there

## State File Location

`.claude/state/session_state.json`
