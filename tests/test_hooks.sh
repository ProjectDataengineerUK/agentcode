#!/usr/bin/env bash
# test_hooks.sh — Regression suite for agentcode hooks.
#
# Covers the scenarios from the 2026-07-22 security/logic audit:
#   lesson_capture : error trigger, no-trigger, slow_op, 1MB payload (E2BIG),
#                    secret redaction, anti-bloat cap, fail-open
#   lesson_timing  : t0 marker, fail-open
#   sync_context_reminder : no-drift, drift block, anti-nag, stop_hook_active,
#                    fail-open, sanitized relative path
#   install-global merge : preserves user hooks, idempotent re-run
#
# Runs against an ISOLATED $HOME so the real ~/.mempalace is never touched.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS="$REPO_ROOT/.claude/hooks"

export HOME="$(mktemp -d)"
WORK="$(mktemp -d)"
trap 'rm -rf "$HOME" "$WORK"' EXIT

PASS=0
FAIL=0

ok()   { PASS=$((PASS+1)); echo "  ✔ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ✘ $1"; }
check() { # check <desc> <cmd...>
    local desc="$1"; shift
    if "$@" >/dev/null 2>&1; then ok "$desc"; else fail "$desc"; fi
}

echo "== lesson_timing.sh =="
echo '{"tool_use_id":"t1","tool_name":"Bash"}' | bash "$HOOKS/lesson_timing.sh" >/dev/null
check "grava t0 por tool_use_id" test -f "$HOME/.mempalace/lessons/timing/t1"
OUT=$(echo 'lixo{{{' | bash "$HOOKS/lesson_timing.sh"); RC=$?
[ "$RC" = 0 ] && [ "$OUT" = "{}" ] && ok "fail-open com entrada malformada" || fail "fail-open com entrada malformada"

echo "== lesson_capture.sh =="
BUF="$HOME/.mempalace/lessons/buffer/s1.jsonl"
echo '{"session_id":"s1","tool_name":"Bash","tool_input":{"command":"terraform apply"},"tool_response":"Error: not found"}' | bash "$HOOKS/lesson_capture.sh" >/dev/null
check "trigger error captura no buffer/" test -s "$BUF"
grep -q '"triggers": \["error"\]' "$BUF" && ok "trigger classificado como error" || fail "trigger classificado como error"

N_BEFORE=$(wc -l < "$BUF")
echo '{"session_id":"s1","tool_name":"Read","tool_response":"conteudo ok"}' | bash "$HOOKS/lesson_capture.sh" >/dev/null
[ "$(wc -l < "$BUF")" = "$N_BEFORE" ] && ok "sem trigger não captura" || fail "sem trigger não captura"

echo $(( $(date +%s) - 100 )) > "$HOME/.mempalace/lessons/timing/slow1"
echo '{"session_id":"s1","tool_name":"Bash","tool_use_id":"slow1","tool_response":"done"}' | bash "$HOOKS/lesson_capture.sh" >/dev/null
tail -1 "$BUF" | grep -q '"slow_op"' && ok "trigger slow_op via timing" || fail "trigger slow_op via timing"

python3 -c "import json; print(json.dumps({'session_id':'s1','tool_name':'Read','tool_response':'Error: '+'x'*1000000}))" \
    | bash "$HOOKS/lesson_capture.sh" >/dev/null
tail -1 "$BUF" | grep -q '"tool": "Read"' && ok "payload 1MB captura (sem E2BIG)" || fail "payload 1MB captura (sem E2BIG)"

echo '{"session_id":"s1","tool_name":"Bash","tool_response":"Error: postgres://u:hunter2@db/x api_key=sk_live_0123456789abcdef00 ghp_AAAAbbbbCCCCddddEEEE1234"}' \
    | bash "$HOOKS/lesson_capture.sh" >/dev/null
if tail -1 "$BUF" | grep -qE "hunter2|sk_live_0123|ghp_AAAA"; then
    fail "redação de segredos"
