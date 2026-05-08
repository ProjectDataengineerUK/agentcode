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

**Total: 119+ agents, 31+ KB domains**

## Installation

### As a Claude Code plugin

```bash
cd agentcode
claude plugin install .
```

### Manual (copy to project)

```bash
cp -r .claude /path/to/your/project/
cp -r .codex /path/to/your/project/   # optional — Codex support
cp -r .cursor /path/to/your/project/  # optional — Cursor support
```

## Key Agents

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
