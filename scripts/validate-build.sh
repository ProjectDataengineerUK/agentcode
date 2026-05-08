#!/usr/bin/env bash
# validate-build.sh — Post-build structural validation for agentcode.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE="$ROOT/.claude"
ERRORS=0

check_count() {
  local label="$1" actual="$2" min="$3"
  if [[ "$actual" -ge "$min" ]]; then
    echo "  ✔ $label: $actual (min $min)"
  else
    echo "  ✗ FAIL $label: $actual (min $min required)"
    ERRORS=$((ERRORS + 1))
  fi
}

check_exists() {
  local label="$1" path="$2"
  if [[ -e "$path" ]]; then
    echo "  ✔ $label exists"
  else
    echo "  ✗ FAIL $label missing: $path"
    ERRORS=$((ERRORS + 1))
  fi
}

echo "Validating agentcode build..."
echo ""

# Agent counts
agent_count=$(find "$CLAUDE/agents" -name "*.md" 2>/dev/null | wc -l)
check_count "agents total" "$agent_count" 115

lang_count=$(find "$CLAUDE/agents/languages" -name "*.md" 2>/dev/null | wc -l)
check_count "agents/languages (ECC)" "$lang_count" 46

de_count=$(find "$CLAUDE/agents/data-engineering" -name "*.md" 2>/dev/null | wc -l)
check_count "agents/data-engineering" "$de_count" 24

# KB domain counts
kb_domain_count=$(find "$CLAUDE/kb" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
check_count "KB domains" "$kb_domain_count" 31

# Required files
echo ""
check_exists "hooks.json" "$CLAUDE/hooks/hooks.json"
check_exists "hooks-agentspec-base.json" "$CLAUDE/hooks/hooks-agentspec-base.json"
check_exists "mempalace_save.sh" "$CLAUDE/hooks/mempalace_save.sh"
check_exists "mempalace_precompact.sh" "$CLAUDE/hooks/mempalace_precompact.sh"
check_exists ".agentcode-manifest.json" "$CLAUDE/hooks/.agentcode-manifest.json"
check_exists "guardrails/constitution.md" "$CLAUDE/kb/guardrails/constitution.md"
check_exists "commands/data/" "$CLAUDE/commands/data"
check_exists "skills/" "$CLAUDE/skills"
check_exists ".codex/" "$ROOT/.codex"
check_exists ".cursor/" "$ROOT/.cursor"
check_exists "scripts/update-agentspec.sh" "$ROOT/scripts/update-agentspec.sh"
check_exists "CLAUDE.md" "$ROOT/CLAUDE.md"

# hooks.json validity
echo ""
PYTHON_CMD="python"
if "$PYTHON_CMD" -m json.tool "$CLAUDE/hooks/hooks.json" > /dev/null 2>&1; then
  echo "  ✔ hooks.json is valid JSON"
else
  echo "  ✗ FAIL hooks.json is not valid JSON"
  ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
if [[ $ERRORS -eq 0 ]]; then
  echo "✔ Build valid — $agent_count agents, $kb_domain_count KB domains"
  exit 0
else
  echo "✗ Build FAILED — $ERRORS error(s) found"
  exit 1
fi
