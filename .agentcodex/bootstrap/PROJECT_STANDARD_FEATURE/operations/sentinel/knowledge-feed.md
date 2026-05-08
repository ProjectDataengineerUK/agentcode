# Sentinel Knowledge Feed

## Purpose

Define how production logs feed the knowledge base and memory surfaces used by Sentinel and other agents.

## log sources

- application logs
- pipeline and scheduler logs
- security and access audit logs
- infrastructure and resource logs
- feature-health and synthetic monitoring logs
- sentinel-generated diagnostic logs

## knowledge extraction rules

- extract only stable, reviewable operational knowledge
- separate facts from inferred diagnosis
- group repeated incidents into patterns before proposing KB updates
- preserve correlation keys, timestamps, severity, and affected scope

## review before kb update

- every KB update candidate must be reviewed before entering the authoritative KB
- critical incidents require owner review before pattern promotion
- low-confidence interpretation should remain in candidate memory, not final KB

## memory candidate flow

- logs -> observability summaries -> memory candidates -> review -> approve -> ingest
- store raw evidence separately from curated knowledge
- keep references to the source log files or run reports

## Local Notes

- do not let production log ingestion silently write into final KB pages
- use repo-local artifacts to keep the learning loop auditable
