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
