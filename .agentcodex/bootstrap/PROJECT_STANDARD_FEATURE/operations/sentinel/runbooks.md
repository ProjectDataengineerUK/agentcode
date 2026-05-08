# Sentinel Runbooks

## Purpose

Document the operating model for Sentinel monitoring in this project.

## Core Concepts

- event-driven state: each alert or diagnosis starts from explicit runtime events
- autonomous agent team: watcher, analyzer, and interpreter roles are separable
- role + goal + tools: every monitoring unit must declare its bounded function and evidence sources
- escalation path: define who is paged or informed at each severity level

## Minimum Runbook

- detection path: watcher -> analyzer -> interpreter
- decision path: who can acknowledge, suppress, escalate, or close
- evidence path: where raw signals, reports, and summaries are stored
- rollback path: what to do if the diagnosis is wrong or incomplete

## Escalation Path

- severity low: [owner]
- severity medium: [owner]
- severity high: [owner]
- severity critical: [owner]

## Local Notes

- tie this runbook to `operations/observability/alerts.md` and `controls/ownership.md`
