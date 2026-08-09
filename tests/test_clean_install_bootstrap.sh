#!/usr/bin/env bash
# Test: clean-install bootstrap of the domain gate enforcer (backlog 287)
#
# Backlog 286 proved the canonical kernel survives packaging + a clean install.
# It could not cover the domain gate, which did not exist yet: backlog 307 added
# the template and made /kernel/domain-setup instantiate and register it.
#
# This closes that gap. It performs the deterministic half of domain-setup's
# step-10 in a throwaway repo -- instantiate the template, register it as a
# second PreToolUse entry -- and then asserts the instantiated hook ACTUALLY
# FIRES. Registration is not the property under test; enforcement is. A hook
# that registers correctly and never fires looks identical to one that works.
#
# Windows/Git-Bash: paths crossing into native python are converted with
# `cygpath -m`.

set -u

REPO="$(readlink -f "$(dirname "${BASH_SOURCE[0]}")/..")"
TEMPLATE="$REPO/.claude/hooks/domain-gate-enforcer.template.py"

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "  PASS  $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL  $1"; }

[ -f "$TEMPLATE" ] || { echo "FATAL: template missing at $TEMPLATE"; exit 2; }

SB="$(mktemp -d)"
SB_PY="$SB"
command -v cygpath >/dev/null 2>&1 && SB_PY="$(cygpath -m "$SB")"
trap 'rm -rf "$SB"' EXIT

DOMAIN="acme"
INSTALL="$SB/fresh-repo"

echo "=== BOOTSTRAP (simulating domain-setup step-10 in a fresh repo) ==="

# A fresh install carries the kernel's hooks + commands, nothing else.
mkdir -p "$INSTALL/.claude/hooks" "$INSTALL/.claude/state" "$INSTALL/.claude/protocols"
cp "$REPO"/.claude/hooks/*.py "$INSTALL/.claude/hooks/" 2>/dev/null

# Step 10.2 — instantiate the template with the domain substituted.
sed "s/{{DOMAIN}}/${DOMAIN}/" "$TEMPLATE" > "$INSTALL/.claude/hooks/${DOMAIN}-gate-enforcer.py"
if [ -f "$INSTALL/.claude/hooks/${DOMAIN}-gate-enforcer.py" ]; then
  ok "template instantiated as ${DOMAIN}-gate-enforcer.py"
else
  bad "instantiation produced no file"; echo "=== RESULT: $PASS pass / $FAIL fail ==="; exit 1
fi

if grep -q "{{DOMAIN}}" "$INSTALL/.claude/hooks/${DOMAIN}-gate-enforcer.py"; then
  bad "placeholder {{DOMAIN}} survived substitution"
else
  ok "no unsubstituted placeholder remains"
fi

# Step 10.3 — register as a SECOND PreToolUse entry, preserving the universal one.
cat > "$INSTALL/.claude/settings.local.json" <<JSON
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          { "type": "command", "command": "python .claude/hooks/universal-gate-enforcer.py" }
        ]
      },
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          { "type": "command", "command": "python .claude/hooks/${DOMAIN}-gate-enforcer.py" }
        ]
      }
    ]
  }
}
JSON

# Registration checks: both entries present, and the domain matcher includes Bash.
reg=$(python -c "
import json, io
s = json.load(io.open(r'$SB_PY/fresh-repo/.claude/settings.local.json', encoding='utf-8'))
pre = s['hooks']['PreToolUse']
cmds = [h['command'] for e in pre for h in e['hooks']]
uni = any('universal-gate-enforcer' in c for c in cmds)
dom = any('${DOMAIN}-gate-enforcer' in c for c in cmds)
mat = [e['matcher'] for e in pre if any('${DOMAIN}-gate-enforcer' in h['command'] for h in e['hooks'])]
print(f\"{len(pre)}|{uni}|{dom}|{'Bash' in (mat[0] if mat else '')}\")
" 2>/dev/null)
IFS='|' read -r n_entries has_uni has_dom has_bash <<< "$reg"

[ "$n_entries" = "2" ]     && ok "PreToolUse holds TWO entries"                  || bad "expected 2 PreToolUse entries, got '$n_entries'"
[ "$has_uni" = "True" ]    && ok "universal entry preserved (not replaced)"      || bad "universal entry lost"
[ "$has_dom" = "True" ]    && ok "domain entry registered"                       || bad "domain entry missing"
[ "$has_bash" = "True" ]   && ok "domain matcher includes Bash"                  || bad "domain matcher omits Bash -- checks would be dead code"

echo "=== ENFORCEMENT (the property that actually matters) ==="

HOOK="$SB_PY/fresh-repo/.claude/hooks/${DOMAIN}-gate-enforcer.py"

# Setup assertion: the instantiated hook must load before any case depends on it.
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"mkdir /x"}}' | python "$HOOK" >"$SB/s.out" 2>&1
rc=$?
if [ "$rc" -gt 2 ]; then
  echo "INVALID: instantiated hook did not load (rc=$rc):"; cat "$SB/s.out"; exit 2
fi
ok "instantiated hook loads in the fresh install (rc=$rc)"

# A fresh install ships no lib/validators. The bash check must STILL enforce --
# that is the whole point of inlining it.
standalone=$(python -c "
import importlib.util as u
sp = u.spec_from_file_location('h', r'$HOOK')
m = u.module_from_spec(sp); sp.loader.exec_module(m)
print('YES' if m.VALIDATORS is None else 'NO')
" 2>/dev/null | tail -1)
[ "$standalone" = "YES" ] && ok "fresh install has no validators (standalone tier active)" \
                          || bad "validators resolved unexpectedly; standalone tier not under test"

T="$(printf 'c'; printf 'd')"

run_case() {
  local label="$1" want="$2" cmdjson="$3"
  printf '%s' "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":$cmdjson}}" | python "$HOOK" >"$SB/o" 2>&1
  local got=$?
  [ "$got" = "$want" ] && ok "$label (rc=$got)" || bad "$label — want rc=$want got rc=$got: $(head -1 "$SB/o")"
}

run_case "bootstrapped hook BLOCKS a directory change" 2 "\"$T /tmp && ls\""
run_case "bootstrapped hook allows a benign command"   0 '"git status"'
run_case "bootstrapped hook allows a quoted mention"   0 "\"git commit -m 'about $T usage'\""

echo ""
echo "=== RESULT: $PASS pass / $FAIL fail ==="
[ "$FAIL" -eq 0 ] || exit 1
exit 0
