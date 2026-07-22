#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ROLES_DOCS = ROOT / "docs" / "roles"
ROLES_MANIFEST = ROOT / ".agentcodex" / "roles" / "roles.yaml"


ROLE_KB_MAP = {
    "workflow-brainstormer": [],
    "workflow-definer": [],
    "workflow-designer": ["orchestration", "data-modeling"],
    "workflow-builder": [],
    "workflow-shipper": [],
    "workflow-iterator": [],
    "code-reviewer": [],
    "codebase-explorer": [],
    "context-optimizer": [],
    "build-error-resolver": [],
    "architect": [],
    "docs-lookup": [],
    "code-architect": [],
    "code-documenter": [],
    "doc-updater": [],
    "llm-specialist": ["genai", "ai-data-engineering"],
    "performance-optimizer": [],
    "pr-test-analyzer": [],
    "prompt-crafter": [],
    "python-developer": [],
    "kb-architect": [],
    "meeting-analyst": ["orchestration", "data-modeling", "data-quality"],
    "metadata-platform-engineer": ["lineage", "governance", "data-contracts"],
    "lineage-analyst": ["lineage", "orchestration", "data-contracts", "observability"],
    "memory-architect": ["genai", "ai-data-engineering", "mcp", "rag"],
    "memory-governance-engineer": ["governance", "access-control", "data-contracts", "observability"],
    "memory-observability-engineer": ["observability", "genai", "ai-data-engineering", "governance"],
    "sentinel-supervisor": ["observability", "governance", "access-control", "lineage"],
    "sentinel-runtime-watcher": ["observability", "orchestration", "data-quality", "lineage"],
    "sentinel-security-watcher": ["access-control", "governance", "observability"],
    "sentinel-analyzer": ["observability", "lineage", "data-quality"],
    "sentinel-interpreter": ["observability", "governance", "lineage", "ai-data-engineering"],
    "planner": [],
    "pipeline-architect": ["orchestration", "airflow"],
    "platform-access-engineer": ["access-control", "governance"],
    "airflow-specialist": ["airflow", "orchestration"],
    "ai-data-engineer": ["ai-data-engineering", "data-quality", "streaming"],
    "azure-ai-architect": ["azure", "rag", "mcp", "ai-data-engineering", "observability"],
    "data-governance-architect": ["governance", "access-control", "data-contracts", "lineage", "observability"],
    "data-observability-engineer": ["observability", "data-quality", "orchestration", "lineage", "ai-data-engineering"],
    "business-monitor": ["observability", "data-quality", "orchestration"],
    "data-platform-engineer": ["aws", "gcp", "lakehouse", "medallion", "terraform", "microsoft-fabric"],
    "data-security-architect": ["access-control", "governance", "observability", "azure", "databricks", "snowflake"],
    "databricks-architect": ["databricks", "lakehouse", "medallion", "spark", "governance"],
    "aws-data-architect": ["aws", "terraform", "data-quality"],
    "data-contracts-engineer": ["data-quality", "data-modeling"],
    "mosaic-ai-engineer": ["databricks", "rag", "ai-data-engineering", "observability", "data-contracts"],
    "gcp-data-architect": ["gcp", "terraform", "data-quality", "streaming"],
    "fabric-architect": ["microsoft-fabric", "lakehouse", "medallion"],
    "lakeflow-architect": ["lakeflow", "lakehouse", "medallion", "spark"],
    "schema-governance-engineer": ["data-contracts", "data-quality", "lineage", "dbt"],
    "schema-designer": ["data-modeling", "sql-patterns"],
    "semantic-modeler": ["data-modeling", "sql-patterns", "microsoft-fabric", "databricks"],
    "dbt-specialist": ["dbt", "data-modeling", "data-quality", "sql-patterns"],
    "sql-optimizer": ["sql-patterns", "data-modeling"],
    "lakehouse-architect": ["lakehouse", "medallion", "data-modeling"],
    "medallion-architect": ["medallion", "lakehouse", "data-modeling"],
    "spark-engineer": ["spark"],
    "streaming-engineer": ["streaming", "spark"],
    "terraform-specialist": ["terraform", "aws", "gcp"],
    "data-quality-analyst": ["data-quality"]
}

