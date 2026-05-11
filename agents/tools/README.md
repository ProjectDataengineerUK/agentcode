# Agent Tools

Document tool surfaces and capability boundaries for project-local agents.

Minimum baseline:
- read-only tools
- write-capable tools
- deployment or production-control tools
- observability and evidence tools
- KB and memory update tools

For every tool, state:
- allowed scope
- forbidden scope
- approval requirement
- audit artifact generated after use

Do not grant direct production mutation capability without a matching approval path in Sentinel supervision.
