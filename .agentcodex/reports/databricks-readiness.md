# Databricks Readiness Report

- generated_at: 2026-07-22T23:23:19.261331+00:00
- target_root: /home/jonatas/Projetos/agentcode

## environment

- status: warn

- databricks-cli: pass - databricks CLI found in PATH
- databricks-host: warn - DATABRICKS_HOST is not set
- databricks-auth: warn - Databricks token or OAuth client variables not found

## bundles

- status: warn

- bundle-file: warn - databricks.yml or bundle.yml not found

## apps

- status: warn

- app-manifest: warn - app.yaml not found

## governance

- status: warn

- uc-three-level-names: warn - no explicit catalog.schema.object reference found
- uc-parent-grants: warn - no clear USE CATALOG and USE SCHEMA grant hints found
- uc-volumes-vs-dbfs: pass - no DBFS-first anti-pattern detected

## jobs

- status: warn

- jobs-resources: warn - no Databricks resource yml files found for jobs review

## boundary

- status: warn

- governance-runtime-boundary: pass - no obvious governance/runtime mixing detected in resource files
- runtime-principal-explicit: warn - no explicit runtime principal marker found
