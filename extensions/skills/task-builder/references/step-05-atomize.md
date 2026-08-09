# Step 5: Expand to Atomic Subtasks + Gate Contract

Break each main task into atomic, verifiable subtasks. For the project as a whole, generate a gate contract that serves as the mechanical test specification.

## What is Atomic

An atomic subtask is:
- **One action** — a single file write, a single test run, a single config change
- **Verifiable** — you can check if it's done mechanically (file exists, grep matches, test passes)
- **Independent** — can be verified without reading other subtasks

## Process

For each main task from step 4:

1. **Classify task type:**

   | Type | Characteristics | Execution Mode |
   |------|----------------|----------------|
   | BUILD | Creates/modifies files, writes code, edits configs | In-session cycling |
   | TEST | Verifies deliverables, runs in isolation, may need restarts | Spawn run-task.sh in background |
   | RESEARCH | Web search, document analysis, produces docs | In-session cycling |

2. **List the concrete actions needed:**
   - What files get created/modified?
   - What commands get run?
   - What gets verified?

3. **Write as acceptance criteria checklist:**
   ```markdown
   ## Acceptance Criteria
   - [ ] `src/config.json` exists with `version` field
   - [ ] `src/index.ts` exports `createConfig` function
   - [ ] `npm run build` exits 0
   - [ ] `npm test` passes all tests
   ```

4. **Order within the task:**
   - Setup/prerequisites first
   - Implementation middle
   - Verification last

## Path Validation Rule (MANDATORY for platform builds)

When step 3 produced `_context/path-mapping.json`, every BUILD task that creates a file MUST derive its target path from that mapping.

→ [[references/template-resolution.md]] for the full platform schema and banned patterns.

1. **Every file path in a BUILD task must trace back to `_context/path-mapping.json`** — never invented from context or memory.

2. **Banned path patterns** (hard gate, no exceptions):
   - `framework/_reference/*_interface.py` — interface MUST be in `framework/interfaces/`
   - `framework/_reference/tests/` as the sole test location — tests MUST exist at top-level `tests/`
   - `framework/_reference/fixtures/` — fixtures go in `tests/data/`
   - Config as a `.py` file in `resources/` — use `environment_config.json` in `framework/resources/config/`

3. **Required path patterns** (must appear in at least one BUILD task):
   - `framework/interfaces/{domain}_interface.py`
   - `framework/resources/utilities/autologger.py`
   - `framework/resources/config/environment_config.json`
   - `tests/conftest.py`
   - `FRAMEWORK.md` (detailed, not a stub)
   - `CONTRIBUTING.md`

4. **If a BUILD task's path matches a banned pattern, STOP.** Re-read `_context/path-mapping.json` and correct the path before writing the task.

## Structural Validation Gates (auto-generated for platform builds)

When `_context/path-mapping.json` exists, add these gates to EVERY platform build gate contract:

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| STRUCT-01 | Interface in correct dir | file_exists | `test -f framework/interfaces/*_interface.py` | Move file |
| STRUCT-02 | No interface in _reference | run_code | `! ls framework/_reference/*_interface.py 2>/dev/null` | Move file |
| STRUCT-03 | Top-level tests dir | file_exists | `test -d tests/` | Create dir |
| STRUCT-04 | conftest at top level | file_exists | `test -f tests/conftest.py` | Move file |
| STRUCT-05 | autologger exists | file_exists | `test -f framework/resources/utilities/autologger.py` | Create file |
| STRUCT-06 | env config exists | file_exists | `test -f framework/resources/config/environment_config.json` | Create file |
| STRUCT-07 | CONTRIBUTING exists | file_exists | `test -f CONTRIBUTING.md` | Create file |
| STRUCT-08 | FRAMEWORK.md detailed | run_code | `test $(wc -l < FRAMEWORK.md) -gt 50` | Expand doc |

These STRUCT gates are in addition to the project-specific BUILD/FUNC/TEST/DATA gates.

## Gate Contract Generation

After atomizing all tasks, generate a gate contract for the project. This is the mechanical test specification — every deliverable gets a gate.

### Gate Contract Format (5 columns):

