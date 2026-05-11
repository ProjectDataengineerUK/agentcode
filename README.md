# agentcode

A unified Claude Code plugin combining the best of agentspec, ECC (everything-claude-code),
data-agents, agentcodex, and mempalace into a single installable plugin.

## What's Included

| Source | What it brings | Count |
|--------|---------------|-------|
| agentspec | Core workflow, cloud, data-engineering agents + 25 KB domains + 33 commands + 5 skills + SDD | ~290 files |
| ECC | 46 language-specialist agents + 2 security agents + .cursor + .codex | 48 agents + 66 files |
| data-agents | Databricks/Fabric specialized agents + 7 KB domains (databricks, fabric, governance, doma-protocol, semantic-modeling, migration, guardrails) | 9 agents + ~53 files |
| agentcodex | 8 unique KB domains (controls, foundations, integrations, metadata, operations, orchestration, patterns, platforms) | ~40 files |
| mempalace | Auto-save hooks for session memory persistence | 2 scripts |

**Total: 136+ agents, 42+ KB domains**

## Installation

### Opção A — Marketplace (recomendado)

Instala globalmente via Claude Code marketplace em dois comandos:

```bash
claude plugin marketplace add ProjectDataengineerUK/agentcode
claude plugin install agentcode
```

Após instalar, abra qualquer sessão Claude Code — os 136+ agentes, KB e commands estarão disponíveis automaticamente.

### Opção B — Global manual (todos os projetos)

Copia os agentes/kb/commands para `~/.claude/`, ativando em qualquer sessão:

```bash
cd agentcode
cp -r .claude/agents   ~/.claude/
cp -r .claude/commands ~/.claude/
cp -r .claude/kb       ~/.claude/
cp -r .claude/skills   ~/.claude/
```

Para registrar os hooks de mempalace no Claude Code global, adicione em `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/mempalace_setup.sh || true"}]}],
    "Stop":         [{"hooks": [{"type": "command", "command": "command -v mempalace > /dev/null 2>&1 && bash ~/.claude/hooks/mempalace_save.sh || true"}]}],
    "PreCompact":   [{"hooks": [{"type": "command", "command": "command -v mempalace > /dev/null 2>&1 && bash ~/.claude/hooks/mempalace_precompact.sh || true"}]}]
  }
}
```

Copie também os scripts de hook:

```bash
mkdir -p ~/.claude/hooks
cp .claude/hooks/mempalace_*.sh ~/.claude/hooks/
```

### Opção C — Por projeto (este diretório apenas)

O Claude Code carrega `.claude/` automaticamente quando você abre uma sessão dentro do projeto.
Não é necessário instalar nada — basta clonar o repositório e abrir `claude` aqui.

```bash
git clone <repo-url> agentcode
cd agentcode
claude   # agentes e KB carregados automaticamente
```

### Opção D — Copiar para outro projeto

```bash
cp -r .claude /path/to/seu/projeto/
cp -r .codex  /path/to/seu/projeto/   # opcional — suporte Codex
cp -r .cursor /path/to/seu/projeto/   # opcional — suporte Cursor
```

## Key Agents

### Data Engineering (Databricks + Fabric)

### Diagram Generation MCP Servers

| MCP Server | Use for |
|------------|---------|
| `diagrams-mcp-server` | Generating cloud architecture diagrams with official AWS/Azure/GCP icons using mingrammer/diagrams, Mermaid, and PlantUML engines |
| `Draw.io MCP` | Creating and editing diagrams visually via draw.io interface with XML/CSV/Mermaid support |
| `mcp-diagrams` | Alternative for infrastructure and architecture diagrams via MCP with simple commands |

### Data Engineering (Databricks + Fabric)

| Agent | Use for |
|-------|---------|
| `@databricks-sql-expert` | Spark SQL, Unity Catalog, T-SQL, KQL |
| `@databricks-spark-expert` | PySpark, DLT, LakeFlow, Delta Lake |
| `@fabric-pipeline-expert` | Fabric Data Factory, Databricks Jobs |
| `@dbt-fabric-expert` | dbt Core with Databricks/Fabric targets |
| `@semantic-modeler` | DAX, Direct Lake, Databricks Genie |
| `@data-governance-auditor` | Unity Catalog governance, LGPD/GDPR |
| `@data-migration-expert` | SQL Server/PostgreSQL → Databricks/Fabric |
| `@doma-supervisor` | Multi-domain orchestration |
| `@business-analyst` | Requirements extraction from meetings |

### Data Commands

```
/sql      — SQL specialist (Databricks / Fabric / KQL)
/spark    — PySpark and DLT specialist
/pipeline — Pipeline design and orchestration
/workflow — Full DOMA multi-agent orchestration
/party    — Multi-perspective parallel analysis
```

### agentspec Core (58 agents)

workflow, cloud, architect, data-engineering, dev, platform, python, test specialists.
See agentspec documentation for the full list.

### ECC Language Specialists (48 agents)

Language and framework reviewers from ECC, prefixed with `ecc-`.
Examples: `ecc-python-reviewer`, `ecc-typescript-reviewer`, `ecc-code-reviewer`.

### Legal Specialists (14 agents)

| Agent | Use for |
|-------|---------|
| `@maestro` | Multi-agent legal orchestration |
| `@pesquisador-legislativo` | Federal/state/municipal legislation research |
| `@analista-processual` | Case analysis via DataJud |
| `@especialista-civel` | Civil law and procedure |
| `@especialista-trabalhista` | Labor law and procedure |
| `@especialista-criminal` | Criminal law and procedure |
| `@especialista-tributario` | Tax law |
| `@especialista-empresarial` | Corporate/business law |
| `@especialista-constitucional` | Constitutional law |
| `@agente-stf` | STF jurisprudence and procedures |
| `@agente-stj` | STJ jurisprudence and procedures |
| `@agente-tst` | TST jurisprudence and procedures |
| `@validador` | Legal citation validation |
| `@redator` | Legal document drafting |

### Legal Commands

```
/consultar-lei          — Federal legislation query
/pesquisar-jurisprudencia — Court jurisprudence search
/analisar-processo      — Case data analysis
/redigir                — Legal document drafting
/validar                — Citation validation
```

## Updating agentspec Components

```bash
# Dry run first
bash scripts/update-agentspec.sh --dry-run

# Apply
bash scripts/update-agentspec.sh

# Override source path
AGENTSPEC_PATH=/custom/path/agentspec/plugin bash scripts/update-agentspec.sh
```

## Validation

```bash
bash scripts/validate-build.sh
```

Expected output: `✔ Build valid — 119+ agents, 31+ KB domains`

## mempalace Auto-Save

If mempalace is installed (`pip install mempalace` or `uv add mempalace`):
- Session memory is auto-saved on Stop
- Context is compacted before PreCompact events
- No configuration needed — hooks use `command -v mempalace` guard

## Requirements

- Claude Code CLI (claude)
- Bash (for scripts)
- Python 3.8+ (for update script merge logic)
- mempalace (optional — for auto-save hooks)

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
