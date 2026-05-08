# Lakehouse

## Purpose

Design or review lakehouse table format, catalog, governance, and operations decisions. This is the Codex-native port of AgentSpec's `lakehouse` command.

Use this for Iceberg, Delta Lake, Unity Catalog, Polaris, Nessie, OneLake, Databricks, open table format migrations, and table maintenance strategy.

## Primary Role

- lakehouse-architect

## Escalation Roles

- data-platform-engineer
- spark-engineer
- metadata-platform-engineer

## KB Domains

- lakehouse
- spark
- databricks
- microsoft-fabric
- aws
- gcp

## Inputs

- lakehouse question or design request
- current platform and cloud
- target table format or catalog when known
- source/target table patterns
- workload type: batch, streaming, CDC, BI, ML, or mixed
- governance requirements: access control, lineage, retention, compliance

## Procedure

### Step 1: Classify The Lakehouse Decision

Classify the request as one or more:

- table format selection
- catalog and namespace design
- migration from Hive, Parquet, warehouse tables, or proprietary formats
- medallion/layering design
- Spark read/write optimization
- compaction, vacuum, clustering, Z-ordering, or maintenance
- governance and access-control design
- cross-platform interoperability

### Step 2: Load KB And Platform Context

Read:

- `.agentcodex/kb/lakehouse/`
- `.agentcodex/kb/spark/` when Spark is involved
- `.agentcodex/kb/platforms/databricks/` or `.agentcodex/kb/platforms/azure/` when applicable
- cloud KB for AWS/GCP/Fabric when applicable

Inspect existing project files for table format, catalog, and orchestration conventions before proposing a new pattern.

### Step 3: Recommend Architecture

Produce a recommendation covering:

- table format: Iceberg, Delta, Hudi, native warehouse table, or not applicable
- catalog: Unity Catalog, Glue, Polaris, Nessie, Hive Metastore, OneLake/Fabric, or warehouse-native
- namespace and ownership model
- storage layout and partitioning
- schema evolution policy
- retention and cleanup policy
- read/write engine compatibility

### Step 4: Define Operational Controls

Include:

- compaction strategy
- small-file mitigation
- vacuum/expiration policy
- checkpoint and metadata maintenance
- monitoring and freshness checks
- rollback and disaster recovery
- access-control and lineage expectations

### Step 5: Produce Implementation Artifacts

When useful, generate:

- table DDL
- catalog configuration
- Spark or SQL read/write examples
- migration sequence
- validation queries
- operations runbook

## Outputs

- lakehouse decision record
- recommended format and catalog
- table and namespace design
- migration or implementation plan
- maintenance runbook
- risks and tradeoffs

## Quality Gate

- [ ] platform and workload context identified
- [ ] table format recommendation includes tradeoffs
- [ ] catalog/governance model specified
- [ ] partition/schema evolution strategy documented
- [ ] maintenance and rollback covered
- [ ] Spark or engine-specific constraints considered
- [ ] validation queries or checks included when implementing
