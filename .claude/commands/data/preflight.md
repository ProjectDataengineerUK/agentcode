# /preflight — Project Readiness Check

Run a stack-aware environment and platform check before entering build or deploy work.
Verifies that the AgentCodex Project Standard blocks are in place and surfaces gaps.

## Usage

```
/preflight
/preflight --profile data-platform
/preflight --profile regulated-enterprise
```

## What This Does

1. **Reads** `.agentcodex/project-standard.json` — loads the 15 mandatory blocks
2. **Scans** the current project directory for each required artifact path
3. **Reports** which blocks are complete, missing, or marked NOT_APPLICABLE
4. **Surfaces** the maturity profile baseline from `.agentcodex/maturity/maturity5-baseline.json`
5. **Delegates** platform-specific checks to `@doma-supervisor`:
   - Databricks: cluster state, Unity Catalog connectivity, job health
   - Fabric: capacity status, workspace permissions, pipeline health

## Project Standard Blocks (15 required)

| Block | Phase | Artifacts |
|-------|-------|----------|
| contexto | define | problem.md, scope.md, stakeholders.md, domain.md, glossary.md |
| arquitetura | design | architecture.md, data-flow.md, system-diagram.md, decisions/ |
| dados | design | sources.md, storage.md, schemas/, models/, transformations/ |
| governanca | design | controls/governance.md, controls/ownership.md, controls/policies.md |
| lineage | design | metadata/lineage.md |
| execucao | build | execution/orchestration.md, execution/jobs/ |
| validacao | build | validation/data-quality.md, validation/rules.md, validation/tests/ |
| **observabilidade** | build | operations/observability/ (alerts, dashboards, logs, metrics) |
| **monitoramento sentinela** | build | operations/sentinel/ (architecture, watchers, analyzers, runbooks) |
| access control | design | security/access-control.md |
| data contracts | design | contracts/compatibility.md, contracts/schema-contracts/ |
| operacao | ship | operations/slas.md, operations/incidents.md |
| deploy | ship | deploy/ci-cd.md, deploy/environments.md |
| custo | ship | operations/cost/cost-model.md |
| compliance | ship | compliance/audit.md, compliance/regulations.md |

## Completion Rule

> **Do not treat the project as complete until all required blocks are implemented or explicitly justified as not applicable.**
> — `.agentcodex/project-standard.json`

## Bootstrap

To scaffold all required artifacts for a new project:
```
/start
```
This copies `.agentcodex/bootstrap/PROJECT_STANDARD_FEATURE/` into your feature directory.

## References

- Standard: `.agentcodex/project-standard.json`
- Maturity: `.agentcodex/maturity/maturity5-baseline.json`
- Scaffold: `.agentcodex/bootstrap/PROJECT_STANDARD_FEATURE/`
- Sentinel KB: `kb/operations/`
