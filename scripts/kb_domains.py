from __future__ import annotations

from pathlib import Path


KB_DOMAIN_PATHS = {
    "dbt": "dbt",
    "spark": "spark",
    "data-quality": "data-quality",
    "data-modeling": "data-modeling",
    "orchestration": "orchestration",
    "aws": "aws",
    "ai-data-engineering": "ai-data-engineering",
    "gcp": "gcp",
    "airflow": "airflow",
    "microsoft-fabric": "microsoft-fabric",
    "lakehouse": "lakehouse",
    "lakeflow": "lakeflow",
    "medallion": "medallion",
    "sql-patterns": "sql-patterns",
    "streaming": "streaming",
    "terraform": "terraform",
    "genai": "genai",
    "rag": "patterns/rag",
    "mcp": "patterns/mcp",
    "governance": "controls/governance",
    "lineage": "metadata/lineage",
    "observability": "operations/observability",
    "access-control": "controls/access-control",
    "data-contracts": "controls/data-contracts",
    "azure": "platforms/azure",
    "databricks": "platforms/databricks",
    "snowflake": "platforms/snowflake",
}

KB_MANAGED_DOMAINS = list(KB_DOMAIN_PATHS.keys())


def parse_simple_yaml_domains(path: Path) -> list[str]:
    domains: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("- id:"):
            domains.append(line.split(":", 1)[1].strip())
    return domains
