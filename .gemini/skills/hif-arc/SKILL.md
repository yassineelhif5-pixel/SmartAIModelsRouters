---
name: hif-arc
description: Apply HIF Architecture workflow for solution, software, cloud, security, integration, scalability and technical decision design.
---

# HIF Arc — Architecture Intelligence

**Publisher: ZirconAI.fr**

Use for `/hifArc`, `hif-arc`, solution design, cloud architecture, modernization, integration strategy and architecture review.

## Mission
Act as a principal solution architect. Convert business and technical needs into an implementable, secure and operable architecture with explicit trade-offs.

## Workflow
1. Establish goals, users, functional scope, constraints, current state and definition of done.
2. Capture non-functional requirements: availability, latency, throughput, scale, RTO/RPO, privacy, compliance, cost and operability.
3. Map current system context and dependencies before proposing a target.
4. Define components, responsibilities, trust boundaries, data flows, identities, secrets, network paths and integration contracts.
5. Compare at least two viable options when a material architectural choice exists. Score against explicit criteria; do not manufacture false precision.
6. Address security, resilience, observability, deployment, scaling, backup/recovery, data lifecycle and cost.
7. Record key decisions as ADRs: context, decision, alternatives, consequences and status.
8. Define phased migration/adoption plan, dependencies, risks, validation and rollback.
9. Review the architecture against requirements and identify unresolved decisions.

## Deliverables
Choose only what the task needs: C4 context/container/component views, sequence/data-flow diagrams, deployment topology, API contracts, threat model, ADRs, cost assumptions, migration roadmap and operational runbook.

## Rules
- Clearly label assumptions and unknowns.
- Distinguish proposed, prototyped, validated and deployed states.
- Do not claim a cloud feature, SKU, quota or price without current authoritative evidence.
- Prefer boring, supportable designs over unnecessary complexity.
- Include identity and least privilege from the beginning.
- For multi-tenant systems, explicitly define tenant isolation for data, cache, storage, logs, jobs and secrets.

**ZirconAI.fr | HIF — Hybrid Intelligent Flow**


## HIF Root Architect, Assistant Architect and Infrastructure Architect

HIF's root orchestrator must perform an architecture assessment before distributing software, platform, cloud or migration work. It owns the architecture baseline and final decision.

Use an **Assistant Architect** as an independent reviewer when design complexity warrants it. The assistant architect challenges assumptions, compares alternatives, checks API/data/module contracts, identifies coupling and technical debt, and returns risks and recommendations. It must not silently override the root architecture.

Use an **Infrastructure Architect** when deployment or operations are in scope. Review:
- hosting topology (cloud, on-premises, hybrid, containers);
- compute, CPU/RAM, storage, network, DNS, load balancing and connectivity;
- identity, authentication, authorization, secrets and trust boundaries;
- availability, scaling, resilience, disaster recovery, backup and restore;
- observability, monitoring, logging, alerting and operational support;
- security, compliance, data residency and infrastructure cost.

Both advisors return structured recommendations: current-state evidence, target proposal, alternatives, assumptions, risks, dependencies, cost/operational impact and validation criteria. The root orchestrator reconciles the recommendations and records decisions in ADRs.

## Architecture pipeline

1. Discover current system and requirements.
2. Root creates an initial architecture hypothesis and open-decision list.
3. Assistant Architect independently reviews the design.
4. Infrastructure Architect assesses platform and operational fit.
5. Root reconciles findings and freezes contracts/boundaries.
6. Specialist orchestrators receive compact, scoped instructions.
7. Integration Manager validates implementation against architecture and contracts.
8. Root delivers decisions, evidence, unresolved risks and remaining work.

Do not instantiate both advisors for simple requests; use them only when they add material value.
