# Cross-Repo Agent Delegation

Delegate work to other repos via spawned agents. Used when a task requires operating in a different repo (e.g., running the spec factory).

## When to Use

- Goal requires the spec factory (`domain-spec-factory`) to produce a domain spec
- Goal requires building/testing in a template platform repo
- Any task where the target files live outside the current workspace

## Task Format

Tasks with `## Execution: factory` must include a `## Factory` section:

```markdown
## Execution
factory

## Factory
- target_repo: C:/path/to/target-repo
- command: /spec-factory-run ssh-image-testing
- template: C:/path/to/template-platform (optional — for factory builds)
- expected_output: output/ssh-image-testing/.claude/skills/*/SKILL.md
```

## Agent Prompt Template

When the cycling agent encounters a factory task, it spawns an Agent with this prompt structure:

```
You are operating in [target_repo].
Read [target_repo]/CLAUDE.md for kernel rules.
Read [target_repo]/.claude/skills/[skill]/SKILL.md for the pipeline.

Your goal: [command description]
Template platform: [template path] (read FRAMEWORK.md, framework/ structure)

Execute the pipeline steps. Write output to [target_repo]/output/[domain]/.
Report: what files were produced, any errors, validation results.
```

## How Parent Verifies

After the agent completes:
1. Check `expected_output` exists (file_exists or glob)
2. Read key output files to verify content quality
3. If expected_output missing: retry once with more context
4. After 3 attempts: skip task per cycling rules

## HUMAN REQUIRED Handling

When a factory task or any task says HUMAN REQUIRED:
1. Try to automate via `gh` CLI (create repos, PRs, releases)
2. Try API calls (REST, GraphQL)
3. Try writing state files directly
4. Only skip if physically impossible to automate

## Key Repos

| Repo | Purpose | Location |
|------|---------|----------|
| domain-spec-factory | Produces domain specs (12-step pipeline) | `C:/Users/solos/my_ai_projects/domain-spec-factory` |
| platform-docker | Docker image testing template | `C:/Users/solos/my_ai_projects/platform-docker` |
| py-selenium-framework-mcp | Selenium QA template | `C:/Users/solos/my_ai_projects/py-selenium-framework-mcp` |
| isagawa-kernel | Canonical kernel repo | `C:/Users/solos/my_ai_projects/isagawa-kernel` |
