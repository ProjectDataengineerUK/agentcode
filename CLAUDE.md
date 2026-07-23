# agentcode — Unified Claude Code Agent Plugin

agentcode is a Claude Code plugin that fuses agentspec + ECC + data-agents + agentcodex + mempalace
into a single installable plugin providing 117+ agents, 40+ KB domains, and cross-harness support
for Claude Code, Cursor, and Codex.

---

## REGRAS INVIOLÁVEIS — Ler Antes de Qualquer Ação

> Estas regras têm origem em incidentes reais com consequências sérias. Prioridade máxima.

### Protocolo de Início de Sessão

**ANTES de qualquer ação técnica** (código, deploy, terraform, schema, execução de job):

```
1. Ler memory/MEMORY.md (ou equivalente no projeto)
2. Declarar ao usuário: o que já foi feito, o que está pendente, qual o estado atual
3. Ações irreversíveis → confirmar com usuário mesmo que memória diga "pendente"
4. Sem memória disponível → perguntar o estado antes de prosseguir
```

**Por quê:** Terraform apply foi executado sem verificar memórias → infraestrutura destruída.

### Verificação de Execução (Anti Re-execução Cega)

**ANTES de recomendar executar qualquer job, pipeline ou processo:**

```bash
# GCP Cloud Run Jobs:
gcloud run jobs executions list --project {PROJECT_ID} --region {REGION} --limit 50

# Databricks:
SELECT job_name, status, start_time FROM system.lakeflow.job_run_timeline
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL 7 DAYS ORDER BY start_time DESC;

# Airflow: airflow dags list-runs -d {dag_id} --limit 10
```

**Só recomendar execução se:** última execução falhou, dados desatualizados além do SLO, ou nunca rodou.

**Por quê:** Jobs Social, Emendas e Sanções foram declarados como "precisam rodar" quando já tinham sido executados com sucesso em 2026-05-07.

> Detalhes completos: `kb/guardrails/constitution.md` §9 e §10

### Honestidade Técnica (TODO-VALIDAR)

Incerteza técnica é sinalizada com `TODO-VALIDAR` **na linha exata** — nunca escondida,
nunca em aviso genérico. Fórmulas determinísticas públicas não levam TODO. Evidência
verificada que contraria preferência do usuário é apresentada, nunca contornada em silêncio.

> Detalhes: `kb/guardrails/constitution.md` §11 · Terraform: `kb/guardrails/terraform-anti-hallucination.md` · Incidentes conhecidos: `kb/databricks/patterns/known-incidents.md` · Lições Python/FastAPI/SQLAlchemy/LangChain: `kb/python/patterns/project-lessons.md`

---

## Mandatory Project Standard

**Every project built with agentcode must satisfy the AgentCodex Project Standard.**
See `.agentcodex/project-standard.json` — 15 required blocks across define/design/build/ship phases.

> Do not treat the project as complete until all required blocks are implemented or explicitly justified as not applicable.

Run `/preflight` at any time to check which blocks are complete or missing.
Run `/start` to scaffold all required artifacts for a new project.

### Required Blocks

| Phase | Block |
|-------|-------|
| define | contexto (problem, scope, stakeholders, domain, glossary) |
| design | arquitetura, dados, governanca, lineage, access control, data contracts |
| build | execucao, validacao, **observabilidade**, **monitoramento sentinela** |
| ship | operacao, deploy, custo, compliance |

For high DataOps + LLMOps maturity projects, start from `.agentcodex/maturity/maturity5-baseline.json`.

## Plugin Structure

```
.claude/
├── agents/
│   ├── architect/        (8 — agentspec OWNED)
│   ├── cloud/            (10 — agentspec OWNED)
│   ├── data-engineering/ (24 — 15 agentspec + 9 agentcode extensions)
│   ├── dev/              (5 — 4 agentspec OWNED + interview-coach AGENTCODE)
│   ├── platform/         (6 — agentspec OWNED)
│   ├── python/           (6 — agentspec OWNED)
│   ├── test/             (3 — agentspec OWNED)
│   ├── workflow/         (6 — agentspec OWNED)
│   ├── languages/        (46 — ECC agents, ecc- prefixed, AGENTCODE)
│   ├── security/         (2 — ECC security agents, AGENTCODE)
│   └── legal/            (14 — legal specialist agents, AGENTCODE)
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
│   ├── platforms/              (AGENTCODE — agentcodex)
│   ├── snowflake/              (AGENTCODE — Snowflake KB domain)
│   └── legal/                  (AGENTCODE — legal KB domain)
├── commands/
│   ├── [6 agentspec subdirs]   (OWNED)
│   ├── data/                   (AGENTCODE — 7 data commands)
│   └── legal/                  (AGENTCODE — 5 legal commands)
├── skills/         (33 — 16 agentspec OWNED + 16 ECC AGENTCODE: python-testing, fastapi-patterns,
│                    postgres-patterns, api-design, backend-patterns, database-migrations, docker-patterns,
│                    tdd-workflow, verification-loop, error-handling, security-review, deployment-patterns,
│                    eval-harness, cost-aware-llm-pipeline, mcp-server-patterns, python-patterns
│                    + premium-presentations AGENTCODE: decks HTML completos com temas, Mermaid,
│                    presenter mode, export PDF/OG cover — comandos /present-* em commands/presentation/)
├── tools/          (spec-linter + spec-judge — agentspec OWNED)
├── sdd/            (agentspec OWNED)
└── hooks/
    ├── hooks.json             (MERGED: agentspec base + mempalace)
    ├── hooks-agentspec-base.json  (base for update re-merge)
    ├── mempalace_setup.sh     (AGENTCODE — auto-install via pip/uv)
    ├── mempalace_save.sh      (AGENTCODE — periodic save every 15 exchanges)
    └── mempalace_precompact.sh (AGENTCODE — emergency save before compaction)
```

