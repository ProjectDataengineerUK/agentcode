from __future__ import annotations

from kb_domains import KB_MANAGED_DOMAINS


SOURCE_CATEGORY_DOMAIN_MAP = {
    "agents": "ai-data-engineering",
    "parsing": "ai-data-engineering",
    "vector-db": "rag",
    "ingestion": "orchestration",
    "dbt": "dbt",
    "mcp": "mcp",
    "rag": "rag",
    "governance": "governance",
    "lineage": "lineage",
    "observability": "observability",
    "access-control": "access-control",
    "data-contracts": "data-contracts",
    "azure": "azure",
    "databricks": "databricks",
    "snowflake": "snowflake",
}


def normalize_source_category(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def resolve_source_domain(category: str) -> str:
    normalized = normalize_source_category(category)
    mapped = SOURCE_CATEGORY_DOMAIN_MAP.get(normalized, normalized)
    if mapped in KB_MANAGED_DOMAINS:
        return mapped
    return "ai-data-engineering"
