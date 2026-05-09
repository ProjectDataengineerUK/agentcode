---
date: 2026-05-08
type: concept-capture
status: brainstorm
topic: Sistema multiagentes especialistas — ecossistema Snowflake
next_step: /brainstorm → BRAINSTORM_SNOWFLAKE_MULTIAGENT.md
---

# Conceito: Sistema Multiagentes — Ecossistema Snowflake

## Origem

Ideia capturada em sessão 2026-05-08. O sistema proposto é um conjunto de
agentes especialistas no ecossistema Snowflake, construído sobre 5 grupos de fontes.

---

## 5 Grupos de Fontes (Arquitetura Proposta)

### Grupo 1 — MCP Servers para Snowflake (fonte principal)

Snowflake tem um **Snowflake-managed MCP Server** oficial que expõe:
- **Cortex Analyst** — natural language to SQL sobre dados estruturados
- **Cortex Search** — busca semântica sobre dados não estruturados
- **Cortex Agents** — agentes nativos do Snowflake com tool use
- **Ferramentas customizadas** — funções Snowflake expostas via MCP
- **Execução SQL** — queries diretas via interface MCP

> Referência: Snowflake Developer Documentation — Snowflake-managed MCP Server

### Grupo 2 — MCP Servers para Ferramentas Externas

Serviços externos conectados via MCP ao ecossistema Snowflake:
- Salesforce MCP (confirmado: "Introducing MCP Support Across Salesforce")
- Ferramentas de observabilidade e qualidade
- Fontes de dados externas para enriquecimento

### Grupo 3 — KBs / Bases de Conhecimento para RAG

Knowledge bases estruturadas que os agentes consultam antes de agir:
- Padrões Snowflake (Cortex, Iceberg, Snowpark, Data Sharing)
- Regras de negócio e catálogo de dados
- Histórico de queries otimizadas e padrões de performance
- Data contracts e acordos de qualidade

### Grupo 4 — Docs Oficiais Snowflake para Consulta pelos Agentes

Documentação oficial usada como fonte de verdade pelos agentes:
- Snowflake SQL Reference
- Cortex Functions Reference (ML functions, LLM functions)
- Snowpark (Python/Java/Scala)
- Dynamic Tables, Streams, Tasks
- Snowflake Cortex Analyst / Cortex Search

### Grupo 5 — Arquitetura de Agentes Especialistas

Agentes especializados por domínio Snowflake:
- `snowflake-sql-expert` — Snowflake SQL, Snowpark, performance
- `cortex-analyst` — NL→SQL, Cortex Analyst API
- `cortex-search` — busca semântica, embedding, unstructured data
- `snowflake-data-engineer` — Dynamic Tables, Streams, Tasks, CDC
- `snowflake-governance` — RBAC, data classification, access policies
- `snowflake-cost-optimizer` — Warehouse sizing, credit consumption, Query Profile
- `snowflake-ml-engineer` — Cortex ML functions, Feature Store, Snowpark ML

---

## Notas de Segurança

Mencionado na captura: MCP tem vulnerabilidade conhecida de RCE (Tom's Hardware, 2026).
Implicação: MCP servers Snowflake devem rodar com least-privilege e sem exposição pública.
Guardrail obrigatório: validar inputs antes de passar para execução SQL via MCP.

---

## Próximos Passos

1. `/brainstorm` — explorar arquitetura detalhada dos 5 grupos
2. Definir quais Cortex APIs são expostas via MCP vs. chamadas diretas
3. Criar KB domain `kb/snowflake/` no agentcode
4. Criar agentes especialistas Snowflake em `.claude/agents/data-engineering/`
5. Avaliar posição: agentcode extension vs. plugin separado `agentcode-snowflake`

---

## Referências Citadas

- Snowflake-managed MCP Server — Snowflake Developer Docs
- Salesforce MCP: https://developer.salesforce.com/blogs/2025/06/introducing-mcp-support-across-salesforce
- MCP RCE vulnerability: Tom's Hardware (Anthropic MCP critical security flaw)
