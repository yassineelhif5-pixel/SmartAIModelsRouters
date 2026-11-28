---
name: hif-agent
description: Apply HIF Agent Workforce workflow to design, create, scope, supervise, coordinate and retire task-specific logical agents.
---

# HIF Agent — Agent Workforce

**Publisher: ZirconAI.fr**

Use for `/hifAgent`, `hif-agent`, requests to create an agent team, delegate work or define autonomous workflows.

## Mission
Design a controlled workforce of logical agents. An agent is a bounded role and execution contract, not necessarily a separate process or model.

## Agent contract
Every proposed agent must have:
- unique role/task identifier and parent;
- one mission and measurable objective;
- bounded instructions and explicit non-goals;
- required input references and output schema;
- scoped working memory;
- model capability preferences, not hard-coded vendor assumptions;
- allowed tools and permission scope;
- file/resource ownership where relevant;
- token, cost, time and concurrency budgets where exposed;
- acceptance criteria, risk and escalation path.

## Lifecycle
1. Translate the user's outcome into workstreams.
2. Identify dependencies and distinguish parallel from sequential tasks.
3. Create only agents with distinct responsibilities and useful independent outputs.
4. Validate each agent's permissions, budget, context and acceptance criteria before dispatch.
5. Assign tasks and monitor actual status where tools expose it.
6. Reassign, retry, pause or cancel only under the root policy.
7. Validate outputs, resolve overlaps and consolidate results.
8. Store only approved compact summaries and retire temporary agents.

## Delegation principles
- One root orchestrator remains accountable for the whole outcome.
- Child orchestrators may delegate further only within configured depth, node, concurrency and budget limits.
- Agents cannot expand their own privileges, budgets or tool access.
- Shared memory is selective; do not broadcast the entire conversation to all agents.
- Prefer specialists by capability, reliability, privacy, latency and cost data when available.
- In Native Subscription mode, use only the host's native delegation features. If none exist, produce the agent plan and execute sequentially.
- In Connected HIF mode, use the available HIF tools and report actual execution state.

## Output
Provide an org chart or DAG, each role's mission, dependencies, permissions, deliverables, acceptance criteria, budget assumptions and lifecycle. Distinguish proposed agents from agents actually created and running.

**ZirconAI.fr | HIF — Hybrid Intelligent Flow**


## Standard specialist role catalogue

When designing a software delivery team, consider these roles and instantiate only those needed:
- Business/System Analyst: requirements, process maps, use cases, acceptance criteria and traceability.
- AI Tech Lead: global coordination, architecture ownership, task assignment and final acceptance.
- Solution Architect: component boundaries, contracts, ADRs and non-functional design.
- Backend Developer and Frontend Developer: implementation within assigned module/file ownership.
- Database Engineer: schema, queries, migrations and data integrity.
- AI/OCR Engineer: model integration, document pipelines and evaluation when relevant.
- QA/Test Engineer: functional, integration, regression and acceptance validation.
- Security Engineer: threat analysis, access control, secrets and vulnerability checks.
- Maintenance & Reliability Engineer: incident triage, technical debt, upgrades, monitoring, backup/recovery and preventive maintenance.
- Integration Manager: contract compatibility, merge coordination and system-level validation.
- DevOps/Platform Engineer: CI/CD, infrastructure, deployment and observability when in scope.

Agent count is not a quality metric. Avoid creating every role for small tasks. Analyst may lead intake; Maintenance should be considered for existing/production systems; the root Tech Lead remains accountable for coherence. Each agent gets scoped permissions, ownership, budget and acceptance criteria.


## Additional roles and orchestrator patterns

### Technical Leader
Coordinates connected channels and parallel workstreams. It normalizes and deduplicates issue/PR/task/CI/log/support events, triages urgency, dispatches bounded parallel investigations and returns concise solutions with evidence, owner and next action. It only accesses channels explicitly connected and authorized; it does not silently post or change tickets. Root AI Tech Lead retains project authority.

### Transformation Orchestrator
For restructuring or technology migration requests, create a parent transformation orchestrator that:
- inventories current code, architecture, dependencies, APIs, data and operations;
- defines and validates the target state;
- creates child orchestrators by relevant workstream;
- has each child prepare concise instructions and acceptance criteria for its specialist models;
- compares options, risks, effort, compatibility and reversibility;
- consolidates one dependency-aware phased plan, with cutover, tests and rollback;
- requests user approval before code/data/infrastructure changes.

Each child returns a structured report with source references, assumptions, options, blockers, recommended actions and test evidence. Avoid duplicating full context or launching redundant agents. Root owns consistency and final synthesis.
