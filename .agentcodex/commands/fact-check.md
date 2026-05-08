# Fact Check

## Purpose

Verify factual claims in a document against the current codebase, command output, or git history, and correct inaccuracies when editing is requested.

## Primary Role

- reviewer

## Escalation Roles

- codebase-explorer
- code-documenter

## Inputs

- target markdown, HTML, plan, report, or documentation file
- referenced source files, commands, git refs, or workflow artifacts
- optional correction mode: report-only or edit-in-place

## Procedure

1. Read the target document in full.
2. Extract verifiable claims: numbers, file paths, function names, module names, behavior descriptions, architecture claims, and timeline statements.
3. Verify each claim against files, tests, command output, or git history.
4. Classify claims as confirmed, corrected, or unverifiable.
5. In report-only mode, write a verification summary without editing the target.
6. In edit-in-place mode, make surgical corrections while preserving the document's structure and visual layout.
7. Append or insert a verification summary with counts and notable corrections.

## Outputs

- verification summary
- corrected document when edit-in-place is requested
- list of unverifiable claims

## Quality Gate

- [ ] subjective opinions are not rewritten as factual corrections
- [ ] every correction cites source evidence
- [ ] document structure is preserved
- [ ] unverifiable claims remain visible
- [ ] sensitive or external claims are not guessed
