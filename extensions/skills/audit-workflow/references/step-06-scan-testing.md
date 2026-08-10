# Step 6: Scan Testing Completeness

Verify that any project with BUILD tasks also has adequate TEST tasks covering all 3 levels.

## Process

1. **Scan active task folders:**
   - Glob `tasks/*/000-index.md` (skip `tasks/completed/`)
   - For each active task set, read the index

2. **Check testing levels per task set:**

   Every project that builds something MUST have:

   | Level | What | How to Check |
   |-------|------|-------------|
   | Level 1: Structural | Files exist, content present | At least 1 task with `file_exists` or `grep` acceptance criteria |
   | Level 2: Functional | Code runs, imports work | At least 1 task with `run_code`, `run_test`, or `mock_data` criteria |
   | Level 3: Production | E2E in realistic conditions | At least 1 TEST-type task that spawns a sub-agent or runs the deliverable e2e |

   Flag any project missing Level 2 or Level 3 tests.

3. **Check kernel integration testing:**

   If the project produces a domain spec (SKILL.md + workflow.md), it MUST have a kernel integration test:

   | Check | Required |
   |-------|----------|
   | Install kernel into clean workspace | Yes |
   | Run domain-setup (discovers spec) | Yes |
   | Restart for hooks | Yes (simulated via run-task.sh iterations) |
   | Run anchor (reads protocol) | Yes |
   | Execute at least 1 task under enforcement | Yes |
   | Verify hooks fire (counter increments) | Yes |

   Flag any domain spec project without a kernel integration test task.

4. **Check gate contract exists:**
   - Every task set should have a `gate-contract.md`
   - Flag task sets without one
   - If gate contract exists, verify gate count is reasonable (10-30)

5. **Check test fixtures:**
   - If gate contract has `mock_data` or `run_code` gates, `_test/fixtures/` should exist
   - Flag functional gates without corresponding fixtures

## Output

```
Testing completeness: [N task sets scanned]
Gaps:
- [project] missing Level 2 tests (no functional verification)
- [project] missing Level 3 tests (no production e2e)
- [project] produces domain spec but has no kernel integration test
- [project] missing gate-contract.md
- [project] has mock_data gates but no fixtures
Clean: [list of projects with complete testing]
```

## Why This Matters

Without this check:
- Projects ship with only "does the file exist?" tests
- Domain specs are never tested with the actual kernel
- The agent claims "all tests pass" based on grep checks alone
- Production failures surface at the customer, not during build
