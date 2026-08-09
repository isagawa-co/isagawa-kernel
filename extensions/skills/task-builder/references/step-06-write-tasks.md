# Step 6: Write Task Files + Gate Contract + Fixtures

Create the task folder, write all task files, the gate contract, and test fixtures.

## Process

1. **Create the project folder:**
   ```
   tasks/[project-name]/
   tasks/[project-name]/_context/      ← template + path mapping (from step 3)
   tasks/[project-name]/_test/fixtures/
   tasks/[project-name]/_test/expected/
   ```
   If step 3 produced `_context/template-file-map.json` and `_context/path-mapping.json`, they are already in `_context/`. Verify they exist.

2. **Write the index file (000-index.md):**

   ```markdown
   # [Project Name] — Task Index

   ## Goal
   [One-line goal from step 1]

   ## Template
   → [[_context/template-file-map.json]] — template platform file tree
   → [[_context/path-mapping.json]] — template-to-target path mapping
   (Omit this section if step 3 was skipped)

   ## Tasks

   | # | Task | Type | Dependencies | Status |
   |---|------|------|-------------|--------|
   | 001 | [[001-tag-verb-object]] | BUILD | none | pending |
   | 002 | [[002-tag-verb-object]] | BUILD | 001 | pending |
   | 003 | [[003-tag-verb-object]] | TEST | 001, 002 | pending |
   | ... | ... | ... | ... | ... |

   ## Gate Contract
   → [[gate-contract.md]]

   ## Deliverables
   - [What exists when all tasks complete]
   ```

3. **Write the gate contract (gate-contract.md):**

   ```markdown
   # Gate Contract — [Project Name]

   ## Verification Methods
   → [[references/verification-methods.md]]

   ## Structural Gates (platform builds only)
   → Generated from [[_context/path-mapping.json]]

   | ID | Check | Method | Pass Criteria | Fail Action |
   |----|-------|--------|---------------|-------------|
   | STRUCT-01 | ... | file_exists | ... | ... |
   | ... | ... | ... | ... | ... |

   ## Gates

   | ID | Check | Method | Pass Criteria | Fail Action |
   |----|-------|--------|---------------|-------------|
   | BUILD-01 | ... | file_exists | ... | ... |
   | FUNC-01 | ... | run_code | ... | ... |
   | TEST-01 | ... | run_test | ... | ... |
   | DATA-01 | ... | mock_data | ... | ... |

   ## Requirements Coverage
   Each gate maps to a task acceptance criterion. All acceptance criteria
   must have a corresponding gate.
   ```

4. **Write test fixtures (for mock_data and run_code gates):**

   For each gate with method `mock_data`:
   - Write `_test/fixtures/{{GATE-ID}}-input.json`
   - Write `_test/expected/{{GATE-ID}}-expected.json`
   - Use realistic data from step 2 research, not lorem ipsum

5. **Write each task file:**

   Follow this template exactly:

   ```markdown
   # [Task Title]

   ## Context
   [Why this task exists. What it produces. How it fits the project.]

   ## Type
   BUILD | TEST | RESEARCH

   ## Execution
   inline | agent | factory
   - `inline` — BUILD and RESEARCH tasks. Executed in the current session.
   - `agent` — TEST tasks. Spawned in isolation via the Agent tool. Reports results back.
   - `factory` — Cross-repo tasks. Spawns agent in a target repo. Agent operates under
     that repo's kernel (hooks, commands, state). Requires `## Factory` section with
     target_repo path, command to run, and expected output. See `references/cross-repo-delegation.md`.

   → [[references/cross-repo-delegation.md]] for factory execution details.

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

   ## Gates Satisfied
   [List gate IDs from gate-contract.md that this task covers]
   - BUILD-01, BUILD-02

   ## Completion Signal
   When ALL acceptance criteria are met, invoke `/kernel/complete`.
   ```

   **Phase Gate vs Acceptance Criteria:**
   - Phase Gate = what must exist BEFORE you start (inputs)
   - Acceptance Criteria = what must exist AFTER you finish (outputs)
   - Agent checks Phase Gate first. If any gate fails, stop and report.

6. **Verify all files written:**
   - Glob `tasks/[project-name]/*.md` — count matches expected total
   - Read 000-index.md — verify all tasks listed
   - Read gate-contract.md — verify all gates present
   - Check `_test/fixtures/` has one file per mock_data gate
   - Check `_test/expected/` has one file per mock_data gate
   - If platform build: verify `_context/template-file-map.json` and `_context/path-mapping.json` exist
   - Spot-check one task file — verify template followed

## Rules

- **Self-contained tasks** — each task has enough context to implement alone
- **No forward references** — task 002 can reference 001's output, not 003's
- **HUMAN REQUIRED** label — add to any task needing user decisions
- **Naming convention** — `NNN-[tag]-verb-object.md`
- **Completion signal** — every task ends with the `/kernel/complete` instruction
- **Gate coverage** — every acceptance criterion maps to at least one gate
- **Fixture coverage** — every mock_data gate has an input/expected pair
- **Type annotation** — every task has BUILD, TEST, or RESEARCH type
- **Execution mode** — every TEST task has `## Execution: agent`. BUILD/RESEARCH have `## Execution: inline`. TEST tasks ALWAYS run as spawned agents in isolation — no exceptions
- **Path provenance** — for platform builds, every BUILD task's target path must trace to `_context/path-mapping.json`. If a path cannot be traced, the task is malformed.
