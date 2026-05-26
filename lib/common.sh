#!/bin/bash
#
# common.sh — Shared helper functions for run-task scripts
#
# Source this file: source "$(dirname "$0")/lib/common.sh"

# --- Detect platform ---
IS_WINDOWS=false
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
  IS_WINDOWS=true
fi

# --- Validate dependencies ---
validate_deps() {
  # Find a working Python — test with actual execution, not just PATH lookup
  # (Windows has a fake python3 alias that points to Microsoft Store)
  PYTHON_CMD=""
  if python --version &>/dev/null 2>&1; then
    PYTHON_CMD="python"
  elif python3 --version &>/dev/null 2>&1; then
    PYTHON_CMD="python3"
  fi
  if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3 is required but not found (neither python nor python3 works)"
    exit 1
  fi
  if ! command -v claude &>/dev/null; then
    echo "ERROR: Claude CLI is required but not found in PATH"
    exit 1
  fi
}

# --- Validate repo ---
validate_repo() {
  local repo="$1"
  if [ ! -d "$repo" ]; then
    echo "ERROR: Directory not found: $repo"
    exit 1
  fi
  if [ ! -f "$repo/CLAUDE.md" ]; then
    echo "ERROR: Not a kernel repo (no CLAUDE.md): $repo"
    exit 1
  fi
}

# --- Resolve paths for Windows compatibility ---
resolve_paths() {
  local repo="$1"
  if command -v cygpath &>/dev/null; then
    STATE_FILE=$(cygpath -m "$repo/.claude/state/session_state.json")
    LOG_DIR=$(cygpath -m "$repo/.claude/state")
  else
    STATE_FILE="$repo/.claude/state/session_state.json"
    LOG_DIR="$repo/.claude/state"
  fi
  mkdir -p "$LOG_DIR"
}

# --- Kill a process and its children ---
kill_process_tree() {
  local pid="$1"
  if [ -z "$pid" ]; then return; fi

  if [ "$IS_WINDOWS" = true ]; then
    # Windows: taskkill with /T kills entire process tree
    taskkill //F //T //PID "$pid" &>/dev/null || true
  else
    # Unix: kill process group
    kill -- -"$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
  fi
}

# --- Pre-initialize session state ---
# Avoids deadlock where agent can't write session_started=true
# because Claude Code's sensitive file guard blocks .claude/state/ writes
pre_init_state() {
  local key_values="$1"  # e.g. "session_started=True,one_shot=True"
  $PYTHON_CMD -c "
import json, pathlib
f = pathlib.Path('$STATE_FILE')
s = json.loads(f.read_text()) if f.exists() else {}
for kv in '$key_values'.split(','):
    k, v = kv.strip().split('=')
    s[k] = True if v == 'True' else (False if v == 'False' else v)
f.parent.mkdir(parents=True, exist_ok=True)
f.write_text(json.dumps(s, indent=2))
" || {
    echo "ERROR: Failed to pre-initialize state in $STATE_FILE"
    exit 1
  }
}

# --- Print current state ---
print_state() {
  $PYTHON_CMD -c "
import json, pathlib
sf = pathlib.Path('$STATE_FILE')
if not sf.exists():
    print('  (no state file)')
else:
    s = json.loads(sf.read_text())
    print('  session_started:', s.get('session_started'))
    print('  one_shot:', s.get('one_shot'))
    d = s.get('domain', '')
    if d:
        wf = sf.parent / (d + '_workflow.json')
        if wf.exists():
            w = json.loads(wf.read_text())
            print('  anchored:', w.get('anchored'))
            print('  completed:', len(w.get('completed_tasks', [])))
            print('  skipped:', len(w.get('skipped_tasks', [])))
            print('  current:', w.get('current_task'))
" || echo "  (state read failed)"
}

# --- Extract session_id from JSON output ---
extract_session_id() {
  local logfile="$1"
  if [ ! -f "$logfile" ] || [ ! -s "$logfile" ]; then
    echo ""
    return
  fi
  $PYTHON_CMD -c "
import sys, json
try:
    data = json.loads(open('$logfile').read())
    print(data.get('session_id', ''))
except Exception:
    print('')
"
}

# --- Extract result text from JSON output ---
extract_result() {
  local logfile="$1"
  if [ ! -f "$logfile" ] || [ ! -s "$logfile" ]; then
    echo ""
    return
  fi
  $PYTHON_CMD -c "
import sys, json
try:
    data = json.loads(open('$logfile').read())
    print(data.get('result', ''))
except Exception:
    print('')
"
}

# --- Check for completion signals in text ---
check_completion() {
  local text="$1"
  if printf '%s' "$text" | grep -q "ALL_TASKS_COMPLETE"; then
    echo "all_done"
  elif printf '%s' "$text" | grep -q "ONE_SHOT_COMPLETE"; then
    echo "task_done"
  elif printf '%s' "$text" | grep -qi "no incomplete tasks"; then
    echo "all_done"
  else
    echo "no_signal"
  fi
}

# --- Skip current task in workflow state ---
skip_current_task() {
  $PYTHON_CMD -c "
import json, pathlib
sf = pathlib.Path('$STATE_FILE')
if not sf.exists():
    exit(0)
s = json.loads(sf.read_text())
domain = s.get('domain', '')
if not domain:
    exit(0)
wf = sf.parent / (domain + '_workflow.json')
if not wf.exists():
    exit(0)
w = json.loads(wf.read_text())
task = w.get('current_task')
if task and task not in w.get('skipped_tasks', []):
    if 'skipped_tasks' not in w:
        w['skipped_tasks'] = []
    w['skipped_tasks'].append(task)
    w['current_task'] = None
    w['attempts_on_current'] = 0
    wf.write_text(json.dumps(w, indent=2))
    print('SKIPPED: ' + task)
else:
    print('(no task to skip)')
"
}

# --- Write output safely (handles -n, -e in content) ---
write_log() {
  local content="$1"
  local logfile="$2"
  printf '%s\n' "$content" > "$logfile"
}
