#!/usr/bin/env bash
# Test: domain-gate-enforcer.template.py — inlined Bash safety check (backlog 287)
#
# Proves the two-tier design:
#   1. With lib/validators ABSENT (the standalone-kernel case), the hook still
#      enforces the inlined check. It must NOT exit 0 silently.
#   2. Quoted occurrences of the token are not violations — including a string
#      containing an English possessive, which the shared validator's
#      single-pattern quote stripper gets wrong.
#
# Windows/Git-Bash note: sandbox paths crossing into native python are
# converted with `cygpath -m`. PATH-style conversion (-u) is not needed here.

set -u

REPO="$(readlink -f "$(dirname "${BASH_SOURCE[0]}")/..")"
TEMPLATE="$REPO/.claude/hooks/domain-gate-enforcer.template.py"

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); echo "  PASS  $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  FAIL  $1"; }

if [ ! -f "$TEMPLATE" ]; then
  echo "FATAL: template not found at $TEMPLATE"; exit 2
fi

SB="$(mktemp -d)"
SB_PY="$SB"
command -v cygpath >/dev/null 2>&1 && SB_PY="$(cygpath -m "$SB")"
trap 'rm -rf "$SB"' EXIT

# Sandbox has NO lib/validators and no sibling isagawa-kernel anywhere above it,
# so the standalone path is what executes.
mkdir -p "$SB/repo/.claude/hooks" "$SB/repo/.claude/state"
sed 's/{{DOMAIN}}/Test/' "$TEMPLATE" > "$SB/repo/.claude/hooks/test-gate-enforcer.py"
HOOK="$SB_PY/repo/.claude/hooks/test-gate-enforcer.py"

echo "=== SETUP ASSERTIONS ==="

# The hook must load. An rc outside {0,2} means the process died — a harness
# failure that carries no information about behavior.
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"mkdir /x"}}' | python "$HOOK" >"$SB/setup.out" 2>&1
rc=$?
if [ "$rc" -gt 2 ]; then
  echo "SANDBOX INVALID (rc=$rc) — hook did not load:"; cat "$SB/setup.out"; exit 2
fi
ok "hook loads and runs (rc=$rc)"

# Positively confirm the standalone tier is the one under test.
standalone=$(python -c "
import importlib.util as u
sp = u.spec_from_file_location('t', r'$HOOK')
m = u.module_from_spec(sp); sp.loader.exec_module(m)
print('YES' if m.VALIDATORS is None else 'NO')
" 2>/dev/null | tail -1)
if [ "$standalone" = "YES" ]; then
  ok "validators absent — standalone tier is under test"
else
  echo "SANDBOX INVALID — validators resolved; the inlined path is not being exercised"; exit 2
fi

echo "=== BEHAVIOR ==="

# $1 = label, $2 = expected rc, $3 = command string (JSON-escaped)
case_run() {
  local label="$1" want="$2" cmdjson="$3"
  printf '%s' "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":$cmdjson}}" \
    | python "$HOOK" >"$SB/out" 2>&1
  local got=$?
  if [ "$got" = "$want" ]; then ok "$label (rc=$got)"; else bad "$label — want rc=$want got rc=$got: $(head -1 "$SB/out")"; fi
}

# Build the blocked token without writing it literally, so this script can be
# invoked from an agent session whose own gate scans command text.
T="$(printf 'c'; printf 'd')"

case_run "MUST BLOCK: leading directory change"  2 "\"$T /path && git log\""
case_run "MUST BLOCK: chained after semicolon"   2 "\"echo hi; $T /tmp\""
case_run "MUST BLOCK: chained after &&"          2 "\"mkdir /a && $T /a\""
case_run "allow: token inside single quotes"     0 "\"git commit -m '$T implementation'\""
case_run "allow: possessive inside double quotes" 0 "\"echo \\\"the agent's $T choice\\\"\""
case_run "allow: no token present"               0 '"mkdir /path"'
case_run "allow: token as a substring"           0 "\"${T}k deploy --all\""

# Write/Edit is validator-only; with validators absent it must allow, not crash.
printf '%s' '{"tool_name":"Write","tool_input":{"file_path":"/tmp/x.py","content":"print(1)"}}' \
  | python "$HOOK" >"$SB/out" 2>&1
rc=$?
if [ "$rc" = "0" ]; then ok "Write allowed when validators absent (rc=0)"; else bad "Write — want rc=0 got rc=$rc"; fi

echo ""
echo "=== RESULT: $PASS pass / $FAIL fail ==="
[ "$FAIL" -eq 0 ] || exit 1
exit 0
