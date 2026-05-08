# Create PR

## Purpose

Prepare a pull request with conventional commit naming, structured description, and explicit test evidence. This is the Codex-native port of AgentSpec's `create-pr` command.

This procedure prepares and validates the PR flow. Do not commit, push, or create a GitHub PR without explicit user approval.

## Primary Role

- reviewer

## Escalation Roles

- doc-updater
- security-reviewer

## Inputs

- current git diff and branch state
- related workflow artifacts when available
- test commands and results
- optional PR title, draft flag, or review flag

## Procedure

### Step 1: Inspect Repository State

Run read-only checks first:

```bash
git status --short
git branch --show-current
git diff --stat
git log origin/main..HEAD --oneline
```

If `origin/main` is unavailable, identify the appropriate base branch before continuing.

### Step 2: Categorize Changes

Classify the primary PR type:

| Type | Use When |
|---|---|
| `feat` | new capability or user-visible behavior |
| `fix` | bug fix or correction |
| `refactor` | structure change without intended behavior change |
| `docs` | documentation or generated report changes |
| `test` | test-only additions or corrections |
| `chore` | packaging, build, generated metadata, maintenance |
| `ci` | workflow and automation changes |
| `perf` | measurable performance change |

Choose a scope from the dominant area: `workflow`, `commands`, `kb`, `cli`, `plugin`, `docs`, `memory`, `security`, `data`, `tests`, or a project-specific module.

### Step 3: Review Before PR

If `--review` is requested or the change touches security, migrations, workflow validation, install/sync, or generated runtime assets:

1. Run local tests and validation.
2. Run `review` procedure for code risks.
3. Optionally run `judge` on high-stakes files when `OPENROUTER_API_KEY` is configured.
4. Stop on critical findings.
5. Ask the user before proceeding when errors remain but may be acceptable.

### Step 4: Draft Conventional Commit

Format:

```text
<type>(<scope>): <short description>

- what changed
- why it changed
- validation performed
```

Keep the subject under 72 characters when possible.

### Step 5: Draft PR Description

Use:

```markdown
## Summary

- ...

## Key Changes

- ...

## Files Changed

| Category | Files | Description |
|---|---:|---|
| ... | ... | ... |

## Test Plan

- [ ] ...

## Breaking Changes

None / ...

## Related Issues

None / Closes #...

## Residual Risk

- ...
```

### Step 6: Confirm Before Mutating Git

Before running any mutating command, show:

- branch name
- commit message
- PR title
- PR body summary
- test evidence
- residual risks

Ask for explicit approval before:

```bash
git checkout -b ...
git add ...
git commit ...
git push ...
gh pr create ...
```

### Step 7: Create PR After Approval

After approval, use non-interactive commands where possible:

```bash
git push -u origin <branch>
gh pr create --title "<title>" --body-file <body-file> --base main
```

For draft PRs:

```bash
gh pr create --draft --title "<title>" --body-file <body-file> --base main
```

## Outputs

- recommended branch name
- conventional commit message
- PR title
- PR body
- test plan
- residual risk summary
- PR URL if creation is approved and succeeds

## Quality Gate

- [ ] repository state inspected
- [ ] PR type and scope justified
- [ ] tests and validations recorded
- [ ] breaking changes documented
- [ ] residual risk documented
- [ ] user approved mutating git/GitHub commands
- [ ] PR body explains why, not only what
