#!/usr/bin/env bash
# update-agentspec.sh — Surgically updates agentspec-owned components without touching agentcode extensions.
set -euo pipefail

AGENTSPEC_SOURCE="${AGENTSPEC_PATH:-$(cd "$(dirname "$0")/../../agentspec/plugin" 2>/dev/null && pwd || echo "AGENTSPEC_PATH_NOT_SET")}"
AGENTCODE_TARGET="$(cd "$(dirname "$0")/.." && pwd)/.claude"
DRY_RUN=false
ERRORS=0

[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

if [[ "$AGENTSPEC_SOURCE" == "AGENTSPEC_PATH_NOT_SET" ]]; then
  echo "ERROR: Could not find agentspec/plugin. Set AGENTSPEC_PATH env var."
  exit 1
fi

echo "Updating agentspec → agentcode"
echo "  Source : $AGENTSPEC_SOURCE"
echo "  Target : $AGENTCODE_TARGET"
echo "  DryRun : $DRY_RUN"
echo ""

# Directories fully owned by agentspec — safe to overwrite
AGENTSPEC_OWNED_DIRS=(
  "agents/architect"
  "agents/cloud"
  "agents/dev"
  "agents/platform"
  "agents/python"
  "agents/test"
  "agents/workflow"
  "kb/ai-data-engineering"
  "kb/airflow"
  "kb/aws"
  "kb/cloud-platforms"
  "kb/data-modeling"
  "kb/data-quality"
  "kb/dbt"
  "kb/gcp"
  "kb/genai"
  "kb/lakeflow"
  "kb/lakehouse"
  "kb/medallion"
  "kb/microsoft-fabric"
  "kb/modern-stack"
  "kb/prompt-engineering"
  "kb/pydantic"
  "kb/python"
  "kb/shared"
  "kb/spark"
  "kb/sql-patterns"
  "kb/streaming"
  "kb/supabase"
  "kb/terraform"
  "kb/testing"
  "commands/workflow"
  "commands/data-engineering"
  "commands/core"
  "commands/knowledge"
  "commands/review"
  "commands/visual-explainer"
  "skills/agent-router"
  "skills/component-model"
  "skills/data-engineering-guide"
  "skills/excalidraw-diagram"
  "skills/github-cr-adr"
  "skills/github-cr-issue"
  "skills/github-post-issue"
  "skills/kb-build"
  "skills/sdd-brainstorm"
  "skills/sdd-build"
  "skills/sdd-define"
  "skills/sdd-design"
  "skills/sdd-iterate"
  "skills/sdd-ship"
  "skills/sdd-workflow"
  "skills/visual-explainer"
  "sdd"
  "tools/spec-judge"
  "tools/spec-linter"
  "scripts"
)

# agents/data-engineering is SHARED: agentspec owns 15 files, agentcode adds 9.
# Only update files that exist in the agentspec source — never delete agentcode extensions.
AGENTSPEC_OWNED_DATA_ENG_FILES=(
  "ai-data-engineer.md"
  "airflow-specialist.md"
  "dbt-specialist.md"
  "lakeflow-architect.md"
  "lakeflow-expert.md"
  "lakeflow-pipeline-builder.md"
  "lakeflow-specialist.md"
  "qdrant-specialist.md"
  "spark-engineer.md"
  "spark-performance-analyzer.md"
  "spark-specialist.md"
  "spark-streaming-architect.md"
  "spark-troubleshooter.md"
  "sql-optimizer.md"
  "streaming-engineer.md"
)

copy_dir() {
  local src="$1" dst="$2"
  if $DRY_RUN; then
    echo "  [DRY] cp -r '$src/' → '$dst/'"
  else
    mkdir -p "$dst"
    cp -r "$src/." "$dst/"
  fi
}

copy_file() {
  local src="$1" dst="$2"
  if $DRY_RUN; then
    echo "  [DRY] cp '$src' → '$dst'"
  else
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
  fi
}

# Update owned directories
for dir in "${AGENTSPEC_OWNED_DIRS[@]}"; do
  src="$AGENTSPEC_SOURCE/$dir"
  dst="$AGENTCODE_TARGET/$dir"
  if [[ -d "$src" ]]; then
    copy_dir "$src" "$dst"
    echo "  ✔ $dir"
  else
    echo "  ⚠ $dir — not found in source (agentspec restructured?)"
    ERRORS=$((ERRORS + 1))
  fi
done

# Update shared agents/data-engineering (file-by-file, preserving agentcode additions)
echo ""
echo "Updating agents/data-engineering (SHARED — file-by-file)..."
for file in "${AGENTSPEC_OWNED_DATA_ENG_FILES[@]}"; do
  src="$AGENTSPEC_SOURCE/agents/data-engineering/$file"
  dst="$AGENTCODE_TARGET/agents/data-engineering/$file"
  if [[ -f "$src" ]]; then
    copy_file "$src" "$dst"
    echo "  ✔ agents/data-engineering/$file"
  else
    echo "  ⚠ agents/data-engineering/$file — not found in source"
    ERRORS=$((ERRORS + 1))
  fi
done

# Re-merge hooks.json (never overwrite — re-generate merged version)
echo ""
echo "Re-merging hooks.json..."
AGENTSPEC_HOOKS="$AGENTSPEC_SOURCE/hooks/hooks.json"
if [[ -f "$AGENTSPEC_HOOKS" ]]; then
  if $DRY_RUN; then
    echo "  [DRY] merge hooks.json (agentspec base + mempalace entries)"
  else
    cp "$AGENTSPEC_HOOKS" "$AGENTCODE_TARGET/hooks/hooks-agentspec-base.json"
    # Merge: read agentspec hooks + add mempalace entries
    # IMPORTANT: export before the heredoc so os.environ is populated inside Python
    export AGENTCODE_TARGET
    python3 - <<'PYEOF'
import json, sys, os

base_path = os.environ.get("AGENTCODE_TARGET", "") + "/hooks/hooks-agentspec-base.json"
out_path  = os.environ.get("AGENTCODE_TARGET", "") + "/hooks/hooks.json"

with open(base_path) as f:
    merged = json.load(f)

hooks = merged.setdefault("hooks", {})

mempalace_setup = {
    "matcher": "",
    "hooks": [{"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/mempalace_setup.sh\" || true"}]
}
mempalace_stop = {
    "matcher": "",
    "hooks": [{"type": "command", "command": "command -v mempalace > /dev/null 2>&1 && bash \"${CLAUDE_PLUGIN_ROOT}/hooks/mempalace_save.sh\" || true"}]
}
mempalace_precompact = {
    "matcher": "",
    "hooks": [{"type": "command", "command": "command -v mempalace > /dev/null 2>&1 && bash \"${CLAUDE_PLUGIN_ROOT}/hooks/mempalace_precompact.sh\" || true"}]
}

hooks.setdefault("SessionStart", []).append(mempalace_setup)
hooks.setdefault("Stop", []).append(mempalace_stop)
hooks.setdefault("PreCompact", []).append(mempalace_precompact)

with open(out_path, "w") as f:
    json.dump(merged, f, indent=2)
print("  ✔ hooks.json merged")
PYEOF
  fi
else
  echo "  ⚠ agentspec hooks/hooks.json not found"
  ERRORS=$((ERRORS + 1))
fi

# Final summary
echo ""
if [[ $ERRORS -eq 0 ]]; then
  echo "✔ Update complete — no errors."
else
  echo "⚠ Update complete with $ERRORS warning(s). Review output above."
  exit 1
fi
