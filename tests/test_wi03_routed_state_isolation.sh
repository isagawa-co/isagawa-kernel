#!/bin/bash
# L2 live test — WI-03 (271 worktree isolation completion)
#
# Proves skip_current_task() (lib/common.sh), the routed state-write path
# run-task.sh uses, writes ONLY agent-{id}-workflow.json when KERNEL_AGENT_ID
# is set — never the parent domain workflow file.
#
# Uses THROWAWAY fixtures under mktemp — never touches the real
# sr_dev_workflow.json / session_state.json.

set -euo pipefail

# Resolve the repo from this script's own location. A hardcoded absolute path
# here previously pinned the suite to one machine's worktree layout, so it
# could not run anywhere else — including in the kernel repo it ships in.
REPO_ROOT="$(readlink -f "$(dirname "${BASH_SOURCE[0]}")/..")"
source "$REPO_ROOT/lib/common.sh"

FIXTURE_DIR=$(mktemp -d)
trap 'rm -rf "$FIXTURE_DIR"' EXIT

PYTHON_CMD="python"
if ! python --version &>/dev/null 2>&1; then
  PYTHON_CMD="python3"
fi

resolve_paths "$FIXTURE_DIR"
# resolve_paths only mkdir's LOG_DIR; state files themselves must be seeded.
# Derive state-dir paths from LOG_DIR (already cygpath -m resolved), not the
# raw mktemp path, so the Windows-native Python invoked below can open them.

AGENT_ID="wi03-test-agent"
PARENT_WF="$LOG_DIR/sr_dev_workflow.json"
AGENT_WF="$LOG_DIR/agent-${AGENT_ID}-workflow.json"

$PYTHON_CMD -c "
import json, pathlib
sf = pathlib.Path(r'$STATE_FILE')
sf.parent.mkdir(parents=True, exist_ok=True)
sf.write_text(json.dumps({'domain': 'sr_dev', 'session_started': True}, indent=2))

pf = pathlib.Path(r'$PARENT_WF')
pf.write_text(json.dumps({
    'current_task': 'PARENT-SHOULD-NOT-CHANGE.md',
    'skipped_tasks': [],
    'attempts_on_current': 0
}, indent=2))

af = pathlib.Path(r'$AGENT_WF')
af.write_text(json.dumps({
    'current_task': '003-fixture-task.md',
    'skipped_tasks': [],
    'attempts_on_current': 2
}, indent=2))
"

parent_hash_before=$($PYTHON_CMD -c "import hashlib; print(hashlib.sha256(open(r'$PARENT_WF','rb').read()).hexdigest())")

skip_current_task "$AGENT_ID"

parent_hash_after=$($PYTHON_CMD -c "import hashlib; print(hashlib.sha256(open(r'$PARENT_WF','rb').read()).hexdigest())")

pass=true

if [ "$parent_hash_before" != "$parent_hash_after" ]; then
  echo "FAIL: parent workflow file changed (hash before=$parent_hash_before after=$parent_hash_after)"
  pass=false
else
  echo "PASS: parent workflow file byte-identical before/after"
fi

agent_result=$($PYTHON_CMD -c "
import json, pathlib
af = pathlib.Path(r'$AGENT_WF')
w = json.loads(af.read_text(encoding='utf-8-sig'))
ok = (
    w.get('current_task') is None
    and '003-fixture-task.md' in w.get('skipped_tasks', [])
    and w.get('attempts_on_current') == 0
)
print('true' if ok else 'false')
")

if [ "$agent_result" = "true" ]; then
  echo "PASS: agent-${AGENT_ID}-workflow.json updated (task skipped, current_task cleared)"
else
  echo "FAIL: agent-${AGENT_ID}-workflow.json not updated as expected"
  pass=false
fi

if [ "$pass" = "true" ]; then
  echo "WI-03: L2 ROUTED STATE ISOLATION TEST PASSED"
  exit 0
else
  echo "WI-03: L2 ROUTED STATE ISOLATION TEST FAILED"
  exit 1
fi
