# Production Functionality Testing

TEST tasks are NOT just structural checks. They must exercise the deliverable in production-like conditions.

## What "full prod testing" means:

| Deliverable Type | How to Test |
|-----------------|-------------|
| Script (run-task.sh, etc.) | Actually run it against a test repo. Verify outputs, state, logs. |
| Hook (*.py) | Pipe real input JSON to it. Verify stdout/stderr and state changes. |
| Command (*.md) | Invoke it in a test workspace. Verify it produces expected results. |
| Domain spec (SKILL.md + workflow) | Install kernel → domain-setup → restart → cycling → verify all steps work |
| API integration | Call real endpoints (or mock server). Verify responses. |
| Data pipeline | Feed real input data. Verify output matches expected. |

## Testing Hierarchy

All three levels are required, not just level 1:

```
Level 1: Does it exist? (structural — file_exists, grep)
Level 2: Does it run? (functional — run_code, run_test, mock_data)
Level 3: Does it produce correct results in a real scenario? (production — spawn sub-agent, run e2e)
```

**Every project must have Level 3 tests.** If the task-builder only produces Level 1 gates, the testing is incomplete. The deliverable must be exercised in a realistic scenario:

- Run the script and check the actual output files (not just that the script exists)
- Invoke the command and verify the state changes it makes (not just that the command file exists)
- Execute the workflow end-to-end and compare results against expectations (not just that the workflow.md is well-formatted)

## Production Test Task Template

```markdown
# Production Test: [Deliverable Name]

## Type
TEST

## Requirements
- Set up test environment (reset state, clean outputs, copy files)
- Execute the deliverable in production-like conditions
- Wait for completion
- Read ALL output files and verify content matches expectations
- Read ALL state files and verify values are correct
- Check for unexpected side effects (files that shouldn't exist, state that shouldn't change)

## Acceptance Criteria
- [ ] Test environment set up (verify before run)
- [ ] Deliverable executed successfully (verify exit code or completion signal)
- [ ] Output file 1: [expected content] (verify by READING the file)
- [ ] Output file 2: [expected content] (verify by READING the file)
- [ ] State file: [expected values] (verify by READING the JSON)
- [ ] No unexpected side effects (verify by listing directory)
```
