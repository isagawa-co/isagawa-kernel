# Step 7: Execute — Dual Mode (BUILD inline + TEST spawned)

Start autonomous cycling for BUILD tasks. Spawn isolated sub-agents for TEST tasks. Produce validation report.

## Process

1. **Report task plan to user:**

   ```
   TASK BUILDER COMPLETE

   Project: [project-name]
   Tasks created: N (B build, T test, R research)
   Gates: G total in gate-contract.md
   Fixtures: F input/expected pairs
   Folder: tasks/[project-name]/

   Task summary:
   - 001: [title] — BUILD
   - 002: [title] — BUILD
   - 003: [title] — TEST (will spawn sub-agent)
   - ...

   Starting execution.
   ```

2. **Execute BUILD + RESEARCH tasks via in-session cycling:**
   - Invoke `/kernel/autonomous-cycle [project-name]`
   - Agent cycles through BUILD and RESEARCH tasks in order
   - Skip TEST tasks during this phase (they run after BUILD completes)
   - `/kernel/complete` advances to next task

3. **Execute TEST tasks via sub-agent spawning:**

   After all BUILD/RESEARCH tasks complete, execute each TEST task:

   ### For each TEST task:

   a. **Setup test workspace** (if task requires isolation):
      ```python
      # Via python script — no cd
      # Create temp workspace, copy necessary files
      # Do NOT git init in test workspace
      ```

   b. **Spawn run-task.sh in background:**
      ```bash
      bash /path/to/run-task.sh /path/to/test-workspace max_iterations 2>&1
      ```
      Run as background Bash task. Get notified on completion.

   c. **Wait for completion** — do NOT poll. The task notification will arrive.

   d. **Read results:**
      - Read the task output file
      - Read the test workspace state files
      - Read any output/log files produced
      - Check for validation report if applicable

   e. **Verify gates:**
      For each gate in gate-contract.md that maps to this TEST task:

      | Method | Verification |
      |--------|-------------|
      | `file_exists` | `test -f {{path}}` |
      | `grep` | `grep -q '{{pattern}}' {{file}}` |
      | `run_code` | Execute command, check exit 0 |
      | `run_test` | Execute test suite, check exit 0 |
      | `mock_data` | Read `_test/output/`, compare to `_test/expected/` |
      | `manual` | Read artifact, judge against pass criteria |

   f. **Handle failures** (retry decision tree):
      ```
      Gate failed?
        ├─ Fixture problem → fix fixture, re-verify gate only
        ├─ Task problem → fix implementation, re-spawn sub-agent
        ├─ Design problem → fix gate contract, regenerate, re-run
        └─ Environment problem → fix setup, re-spawn
      Max 3 retries per failure type.
      ```

4. **Produce validation report:**

   After all tasks (BUILD + TEST) complete, write:

   `tasks/[project-name]/_test/validation-report.json`:
   ```json
   {
     "project": "[project-name]",
     "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
     "total_gates": N,
     "passed": N,
     "failed": N,
     "skipped": N,
     "gates": [
       {
         "id": "BUILD-01",
         "check": "Config file exists",
         "method": "file_exists",
         "result": "PASS",
         "detail": null
       }
     ],
     "tasks": {
       "total": N,
       "build_completed": N,
       "test_completed": N,
       "skipped": N
     }
   }
   ```

5. **Present results to user:**

   ```
   EXECUTION COMPLETE

   Project: [project-name]
   BUILD tasks: N/N completed
   TEST tasks: N/N completed (M spawned as sub-agents)
   Gates: N/N passed

   Failed gates:
   - [GATE-ID]: [check] — [detail]

   Validation report: tasks/[project-name]/_test/validation-report.json

   Proceeding to structural audit.
   ```

   If step 3 was skipped (non-platform build), this is the final step. Otherwise proceed to step 8.

## Factory Task Execution

When cycling encounters a task with `## Execution: factory`, delegate to a spawned agent in the target repo.

→ [[references/cross-repo-delegation.md]] for full details.

### Quick Reference:

1. Read the task's `## Factory` section:
   ```markdown
   ## Factory
   - target_repo: C:/path/to/factory-repo
   - command: /spec-factory-run ssh-image-testing
   - expected_output: output/ssh-image-testing/.claude/skills/*/SKILL.md
   ```

2. Spawn Agent with prompt:
   - "You are operating in [target_repo]. Read [target_repo]/CLAUDE.md for kernel rules."
   - "Read [target_repo]/.claude/skills/spec-factory/SKILL.md for the pipeline."
   - "Execute: [command]"
   - "Report: what files were produced, any errors."

3. Wait for agent result. Read output. Verify expected_output exists.

4. If agent fails: retry once with more context. If still fails: skip task (3-attempt rule).

## Full Production Functionality Testing

→ [[references/production-testing.md]]

Every project MUST have Level 3 tests (production e2e). Read the reference for the testing hierarchy, deliverable-specific methods, and production test task template.

## When TEST Tasks Don't Need Isolation

Not every TEST task needs a sub-agent. Use this decision:

| Condition | Execution |
|-----------|-----------|
| Task needs restart (domain-setup, hook changes) | Spawn run-task.sh |
| Task needs clean state (fresh repo, no prior work) | Spawn run-task.sh |
| Task runs external process (run-task-batch.sh, scripts) | Spawn via background Bash |
| Task verifies files in current workspace | Run inline (grep, read, check) |

Simple verification tasks (read a file, grep for a pattern) run inline. Only spawn when the test genuinely needs isolation.

## Rules

- Do NOT ask "should I start?" — just start
- BUILD before TEST — always implement before verifying
- Sub-agents run in background — don't poll, wait for notification
- Every TEST sub-agent must have its results read and verified
- Validation report is MANDATORY — always produce it
- Present results to user — they want to review, not dig through files
