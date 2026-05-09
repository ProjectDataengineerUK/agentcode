---
description: Snowflake data engineering — pipeline design, SQL, governance, and cost optimization
argument-hint: "[task description]"
---

Invoke the appropriate Snowflake specialist agent based on the task:

- **Pipeline / Dynamic Tables / Iceberg / Snowpipe** → `@snowflake-data-engineer`
- **SQL writing / VARIANT / Query Profile / Snowpark** → `@snowflake-sql-expert`
- **Cortex Analyst / Cortex Search / AI_* functions / MCP** → `@snowflake-cortex-expert`
- **RBAC / Masking Policies / RLS / Trust Center** → `@snowflake-governance-expert`
- **Credit analysis / warehouse sizing / cost** → `@snowflake-cost-optimizer`

## Task: $ARGUMENTS

Analyze the task and route to the correct specialist. If the task spans multiple domains, 
coordinate in sequence: data-engineer → sql-expert → governance-expert.

All specialists follow KB-First Protocol — read `kb/snowflake/index.md` before generating code.
