# SQL Review

## Purpose

Review SQL code for semantic correctness, performance risks, data-quality gaps, and cross-dialect issues. This is the Codex-native port of AgentSpec's `sql-review` command.

Use this for dbt models, warehouse SQL, migration scripts, analytics queries, and SQL embedded in orchestration jobs.

## Primary Role

- reviewer

## Escalation Roles

- sql-optimizer
- dbt-specialist
- data-quality-analyst

## KB Domains

- sql-patterns
- data-quality
- dbt

## Inputs

- SQL file, directory, diff, or PR scope
- target warehouse or dialect when known
- related dbt model metadata, contracts, tests, or lineage notes
- execution plan, row counts, or failure logs when available

## Procedure

### Step 1: Establish Scope

Identify:

- files or query blocks under review
- SQL dialect: Snowflake, BigQuery, Postgres, DuckDB, Spark SQL, Databricks SQL, or unknown
- runtime context: ad hoc query, dbt model, migration, materialized view, pipeline step
- data sensitivity: PII, financial, regulated, or public

### Step 2: Load Local Patterns

Read relevant local KB before reviewing:

- `.agentcodex/kb/sql-patterns/`
- `.agentcodex/kb/data-quality/`
- `.agentcodex/kb/dbt/` when dbt is involved

Use repository conventions and existing models before recommending style changes.

### Step 3: Review Semantic Correctness

Check:

- query grain is explicit and preserved
- joins cannot multiply rows unexpectedly
- filters match the intended time window and population
- null handling is deliberate
- deduplication uses deterministic ordering
- aggregations match the business definition
- window functions partition and order on the right keys

### Step 4: Review Performance

Check:

- `SELECT *` in production paths
- missing partition or date filters
- avoidable full scans
- repeated subqueries or CTEs that should be materialized
- expensive cross joins
- non-sargable predicates
- missing clustering, indexes, or sort keys when applicable
- incremental model guards in dbt

### Step 5: Review Portability And Dialect

Check:

- dialect-specific functions
- timestamp and timezone behavior
- identifier quoting
- boolean and numeric casts
- semi-structured data access syntax
- `QUALIFY`, `MERGE`, `UNNEST`, and window-function differences

### Step 6: Review Data Quality And Governance

Check:

- PII fields are masked, excluded, or justified
- primary keys and uniqueness expectations are testable
- freshness and completeness are covered
- schema changes are backward compatible
- dbt tests or warehouse checks exist for critical assumptions

### Step 7: Produce Findings

Lead with findings ordered by severity.

Each finding must include:

- severity
- file and line when available
- concrete failure mode
- evidence from SQL text
- suggested fix
- affected role or owner

## Outputs

- SQL review report
- severity-ranked findings
- fix suggestions
- test or data-quality gaps
- portability notes
- merge/readiness recommendation

## Quality Gate

- [ ] dialect and runtime context identified or marked unknown
- [ ] semantic correctness reviewed before performance tuning
- [ ] grain and join risks checked
- [ ] data-quality tests reviewed or recommended
- [ ] PII/security implications checked
- [ ] dbt-specific checks included when applicable
- [ ] findings include evidence and concrete fixes
