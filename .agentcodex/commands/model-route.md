# model-route

## Purpose

Choose the Codex model tier for the current task and persist the automatic selection.

## Primary Role

- workflow-designer

Use this as the native token and model routing gate for AgentCodex workflows.

## Inputs

- Task description.
- Optional `--activity`, `--role`, `--budget`, `--risk`, and `--json`.

## Procedure

1. Load `.agentcodex/model-routing.json`.
2. Prefer explicit activity, then specialist role mapping, then keyword inference.
3. Escalate or downgrade by risk, budget, and context pressure.
4. Write the selected tier, model, effort, and reason to `.agentcodex/reports/model-routing/`.

## Outputs

- Latest JSON selection report.
- Latest Markdown selection report.
- Selected model summary on stdout.
