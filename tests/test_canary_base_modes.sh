#!/bin/bash
# ============================================================================
# 286 CANARY — affirmative failure-injection for the BASE canonical kernel.
#
# Each mode deliberately INJECTS a failure the base hardening is meant to
# catch, then asserts the hardening CAUGHT/REPAIRED it. Pass condition is
# "every injected failure was caught", not "a normal run completed".
#
# Scope = BASE hardening only (270 + 271 + 262 + 244). The original 286
# modes for the completion-truth oracle / stranded-deliverable / portability
# linter / build-verb router belong to the OPTIONAL layers (276/273/272),
# which are intentionally not in this base kernel — they are validated when
# those layers are packaged, not here.
# ============================================================================
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$INSTALL/lib/common.sh"
validate_deps   # sets PYTHON_CMD

SANDBOX_MSYS="$INSTALL/.claude/state/_canary"
rm -rf "$SANDBOX_MSYS"; mkdir -p "$SANDBOX_MSYS"
# Cross the bash->native-Windows-python boundary safely: cygpath -m the raw /d/... path,
# else pathlib on native python reads it as \d\... (lesson 2026-07-23 MR-03).
if command -v cygpath >/dev/null 2>&1; then SANDBOX="$(cygpath -m "$SANDBOX_MSYS")"; else SANDBOX="$SANDBOX_MSYS"; fi
STATE_FILE="$SANDBOX/session_state.json"

CAUGHT=0; MISSED=0
caught(){ echo "  [CAUGHT] $1"; CAUGHT=$((CAUGHT+1)); }
missed(){ echo "  [MISSED] $1"; MISSED=$((MISSED+1)); }

seed_state(){ # $1=domain $2=agent_id(optional)
  $PYTHON_CMD -c "
import json,sys,pathlib
d={'domain':'$1','session_started':True}
aid='${2:-}'
if aid: d['agent_id']=aid
pathlib.Path(r'$STATE_FILE').write_text(json.dumps(d,indent=2))
"
}

