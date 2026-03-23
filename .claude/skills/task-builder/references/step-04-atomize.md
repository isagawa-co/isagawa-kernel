# Step 4: Expand to Atomic Subtasks

Break each main task into atomic, verifiable subtasks.

## What is Atomic

An atomic subtask is:
- **One action** — a single file write, a single test run, a single config change
- **Verifiable** — you can check if it's done mechanically (file exists, grep matches, test passes)
- **Independent** — can be verified without reading other subtasks

## Process

For each main task from step 3:

1. **List the concrete actions needed:**
   - What files get created/modified?
   - What commands get run?
   - What gets verified?

2. **Write as acceptance criteria checklist:**
   ```markdown
   ## Acceptance Criteria
   - [ ] `src/config.json` exists with `version` field
   - [ ] `src/index.ts` exports `createConfig` function
   - [ ] `npm run build` exits 0
   - [ ] `npm test` passes all tests
   ```

3. **Order within the task:**
   - Setup/prerequisites first
   - Implementation middle
   - Verification last

## Subtask Threshold

- If a main task has > 10 atomic subtasks → split into two main tasks
- If a main task has < 3 atomic subtasks → merge with adjacent task or it's already atomic

## Output

Each main task now has its full acceptance criteria defined. Ready for step 5 (writing task files).

## Rules

- Every subtask must be a checkbox item in acceptance criteria
- No vague criteria ("works well", "looks good") — must be mechanically testable
- Include the verification command where applicable (`grep`, `test -f`, `npm test`)
