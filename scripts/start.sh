#!/usr/bin/env bash
# start.sh — Instala agentcode num projeto e gera CLAUDE.md via varredura automática.
#
# Uso:
#   bash /path/to/agentcode/scripts/start.sh              # projeto = diretório atual
#   bash /path/to/agentcode/scripts/start.sh /path/proj   # projeto específico
#   bash /path/to/agentcode/scripts/start.sh --force      # regenera mesmo com CLAUDE.md existente
#
# O que faz:
#   1. Instala agents, commands, kb, skills, hooks em .claude/ do projeto
#   2. Atualiza .claude/settings.json (preserva model, permissions)
#   3. Varre o projeto: lê arquivos-chave, detecta stack, estrutura, dependências
#   4. Gera CLAUDE.md com contexto prático para o Claude Code

set -euo pipefail

# ─── Cores ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'
info()    { printf "${BLUE}[INFO]${NC} %s\n" "$1"; }
ok()      { printf "${GREEN}[OK]${NC} %s\n" "$1"; }
warn()    { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; }
header()  { printf "\n${BOLD}%s${NC}\n" "$1"; }

# ─── Args ────────────────────────────────────────────────────────────────────
FORCE=false
PROJECT_DIR=""

for arg in "$@"; do
    case "$arg" in
        --force|-f) FORCE=true ;;
        -*) warn "Flag desconhecida: $arg" ;;
        *)  PROJECT_DIR="$arg" ;;
    esac
done

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
AGENTCODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_SRC="$AGENTCODE_DIR/.claude"
CLAUDE_DST="$PROJECT_DIR/.claude"
HOOKS_DST="$CLAUDE_DST/hooks"

if [[ ! -d "$AGENTCODE_DIR/.claude/agents" ]]; then
    printf "${RED}[ERRO]${NC} agentcode não encontrado em: $AGENTCODE_DIR\n" >&2
    exit 1
fi

header "═══ agentcode start ═══"
echo "  Projeto : $PROJECT_DIR"
echo "  Agentcode: $AGENTCODE_DIR"
echo ""

# ─── FASE 1: Instalar agentcode ──────────────────────────────────────────────
header "1/3  Instalando agentcode"

mkdir -p "$CLAUDE_DST"

