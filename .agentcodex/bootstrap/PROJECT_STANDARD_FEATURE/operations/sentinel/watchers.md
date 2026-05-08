# Sentinel Watchers

## Purpose

Document the parallel watcher crew for this project.

Required watcher names:

- lambda watcher
- parser watcher
- s3 flow watcher
- pipeline watcher
- quality watcher
- medallion watcher

Additional production watcher scope:

- security watcher
- resource watcher
- environment watcher
- functionality watcher

## Required Watchers

### Lambda Watcher

- monitor: runtime errors, duration, memory, retries, cold-start effects
- evidence sources: [logs, metrics, traces]
- owners: [owner]
- escalation threshold: [threshold]

### Parser Watcher

- monitor: schema mismatch, parse failures, malformed files, contract drift
- evidence sources: [logs, validation outputs]
- owners: [owner]
- escalation threshold: [threshold]

### S3 Flow Watcher

- monitor: expected arrivals, late files, duplicates, empty drops, missing batches
- evidence sources: [storage events, manifests]
- owners: [owner]
- escalation threshold: [threshold]

### Pipeline Watcher

- monitor: failed updates, broken dependencies, schedule misses, stale outputs
- evidence sources: [orchestrator runs, lineage, freshness checks]
- owners: [owner]
- escalation threshold: [threshold]

### Quality Watcher

- monitor: anomalies, failed checks, threshold violations, drift in data quality dimensions
- evidence sources: [quality reports, tests, validation metrics]
- owners: [owner]
- escalation threshold: [threshold]

### Medallion Watcher

- monitor: bronze/silver/gold degradation, blocked promotions, layer-specific contract breaks
- evidence sources: [layer metrics, quality gates, lineage]
- owners: [owner]
- escalation threshold: [threshold]

### Security Watcher

- monitor: auth failures, permission drift, suspicious access, secrets misuse, unsafe changes
- evidence sources: [security logs, audit events, access reviews]
- owners: [owner]
- escalation threshold: [threshold]

### Resource Watcher

- monitor: cpu, memory, storage, queue pressure, concurrency, cost spikes
- evidence sources: [infra metrics, runtime metrics, cost signals]
- owners: [owner]
- escalation threshold: [threshold]

### Environment Watcher

- monitor: prod/stage drift, unhealthy services, deployment regressions, failed rollouts
- evidence sources: [deploy logs, health checks, runtime telemetry]
- owners: [owner]
- escalation threshold: [threshold]

### Functionality Watcher

- monitor: customer-visible failures, feature degradation, core journey breakage, SLA misses
- evidence sources: [synthetic checks, app logs, support evidence, incident traces]
- owners: [owner]
- escalation threshold: [threshold]

## Local Notes

- remove watchers that truly do not apply only with explicit justification
- if the project is not medallion-based, document the alternative layered model explicitly
