---
name: start
description: Initialize agentcode in this project — installs agents/KB/hooks and generates CLAUDE.md by scanning all project files
---

# /start — Initialize agentcode

Scans the entire project and generates `CLAUDE.md` with real context: stack, structure, key files, and agent recommendations. Runs inline without delegation.

## Usage

```
/start            # Generate CLAUDE.md (skips if already exists)
/start --force    # Regenerate even if CLAUDE.md exists
```

---

## Execution

### Step 1 — Install agentcode hooks in this project

Run this bash command to set up `.claude/hooks/` and `settings.json`:

```bash
GLOBAL="$HOME/.claude"
LOCAL=".claude"
mkdir -p "$LOCAL/hooks"

for h in mempalace_setup.sh mempalace_save.sh mempalace_precompact.sh; do
  if [[ -f "$GLOBAL/hooks/$h" ]]; then
    cp "$GLOBAL/hooks/$h" "$LOCAL/hooks/"
    chmod +x "$LOCAL/hooks/$h"
  fi
done

python3 - "$LOCAL/settings.json" "$LOCAL/hooks" <<'PY'
import json, sys, os
path, hooks = sys.argv[1], sys.argv[2]
try:
    cfg = json.load(open(path))
except:
    cfg = {}
def hook(cmd):
    return {"hooks": [{"type": "command", "command": cmd}]}
cfg["hooks"] = {
    "SessionStart": [hook(f'bash "{hooks}/mempalace_setup.sh" || true')],
    "Stop":         [hook(f'command -v mempalace > /dev/null 2>&1 && bash "{hooks}/mempalace_save.sh" || true')],
    "PreCompact":   [hook(f'command -v mempalace > /dev/null 2>&1 && bash "{hooks}/mempalace_precompact.sh" || true')],
}
json.dump(cfg, open(path, "w"), indent=2)
PY
echo "hooks OK"
```

### Step 2 — Scan all project files

Use these tools to read the project:

**Find all files:**
```
Glob("**/*")
```
Exclude: `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `.claude/`, `*.lock`, `*.log`, `dist/`, `build/`

**Read manifest files** (detect stack):
- `pyproject.toml`, `requirements.txt`, `setup.py`
- `package.json`, `tsconfig.json`
- `Cargo.toml`, `go.mod`, `pom.xml`
- `Dockerfile`, `docker-compose.yml`
- `main.tf`, `dbt_project.yml`
- `Makefile`, `justfile`
- `.github/workflows/*.yml`

**Read entry points** (first 50 lines):
- `main.py`, `app.py`, `run.py`, `server.py`, `manage.py`, `cli.py`
- `src/index.ts`, `src/main.ts`, `index.ts`
- `main.go`, `src/main.rs`

**Read documentation** (first 30 lines):
- `README.md`, `CENARIO.MD`, `ARCHITECTURE.md`, `docs/*.md`

**Read 3–5 source files** to understand patterns (look in `src/`, `app/`, `lib/`).

### Step 3 — Detect from what you read

**Stack:** languages, frameworks, libraries, infra tools  
**Entry points:** main files, routes, CLI commands  
**Conventions:** linter (ruff/eslint), formatter (black/prettier), test runner (pytest/jest/vitest)  
**Structure:** monorepo vs single service, feature-based vs layer-based directories  
**Domain:** what the project actually does (from README, code, or any spec document)

### Step 4 — Generate CLAUDE.md

Skip if `CLAUDE.md` already exists and `--force` was NOT passed. Otherwise write `CLAUDE.md` now.

Use only real values found in steps 2–3. No placeholders. Write in Portuguese (pt-BR).

```markdown
# {project name}

> {description from README, spec doc, or inferred from code — one paragraph}

---

## Stack

{bullet list — only detected technologies}

## Estrutura

\`\`\`
{directory tree, 2 levels, no .git/node_modules/.claude}
\`\`\`

## Arquivos-chave

| Arquivo | Função |
|---------|--------|
{one row per important file — entry points, models, config, main modules}

## Convenções

- **Linter:** {detected or "não configurado"}
- **Formatter:** {detected or "não configurado"}
- **Testes:** {detected runner} — `{detected test command}`

## Como rodar

\`\`\`bash
{install command}
{run command}
\`\`\`

---

## Agentes recomendados (agentcode)

| Agente | Quando usar |
|--------|-------------|
{agent table — only agents relevant to the detected stack}

## Comandos úteis

| Comando | Quando usar |
|---------|-------------|
{command table}

---

_Gerado por `/start` em {today's date}._
```

**Agent mapping** (include only matching rows):

| Stack detected | Agents |
|----------------|--------|
| Python | `@python-developer`, `@python-reviewer` |
| FastAPI / Flask / Django | `@python-reviewer`, `@security-reviewer` |
| TypeScript / React / Next.js | `@typescript-reviewer` |
| PySpark / dbt / Airflow | `@databricks-spark-expert`, `@dbt-specialist`, `@airflow-specialist` |
| Claude API / OpenAI / LangChain | `@genai-architect`, `@ai-prompt-specialist` |
| GCP | `@gcp-data-architect`, `@ai-data-engineer-gcp` |
| AWS | `@aws-data-architect`, `@aws-lambda-architect` |
| Docker / Terraform | `@ci-cd-specialist` |
| SQL | `@sql-optimizer` |
| Rust | `@rust-reviewer` |
| Go | `@go-reviewer` |
| Java | `@java-reviewer` |
| No code yet (spec/concept) | `@brainstorm-agent`, `@the-planner`, `@design-agent` |
| Always | `@code-reviewer`, `@security-reviewer`, `@the-planner` |

**Command mapping** (include only matching rows):

| Stack | Commands |
|-------|----------|
| PySpark / dbt / Spark | `/spark`, `/sql` |
| GCP | `/pipeline` |
| Claude API / LLM | `/workflow` |
| Any data | `/party`, `/preflight` |
| No code yet | `/brainstorm`, `/define`, `/design` |
| Always | `/status`, `/preflight` |

---

## Output

After generating CLAUDE.md, print:

```
agentcode initialized in {project name}
  Stack   : {detected}
  CLAUDE.md: written
```
