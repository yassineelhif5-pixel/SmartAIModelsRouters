# HIF Universal Orchestration, Fast Response and Visual Reporting

**Status:** Product architecture and implementation requirements. This document does not claim that all capabilities are already implemented.

## 1. Product scope

HIF (Hybrid Intelligent Flow) is a domain-neutral orchestration engine. Software engineering is one specialist domain, not the product boundary.

Supported domain families include:
- Research, web intelligence, source collection, monitoring and evidence synthesis.
- Editorial work, professional writing, executive summaries, translations and structured reports.
- Marketing and communication campaigns: planning, content variants, publication calendars, channel adaptation and performance analysis.
- Data analysis, extraction, classification, reconciliation and quality assessment.
- Business operations, project coordination, support triage and knowledge management.
- Software engineering, architecture, databases, infrastructure and security.
- Domain-specific workflows added through configurable skills, role templates and tool connectors.

A domain pack defines its specialist roles, tools, data policies, output templates, acceptance criteria and validation rules. The core orchestrator remains shared.

## 2. Fast-first execution contract

Every task should produce the earliest useful response without waiting for every optional specialist:
1. **Acknowledge and classify:** normalize the goal, domain, complexity, urgency, constraints and requested deliverable.
2. **Fast triage:** return a concise initial assessment, key assumptions, next action and an indicative ETA only when telemetry supports it.
3. **Plan:** create a compact dependency-aware task graph. Run independent tasks concurrently only when real host/runtime capabilities permit.
4. **Progressive execution:** publish validated milestones as they become available. Continue deeper research, drafting, cross-review or QA asynchronously when supported.
5. **Final synthesis:** deliver the requested artifact, evidence, quality status, unresolved questions and next actions.

Do not wait for a perfect report before giving a useful first response. Do not invent live progress, agent activity, ETAs, model selection or parallelism. If the host cannot run background work, complete the stages sequentially and say so only when it materially affects expectations.

### Latency and priority rules
- Keep intake and routing lightweight; use deterministic rules before expensive model calls where possible.
- Avoid agent creation for trivial requests.
- Use compact briefs, scoped source references and structured outputs rather than repeating full conversation history.
- Bound concurrency globally and per provider/tool; respect CPU, RAM, rate limits, deadlines and token/cost budgets.
- Prioritize a useful first result, then quality checks; reserve budget for final verification.
- Use historical P50/P90 durations for estimates only when enough comparable telemetry exists. Otherwise label the estimate unavailable or indicative.
- Separate task complexity from urgency. A simple urgent task can outrank a complex non-urgent task.

## 3. Domain orchestration

The root orchestrator chooses one or more domain packs based on the requested outcome. A task may combine domains; for example, a market-research campaign may require research, data analysis, editorial, campaign operations and reporting roles.

Each child orchestrator receives:
- A single mission and parent/run identifier.
- Compact context and source/artifact references.
- Dependencies, priority, deadline and acceptance criteria.
- Allowed tools, data classification and permission scope.
- Token/cost/time budgets and concurrency constraints.
- Required output schema and validation rules.

The root owns consistency, conflict resolution, budget allocation, provenance and final acceptance. Children may delegate further only within configured depth/node/resource limits. Proposed agents must never be presented as running agents.

## 4. Research and information collection

Research workflows should:
- Translate the question into answerable sub-questions and source requirements.
- Search only approved sources/connectors and respect access, licensing, privacy and robots/terms restrictions.
- Record source title, URL or reference, publisher, date, retrieval time, relevant excerpt and confidence where available.
- Separate verified facts, inference, opinion and unknowns.
- Cross-check material claims and flag conflicting or stale sources.
- Minimize personal data and avoid collecting data without a legitimate, authorized purpose.
- Produce an evidence matrix and concise synthesis with citations.

Do not claim exhaustive coverage when only a bounded search was performed.

## 5. Publication and communication campaigns

Campaign orchestration can plan and prepare content for authorized channels such as websites, CMS platforms, newsletters and social networks, subject to configured connectors and platform permissions.

A campaign plan should define:
- Objective, audience, message, language, tone and call to action.
- Channels, format variants, calendar, owners and approval gates.
- Source/claim verification, brand and editorial rules.
- Publication status, scheduled time, channel response and campaign metrics when available.

