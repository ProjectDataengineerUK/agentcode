# AgentCodex Project Standard Checklist

Feature: `example-project-standard`

Mark each item only when the corresponding artifact exists and is materially filled.
If a block is not applicable, justify it explicitly in the referenced file.

- [ ] contexto -> `definition/problem.md`
- [ ] arquitetura documentada -> `design/architecture.md`
- [ ] fluxo de dados claro -> `design/data-flow.md`
- [ ] fontes identificadas -> `data/sources.md`
- [ ] schema definido -> `data/schemas/`
- [ ] lineage mapeado -> `metadata/lineage.md`
- [ ] governanca definida -> `controls/governance.md`
- [ ] ownership definido -> `controls/ownership.md`
- [ ] access control definido -> `security/access-control.md`
- [ ] data contracts -> `contracts/compatibility.md` and `contracts/versioning.md`
- [ ] validacao implementada -> `validation/data-quality.md` and `validation/tests/`
- [ ] observabilidade definida -> `operations/observability/metrics.md`
- [ ] alertas definidos -> `operations/observability/alerts.md`
- [ ] monitoramento sentinela definido -> `operations/sentinel/architecture.md`
- [ ] watcher crew definido -> `operations/sentinel/watchers.md`
- [ ] analyzer crew definido -> `operations/sentinel/analyzers.md`
- [ ] interpreter crew definido -> `operations/sentinel/interpreters.md`
- [ ] knowledge layer definida -> `operations/sentinel/knowledge.md`
- [ ] feed de conhecimento por logs definido -> `operations/sentinel/knowledge-feed.md`
- [ ] supervisao humana definida -> `operations/sentinel/supervision.md`
- [ ] quarentena e contencao definidas -> `operations/sentinel/quarantine.md`
- [ ] pipeline executavel -> `execution/pipelines/`
- [ ] execucao -> `execution/orchestration.md` and `execution/schedules.md`
- [ ] integracao documentada -> `integrations/`
- [ ] agentes definidos (se houver) -> `agents/` or `agents/NOT_APPLICABLE.md`
- [ ] kb local criada -> `kb/`
- [ ] deploy definido -> `deploy/environments.md` and `deploy/ci-cd.md`
- [ ] custo estimado -> `operations/cost/cost-model.md`
- [ ] compliance analisado -> `compliance/regulations.md` and `compliance/audit.md`
- [ ] operacao -> `integrations/` and `kb/`
