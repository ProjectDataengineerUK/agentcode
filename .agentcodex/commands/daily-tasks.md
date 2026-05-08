# Daily Tasks

## Purpose

Record a daily operational snapshot of work completed, work in progress, and backlog items.

Use this when you want a DevOps-style task log that can be reopened later without relying on chat history.

## Primary Role

- workflow-iterator

## Escalation Roles

- planner
- reviewer

## KB Domains

- orchestration
- observability
- governance

## Inputs

- the current date, defaulting to today
- task items marked as done, in progress, or backlog
- optional owner label

## Procedure

1. Run `agentcodex daily-tasks`.
2. Use `--done`, `--in-progress`, and `--backlog` to record individual tasks.
3. Store the daily snapshot in `.agentcodex/history/DAILY_TASKS_YYYY-MM-DD.md`.
4. Keep the file append-friendly and auditable.
5. Move items between sections by re-running the command with the new status.
6. Prefer concise task phrases and exact file references when useful.

## Outputs

- `.agentcodex/history/DAILY_TASKS_YYYY-MM-DD.md`