## Data Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/sql` | `@databricks-sql-expert` | Databricks SQL / Fabric T-SQL / KQL |
| `/spark` | `@databricks-spark-expert` | PySpark, DLT, LakeFlow |
| `/snowflake` | `@snowflake-*` specialists | Snowflake pipelines, SQL, governance, cost |
| `/cortex` | `@snowflake-cortex-expert` | Cortex Analyst (NL→SQL), Cortex Search, AI_* |
| `/pipeline` | `@fabric-pipeline-expert` | Pipeline design and orchestration |
| `/workflow` | `@doma-supervisor` | Multi-domain DOMA orchestration |
| `/party` | `@doma-supervisor` | Multi-perspective parallel analysis |
| `/preflight` | `@doma-supervisor` | Project standard readiness check (15 blocks) |

## AgentCodex Framework (.agentcodex/)

The `.agentcodex/` directory contains the AgentCodex project management framework:

```
.agentcodex/
├── project-standard.json          ← 15 mandatory blocks (THE COMPLETION RULE)
├── maturity/maturity5-baseline.json  ← DataOps + LLMOps maturity profiles
├── bootstrap/
│   ├── PROJECT_STANDARD_FEATURE/  ← Full project scaffold (copy per feature)
│   └── MATURITY_PROFILE_OVERLAYS/ ← data-platform, agentic-llm, regulated-enterprise
├── commands/                      ← 47 agentcodex procedure commands
├── templates/                     ← 19 artifact templates
├── roles/roles.yaml               ← Agent role → KB domain mapping
├── routing/routing.json           ← Workflow phase routing rules
├── observability/integrations/    ← OpenTelemetry, Phoenix, Langfuse targets
└── registry/                      ← Domain, source, and schema registry
```

### AgentCodex CLI Tooling

The `.agentcodex/commands/*.md` procedures execute via the Python dispatcher
(synced from upstream ProjectDataengineerUK/agentcodex — 68 scripts, stdlib-only):

```bash
python3 scripts/agentcodex.py preflight [dir]             # 15-block readiness check
python3 scripts/agentcodex.py databricks-readiness [dir]  # env/bundles/apps/governance/jobs/boundary
python3 scripts/agentcodex.py stack-detect [dir]          # detect project stack
python3 scripts/agentcodex.py start                       # scaffold + maturity report
python3 scripts/agentcodex.py                             # full usage (64 commands)
```

Reports land in `.agentcodex/reports/`, canonical state in `.agentcodex/state/project-state.json`.

### Sentinel System

The AgentCodex Project Standard requires a **Sentinel monitoring layer** in every project:

- **Watcher crew**: pipeline watcher, quality watcher, freshness watcher, medallion watcher
- **Analyzer crew**: z-score detector, trend regressor, pattern matcher, diff analyzer
- **Interpreter crew**: context builder, genai interpreter, reporter, dispatcher
- **Knowledge layer**: explanations, suggested actions, severity, confidence, KB auto-update

See `kb/operations/observability/observability-baseline.md` and scaffold at `.agentcodex/bootstrap/PROJECT_STANDARD_FEATURE/operations/sentinel/`.

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

## mempalace Integration (nativo)

O mempalace é **auto-instalado** na primeira sessão via SessionStart hook:

| Hook | Script | Função |
|------|--------|--------|
| `SessionStart` | `mempalace_setup.sh` | Auto-instala via pip/uv (background, não bloqueia) |
| `Stop` | `mempalace_save.sh` | Salva memória a cada 15 trocas + auto-mine do transcript + mina lições capturadas |
| `PreCompact` | `mempalace_precompact.sh` | Salva ANTES da compactação de contexto |
| `PreToolUse` | `lesson_timing.sh` | Registra t0 de cada tool call (detecção de slow_op) |
| `PostToolUse` | `lesson_capture.sh` | LESSON_LEARNED (portado do data-agents v2.1.0): captura lições em triggers `error`/`slow_op` para `~/.mempalace/lessons/`, cap de 50/sessão |
| `Stop` | `sync_context_reminder.sh` | Detecta drift: SHIPPED/BUILD_REPORT mais novo que CLAUDE.md → pede `/sync-context` (1x por artefato) |
| `SessionStart` | `lesson_recall.sh` | Injeta as lições recentes (30d, dedup, recorrentes primeiro) como contexto — funciona sem mempalace |

Comandos relacionados: `/lessons` (ver/gerenciar lições), `/health` (auto-diagnóstico do plugin),
`/kb-search` (busca nos KBs). Manutenção: `scripts/update-references.sh [--pull]` sincroniza os
6 repos de referência; `tests/test_hooks.sh` roda a regressão dos hooks (também no CI).

**Auto-install**: tenta `uv pip install mempalace` → `pip3 install mempalace` → `pip install mempalace`. Falha silenciosa se não houver Python/pip — hooks continuam funcionando sem memória.

**Verificação**: `command -v mempalace > /dev/null 2>&1` guarda todos os hooks.

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