ROLE_OWNS_MAP = {
    "workflow-brainstormer": ["brainstorm"],
    "workflow-definer": ["define"],
    "workflow-designer": ["design"],
    "workflow-builder": ["build"],
    "workflow-shipper": ["ship"],
    "workflow-iterator": ["iterate"],
    "code-reviewer": ["code-review"],
    "codebase-explorer": ["codebase-analysis"],
    "context-optimizer": ["context-optimization"],
    "build-error-resolver": ["build-repair"],
    "architect": ["system-architecture"],
    "docs-lookup": ["documentation-lookup"],
    "code-architect": ["implementation-architecture"],
    "code-documenter": ["code-documentation"],
    "doc-updater": ["documentation-maintenance"],
    "llm-specialist": ["prompt-optimization", "structured-output"],
    "performance-optimizer": ["performance-analysis"],
    "pr-test-analyzer": ["test-gap-analysis"],
    "prompt-crafter": ["prompt-scoping"],
    "python-developer": ["python-implementation"],
    "kb-architect": ["kb-architecture"],
    "meeting-analyst": ["meeting-analysis"],
    "metadata-platform-engineer": ["metadata-architecture", "catalog-design"],
    "lineage-analyst": ["lineage-analysis", "impact-mapping"],
    "memory-architect": ["memory-architecture", "retrieval-design"],
    "memory-governance-engineer": ["memory-governance", "retention-policy"],
    "memory-observability-engineer": ["memory-observability", "telemetry-design"],
    "sentinel-supervisor": ["sentinel-supervision", "quarantine-policy"],
    "sentinel-runtime-watcher": ["runtime-monitoring", "product-health-watching"],
    "sentinel-security-watcher": ["security-monitoring", "security-quarantine-triggers"],
    "sentinel-analyzer": ["incident-analysis", "signal-diagnosis"],
    "sentinel-interpreter": ["operational-interpretation", "action-recommendation"],
    "planner": ["planning"],
    "pipeline-architect": ["orchestration", "dags"],
    "platform-access-engineer": ["platform-access", "grant-boundaries"],
    "refactor-cleaner": ["cleanup", "dead-code-removal"],
    "security-reviewer": ["security-review"],
    "airflow-specialist": ["airflow", "dag-authoring"],
    "ai-data-engineer": ["rag", "embedding-pipelines"],
    "azure-ai-architect": ["azure-ai-architecture", "azure-retrieval-design"],
    "data-governance-architect": ["governance-architecture", "control-design"],
    "data-observability-engineer": ["data-observability", "signal-design"],
    "business-monitor": ["business-monitoring", "alert-triage"],
    "data-platform-engineer": ["platform-selection", "cost-optimization"],
    "data-security-architect": ["data-security-architecture", "trust-boundaries"],
    "databricks-architect": ["databricks-architecture", "unity-catalog-boundaries"],
    "aws-data-architect": ["aws", "serverless-data-platforms"],
    "data-contracts-engineer": ["data-contracts", "sla-governance"],
    "mosaic-ai-engineer": ["mosaic-ai-implementation", "retrieval-serving-flows"],
    "gcp-data-architect": ["gcp", "bigquery-architecture"],
    "fabric-architect": ["fabric", "workload-selection"],
    "lakeflow-architect": ["lakeflow", "dlt-pipelines"],
    "schema-governance-engineer": ["schema-governance", "compatibility-policy"],
    "schema-designer": ["schema", "dimensional-modeling"],
    "semantic-modeler": ["semantic-modeling", "metric-design", "business-metrics"],
    "dbt-specialist": ["dbt", "analytics-models"],
    "sql-optimizer": ["sql", "query-plans"],
    "lakehouse-architect": ["lakehouse", "storage-layout"],
    "medallion-architect": ["medallion", "layered-pipelines"],
    "spark-engineer": ["spark", "batch-jobs"],
    "streaming-engineer": ["streaming", "event-pipelines"],
    "terraform-specialist": ["terraform", "infrastructure-modules"],
    "data-quality-analyst": ["validation", "quality-gates"]
}

