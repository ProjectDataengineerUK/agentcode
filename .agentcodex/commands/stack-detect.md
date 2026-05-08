# Stack Detect Procedure

## Purpose

Codex-native procedure for detecting the real project stack by layer and turning that into specialist and risk guidance.

## Primary Role

- `codebase-explorer`

## Escalation Roles

- `architect`
- `ci-cd-specialist`
- `data-observability-engineer`

## KB Domains

- `ai-data-engineering`
- `observability`
- `orchestration`

## Use When

- the detected stack is shallower than the repo reality
- specialist routing should be grounded in actual repo layers
- the project needs risks listed by interface, backend, IaC, data, governance, AI, and observability planes

## Inputs

- optional target project directory
- optional `--json`

## Procedure

1. Route to `codebase-explorer`.
2. Run `python3 scripts/agentcodex.py stack-detect [target-project-dir] [--json]`.
3. Scan the repo for layer markers across interface/app, backend, IaC, CI/CD, data, governance, AI/LLM, and observability.
4. Record detected components, recommended specialists, and the main risk of each layer.
5. Write the report to `.agentcodex/reports/stack-detect.md`.
6. Persist the machine-readable result to `.agentcodex/state/project-state.json`.
7. Escalate architecture implications to `architect`, pipeline implications to `ci-cd-specialist`, and telemetry implications to `data-observability-engineer`.

## Outputs

- repo-local stack detection report
- layered specialist recommendations
- layered risk inventory in canonical project state
