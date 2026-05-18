#!/bin/bash

# Define the required artifacts from the project standard
declare -a artifacts=(
    "definition/problem.md"
    "definition/scope.md"
    "definition/stakeholders.md"
    "definition/domain.md"
    "definition/glossary.md"
    "design/architecture.md"
    "design/data-flow.md"
    "design/system-diagram.md"
    "design/decisions/README.md"
    "data/sources.md"
    "data/storage.md"
    "data/schemas/README.md"
    "data/models/README.md"
    "data/transformations/README.md"
    "controls/governance.md"
    "controls/ownership.md"
    "controls/policies.md"
    "metadata/lineage.md"
    "execution/orchestration.md"
    "execution/schedules.md"
    "execution/pipelines/README.md"
    "validation/data-quality.md"
    "validation/rules.md"
    "validation/tests/README.md"
    "operations/observability/metrics.md"
    "operations/observability/alerts.md"
    "operations/observability/dashboards.md"
    "operations/observability/logs.md"
    "operations/sentinel/architecture.md"
    "operations/sentinel/watchers.md"
    "operations/sentinel/analyzers.md"
    "operations/sentinel/interpreters.md"
    "operations/sentinel/knowledge.md"
    "operations/sentinel/knowledge-feed.md"
    "operations/sentinel/runbooks.md"
    "operations/sentinel/supervision.md"
    "operations/sentinel/quarantine.md"
    "security/access-control.md"
    "security/roles.md"
    "security/permissions.md"
    "security/secrets.md"
    "contracts/compatibility.md"
    "contracts/versioning.md"
    "contracts/schema-contracts/README.md"
    "contracts/api-contracts/README.md"
    "integrations/README.md"
    "kb/domain/README.md"
    "kb/patterns/README.md"
    "kb/decisions/README.md"
    "deploy/environments.md"
    "deploy/ci-cd.md"
    "deploy/infra/README.md"
    "operations/cost/cost-model.md"
    "operations/cost/optimization.md"
    "compliance/regulations.md"
    "compliance/audit.md"
)

echo "Checking AgentCodex Project Standard compliance..."
echo "=================================================="

missing=0
total=${#artifacts[@]}

for artifact in "${artifacts[@]}"; do
    if [[ -f "$artifact" || -d "$artifact" ]]; then
        echo "✓ $artifact"
    else
        echo "✗ $artifact"
        missing=$((missing + 1))
    fi
done

echo ""
echo "Summary:"
echo "--------"
echo "Total artifacts: $total"
echo "Missing artifacts: $missing"
echo "Completion percentage: $(( (total - missing) * 100 / total ))%"
