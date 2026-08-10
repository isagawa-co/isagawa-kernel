# Step 3: Resolve Template

Identify and read the template platform that this build must match. Produce a file map and path mapping that all downstream steps consume.

## When This Step Applies

This step is **MANDATORY** when the goal involves:
- Building a platform spec (domain-spec-factory output)
- Creating a new QA platform (platform-*)
- Any BUILD that must match an existing platform's structure

If the goal is a standalone script, research task, or non-platform deliverable, skip this step and proceed to step 4.

## Process

1. **Identify the template platform:**
   - User specifies it in the goal (e.g., "use Docker as template")
   - If not specified, pick the closest existing platform from isagawa-qa org:
     - Web testing → platform-selenium or platform-playwright
     - Container/image testing → platform-docker
     - Evaluation/AI → test-platform-deepeval
     - SSH/remote → platform-ssh (if it already follows conventions)

2. **Read the template platform's actual structure:**
   - Clone or fetch the repo
   - Walk the full file tree — every directory, every file
   - Read FRAMEWORK.md for layer definitions
   - Read CONTRIBUTING.md for architecture rules
   - Read at least one interface, one task, one role, one test for patterns

3. **Write `_context/template-file-map.json`** in the task folder:
   → [[references/template-resolution.md]] for schema format and required/banned patterns

4. **Write `_context/path-mapping.json`** in the task folder:
   → [[references/template-resolution.md]] for mapping format

5. **Validate against platform schema:**
   - Check that every required directory from the schema has a mapping
   - Check that no mapping targets a banned pattern
   - If any required directory is unmapped, add it before proceeding

## Output

```
TEMPLATE RESOLVED

Template: [repo name]
Files mapped: N
Path mappings: M
Banned patterns checked: K (0 violations)

_context/template-file-map.json written
_context/path-mapping.json written

Proceeding to decompose.
```

## Rules

- NEVER skip this step for platform builds — it is the only thing preventing path drift
- NEVER invent paths from context — all BUILD task paths come from the mapping
- The template repo must be actually read, not recalled from memory
- Both `_context/` files are hard gates for step 4 — decomposition cannot start without them
- If the template repo is unavailable, STOP and ask the user — do not guess the structure
