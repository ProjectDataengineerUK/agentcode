# Migrate

## Purpose

Plan and execute migration from legacy ETL to a modern data stack. This is the Codex-native port of AgentSpec's `migrate` command.

Use this for stored procedures, SSIS, Informatica, shell ETL, legacy Spark jobs, warehouse scripts, and undocumented batch workflows.

## Primary Role

- dbt-specialist

## Escalation Roles

- spark-engineer
- pipeline-architect
- sql-optimizer
- data-quality-analyst

## KB Domains

- dbt
- spark
- airflow
- sql-patterns
- data-quality
- orchestration

## Inputs

- legacy ETL file, folder, or description
- source and target platforms
- target stack preference: dbt, Spark, Airflow, warehouse SQL, lakehouse, or mixed
- sample inputs and outputs when available
- source-to-target mappings
- current scheduling and dependency information
- known SLAs, quality rules, and reconciliation reports

## Procedure

### Step 1: Inventory Legacy Behavior

Extract:

- inputs and source systems
- outputs and target tables/files
- transformation rules
- joins, filters, deduplication, and aggregations
- stateful behavior and watermarks
- schedules and dependencies
- failure handling and retries
- side effects such as deletes, truncates, grants, or notifications

### Step 2: Classify Migration Target

Choose the primary migration path:

| Legacy Pattern | Preferred Target |
|---|---|
| SQL stored procedure models | dbt models and macros |
| heavy row/column transformations | Spark or warehouse-native SQL |
| orchestration-only workflow | Airflow or project orchestrator |
| file ingestion and bronze/silver/gold | Spark, lakehouse, or medallion pipeline |
| ad hoc warehouse scripts | governed SQL models plus tests |

Document why the target is appropriate.

### Step 3: Map Source To Target

Create a mapping table:

- legacy object
- target object
- transformation owner
- semantic differences
- validation query
- rollout status

### Step 4: Generate Modern Implementation Plan

Produce:

- dbt model layout or Spark job structure
- orchestration DAG or workflow sequence
- data contracts and schemas
- incremental or backfill strategy
- deployment and environment plan
- rollback plan

### Step 5: Build Parity Validation

Define parity checks:

- row counts by partition
- checksums or aggregate comparisons
- null and uniqueness checks
- referential checks
- freshness and completeness checks
- sampling strategy for complex transformations

### Step 6: Plan Cutover

Specify:

- dual-run period
- acceptance thresholds
- stakeholder signoff
- rollback trigger
- final decommission steps

## Outputs

- migration assessment
- source-to-target mapping
- target implementation plan
- generated dbt/Spark/Airflow/SQL artifacts when requested
- parity validation queries
- cutover and rollback plan

## Quality Gate

- [ ] legacy inputs, outputs, schedules, and side effects inventoried
- [ ] target stack decision justified
- [ ] source-to-target mapping complete
- [ ] parity checks defined before cutover
- [ ] rollback plan documented
- [ ] data-quality and freshness checks included
- [ ] migration risks and unresolved assumptions explicit
