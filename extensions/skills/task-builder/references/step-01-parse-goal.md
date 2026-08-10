# Step 1: Parse Goal

Understand what the user wants before decomposing.

## Input Types

The task-builder accepts two input types:

### Type A: Direct goal (user provides a sentence)
```
/kernel/task-builder Build a webhook receiver for Stripe events
```
The agent must extract deliverable, scope, and constraints from the sentence.

### Type B: Backlog reference (user points to a backlog item)
```
/kernel/task-builder docs/backlog/018-domain-research-roberts-hawaii-ai.md
```
The agent reads the backlog item and extracts the `## Task Builder Input` section if present. If not present, extract from the full backlog content.

## Process

1. **Detect input type:**
   - If the argument is a file path or references a backlog item → Type B (read it)
   - Otherwise → Type A (parse the sentence)

2. **For Type B — read the backlog item:**
   - Read the file
   - Look for `## Task Builder Input` section — if present, use it directly
   - If no Task Builder Input section, extract from the full content:
     - Deliverable from `## Output` or `## Summary`
     - Scope from the nature of the work
     - Constraints from `## Dependencies`, `## Key Questions`, or `## Steps`

3. **For Type A — extract from the sentence:**
   - Deliverable: what artifact(s) must exist when done?
   - Scope: BUILD, RESEARCH, TEST, or REFACTOR?
   - Constraints: any repos, dependencies, or human decisions mentioned?

4. **For both types:**
   - Identify the project name — normalize to kebab-case for the folder name
   - Check for additional context:
     - Other backlog items that relate? (check `docs/backlog/`)
     - Prior research? (check `docs/`, `research/`)
     - Template or reference repo? (user may specify)

## Output

Report to user:

```
GOAL PARSED

Project: [project-name]
Source: [direct goal | backlog item NNN]
Deliverable: [what will exist when done]
Scope: [BUILD | RESEARCH | TEST | REFACTOR]
Constraints: [any blockers or human decisions needed]
Target: tasks/[project-name]/

Proceeding to research.
```

## Rules

- Do NOT start decomposing yet — just understand
- If the goal is ambiguous AND no backlog item exists, clarify with the user BEFORE proceeding
- If a backlog item exists, read it — it has requirements already defined
- Backlog items with `## Task Builder Input` are pre-formatted for fast intake
