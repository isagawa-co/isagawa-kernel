# Step 3: Scan Hooks + Settings

Verify all hooks exist, are wired, and settings are consistent.

## Process

1. **List actual hook files:**
   - Glob `.claude/hooks/*.py`
   - Note each filename

2. **Read settings.local.json:**
   - Extract all hook commands from PreToolUse, PermissionRequest, PostToolUse
   - Note which hook files are referenced

3. **Cross-reference:**
   - Every hook file should be wired in settings.local.json
   - Every hook referenced in settings.local.json should have a matching file
   - Flag unwired hooks and missing files

4. **Check hook content:**
   - Each hook should have a docstring explaining what it does
   - Each hook should handle JSON stdin gracefully (try/except)
   - Each hook should exit(0) for pass-through cases

5. **Cross-reference with protocol:**
   - Hooks should be listed in protocol index
   - Flag unlisted hooks

## Output

```
Hooks: [N found]
Settings wiring:
- PreToolUse: [list]
- PermissionRequest: [list]
- PostToolUse: [list]
Gaps:
- [hook.py] exists but not wired in settings.local.json
- [hook.py] wired but file missing
- [hook.py] missing from protocol index
Clean: [list of hooks with no issues]
```
