# Step 1: Parse Goal

Understand what the user wants before decomposing.

## Input

The user provides a goal as a string. Examples:
- "Build the RAGA eval spec using DeepEval as template"
- "Create a run-task-batch.sh script for batch task execution"
- "Set up CI/CD for the kernel repo"

## Process

1. **Extract the core deliverable** — what artifact(s) must exist when done?
2. **Identify the project name** — normalize to kebab-case for the folder name
3. **Check for existing context:**
   - Is there a backlog item for this? (check `docs/backlog/`)
   - Is there prior research? (check `docs/`, `research/`)
   - Is there a template or reference? (user may specify)
4. **Identify constraints:**
   - Target repo (this workspace or another?)
   - Dependencies on other projects
   - Human-required decisions

## Output

Report to user:

```
GOAL PARSED

Project: [project-name]
Deliverable: [what will exist when done]
Context found: [backlog items, research, templates]
Constraints: [any blockers or human decisions needed]
Target: tasks/[project-name]/

Proceeding to research.
```

## Rules

- Do NOT start decomposing yet — just understand
- If the goal is ambiguous, clarify with the user BEFORE proceeding
- If a backlog item exists, read it — it may have requirements already defined
