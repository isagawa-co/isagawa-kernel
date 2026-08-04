# Step 10: Update State

## Session State

Create/update `.claude/state/session_state.json`.

**MERGE rule:** If `session_state.json` already exists, MERGE these fields into the existing state. Preserve the `context` key and any other existing keys. Do NOT overwrite the entire file.

Fields to set (merge into existing):

```json
{
  "session_started": true,
  "domain": "[domain]",
  "timestamp": "[ISO-8601]",
  "needs_restart": true,
  "resume_after_restart": "anchor"
}
```

**Preserve these keys if they exist:** `context`, `actions_log`, `needs_learn`, `needs_learn_reason`

## Workflow State

Create `.claude/state/[domain]_workflow.json`:

```json
{
  "domain": "[domain]",
  "setup_complete": true,
  "protocol_created": true,
  "protocol_path": ".claude/protocols/[domain]-protocol.md",
  "anchored": false,
  "actions_since_anchor": 0,
  "actions_limit": 10,
  "timestamp": "[ISO-8601]"
}
```

## Hook Registration

Create/update `.claude/settings.local.json` to register hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/universal-gate-enforcer.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/test-failure-detector.py"
          }
        ]
      }
    ]
  }
}
```

**MERGE rule:** If `settings.local.json` already exists, merge the `hooks` key into it. Do NOT overwrite existing keys like `permissions`. Note: after the **Domain Gate Enforcer** step below, the `PreToolUse` array holds TWO hook entries (universal + domain) — this merge rule applies to both; preserve the universal entry when adding the domain one.

## Domain Gate Enforcer

The universal hook registered above is domain-agnostic. Each domain ALSO gets its own gate enforcer so domain-specific safety checks (e.g., bash `cd`-blocking, direct `intent.py` blocking) actually fire. Instantiate and register it now:

1. **Read the template.** Open `.claude/hooks/domain-gate-enforcer.template.py` from the kernel. It is a thin orchestrator over `lib.validators` with `{{DOMAIN}}` placeholders in its header comment.

2. **Instantiate it.** Write it as `.claude/hooks/[domain]-gate-enforcer.py` in the target repo, substituting `{{DOMAIN}}` with the actual domain name in the header comment.

3. **Register it as a SECOND `PreToolUse` entry.** Add the entry below to the `PreToolUse` array in `.claude/settings.local.json` — ALONGSIDE the existing `universal-gate-enforcer.py` entry. Do NOT replace or remove the universal entry; both hooks run.

   ```json
   {
     "matcher": "Edit|Write|Bash",
     "hooks": [
       {
         "type": "command",
         "command": "python .claude/hooks/[domain]-gate-enforcer.py"
       }
     ]
   }
   ```

   **The matcher MUST include `Bash`.** The domain hook's bash-safety checks (cd-blocker, intent.py-blocker) only fire when `Bash` is in the matcher. Registering it as `"Edit|Write"` silently makes those checks dead code — this exact omission is what let bash `cd` violations recur despite a fully-implemented, correct blocker. Use `"Edit|Write|Bash"` literally.

## Commit Domain-Setup Output

Before setting `needs_restart`, commit all domain-setup artifacts:

```bash
git add .claude/protocols/ .claude/lessons/ .claude/state/ tasks/
git add .claude/commands/ .claude/hooks/ .claude/skills/ .claude/settings.local.json
# Add any framework files, commands, or configs created during setup
git commit -m "feat: domain-setup output for [domain]"
```

This ensures the project starts clean on restart — no untracked domain-setup files.

## State Fields

| Field | Purpose |
|-------|---------|
| `session_started` | Session initialized |
| `domain` | Active domain name |
| `needs_restart` | Hooks require restart |
| `resume_after_restart` | What to do after restart |
| `anchored` | Protocol read this session |
| `actions_since_anchor` | Counter (auto-incremented by hook) |
| `actions_limit` | Threshold before re-anchor required |
