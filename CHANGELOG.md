# Changelog

All notable changes to agentcode are tracked here.
Format: `[date] agentspec-version | description`

---

## [2026-07-22] — v1.1.0 — Reference Sync + Lessons System + Audit

### Added
- **agentspec v3.2+ sync**: 11 novas skills (6 `sdd-*` por fase, component-model,
  kb-build, github-cr-*), `tools/spec-linter` + `spec-judge`, build autônomo
- **16 skills ECC** (upstream affaan-m/everything-claude-code): python-testing,
  fastapi-patterns, postgres-patterns, api-design, eval-harness, e mais
- **premium-presentations** (bruno-rv, MIT): skill de decks HTML + `/present-*`
- **Sistema LESSON_LEARNED** (portado do data-agents v2.1.0): hooks
  `lesson_timing.sh`/`lesson_capture.sh` (captura em triggers error/slow_op,
  redação de segredos) + `lesson_recall.sh` (injeção no SessionStart) + `/lessons`
- **agentcodex CLI tooling**: 68 scripts + dispatcher — `/preflight`,
  `/databricks-readiness`, `/stack-detect` executáveis
- **KBs de lições reais**: `known-incidents.md` (9 incidentes de produção),
  `kafka-schema-registry-patterns.md`, `terraform-anti-hallucination.md`,
  `project-lessons.md` (19 padrões Python), constituição §11 (TODO-VALIDAR)
- **Hook anti-drift** `sync_context_reminder.sh`: SHIPPED/BUILD_REPORT mais novo
  que CLAUDE.md → pede `/sync-context`
- **/start Step 0**: git init + .gitignore obrigatórios antes de artefatos
- **CI (GitHub Actions)**: validate-build, testes de hooks, bash -n, JSON,
  referências de hooks, gitleaks
- **tests/test_hooks.sh**: suite de regressão (18 cenários)
- **scripts/update-references.sh**: sincronização dos 6 repos de referência

### Fixed (auditoria de segurança/lógica)
- lesson_capture: E2BIG com payloads >128KB perdia lições (input via temp file)
- Layout lessons/{buffer,timing,archive} — miner não re-ingere lixo/duplicatas
- install-global e /start não sobrescrevem mais hooks existentes do usuário
- sync_context_reminder: portabilidade macOS (find/cksum POSIX), caminho saneado
  na reason, guarda de vazio no xargs (falso positivo de drift)
- Redação de segredos na evidência de lições (connection strings, tokens, PEM)

---

## [2026-05-08] — v1.0.0 — Initial Build

### Sources merged

| Source | Version | Components |
|--------|---------|-----------|
| agentspec | 3.2.0 | 58 agents, 25 KB domains, 33 commands, 5 skills, sdd |
| ECC (everything-claude-code) | latest | 48 agents (ecc-*), .codex, .cursor |
| data-agents | latest | 9 adapted agents, 7 KB domains |
| agentcodex | latest | 8 unique KB domains |
| mempalace | latest | 2 hook scripts |

### New in agentcode (AGENTCODE-owned)

**Agents:**
- `agents/data-engineering/databricks-sql-expert.md`
- `agents/data-engineering/databricks-spark-expert.md`
- `agents/data-engineering/fabric-pipeline-expert.md`
- `agents/data-engineering/dbt-fabric-expert.md`
- `agents/data-engineering/doma-supervisor.md`
- `agents/data-engineering/semantic-modeler.md`
- `agents/data-engineering/data-governance-auditor.md`
- `agents/data-engineering/data-migration-expert.md`
- `agents/data-engineering/business-analyst.md`

**Commands:**
- `commands/data/sql.md`
- `commands/data/spark.md`
- `commands/data/pipeline.md`
- `commands/data/workflow.md`
- `commands/data/party.md`

**KB domains:**
- `kb/databricks/` (data-agents)
- `kb/fabric/` (data-agents)
- `kb/governance/` (data-agents)
- `kb/doma-protocol/` (data-agents pipeline-design)
- `kb/semantic-modeling/` (data-agents)
- `kb/migration/` (data-agents)
- `kb/guardrails/` (data-agents constitution)
- `kb/controls/` (agentcodex)
- `kb/foundations/` (agentcodex)
- `kb/integrations/` (agentcodex)
- `kb/metadata/` (agentcodex)
- `kb/operations/` (agentcodex)
- `kb/orchestration/` (agentcodex)
- `kb/patterns/` (agentcodex)
- `kb/platforms/` (agentcodex)

---

## [2026-05-11] — v1.1.0 — Legal specialist agents + KB

### Novo
- **14 agentes jurídicos**: maestro, pesquisador-legislativo, analista-processual, 5 especialistas (civel, trabalhista, criminal, tributario, empresarial, constitucional), agente-stf, agente-stj, agente-tst, validador, redator
- **KB legal**: 4 subdomínios (conceitos, legislacao, jurisprudencia, procedimentos)
- **MCPs jurídicos**: configurações de referência para DataJud, legislação, tribunais, diários
- **Comandos**: `/consultar-lei`, `/pesquisar-jurisprudencia`, `/analisar-processo`

## [2026-05-11] — v1.0.1 — mempalace nativo + bug fixes

### Fixes
- **hooks.json**: Migrado de inline `mempalace save` para scripts `.sh` dedicados (session tracking, auto-mine)
- **mempalace_setup.sh**: Novo — auto-instala mempalace via pip/uv no SessionStart (background, não bloqueia)
- **CLAUDE.md**: Corrigida documentação da integração mempalace (estava incorreta)
- **.agentcode-manifest.json**: Adicionado `mempalace_setup.sh` como AGENTCODE-owned
- **.gitignore**: Adicionado (faltava — mempalace state, __pycache__, etc.)
- **Cross-harness**: Adicionados `.gemini/` e `.kiro/` (mencionados no brainstorm mas ausentes)

---

## Update History

| Date | Action | agentspec version | Notes |
|------|--------|------------------|-------|
| 2026-05-11 | Bug fixes + mempalace nativo | 3.2.0 | hooks, setup, docs |
| 2026-05-08 | Initial build | 3.2.0 | — |

---

To update agentspec components: `bash scripts/update-agentspec.sh`
Add a row to this table after each update.
