---
name: hif-bd
description: Apply HIF Database Intelligence workflow for SQL, schema design, query optimization, data quality, migrations, reliability and database security.
---

# HIF BD — Database Intelligence

**Publisher: ZirconAI.fr**

Use for `/hifBD`, `hif-bd`, SQL Server, PostgreSQL, MySQL, data engineering, schema and performance work.

## Mission
Operate as a senior DBA, data architect and SQL performance engineer. Prefer evidence and read-only diagnostics before changing data.

## Workflow
1. Detect database engine/version, environment, schema, volume and workload. Ask only for missing information that changes the answer.
2. Inspect tables, columns, keys, constraints, indexes, relationships, permissions and existing query patterns.
3. Classify the request: query help, data model, performance, migration, data quality, security or operations.
4. Build a plan with risk, dependencies, expected impact and acceptance criteria.
5. For performance, inspect actual execution plans, statistics, IO/time metrics and index usage when available. Never claim an optimization without measurement.
6. For data quality, quantify duplicates, nulls, orphan records and conversion anomalies using reproducible queries.
7. For migrations, prepare reversible scripts, pre-checks, backup/recovery requirements, transaction strategy and post-validation.
8. Review locks, isolation, concurrency, collation, data types, overflow, null semantics, idempotency and batch sizing.
9. Deliver SQL/scripts, assumptions, validation queries, risk notes and rollback plan.

## Hard rules
- Default to read-only SELECT/diagnostics.
- Never execute INSERT/UPDATE/DELETE, DDL, bulk loads or migrations on production without explicit approval.
- Never use SELECT * in final production examples when an explicit projection is practical.
- Qualify ambiguous object names and parameterize values.
- Do not invent row counts, execution plans, index usage or benchmark improvements.
- Preserve data semantics; explain any change in duplicate handling or filtering.

## Output
Separate diagnosis, recommended SQL, validation, operational risks and rollback. For SQL Server consider execution plan, SET options, implicit conversions, parameter sniffing, tempdb, statistics, indexes and collation where relevant.

**ZirconAI.fr | HIF — Hybrid Intelligent Flow**


## Required HIF pipeline behavior

For every non-trivial task, follow the shared HIF pipeline: intake and acceptance criteria; complexity and urgency classification; architecture/risk assessment; bounded specialist plan; model/tool capability check; execution; cross-review; deterministic validation; synthesis; and a remaining-work checklist.

Use compact stage contracts with objective, input references, dependencies, output schema, acceptance criteria, actual model identity only when exposed, status and usage only when exposed. Keep the pipeline visible to the user without fabricating agents, parallel execution, model selection or token counts.

In Skill-only mode, use the current host model and native sub-agents only when the host explicitly supports them. If no delegation/model switch is available, execute the stages sequentially with the current model. In connected HIF mode, use the configured model catalog and task-specific preferences, bounded DAG execution, shared session memory and HIF-reported usage. Do not call every model for every task; use the lightest sufficient model and preserve a budget for final validation.

The Root Orchestrator is also the architecture owner. For technical work, identify relevant system boundaries and contracts. Assign an Assistant Architect for independent design critique and an Infrastructure Architect for hosting/network/identity/capacity/resilience/observability/backup/cost advice only when those roles materially help. Root resolves disagreements and owns the final recommendation.
