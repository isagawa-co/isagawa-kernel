#!/bin/bash
# L2 test for RH-05: simulate a completed-but-unpersisted task and assert
# verify_completion_write() (lib/common.sh) re-persists it to a routed
# workflow.json and that the append survives a fresh read-back (utf-8-sig
# round trip). Uses only throwaway state files under a mktemp dir — never
# touches real session_state.json / sr_dev_workflow.json.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Walk up to the repo root by locating lib/common.sh, so this test is portable
# regardless of whether it lives in tasks/ or was moved to tasks/completed/.
REPO_ROOT="$SCRIPT_DIR"
while [ "$REPO_ROOT" != "/" ] && [ ! -f "$REPO_ROOT/lib/common.sh" ]; do
  REPO_ROOT="$(dirname "$REPO_ROOT")"
done

source "$REPO_ROOT/lib/common.sh"
validate_deps

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
if command -v cygpath &>/dev/null; then
  TMP_DIR=$(cygpath -m "$TMP_DIR")
fi

AGENT_ID="l2-test-agent"
TASK_NAME="999-fake-task.md"

STATE_FILE="$TMP_DIR/session_state.json"
WORKFLOW_FILE="$TMP_DIR/agent-${AGENT_ID}-workflow.json"

# Seed throwaway fixtures WITH a UTF-8 BOM (lesson 2026-07-22) and with the
# task ABSENT from completed_tasks, simulating a completion that never made
# it to disk.
$PYTHON_CMD -c "
import json, pathlib
sf = pathlib.Path(r'$STATE_FILE')
s = {'domain': 'l2test', 'agent_id': '$AGENT_ID', 'one_shot': True}
sf.write_bytes(b'\xef\xbb\xbf' + json.dumps(s, indent=2).encode('utf-8'))

wf = pathlib.Path(r'$WORKFLOW_FILE')
w = {'completed_tasks': [], 'skipped_tasks': [], 'current_task': '$TASK_NAME'}
wf.write_bytes(b'\xef\xbb\xbf' + json.dumps(w, indent=2).encode('utf-8'))
"

BEFORE=$($PYTHON_CMD -c "
import json, pathlib
w = json.loads(pathlib.Path(r'$WORKFLOW_FILE').read_text(encoding='utf-8-sig'))
print('$TASK_NAME' in w.get('completed_tasks', []))
")
echo "[SETUP] fixtures at $TMP_DIR ; task persisted before call: $BEFORE"

if [ "$BEFORE" != "False" ]; then
  echo "FAIL: fixture setup is wrong — task should be ABSENT before the call"
  exit 1
fi

verify_completion_write "$TASK_NAME" "$AGENT_ID"
RESULT=$?
echo "[CHECK] verify_completion_write exit code: $RESULT"

if [ "$RESULT" -ne 0 ]; then
  echo "FAIL: verify_completion_write returned non-zero (could not confirm re-persistence)"
  exit 1
fi

# Fresh read-back from disk (not the function's in-memory state) — proves
# the retry actually wrote through, and that utf-8-sig round-trips cleanly.
AFTER=$($PYTHON_CMD -c "
import json, pathlib
w = json.loads(pathlib.Path(r'$WORKFLOW_FILE').read_text(encoding='utf-8-sig'))
print('$TASK_NAME' in w.get('completed_tasks', []))
")

if [ "$AFTER" != "True" ]; then
  echo "FAIL: completed task not found in fresh read-back of $WORKFLOW_FILE"
  exit 1
fi

echo "PASS: completion for '$TASK_NAME' was re-persisted by verify_completion_write and confirmed on a fresh read-back (utf-8-sig round trip verified)."
exit 0
