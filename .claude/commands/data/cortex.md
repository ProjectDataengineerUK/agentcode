---
description: Snowflake Cortex AI — Cortex Analyst (NL→SQL), Cortex Search (RAG), AI_* functions
argument-hint: "[natural language question or task]"
---

You are invoking `@snowflake-cortex-expert` for Cortex AI tasks within Snowflake.

## Request: $ARGUMENTS

### Decision Tree

```
Is this a business metric question? (revenue, orders, customers by X)
  → cortex_analyst with semantic model

Is this searching/finding documents or unstructured data?
  → cortex_search + RAG pattern

Is this classifying, summarizing, or translating rows in a table?
  → AI_CLASSIFY / AI_COMPLETE / AI_TRANSLATE in SQL

Is this about connecting an agent to Snowflake?
  → Snowflake MCP Server configuration

Is this a complex SQL query beyond Cortex Analyst capability?
  → escalate to @snowflake-sql-expert
```

### Security Rules (Always Apply)

1. Trust Score < 0.7 → do not present result, request refinement
2. PII in result → apply `AI_REDACT` before returning
3. MCP SQL → always validate with `validate_mcp_sql()` before executing
4. Role for MCP → least-privilege `MCP_ANALYST_ROLE`, never ACCOUNTADMIN

Read `kb/snowflake/concepts/cortex-analyst.md` and `kb/snowflake/concepts/cortex-search.md` before responding.