```markdown
## Gate Contract

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| BUILD-01 | Config file exists | file_exists | `test -f src/config.json` | Create file |
| BUILD-02 | Config has version field | grep | `grep -q '"version"' src/config.json` | Add field |
| FUNC-01 | Module imports cleanly | run_code | `python -c "from src import config"` exits 0 | Fix imports |
| TEST-01 | All tests pass | run_test | `pytest tests/ -v` exits 0 | Fix failing tests |
| DATA-01 | Pipeline processes input | mock_data | Input fixture → expected output | Fix processing logic |
```

### Verification Methods (3 tiers):

| Tier | Method | When to Use |
|------|--------|-------------|
| **Structural** | `file_exists`, `grep`, `json_valid` | File and content presence checks |
| **Functional** | `run_code`, `run_test`, `mock_data` | Code execution and data processing |
| **Semantic** | `manual` (LLM judgment) | Content quality, documentation clarity |

→ [[references/verification-methods.md]] for details on each method.

### Gate Rules:
- **One check per gate** — never combine two verifications
- Target **10-30 gates** depending on project complexity (STRUCT gates count toward this)
- Prefer machine-verifiable methods (structural > functional > semantic)
- Every BUILD task should have at least 1 structural gate
- Every TEST task should have at least 1 functional gate
- `manual` gates are last resort only

## Granularity Rule (CRITICAL)

**One task = one action. No exceptions. No bundling.**

- Each task file produces exactly ONE deliverable: one file written, one command run, one config changed
- If a task requires writing 4 files → that's 4 tasks, not 1 task with 4 criteria
- If a test requires 3 setup steps + 1 verification → that's 4 tasks
- If a main task has > 10 atomic subtasks → split into multiple main tasks
- **NEVER merge tasks for being "too small."** A task that copies one file IS a valid task. A task that runs one command IS a valid task. Small tasks are correct tasks.
- The "merge if <3" rule is REMOVED — it caused the agent to bundle actions 3 times despite user correction
- Acceptance criteria verify the ONE action, not multiple bundled actions

## Testing Completeness Check (MANDATORY)

Before finishing atomization, verify every deliverable has all 3 testing levels.

→ [[references/production-testing.md]] for deliverable-specific test methods and the production test task template.

### 3-Tier Testing Hierarchy:

```
Level 1: Does it exist? (structural — file_exists, grep)
Level 2: Does it run? (functional — run_code, run_test, mock_data)
Level 3: Does it produce correct results in a real scenario? (production — spawn run-task.sh, run e2e)
```

### Checklist — run for EACH deliverable:

| Deliverable | L1 test task? | L2 test task? | L3 test task? |
|-------------|---------------|---------------|---------------|
| [deliverable 1] | ✓/MISSING | ✓/MISSING | ✓/MISSING |
| [deliverable 2] | ✓/MISSING | ✓/MISSING | ✓/MISSING |
| ... | ... | ... | ... |

- If ANY cell is MISSING → add a TEST task for that level before proceeding to step 6
- L3 tests MUST exercise the deliverable under real conditions (spawn run-task.sh, invoke the outer kernel loop, run the actual workflow)
- "Simulate" is NOT Level 3 — Level 3 means actually running the thing, not reading/writing state files manually
- Reference the deliverable-specific methods table in production-testing.md for how to test each type

### Common L3 gaps to watch for:
- Scripts exist but are never actually executed
- Hooks are piped test JSON but never fire during a real session
- Commands are copied but never invoked under kernel enforcement
- Domain specs are built but never run through domain-setup → restart → cycling
- Validation flows are designed but never tested against even a mock spec

## Output

- Each main task has its full acceptance criteria defined
- Project-level gate contract generated (including STRUCT gates if platform build)
- Task types classified (BUILD/TEST/RESEARCH)
- **Path validation passed — all BUILD paths trace to path-mapping.json** (if platform build)
- **Testing completeness verified — all deliverables have L1/L2/L3 coverage**
- Ready for step 6 (writing task files)

## Rules

- Every subtask must be a checkbox item in acceptance criteria
- No vague criteria ("works well", "looks good") — must be mechanically testable
- Include the verification command where applicable
- Gate contract IDs use prefix: STRUCT-, BUILD-, FUNC-, TEST-, DATA-, DOC-
- **NEVER bundle multiple file writes, copies, or commands into one task** — if it touches N files, it's N tasks
- **NEVER group test steps** — setup workspace, install deps, run test, verify results are each separate tasks
- If you find yourself writing "Step 1... Step 2... Step 3..." in a Requirements section, each step should be its own task
- **NEVER generate a BUILD task path that isn't in path-mapping.json** (platform builds only)
