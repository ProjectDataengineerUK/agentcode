# Model Policy

## Allowed Models

- economy: `gpt-5.4-mini` for status, exploration, deterministic summaries, and low-risk documentation
- coding: `gpt-5.3-codex` for implementation, tests, command work, and bounded refactors
- balanced: `gpt-5.4` for brainstorm, define, design, domain synthesis, and standard review
- frontier: `gpt-5.5` for high-risk security, compliance, production, migration, and architecture arbitration

## Activity Routing

- brainstorm, define, and design use balanced by default and escalate to frontier for high risk
- implementation uses coding by default and escalates to frontier for high risk
- status and exploration use economy unless risk is elevated
- judge and security use frontier by default

## Token Budget

- compact before expanding when context status is warning or critical
- retrieve repo-local context before adding broad chat history
- prefer summaries and file references over copying large artifacts into prompts
- record every automatic model selection for audit

## Governance

- approval owner: platform or agentic runtime owner
- change process: update `.agentcodex/model-routing.json`, run validation, and preserve report evidence
- deprecation policy: remove models from the policy only after replacement tier and fallback are documented
- audit path: `.agentcodex/reports/model-routing/`
