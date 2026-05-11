# Agent Prompts

Document prompts, guardrails, and output contracts for project-local agents.

Baseline guardrails:
- require evidence-first reasoning from repo-local files or approved runtime logs
- separate observation, diagnosis, recommendation, and action
- require confidence and severity when the agent reports incidents
- require escalation on security, cost-spike, or quarantine conditions
- forbid silent self-approval for high-impact actions

Output contract baseline:
- summary
- evidence references
- risk or confidence
- recommended next action
- required human approver when applicable
