# Step 8: Structural Audit

Diff the built output against the template platform to catch structural drift before packaging or pushing.

## When This Step Applies

This step is **MANDATORY** when step 3 produced `_context/` files (platform builds). If step 3 was skipped (non-platform deliverable), this step is skipped and step 7 is the final step.

## Process

1. **Read `_context/template-file-map.json`** — get the template platform's complete file tree.

2. **Read `_context/path-mapping.json`** — get the template-to-target path mappings.

3. **Walk the output directory tree** — list every file and directory in the build output.

4. **For each template path, verify the mapped target path exists in the output:**
   - Template `framework/interfaces/image_interface.py` → target `framework/interfaces/ssh_interface.py` → verify exists
   - Template `tests/conftest.py` → target `tests/conftest.py` → verify exists
   - Track: matched, missing, extra (files in output with no template mapping)

5. **Check for banned pattern violations:**

   → [[references/template-resolution.md]] for the full banned patterns list.

   - Interface file inside `framework/_reference/` → VIOLATION
   - Tests only inside `framework/_reference/tests/` with no top-level `tests/` → VIOLATION
   - Fixtures inside `framework/_reference/fixtures/` instead of `tests/data/` → VIOLATION
   - Config as `.py` instead of `.json` in `framework/resources/config/` → VIOLATION

6. **Verify required files meet quality thresholds:**
   - `FRAMEWORK.md` has >50 lines (not a stub)
   - `CONTRIBUTING.md` exists and has architecture rules
   - `README.md` has installation + usage sections
   - `autologger.py` exists in `framework/resources/utilities/`

7. **Write structural audit results to the validation report:**

   Update `tasks/[project-name]/_test/validation-report.json`:
   ```json
   {
     "structural_audit": {
       "template_repo": "isagawa-qa/platform-docker",
       "total_mappings": 28,
       "matched": 26,
       "missing": [
         "framework/resources/utilities/autologger.py",
         "CONTRIBUTING.md"
       ],
       "violations": [],
       "extra_files": ["references/architecture.md"],
       "pass": false
     }
   }
   ```

8. **If structural audit fails (missing >0 or violations >0):**
   - List every missing path and every violation
   - Generate fix tasks for each gap (one task per missing file, one task per violation)
   - Execute fix tasks inline
   - Re-run the audit until it passes
   - Do NOT proceed to packaging/pushing until the audit passes

9. **Present final results to user:**

   ```
   STRUCTURAL AUDIT

   Template: [repo name]
   Mappings checked: N
   Matched: M
   Missing: K
   Violations: V

   Missing paths:
   - [path] (template: [template path])

   Violations:
   - [description]

   Fix tasks generated: F
   Fix tasks completed: F

   AUDIT RESULT: PASS | FAIL

   Done.
   ```

## Rules

- Structural audit is a hard gate — the build is not shippable until it passes
- Every missing path gets a fix task — no manual intervention needed
- Every violation gets a fix task — the agent moves files to correct locations
- Re-audit after fixes — never trust a single pass after corrections
- Do NOT package, push, or mark the project complete until the audit passes