ROLE_ESCALATIONS_MAP = {
    "workflow-brainstormer": [],
    "workflow-definer": ["workflow-brainstormer"],
    "workflow-designer": ["workflow-definer"],
    "workflow-builder": ["workflow-designer"],
    "workflow-shipper": [],
    "workflow-iterator": ["workflow-definer", "workflow-designer"],
    "code-reviewer": [],
    "codebase-explorer": ["planner", "pipeline-architect"],
    "context-optimizer": ["workflow-iterator", "planner", "kb-architect"],
    "build-error-resolver": ["planner", "refactor-cleaner"],
    "architect": ["planner", "workflow-designer"],
    "docs-lookup": ["domain-researcher"],
    "code-architect": ["planner", "workflow-designer"],
    "code-documenter": ["doc-updater", "codebase-explorer"],
    "doc-updater": ["codebase-explorer"],
    "llm-specialist": ["genai-architect", "prompt-crafter"],
    "performance-optimizer": ["code-architect", "planner"],
    "pr-test-analyzer": ["test-generator", "tdd-guide", "code-reviewer"],
    "prompt-crafter": ["workflow-definer", "planner", "genai-architect"],
    "python-developer": ["code-architect", "planner"],
    "kb-architect": ["domain-researcher"],
    "meeting-analyst": ["planner", "workflow-definer", "pipeline-architect"],
    "metadata-platform-engineer": ["lineage-analyst", "data-governance-architect"],
    "lineage-analyst": ["metadata-platform-engineer", "data-governance-architect"],
    "memory-architect": ["memory-governance-engineer", "memory-observability-engineer", "genai-architect"],
    "memory-governance-engineer": ["memory-architect", "data-governance-architect"],
    "memory-observability-engineer": ["memory-architect", "data-observability-engineer"],
    "sentinel-supervisor": ["data-observability-engineer", "data-security-architect", "data-governance-architect"],
    "sentinel-runtime-watcher": ["data-observability-engineer", "sentinel-supervisor"],
    "sentinel-security-watcher": ["data-security-architect", "sentinel-supervisor"],
    "sentinel-analyzer": ["sentinel-interpreter", "data-observability-engineer"],
    "sentinel-interpreter": ["sentinel-supervisor", "kb-architect"],
    "planner": ["workflow-definer", "workflow-designer"],
    "pipeline-architect": ["data-quality-analyst"],
    "platform-access-engineer": ["data-security-architect", "data-governance-architect"],
    "refactor-cleaner": ["planner", "code-reviewer"],
    "security-reviewer": ["code-reviewer", "reviewer"],
    "airflow-specialist": ["pipeline-architect"],
    "ai-data-engineer": ["streaming-engineer", "data-quality-analyst", "pipeline-architect"],
    "azure-ai-architect": ["genai-architect", "data-security-architect", "platform-access-engineer"],
    "data-governance-architect": ["data-security-architect", "schema-governance-engineer", "metadata-platform-engineer"],
    "data-observability-engineer": ["silent-failure-hunter", "data-governance-architect"],
    "business-monitor": ["data-observability-engineer", "sentinel-runtime-watcher", "data-quality-analyst"],
    "data-platform-engineer": [
        "lakehouse-architect",
        "schema-designer",
        "pipeline-architect",
        "aws-data-architect",
        "gcp-data-architect"
    ],
    "data-security-architect": ["security-reviewer", "platform-access-engineer"],
    "databricks-architect": ["lakeflow-architect", "spark-engineer", "data-platform-engineer"],
    "aws-data-architect": ["terraform-specialist", "data-quality-analyst"],
    "data-contracts-engineer": ["data-quality-analyst", "schema-designer", "dbt-specialist"],
    "mosaic-ai-engineer": ["databricks-architect", "genai-architect", "data-observability-engineer"],
    "gcp-data-architect": ["terraform-specialist", "streaming-engineer"],
    "fabric-architect": ["medallion-architect", "pipeline-architect"],
    "lakeflow-architect": ["spark-engineer", "medallion-architect"],
    "schema-governance-engineer": ["schema-designer", "data-governance-architect"],
    "schema-designer": [],
    "semantic-modeler": ["schema-designer", "fabric-architect", "databricks-architect"],
    "dbt-specialist": ["schema-designer"],
    "silent-failure-hunter": ["code-reviewer", "security-reviewer"],
    "sql-optimizer": ["schema-designer", "dbt-specialist"],
    "lakehouse-architect": ["schema-designer", "pipeline-architect"],
    "medallion-architect": ["lakehouse-architect", "schema-designer"],
    "spark-engineer": ["pipeline-architect"],
    "streaming-engineer": ["pipeline-architect", "data-quality-analyst"],
    "terraform-specialist": ["aws-data-architect", "gcp-data-architect"],
    "data-quality-analyst": [],
    "test-generator": ["tdd-guide", "data-quality-analyst", "schema-designer"],
    "tdd-guide": ["workflow-definer", "planner", "code-reviewer"]
}