else
    tail -1 "$BUF" | grep -q "REDACTED" && ok "redação de segredos" || fail "redação de segredos (sem marcador)"
fi

for i in $(seq 1 60); do
    echo "{\"session_id\":\"cap\",\"tool_name\":\"Bash\",\"tool_response\":\"Error $i\"}" | bash "$HOOKS/lesson_capture.sh" >/dev/null
done
CAP=$(wc -l < "$HOME/.mempalace/lessons/buffer/cap.jsonl")
[ "$CAP" -le 50 ] && ok "anti-bloat cap 50/sessão (got $CAP)" || fail "anti-bloat cap 50/sessão (got $CAP)"

OUT=$(echo 'lixo{{{' | bash "$HOOKS/lesson_capture.sh"); RC=$?
[ "$RC" = 0 ] && [ "$OUT" = "{}" ] && ok "fail-open com entrada malformada" || fail "fail-open com entrada malformada"

echo "== sync_context_reminder.sh =="
P="$WORK/proj"; mkdir -p "$P/.claude/sdd"
echo r > "$P/.claude/sdd/BUILD_REPORT_A.md"; sleep 0.1; echo c > "$P/CLAUDE.md"
OUT=$(cd "$P" && echo '{"stop_hook_active":false}' | bash "$HOOKS/sync_context_reminder.sh")
[ "$OUT" = "{}" ] && ok "sem drift → não bloqueia" || fail "sem drift → não bloqueia"

sleep 0.1; echo s > "$P/.claude/sdd/SHIPPED_X Y.md"
OUT=$(cd "$P" && echo '{"stop_hook_active":false}' | bash "$HOOKS/sync_context_reminder.sh")
echo "$OUT" | grep -q '"decision": "block"' && ok "drift → bloqueia 1x" || fail "drift → bloqueia 1x"
echo "$OUT" | grep -q "$WORK" && fail "reason usa caminho relativo saneado" || ok "reason usa caminho relativo saneado"

OUT=$(cd "$P" && echo '{"stop_hook_active":false}' | bash "$HOOKS/sync_context_reminder.sh")
[ "$OUT" = "{}" ] && ok "anti-nag (mesmo artefato)" || fail "anti-nag (mesmo artefato)"

OUT=$(cd "$P" && echo '{"stop_hook_active":true}' | bash "$HOOKS/sync_context_reminder.sh")
[ "$OUT" = "{}" ] && ok "stop_hook_active → passa direto" || fail "stop_hook_active → passa direto"

OUT=$(cd "$P" && echo 'lixo' | bash "$HOOKS/sync_context_reminder.sh"); RC=$?
[ "$RC" = 0 ] && ok "fail-open com entrada malformada" || fail "fail-open com entrada malformada"

echo "== install-global.sh: merge de hooks =="
S="$WORK/settings.json"
echo '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"echo HOOK_DO_USUARIO"}]}]}}' > "$S"
run_merge() {
    sed -n '/^python3 - "\$SETTINGS"/,/^PYEOF$/p' "$REPO_ROOT/scripts/install-global.sh" \
        | head -n -1 | tail -n +2 | python3 - "$S" "$HOOKS" >/dev/null
}
run_merge
python3 -c "
import json,sys
d=json.load(open('$S'))
stops=[h['command'] for e in d['hooks']['Stop'] for h in e['hooks']]
sys.exit(0 if any('HOOK_DO_USUARIO' in c for c in stops) else 1)
" && ok "preserva hook existente do usuário" || fail "preserva hook existente do usuário"
run_merge
python3 -c "
import json,sys
d=json.load(open('$S'))
sys.exit(0 if len(d['hooks']['Stop'])==3 else 1)
" && ok "idempotente em re-run" || fail "idempotente em re-run"

echo ""
echo "== resultado: $PASS passed, $FAIL failed =="
[ "$FAIL" -eq 0 ]