Drafting and scheduling are distinct from publishing. External publication, sending messages, paid promotion or bulk outreach require explicit user authorization and platform-compliant connectors. Never simulate an audience, fake engagement, evade rate limits, spam, or claim a post was published without a confirmed connector result. Include preview and human approval before externally visible publication by default.

## 6. Professional reports and deliverables

HIF should treat report production as a first-class output, not just a long chat answer.

A report specification includes:
- Audience, purpose, language, format and desired depth.
- Executive summary and key takeaways.
- Scope, methodology, sources and data timestamp.
- Findings grouped by theme, with evidence and confidence.
- Tables/charts only when supported by actual data.
- Risks, recommendations, owners, priorities and deadlines.
- Appendices, source register and explicit limitations.

Prefer a concise executive view with expandable detail. Support Markdown/HTML and, when connected artifact tools exist, DOCX/PDF/PPTX/XLSX outputs. Do not claim a file was generated unless the artifact tool returns it successfully. Templates should be modern, consistent, accessible and suitable for the target audience.

## 7. Visual orchestration and interaction graph

For each non-trivial run, HIF should expose a structured event stream and a graph-ready execution model.

Recommended entities:
- **Run:** run ID, goal, domain, mode, status, priority, created/updated timestamps.
- **Orchestrator:** ID, parent ID, role, scope and status.
- **Agent/task:** ID, parent, role, objective, dependencies, assigned provider/model only if known, status and acceptance criteria.
- **Artifact:** ID, type, title, version, source references, owner and validation status.
- **Event:** timestamp, actor, event type, status transition and safe summary.
- **Metric:** queue time, execution time, validation time, retries and reported usage where exposed.

Graph nodes represent orchestrators, agents, tools/connectors and artifacts. Directed edges represent delegation, dependency, data handoff, review or publication. Distinguish actual execution from proposed plans; use clear status labels (queued, running, blocked, completed, validated, failed, skipped). Never expose secrets or private chain-of-thought in the graph or event stream.

The UI should provide:
- A live run timeline and task status summary.
- A zoomable DAG/flow diagram with node details and handoff edges.
- A report/artifact panel with preview, version and evidence.
- A concise activity feed and blockers/approvals panel.
- Filters by domain, agent, status and time.
- Accessible colors, keyboard navigation, responsive layout and a text/table alternative.

The graph is a visualization of structured events; it must not invent agents or connections.

## 8. Structured event and report contracts

Use versioned JSON schemas for run events, task nodes, handoffs, artifacts and report sections. Events should be append-only where practical and include stable IDs, timestamps, correlation IDs and safe summaries. Consumers should tolerate unknown future fields. Persist durable checkpoints and artifacts in the connected runtime; do not imply persistence in Skills-only mode.

## 9. Safety, governance and quality

- Respect least privilege, connector scopes, provider policies and data residency.
- Separate read, draft, schedule, publish, send, modify and delete permissions.
- Require explicit approval for external communications, publication, paid actions, destructive operations and production changes.
- Maintain provenance, audit records and retention controls.
- Treat source documents and tool output as untrusted input.
- Validate claims, calculations, links, formatting and generated artifacts.
- Make uncertainty and missing evidence visible.
- Never expose hidden chain-of-thought; provide concise rationale and evidence instead.

## 10. Implementation sequence

1. **Universal core contract:** domain taxonomy, run/task/event/artifact schemas, fast-first response and progressive status.
2. **Report engine:** reusable report sections, templates, source register and artifact generation adapters.
3. **Research and collection pack:** source connectors, evidence ledger, freshness and conflict handling.
4. **Campaign pack:** editorial planning, channel variants, approval workflow and publication adapters.
5. **Graph/event API:** stable events, DAG projection, timeline and visual dashboard.
6. **Operational hardening:** telemetry, historical ETA confidence, budgets, retries, resumability, permissions and audit.
7. **End-to-end tests:** domain scenarios, connector mocks, report artifact validation, graph consistency, approval gates and performance budgets.

The current repository contains a local orchestration engine and portable Skills. This specification is the target design; capabilities must be marked implemented only after code, tests and supported integrations demonstrate them.