def slug_from_filename(path: Path) -> str:
    return path.stem


def category_for_role(role_id: str) -> str:
    return "workflow" if role_id.startswith("workflow-") else "specialist"


def infer_kb_domains(role_id: str) -> list[str]:
    domains: list[str] = []
    token_domains = [
        ("fabric", "microsoft-fabric"),
        ("spark", "spark"),
        ("streaming", "streaming"),
        ("lakeflow", "lakeflow"),
        ("lakehouse", "lakehouse"),
        ("aws", "aws"),
        ("lambda", "aws"),
        ("gcp", "gcp"),
        ("terraform", "terraform"),
        ("database", "data-modeling"),
        ("sql", "sql-patterns"),
        ("data", "ai-data-engineering"),
        ("quality", "data-quality"),
        ("contract", "data-contracts"),
        ("security", "access-control"),
        ("reviewer", "governance"),
        ("performance", "observability"),
        ("troubleshooter", "observability"),
        ("logging", "observability"),
        ("pipeline", "orchestration"),
        ("ci-cd", "orchestration"),
        ("e2e", "data-quality"),
        ("python", "ai-data-engineering"),
        ("typescript", "ai-data-engineering"),
        ("genai", "genai"),
        ("prompt", "genai"),
        ("llm", "genai"),
        ("qdrant", "rag"),
        ("supabase", "data-modeling"),
    ]
    for token, domain in token_domains:
        if token in role_id and domain not in domains:
            domains.append(domain)
    return domains


def infer_owns(role_id: str) -> list[str]:
    ownership = role_id.replace("-specialist", "").replace("-reviewer", "-review")
    ownership = ownership.replace("-resolver", "-resolution")
    return [ownership]


def infer_escalations(role_id: str) -> list[str]:
    if "security" in role_id:
        return ["security-reviewer", "data-security-architect"]
    if "fabric" in role_id:
        return ["fabric-architect", "data-platform-engineer"]
    if "spark" in role_id:
        return ["spark-engineer", "pipeline-architect"]
    if "lakeflow" in role_id:
        return ["lakeflow-architect", "spark-engineer"]
    if "aws" in role_id or "lambda" in role_id:
        return ["aws-data-architect", "terraform-specialist"]
    if "gcp" in role_id:
        return ["gcp-data-architect", "terraform-specialist"]
    if "database" in role_id:
        return ["schema-designer", "data-contracts-engineer"]
    if "reviewer" in role_id:
        return ["code-reviewer", "security-reviewer"]
    if "build" in role_id:
        return ["build-error-resolver", "code-reviewer"]
    if "pipeline" in role_id or "e2e" in role_id or "ci-cd" in role_id:
        return ["pipeline-architect", "data-quality-analyst"]
    if "prompt" in role_id or "llm" in role_id:
        return ["llm-specialist", "prompt-crafter"]
    return ["planner"]


def emit_list(items: list[str], indent: int = 4) -> list[str]:
    if not items:
        return [" " * indent + "[]"]
    return [(" " * indent) + f"- {item}" for item in items]


def main() -> int:
    role_files = sorted(ROLES_DOCS.glob("*.md"))
    lines: list[str] = ["version: 0.1.0", "roles:"]

    for role_file in role_files:
        role_id = slug_from_filename(role_file)
        lines.append(f"  - id: {role_id}")
        lines.append(f"    category: {category_for_role(role_id)}")
        lines.append(f"    doc: docs/roles/{role_file.name}")
        lines.append("    kb_domains:")
        lines.extend(emit_list(ROLE_KB_MAP.get(role_id, infer_kb_domains(role_id)), indent=6))
        lines.append("    owns:")
        lines.extend(emit_list(ROLE_OWNS_MAP.get(role_id, infer_owns(role_id)), indent=6))
        lines.append("    escalates_to:")
        lines.extend(emit_list(ROLE_ESCALATIONS_MAP.get(role_id, infer_escalations(role_id)), indent=6))

    ROLES_MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote roles manifest: {ROLES_MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
