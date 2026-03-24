# One-Shot Task Execution via CLI

## Problem

Currently, autonomous cycling requires an open interactive Claude Code session. There's no way to fire-and-forget a single task from the command line. We need headless invocation — script launches Claude, agent does one task, process exits.

## Goal

Any kernel-enabled repo can execute its next task via a single CLI command with no human interaction (except pre-defined HITL checkpoints).

## Usage

```bash
# From any directory
run-task.sh /path/to/repo

# Or from within the repo
run-task.sh

# Or cron it
*/30 * * * * /path/to/run-task.sh /path/to/repo
```

## What Needs to Happen

### 1. CLI Invocation

A script that calls Claude in non-interactive mode:

```bash
claude -p "<prompt>" --cwd /path/to/repo
```

The prompt tells the agent to: session-start → anchor → pick next task → implement → complete → exit.

### 2. One-Shot Mode Flag

Session state needs a flag so `/kernel/complete` knows to exit instead of cycling:

```json
{
  "one_shot": true
}
```

Set by the invocation prompt or by a new flag on `/kernel/autonomous-cycle --once`.

### 3. Update `/kernel/complete`

Add one-shot check:

- If `one_shot: true` in session/workflow state → report completion, clean up state, exit
- If `cycling: true` and not one-shot → continue to next task (existing behavior)

### 4. Session Close

After complete in one-shot mode:
- State files updated (completed_tasks, etc.)
- Git commit (if configured)
- Agent signals done — CLI process exits cleanly

## Design Questions

- How does Claude CLI handle non-interactive mode? (`-p` flag? `--task`? `--dangerously-skip-permissions`?)
- How do HITL checkpoints work in headless mode? (skip? fail? queue for next run?)
- Should the script accept a specific task number, or always pick next incomplete?
- Windows `.bat` + Unix `.sh`, or just `.sh` with Git Bash on Windows?

## Scope

This is a kernel-level feature. Changes go into:
- `isagawa-kernel` — new script, updated complete command
- Any repo using the kernel inherits it

## Priority

High — enables batch processing, scheduled execution, CI/CD integration.
