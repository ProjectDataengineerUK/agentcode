#!/usr/bin/env bash
# install-global.sh — Instala agentcode globalmente em ~/.claude/
# Isso ativa os 136+ agentes, KB e commands em TODOS os projetos Claude Code.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/../.claude"
DEST="$HOME/.claude"

info()  { printf "\033[0;34m[INFO]\033[0m %s\n" "$1"; }
ok()    { printf "\033[0;32m[OK]\033[0m %s\n" "$1"; }
warn()  { printf "\033[1;33m[WARN]\033[0m %s\n" "$1"; }
error() { printf "\033[0;31m[ERROR]\033[0m %s\n" "$1" >&2; }

if [[ ! -d "$SOURCE" ]]; then
    error ".claude/ não encontrado em $SOURCE"
    exit 1
fi

info "Instalando agentcode globalmente em $DEST ..."
echo ""

for component in agents commands kb skills; do
    if [[ -d "$SOURCE/$component" ]]; then
        info "Copiando $component..."
        cp -r "$SOURCE/$component" "$DEST/"
        ok "$component copiado"
    else
        warn "$component não encontrado — pulando"
    fi
done

# Instalar hooks (mempalace + lesson capture + drift de contexto)
info "Copiando hooks..."
mkdir -p "$DEST/hooks"
for h in mempalace_setup.sh mempalace_save.sh mempalace_precompact.sh \
         lesson_timing.sh lesson_capture.sh sync_context_reminder.sh; do
  [ -f "$SOURCE/hooks/$h" ] && cp "$SOURCE/hooks/$h" "$DEST/hooks/"
done
chmod +x "$DEST/hooks/"*.sh
ok "Hooks copiados"

# Registrar hooks no settings.json global
SETTINGS="$DEST/settings.json"
info "Registrando hooks em $SETTINGS ..."

# Lê settings atual (ou cria objeto vazio) e injeta os hooks
python3 - "$SETTINGS" "$DEST/hooks" <<'PYEOF'
import json, sys, os, shlex

settings_path = sys.argv[1]
hooks_dir = sys.argv[2]

# Load or create settings
try:
    with open(settings_path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

hooks = settings.setdefault("hooks", {})

def make_hook(cmd):
    return {"hooks": [{"type": "command", "command": cmd}]}

qhooks = shlex.quote(hooks_dir)
hooks["SessionStart"] = [make_hook(f"bash {qhooks}/mempalace_setup.sh || true")]
hooks["Stop"]         = [make_hook(f"command -v mempalace > /dev/null 2>&1 && bash {qhooks}/mempalace_save.sh || true")]
hooks["PreCompact"]   = [make_hook(f"command -v mempalace > /dev/null 2>&1 && bash {qhooks}/mempalace_precompact.sh || true")]

def have(name):
    return os.path.exists(os.path.join(hooks_dir, name))

if have("sync_context_reminder.sh"):
    hooks["Stop"].append(make_hook(f"bash {qhooks}/sync_context_reminder.sh || true"))
if have("lesson_timing.sh"):
    hooks["PreToolUse"] = [make_hook(f"bash {qhooks}/lesson_timing.sh || true")]
if have("lesson_capture.sh"):
    hooks["PostToolUse"] = [make_hook(f"bash {qhooks}/lesson_capture.sh || true")]

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print(f"  settings.json atualizado: {settings_path}")
PYEOF

ok "Hooks registrados"

echo ""
AGENT_COUNT=$(find "$DEST/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
KB_COUNT=$(find "$DEST/kb" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
echo "============================================"
printf "\033[0;32magentcode instalado globalmente\033[0m\n"
echo "============================================"
echo "  Agentes:  $AGENT_COUNT"
echo "  KB:       $KB_COUNT domínios"
echo "  Hooks:    SessionStart / Stop / PreCompact"
echo ""
echo "  Abra qualquer sessão Claude Code para usar."
echo "============================================"
