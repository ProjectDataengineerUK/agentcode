# agentcode — Unified Claude Code Agent Plugin

agentcode is a Claude Code plugin that fuses agentspec + ECC + data-agents + agentcodex + mempalace
into a single installable plugin providing 119+ agents, 31+ KB domains, and cross-harness support
for Claude Code, Cursor, and Codex.

## Plugin Structure

```
.claude/
├── agents/
│   ├── architect/        (8 — agentspec OWNED)
│   ├── cloud/            (10 — agentspec OWNED)
│   ├── data-engineering/ (24 — 15 agentspec + 9 agentcode extensions)
│   ├── dev/              (4 — agentspec OWNED)
│   ├── platform/         (6 — agentspec OWNED)
│   ├── python/           (6 — agentspec OWNED)
│   ├── test/             (3 — agentspec OWNED)
│   ├── workflow/         (6 — agentspec OWNED)
│   ├── languages/        (46 — ECC agents, ecc- prefixed, AGENTCODE)
│   └── security/         (2 — ECC security agents, AGENTCODE)
├── kb/
│   ├── [25 agentspec domains]  (OWNED)
│   ├── databricks/             (AGENTCODE — data-agents)
│   ├── fabric/                 (AGENTCODE — data-agents)
│   ├── governance/             (AGENTCODE — data-agents)
│   ├── doma-protocol/          (AGENTCODE — data-agents pipeline-design)
│   ├── semantic-modeling/      (AGENTCODE — data-agents)
│   ├── migration/              (AGENTCODE — data-agents)
│   ├── guardrails/             (AGENTCODE — constitution)
│   ├── controls/               (AGENTCODE — agentcodex)
│   ├── foundations/            (AGENTCODE — agentcodex)
│   ├── integrations/           (AGENTCODE — agentcodex)
│   ├── metadata/               (AGENTCODE — agentcodex)
│   ├── operations/             (AGENTCODE — agentcodex)
│   ├── orchestration/          (AGENTCODE — agentcodex)
│   ├── patterns/               (AGENTCODE — agentcodex)
│   └── platforms/              (AGENTCODE — agentcodex)
├── commands/
│   ├── [6 agentspec subdirs]   (OWNED)
│   └── data/                   (AGENTCODE — 5 data commands)
├── skills/         (5 — agentspec OWNED)
├── sdd/            (agentspec OWNED)
└── hooks/
    ├── hooks.json             (MERGED: agentspec base + mempalace)
    ├── hooks-agentspec-base.json  (base for update re-merge)
    ├── mempalace_save.sh      (AGENTCODE — mempalace)
    └── mempalace_precompact.sh (AGENTCODE — mempalace)
```

## Data Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/sql` | `@databricks-sql-expert` | Databricks SQL / Fabric T-SQL / KQL |
| `/spark` | `@databricks-spark-expert` | PySpark, DLT, LakeFlow |
| `/pipeline` | `@fabric-pipeline-expert` | Pipeline design and orchestration |
| `/workflow` | `@doma-supervisor` | Multi-domain DOMA orchestration |
| `/party` | `@doma-supervisor` | Multi-perspective parallel analysis |

## Updating agentspec Components

When agentspec releases a new version:

```bash
# Preview changes (safe)
AGENTSPEC_PATH=/path/to/agentspec/plugin bash scripts/update-agentspec.sh --dry-run

# Apply update
AGENTSPEC_PATH=/path/to/agentspec/plugin bash scripts/update-agentspec.sh
```

The update script only touches `AGENTSPEC_OWNED` directories and files.
It never modifies `agents/languages/`, `agents/security/`, `kb/databricks/`, `kb/fabric/`,
or any other AGENTCODE-owned path.

## Ownership Rules

| Prefix | Owner | Safe to update? |
|--------|-------|----------------|
| OWNED | agentspec | Yes — `update-agentspec.sh` handles it |
| AGENTCODE | agentcode extensions | Never — script skips these |
| SHARED | agents/data-engineering/ | Partial — only agentspec files updated |

## mempalace Integration

If `mempalace` is installed (`command -v mempalace`):
- `hooks/hooks.json` auto-runs `mempalace_save.sh` on session Stop
- `hooks/hooks.json` auto-runs `mempalace_precompact.sh` on PreCompact
- If mempalace is not installed, hooks exit silently (no error)

## Cross-Harness Support

- **Cursor IDE**: `.cursor/` rules, hooks, and skills from ECC
- **Codex**: `.codex/` AGENTS.md and configuration from ECC

## DOMA Protocol

Data engineering agents follow the DOMA (Domain-Oriented Multi-Agent) protocol:
1. **KB-First**: Read relevant KB domain before generating code
2. **Platform isolation**: Never mix Databricks and Fabric operations
3. **Confidence scoring**: Surface uncertainty before high-stakes operations
4. **Provenance**: Every response includes KB source and confidence score

See `kb/doma-protocol/index.md` and `kb/guardrails/constitution.md`.
