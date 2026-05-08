# Share

## Purpose

Share or publish a generated visual artifact only after explicit approval. This is the Codex-native, safety-constrained port of AgentSpec's visual explainer `share` command.

## Primary Role

- code-documenter

## Escalation Roles

- reviewer
- security-reviewer

## Inputs

- local HTML artifact path
- target publishing mechanism, if approved
- explicit user approval for any public upload or deployment

## Procedure

1. Confirm the artifact exists and is the intended file.
2. Inspect the artifact for secrets, customer data, private paths, tokens, internal URLs, and sensitive screenshots.
3. If any sensitive material exists, stop and report the issue.
4. Ask for explicit approval before running any command that uploads or deploys externally.
5. Prefer repo-local or filesystem sharing when public deployment is not required.
6. If an external publisher is approved, record the command used, destination URL, retention assumptions, and rollback/removal path.
7. Save the sharing record under `.agentcodex/reports/visual/` when relevant.

## Outputs

- local artifact path or approved public URL
- sharing record with command, destination, and removal notes
- sensitivity review result

## Quality Gate

- [ ] external upload was explicitly approved
- [ ] artifact was checked for sensitive data
- [ ] destination and retention are documented
- [ ] rollback or removal path is known
- [ ] local path remains available for future review