echo '=== CANARY-1: completion-write-loss (270 RH-01) ==='
# Inject: task ran to done but is MISSING from completed_tasks (the persist-loss fault)
seed_state canary a1
WF="$SANDBOX/agent-a1-workflow.json"
$PYTHON_CMD -c "
import json,pathlib
pathlib.Path(r'$WF').write_text(json.dumps({'domain':'canary','completed_tasks':[],'current_task':'007-canary.md'},indent=2))
"
verify_completion_write "007-canary.md" "a1" >/dev/null 2>&1
REPAIRED=$($PYTHON_CMD -c "
import json,sys,pathlib
w=json.loads(pathlib.Path(r'$WF').read_text())
sys.stdout.write('yes' if '007-canary.md' in w.get('completed_tasks',[]) else 'no')
")
[ "$REPAIRED" = "yes" ] && caught "verify_completion_write re-persisted the lost completion" || missed "completion still absent after verify"

echo '=== CANARY-2: routed-skip parent-write (271 WI-02) ==='
# Inject: a routed agent skips its task; the PARENT domain workflow must be untouched
seed_state canary a2
PARENT="$SANDBOX/canary_workflow.json"
AWF="$SANDBOX/agent-a2-workflow.json"
$PYTHON_CMD -c "
import json,pathlib
pathlib.Path(r'$PARENT').write_text(json.dumps({'domain':'canary','current_task':'PARENT-DO-NOT-TOUCH','skipped_tasks':[]},indent=2))
pathlib.Path(r'$AWF').write_text(json.dumps({'domain':'canary','current_task':'003-agent.md','skipped_tasks':[]},indent=2))
"
PARENT_BEFORE=$($PYTHON_CMD -c "import hashlib,sys; sys.stdout.write(hashlib.sha256(open(r'$PARENT','rb').read()).hexdigest())")
skip_current_task "a2" >/dev/null 2>&1
PARENT_AFTER=$($PYTHON_CMD -c "import hashlib,sys; sys.stdout.write(hashlib.sha256(open(r'$PARENT','rb').read()).hexdigest())")
AGENT_SKIPPED=$($PYTHON_CMD -c "
import json,sys,pathlib
w=json.loads(pathlib.Path(r'$AWF').read_text())
sys.stdout.write('yes' if '003-agent.md' in w.get('skipped_tasks',[]) else 'no')
")
[ "$PARENT_BEFORE" = "$PARENT_AFTER" ] && [ "$AGENT_SKIPPED" = "yes" ] && caught "skip routed to agent file; parent byte-identical" || missed "parent workflow was mutated by a routed skip"

echo '=== CANARY-3: stale-heartbeat-with-work (262 / 270 RH-02) ==='
# Inject: a stale heartbeat while work remains -> check_stall must flag + mark stalled
seed_state canary a3
SWF="$SANDBOX/agent-a3-workflow.json"
$PYTHON_CMD -c "
import json,pathlib
pathlib.Path(r'$SWF').write_text(json.dumps({'domain':'canary','total_tasks':5,'completed_tasks':['001'],'skipped_tasks':[]},indent=2))
"
HB="$SANDBOX/agent-a3-heartbeat"
$PYTHON_CMD -c "
import os,time,pathlib
p=pathlib.Path(r'$HB'); p.write_text('stamp')
old=time.time()-4000
os.utime(p,(old,old))
"
if check_stall "$HB" 900 "a3" >/dev/null 2>&1; then
  missed "check_stall returned healthy on a stale heartbeat with work remaining"
else
  STALLED=$($PYTHON_CMD -c "
import json,sys,pathlib
w=json.loads(pathlib.Path(r'$SWF').read_text())
sys.stdout.write('yes' if w.get('stalled') else 'no')
")
  [ "$STALLED" = "yes" ] && caught "check_stall flagged stall + marked routed workflow stalled" || missed "non-zero returned but workflow not marked stalled"
fi
# Negative control: fresh heartbeat must be healthy
$PYTHON_CMD -c "import pathlib; pathlib.Path(r'$HB').write_text('fresh')"
if check_stall "$HB" 900 "a3" >/dev/null 2>&1; then caught "negative control: fresh heartbeat = healthy (no false stall)"; else missed "false stall on a fresh heartbeat"; fi

echo '=== CANARY-4: empty-output step (base empty-retry) ==='
# Inject: a claude -p step returns empty -> must NEVER be read as a completion signal
S1=$(check_completion "")
S2=$(check_completion "some work happened but no signal token")
[ "$S1" = "no_signal" ] && [ "$S2" = "no_signal" ] && caught "empty/eof output classified no_signal (never silent-done); runner backs off + retries" || missed "empty output misclassified as completion"

echo '=== CANARY-5: cross-agent workflow isolation (244) ==='
# Inject: two concurrent agents skip their own tasks -> neither clobbers the other
seed_state canary   # parent context; each call passes its own agent id
$PYTHON_CMD -c "
import json,pathlib
for a,t in [('b1','B1-task.md'),('b2','B2-task.md')]:
    pathlib.Path(r'$SANDBOX'+f'/agent-{a}-workflow.json').write_text(json.dumps({'domain':'canary','current_task':t,'skipped_tasks':[]},indent=2))
"
skip_current_task "b1" >/dev/null 2>&1
skip_current_task "b2" >/dev/null 2>&1
ISO=$($PYTHON_CMD -c "
import json,sys,pathlib
b1=json.loads(pathlib.Path(r'$SANDBOX/agent-b1-workflow.json').read_text())
b2=json.loads(pathlib.Path(r'$SANDBOX/agent-b2-workflow.json').read_text())
ok = b1.get('skipped_tasks')==['B1-task.md'] and b2.get('skipped_tasks')==['B2-task.md']
sys.stdout.write('yes' if ok else 'no')
")
[ "$ISO" = "yes" ] && caught "each agent skipped only its own task; no cross-agent clobber" || missed "cross-agent workflow state clobbered"

rm -rf "$SANDBOX_MSYS"
echo ""
echo "=== CANARY RESULT: $CAUGHT caught / $MISSED missed ==="
[ "$MISSED" -eq 0 ] && { echo "286 CANARY PASSED — every injected base failure was caught."; exit 0; } || { echo "286 CANARY FAILED"; exit 1; }
