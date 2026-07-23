#!/usr/bin/env bash
# update-references.sh — Sincroniza os repositórios de referência (diretórios
# irmãos) e reporta o que mudou desde a última sincronização.
#
# Uso:
#   bash scripts/update-references.sh           # fetch + relatório (não altera nada)
#   bash scripts/update-references.sh --pull    # fast-forward das branches locais
#
# Repositórios (ver CREDITS.md):
#   agentspec, agentcodex, data-agents, everything-claude-code,
#   mempalace, premium-presentations
set -euo pipefail

PROJETOS="$(cd "$(dirname "$0")/../.." && pwd)"
PULL=false
[[ "${1:-}" == "--pull" ]] && PULL=true

REPOS=(agentspec agentcodex data-agents everything-claude-code mempalace premium-presentations)

AGENTSPEC_CHANGED=false
printf "%-25s %-10s %s\n" "REPO" "ATRÁS" "ÚLTIMO COMMIT REMOTO"
printf "%s\n" "--------------------------------------------------------------------------"

for repo in "${REPOS[@]}"; do
  dir="$PROJETOS/$repo"
  if [[ ! -d "$dir/.git" ]]; then
    printf "%-25s %-10s %s\n" "$repo" "—" "NÃO CLONADO (ver CREDITS.md)"
    continue
  fi

  git -C "$dir" fetch --quiet 2>/dev/null || {
    printf "%-25s %-10s %s\n" "$repo" "?" "fetch falhou (offline?)"
    continue
  }

  branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD)
  upstream=$(git -C "$dir" rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null || echo "")
  if [[ -z "$upstream" ]]; then
    printf "%-25s %-10s %s\n" "$repo" "—" "sem upstream configurado"
    continue
  fi

  behind=$(git -C "$dir" rev-list --count "HEAD..$upstream" 2>/dev/null || echo "?")
  last=$(git -C "$dir" log -1 --format="%h %s" "$upstream" | cut -c1-60)
  printf "%-25s %-10s %s\n" "$repo" "$behind" "$last"

  if [[ "$behind" != "0" && "$behind" != "?" ]]; then
    echo "    novos commits:"
    git -C "$dir" log --oneline "HEAD..$upstream" | head -5 | sed 's/^/      /'
    [[ "$repo" == "agentspec" ]] && AGENTSPEC_CHANGED=true
    if $PULL; then
      if git -C "$dir" merge --ff-only "$upstream" --quiet 2>/dev/null; then
        echo "      → fast-forward aplicado ✔"
      else
        echo "      → fast-forward IMPOSSÍVEL (branch local divergiu — resolver manualmente)"
      fi
    fi
  fi
done

echo ""
if $AGENTSPEC_CHANGED; then
  echo "⚠ agentspec mudou — depois do pull, rode:"
  echo "    AGENTSPEC_PATH=$PROJETOS/agentspec/plugin bash scripts/update-agentspec.sh --dry-run"
fi
$PULL || echo "(relatório apenas — use --pull para aplicar fast-forward)"
