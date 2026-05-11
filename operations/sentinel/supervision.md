# Sentinel Supervision

## Purpose

Define the supervision model for Sentinel in production.

## human approval points

- customer-visible remediation
- privilege changes
- environment failover
- automated rollback
- data deletion or quarantine release

## supervision model

- low severity: operator review can be asynchronous
- medium severity: assigned owner must acknowledge
- high severity: on-call plus domain owner review
- critical severity: incident commander approval before high-impact action

## blocked autonomous actions

- deleting production data
- granting new privileged access
- changing customer-visible routing without approval
- suppressing repeated critical alerts without review

## operator override

- define who can override
- define required justification
- define where the override is logged
- define expiry for temporary overrides

## Local Notes

- Sentinel may recommend actions automatically, but execution must respect these approval points
