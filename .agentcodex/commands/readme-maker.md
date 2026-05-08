# README Maker

## Purpose

Generate or refresh a project `README.md` from current repo evidence. This is the Codex-native port of AgentSpec's `/readme-maker` procedure.

Use this when a project needs a useful first README, a stale README refresh, or a documentation pass after meaningful product/runtime changes.

## Primary Role

- code-documenter

## Escalation Roles

- codebase-explorer
- reviewer

## Inputs

- target project directory
- optional output path, default `README.md`
- optional style: `minimal` or `comprehensive`
- existing README content, when present
- package/config files such as `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `pom.xml`, or `Makefile`
- docs, tests, examples, and command entrypoints

## Procedure

1. Inspect the existing README first. Preserve accurate human-authored content unless it conflicts with current code or commands.
2. Map project identity from package/config files: name, version, description, license, runtime, entrypoints, and primary commands.
3. Inspect source, tests, examples, and docs to infer the actual product surface. Do not invent features from file names alone.
4. Identify install, run, test, validation, and development commands from executable repo evidence.
5. Draft the README with a quick-start path that a new user can follow without understanding internal architecture first.
6. For `minimal` style, keep only identity, prerequisites, install, usage, tests, and license.
7. For `comprehensive` style, include overview, features, quick start, command reference, architecture, configuration, development, validation, contributing, and license.
8. Verify examples and commands before presenting them as working. If a command was not run, mark it as inferred or documented.
9. Check links and referenced files exist.
10. Leave no placeholders such as `TODO`, `{project}`, or guessed package names.

## Outputs

- updated or proposed `README.md`
- optional README in another requested output path
- concise report listing evidence used, commands verified, commands inferred, and any unresolved documentation gaps

## Quality Gate

- [ ] README reflects current code and documented runtime behavior
- [ ] quick start is concrete and ordered
- [ ] install/test/run commands are verified or explicitly marked as inferred
- [ ] existing accurate content was preserved
- [ ] links and referenced files exist
- [ ] no placeholder text remains