for component in agents commands kb skills; do
    if [[ -d "$CLAUDE_SRC/$component" ]]; then
        cp -r "$CLAUDE_SRC/$component" "$CLAUDE_DST/"
        count=$(find "$CLAUDE_DST/$component" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        ok "$component ($count arquivos)"
    fi
done

mkdir -p "$HOOKS_DST"
cp "$CLAUDE_SRC/hooks/mempalace_setup.sh"      "$HOOKS_DST/"
cp "$CLAUDE_SRC/hooks/mempalace_save.sh"       "$HOOKS_DST/"
cp "$CLAUDE_SRC/hooks/mempalace_precompact.sh" "$HOOKS_DST/"
chmod +x "$HOOKS_DST/"*.sh
ok "hooks mempalace"

SETTINGS="$CLAUDE_DST/settings.json"
python3 - "$SETTINGS" "$HOOKS_DST" <<'PYEOF'
import json, sys

settings_path, hooks_dir = sys.argv[1], sys.argv[2]
try:
    with open(settings_path) as f:
        cfg = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    cfg = {}

def hook(cmd):
    return {"hooks": [{"type": "command", "command": cmd}]}

cfg["hooks"] = {
    "SessionStart": [hook(f'bash "{hooks_dir}/mempalace_setup.sh" || true')],
    "Stop":         [hook(f'command -v mempalace > /dev/null 2>&1 && bash "{hooks_dir}/mempalace_save.sh" || true')],
    "PreCompact":   [hook(f'command -v mempalace > /dev/null 2>&1 && bash "{hooks_dir}/mempalace_precompact.sh" || true')],
}

with open(settings_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
PYEOF
ok "settings.json atualizado"

# ─── FASE 2: Varredura do projeto ────────────────────────────────────────────
header "2/3  Varrendo projeto"

cd "$PROJECT_DIR"

# pipefail desativado na varredura: grep -v com input vazio retorna 1
set +o pipefail

has_file()  { [[ -f "$PROJECT_DIR/$1" ]]; }
has_dir()   { [[ -d "$PROJECT_DIR/$1" ]]; }
file_count(){ find "$PROJECT_DIR" -maxdepth 5 -name "$1" 2>/dev/null \
               | grep -v ".git\|node_modules\|__pycache__\|\.venv\|\.claude" 2>/dev/null \
               | wc -l | tr -d ' '; }
read_head() { head -"${2:-30}" "$PROJECT_DIR/$1" 2>/dev/null || true; }

# ── Nome do projeto ──
PROJ_NAME=""
if has_file "pyproject.toml"; then
    PROJ_NAME=$(python3 -c "
import re
content = open('$PROJECT_DIR/pyproject.toml').read()
m = re.search(r'name\s*=\s*[\"\'](.*?)[\"\']', content)
print(m.group(1) if m else '')
" 2>/dev/null)
elif has_file "package.json"; then
    PROJ_NAME=$(python3 -c "import json; d=json.load(open('$PROJECT_DIR/package.json')); print(d.get('name',''))" 2>/dev/null)
elif has_file "Cargo.toml"; then
    PROJ_NAME=$(grep -m1 '^name' "$PROJECT_DIR/Cargo.toml" 2>/dev/null | sed 's/name = "//' | tr -d '"' || true)
elif has_file "go.mod"; then
    PROJ_NAME=$(head -1 "$PROJECT_DIR/go.mod" 2>/dev/null | awk '{print $2}' | xargs basename 2>/dev/null || true)
fi
PROJ_NAME="${PROJ_NAME:-$(basename "$PROJECT_DIR")}"
info "Nome: $PROJ_NAME"

# ── Stack detection ──
STACK=()

# Python
if has_file "pyproject.toml" || has_file "requirements.txt" || has_file "setup.py"; then
    STACK+=("Python")
    reqs=$(cat "$PROJECT_DIR/requirements"*.txt "$PROJECT_DIR/pyproject.toml" 2>/dev/null | tr '[:upper:]' '[:lower:]' || true)
    if [[ "$reqs" == *"fastapi"*   ]]; then STACK+=("FastAPI");    fi
    if [[ "$reqs" == *"flask"*     ]]; then STACK+=("Flask");      fi
    if [[ "$reqs" == *"django"*    ]]; then STACK+=("Django");     fi
    if [[ "$reqs" == *"pyspark"*   ]]; then STACK+=("PySpark");    fi
    if [[ "$reqs" == *"dbt"*       ]]; then STACK+=("dbt");        fi
    if [[ "$reqs" == *"airflow"*   ]]; then STACK+=("Airflow");    fi
    if [[ "$reqs" == *"pandas"*    ]]; then STACK+=("Pandas");     fi
    if [[ "$reqs" == *"sqlalchemy"* ]]; then STACK+=("SQLAlchemy"); fi
    if [[ "$reqs" == *"anthropic"* ]]; then STACK+=("Claude API"); fi
    if [[ "$reqs" == *"openai"*    ]]; then STACK+=("OpenAI");     fi
    if [[ "$reqs" == *"langchain"* ]]; then STACK+=("LangChain");  fi
    if [[ "$reqs" == *"vertexai"* || "$reqs" == *"google-cloud"* ]]; then STACK+=("GCP"); fi
fi

# JavaScript / TypeScript
if has_file "package.json"; then
    STACK+=("Node.js")
    pkg=$(cat "$PROJECT_DIR/package.json" 2>/dev/null | tr '[:upper:]' '[:lower:]' || true)
    if [[ "$pkg" == *"typescript"* ]]; then STACK+=("TypeScript"); fi
    if [[ "$pkg" == *"\"next\""*   ]]; then STACK+=("Next.js");    fi
    if [[ "$pkg" == *"react"*      ]]; then STACK+=("React");      fi
    if [[ "$pkg" == *"vue"*        ]]; then STACK+=("Vue");        fi
    if [[ "$pkg" == *"express"*    ]]; then STACK+=("Express");    fi
fi

if has_file "Cargo.toml";      then STACK+=("Rust");         fi
if has_file "go.mod";          then STACK+=("Go");           fi
if has_file "pom.xml";         then STACK+=("Java/Maven");   fi
if has_file "build.gradle";    then STACK+=("Java/Gradle");  fi
if has_file "Dockerfile";      then STACK+=("Docker");       fi
if has_dir "infra" || has_file "main.tf"; then STACK+=("Terraform"); fi
if has_file "cloudbuild.yaml"; then STACK+=("Cloud Build");  fi
if has_file "dbt_project.yml"; then STACK+=("dbt");          fi
if has_dir  "dags";            then STACK+=("Airflow");      fi

info "Stack: ${STACK[*]:-desconhecida}"

# ── Estrutura de diretórios (tree leve) ──
TOP_DIRS=$(find "$PROJECT_DIR" -maxdepth 1 -mindepth 1 -type d \
    | grep -v ".git\|node_modules\|__pycache__\|\.venv\|\.claude\|\.cursor\|\.codex" \
    | xargs -I{} basename {} 2>/dev/null | sort)

# Subdiretórios relevantes (segundo nível)
SUBTREE=$(find "$PROJECT_DIR" -maxdepth 2 -mindepth 2 -type d \
    | grep -v ".git\|node_modules\|__pycache__\|\.venv\|\.claude\|\.cursor\|\.codex\|\.agentcodex" \
    | sed "s|$PROJECT_DIR/||" | sort | head -30)

# ── Contagem de arquivos por extensão ──
PY_COUNT=$(file_count "*.py")
TS_COUNT=$(file_count "*.ts")
JS_COUNT=$(file_count "*.js")
SQL_COUNT=$(file_count "*.sql")
RS_COUNT=$(file_count "*.rs")
GO_COUNT=$(file_count "*.go")
TEST_COUNT=$(find "$PROJECT_DIR" -maxdepth 6 \
    \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" -o -name "*.spec.ts" \
       -o -name "*_test.go" -o -name "*_test.rs" \) 2>/dev/null \
    | grep -v ".git\|node_modules" | wc -l | tr -d ' ')

# ── Arquivos-chave: lê conteúdo para enriquecer o CLAUDE.md ──
KEY_FILES_INFO=""

# Entry points Python
for ep in main.py app.py run.py server.py manage.py cli.py __main__.py; do
    if has_file "$ep"; then
        snippet=$(read_head "$ep" 20 | grep -E "^(def |class |@app\.|import |from )" | head -8 | sed 's/^/    /')
        KEY_FILES_INFO+="- \`$ep\`: entry point"
        if [[ -n "$snippet" ]]; then KEY_FILES_INFO+=$'\n'"$snippet"; fi
        KEY_FILES_INFO+=$'\n'
    fi
done

# Entry points JS/TS
for ep in src/index.ts src/main.ts index.ts main.ts src/app.ts app.ts; do
    if has_file "$ep"; then
        KEY_FILES_INFO+="- \`$ep\`: entry point TS/JS"$'\n'
    fi
done

# Makefile / justfile / scripts
for mf in Makefile justfile Taskfile.yml; do
    if has_file "$mf"; then
        targets=$(grep -E "^[a-zA-Z][a-zA-Z0-9_-]+:" "$PROJECT_DIR/$mf" 2>/dev/null \
                  | cut -d: -f1 | head -10 | tr '\n' ' ' || true)
        KEY_FILES_INFO+="- \`$mf\` targets: \`$targets\`"$'\n'
    fi
done

# Docker Compose
if has_file "docker-compose.yml" || has_file "docker-compose.yaml"; then
    services=$(grep -E "^  [a-zA-Z]" "$PROJECT_DIR/docker-compose.yml" "$PROJECT_DIR/docker-compose.yaml" 2>/dev/null \
               | sed 's/://;s/^  //' | head -8 | tr '\n' ', ' || true)
    KEY_FILES_INFO+="- \`docker-compose\` services: $services"$'\n'
fi

# dbt
if has_file "dbt_project.yml"; then
    model_dirs=$(grep -E "model-paths|source-paths" "$PROJECT_DIR/dbt_project.yml" 2>/dev/null | head -3 || true)
    KEY_FILES_INFO+="- \`dbt_project.yml\`: $model_dirs"$'\n'
fi

# Airflow
if has_dir "dags"; then
    dag_count=$(find "$PROJECT_DIR/dags" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
    KEY_FILES_INFO+="- \`dags/\`: $dag_count DAGs encontrados"$'\n'
fi

# ── Git ──
GIT_BRANCH=""; GIT_LAST=""; GIT_REMOTE=""
if [[ -d "$PROJECT_DIR/.git" ]]; then
    GIT_BRANCH=$(git -C "$PROJECT_DIR" branch --show-current 2>/dev/null || true)
    GIT_LAST=$(git -C "$PROJECT_DIR" log --oneline -1 2>/dev/null || echo "sem commits")
    GIT_REMOTE=$(git -C "$PROJECT_DIR" remote get-url origin 2>/dev/null || true)
fi

# ── README / descrição ──
README_EXCERPT=""
if has_file "README.md"; then
    README_EXCERPT=$(head -30 "$PROJECT_DIR/README.md" 2>/dev/null \
        | grep -v "^#\|^!\[" | grep -v "^$" | head -5 | sed 's/^/> /')
fi

info "Varredura concluída"

set -o pipefail  # reativar

# ─── FASE 3: Gerar CLAUDE.md ─────────────────────────────────────────────────
header "3/3  Gerando CLAUDE.md"

CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"

if [[ -f "$CLAUDE_MD" ]] && [[ "$FORCE" == false ]]; then
    warn "CLAUDE.md já existe. Use --force para regenerar."
    echo ""
else

# Montar listas fora do heredoc (evita problemas de expansão)
STACK_LIST=""
for s in "${STACK[@]}"; do STACK_LIST+="- $s"$'\n'; done
[[ -z "$STACK_LIST" ]] && STACK_LIST="- (não detectada)"

DIR_LIST=""
while IFS= read -r d; do
    [[ -n "$d" ]] && DIR_LIST+="  $d/"$'\n'
done <<< "$TOP_DIRS"

SUBTREE_LIST=""
while IFS= read -r d; do
    [[ -n "$d" ]] && SUBTREE_LIST+="  $d/"$'\n'
done <<< "$SUBTREE"

CODE_LINES=""
if [[ "$PY_COUNT"   -gt 0 ]]; then CODE_LINES+="- Python: $PY_COUNT arquivos"$'\n'; fi
if [[ "$TS_COUNT"   -gt 0 ]]; then CODE_LINES+="- TypeScript: $TS_COUNT arquivos"$'\n'; fi
if [[ "$JS_COUNT"   -gt 0 ]]; then CODE_LINES+="- JavaScript: $JS_COUNT arquivos"$'\n'; fi
if [[ "$SQL_COUNT"  -gt 0 ]]; then CODE_LINES+="- SQL: $SQL_COUNT arquivos"$'\n'; fi
if [[ "$RS_COUNT"   -gt 0 ]]; then CODE_LINES+="- Rust: $RS_COUNT arquivos"$'\n'; fi
if [[ "$GO_COUNT"   -gt 0 ]]; then CODE_LINES+="- Go: $GO_COUNT arquivos"$'\n'; fi
if [[ "$TEST_COUNT" -gt 0 ]]; then CODE_LINES+="- Testes: $TEST_COUNT arquivos"$'\n'; fi
if [[ -z "$CODE_LINES" ]]; then CODE_LINES="- (sem código-fonte detectado)"; fi

GIT_SECTION=""
if [[ -n "$GIT_BRANCH" ]]; then
    GIT_SECTION="## Git"$'\n\n'
    GIT_SECTION+="- **Branch:** \`$GIT_BRANCH\`"$'\n'
    GIT_SECTION+="- **Último commit:** $GIT_LAST"$'\n'
    if [[ -n "$GIT_REMOTE" ]]; then GIT_SECTION+="- **Remote:** $GIT_REMOTE"$'\n'; fi
fi

INSTALL_CMD="# adicione o comando aqui"
has_file "pyproject.toml"    && INSTALL_CMD="uv sync"
has_file "requirements.txt"  && INSTALL_CMD="pip install -r requirements.txt"
has_file "package.json"      && INSTALL_CMD="npm install"

# Gerar tabelas de agentes e comandos com Python (stack passada como arg, sem heredoc aninhado)
AGENT_TABLE=$(python3 - "${STACK[*]:-}" <<'PYEOF'
import sys
stack = [s.lower() for s in sys.argv[1].split()]
rows = []

if any(x in stack for x in ["pyspark", "dbt", "airflow", "spark"]):
    rows += [("@databricks-spark-expert", "PySpark, DLT, pipelines"),
             ("@dbt-specialist", "modelos dbt")]
if any(x in stack for x in ["gcp", "cloud build", "vertexai"]):
    rows += [("@gcp-data-architect", "arquitetura GCP, BigQuery, Cloud Run"),
             ("@ai-data-engineer-gcp", "pipelines AI/ML no GCP")]
if any(x in stack for x in ["claude api", "anthropic", "openai", "langchain"]):
    rows += [("@genai-architect", "sistemas multi-agente, LLM"),
             ("@ai-prompt-specialist", "otimização de prompts")]
if any(x in stack for x in ["fastapi", "flask", "django"]):
    rows += [("@python-reviewer", "revisão de código Python")]
if any(x in stack for x in ["next.js", "react", "express", "typescript", "node.js"]):
    rows += [("@typescript-reviewer", "revisão TypeScript/JS")]
if any(x in stack for x in ["docker", "terraform", "kubernetes"]):
    rows += [("@ci-cd-specialist", "pipelines CI/CD, Terraform")]
if "python" in stack:
    rows += [("@python-developer", "código Python, dataclasses, type hints")]
if "sql" in stack or any(x in stack for x in ["pyspark", "dbt"]):
    rows += [("@sql-optimizer", "otimização de queries")]
if any(x in stack for x in ["rust"]):
    rows += [("@rust-reviewer", "revisão Rust, lifetimes, ownership")]
if any(x in stack for x in ["go"]):
    rows += [("@go-reviewer", "revisão Go idiomático")]

rows += [("@code-reviewer", "revisão geral de código"),
         ("@security-reviewer", "vulnerabilidades e segurança"),
         ("@the-planner", "planejamento de features")]

print("| Agente | Uso |")
print("|--------|-----|")
for agent, use in rows:
    print(f"| `{agent}` | {use} |")
PYEOF
)

CMD_TABLE=$(python3 - "${STACK[*]:-}" <<'PYEOF'
import sys
stack = [s.lower() for s in sys.argv[1].split()]
rows = []

if any(x in stack for x in ["pyspark", "spark", "dbt"]):
    rows += [("/spark", "PySpark, DLT, LakeFlow"),
             ("/sql",   "SQL, queries, otimização")]
if any(x in stack for x in ["gcp", "vertexai", "cloud build"]):
    rows += [("/pipeline", "design de pipelines de dados")]
if any(x in stack for x in ["anthropic", "claude api", "openai", "langchain"]):
    rows += [("/workflow", "orquestração multi-agente")]
if any(x in stack for x in ["pyspark", "spark", "dbt", "airflow"]):
    rows += [("/party", "análise multi-perspectiva paralela")]

rows += [("/status",    "estado atual do projeto"),
         ("/preflight", "verificar completude do projeto (15 blocos)")]

print("| Comando | Quando usar |")
print("|---------|-------------|")
for cmd, use in rows:
    print(f"| `{cmd}` | {use} |")
PYEOF
)

DATE_GEN=$(date '+%Y-%m-%d')

cat > "$CLAUDE_MD" <<CLAUDEMD
# $PROJ_NAME

${README_EXCERPT:-> _Adicione aqui uma descrição do projeto._}

---

## Stack

${STACK_LIST}
## Estrutura

\`\`\`
$PROJ_NAME/
${DIR_LIST}${SUBTREE_LIST}\`\`\`

## Código

${CODE_LINES}
${GIT_SECTION}
---

## Arquivos-chave

${KEY_FILES_INFO:-> _Nenhum entry point detectado automaticamente._}

## Como rodar localmente

\`\`\`bash
$INSTALL_CMD

# Executar
# adicione o comando aqui
\`\`\`

## Padrões e Convenções

> _Descreva aqui os padrões do projeto: naming, formatação, lint, testes._

---

## Agentes recomendados (agentcode)

${AGENT_TABLE}

## Comandos úteis (agentcode)

${CMD_TABLE}

---

_Gerado automaticamente por \`agentcode start\` em ${DATE_GEN}._
_Edite livremente — este arquivo guia o comportamento do Claude Code neste projeto._
CLAUDEMD

ok "CLAUDE.md gerado"
fi

# ─── Resumo ──────────────────────────────────────────────────────────────────
AGENT_COUNT=$(find "$CLAUDE_DST/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
KB_COUNT=$(find "$CLAUDE_DST/kb" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')

echo ""
echo "════════════════════════════════════════════"
printf "${GREEN}${BOLD}agentcode instalado em $PROJ_NAME${NC}\n"
echo "════════════════════════════════════════════"
echo "  Agentes : $AGENT_COUNT"
echo "  KB      : $KB_COUNT domínios"
echo "  Stack   : ${STACK[*]:-não detectada}"
echo "  CLAUDE.md: $CLAUDE_MD"
echo ""
echo "  Abra o projeto:"
printf "    ${BOLD}cd $PROJECT_DIR && claude${NC}\n"
echo "════════════════════════════════════════════"
