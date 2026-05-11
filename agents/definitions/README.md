# Agent Definitions

Use this directory to define only the agents that are specific to the project.

Baseline expectation:
- one delivery-oriented agent definition when the product has autonomous or semi-autonomous execution
- one monitoring-oriented agent definition when Sentinel is active in production
- one governance-oriented agent definition when approvals, quarantine, or compliance gates are automated

For each project-local agent, capture:
- role and operational goal
- owned signals, files, or workflows
- allowed actions
- blocked actions
- human escalation path

If the product has no project-local agents, keep the justification in `../NOT_APPLICABLE.md` aligned with actual runtime behavior.
