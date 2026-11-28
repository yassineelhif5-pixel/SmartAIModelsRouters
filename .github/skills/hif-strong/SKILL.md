---
name: hif-strong
description: Apply HIF Strong high-assurance workflow for critical, ambiguous, cross-domain or highly complex tasks requiring independent verification and controlled delegation.
---

# HIF Strong — High Assurance

**Publisher: ZirconAI.fr**

Use for `/hifStrong`, `hif-strong`, critical decisions, broad cross-domain work, complex incident analysis or tasks where failure impact is high.

## Mission
Maximize reliability, not agent count. Build a bounded verification process and preserve a clear root owner.

## Workflow
1. Define the exact outcome, scope, constraints, deadline, risk and acceptance criteria.
2. Classify complexity and consequence. Escalate to Strong for too-complicated work; do not use Strong merely because a task is long.
3. Create a root plan and bounded workstreams. Each workstream receives a role, narrow context, output schema, budget and deadline.
4. Seek independent approaches only where they can expose meaningful uncertainty or improve quality.
5. Separate evidence gathering, proposal, critique, deterministic verification and final decision.
6. Resolve contradictions explicitly. Preserve unresolved disagreements rather than hiding them in a consensus.
7. Verify important claims against source evidence, tests, calculations, schemas or other deterministic checks.
8. Reassess risk and remaining budget after failures or scope changes.
9. Produce a final decision with confidence, evidence, assumptions, risks and uncompleted work.

## Quality gates
- User intent and scope: fulfilled?
- Correctness: independently checked where feasible?
- Evidence: traceable to actual sources or test output?
- Security/privacy: policy and permission compliant?
- Robustness: edge cases, failures and recovery addressed?
- Cost/time: within user constraints?
- Delivery: acceptance criteria met?

A blocking safety, security or policy failure cannot be offset by a high aggregate score. Model self-ratings are weak evidence; prefer tests and external facts. Never select the longest answer by default.

## Resource controls
Use at most the smallest useful set of specialists. Do not call every model for every task. Preserve a reserve for synthesis and verification. If connected HIF budgets or telemetry are absent, do not claim exact token savings, provider quotas or parallel model execution.

## Safety
Require approval for destructive or externally visible actions. Do not bypass host permissions or provider policies. Do not reveal hidden chain-of-thought; provide concise rationale and evidence instead.

**ZirconAI.fr | HIF — Hybrid Intelligent Flow**


## Project-wide engineering coherence

When Strong handles software or application delivery, designate one root AI Tech Lead as the architecture and integration owner. Before parallel coding, establish a versioned Project Constitution, module/dependency map, API/schema contracts, file ownership and acceptance gates. All agents and model outputs must conform to this shared source of truth.

Treat individual agent completion as provisional until the Integration Manager checks diffs, cross-module contracts, architecture boundaries, builds, tests, security and migrations. Use deterministic tooling first; route precise failures to the responsible owner. Revalidate only impacted dependents after a contract change. Preserve disagreements and unresolved risks.

Never report a project as coherent or complete merely because separate agents succeeded. Report integrated and validated status separately, with actual evidence. Protected merges, deployments, production migrations and destructive actions require approval.


## Required HIF pipeline behavior

For every non-trivial task, follow the shared HIF pipeline: intake and acceptance criteria; complexity and urgency classification; architecture/risk assessment; bounded specialist plan; model/tool capability check; execution; cross-review; deterministic validation; synthesis; and a remaining-work checklist.

Use compact stage contracts with objective, input references, dependencies, output schema, acceptance criteria, actual model identity only when exposed, status and usage only when exposed. Keep the pipeline visible to the user without fabricating agents, parallel execution, model selection or token counts.

In Skill-only mode, use the current host model and native sub-agents only when the host explicitly supports them. If no delegation/model switch is available, execute the stages sequentially with the current model. In connected HIF mode, use the configured model catalog and task-specific preferences, bounded DAG execution, shared session memory and HIF-reported usage. Do not call every model for every task; use the lightest sufficient model and preserve a budget for final validation.

The Root Orchestrator is also the architecture owner. For technical work, identify relevant system boundaries and contracts. Assign an Assistant Architect for independent design critique and an Infrastructure Architect for hosting/network/identity/capacity/resilience/observability/backup/cost advice only when those roles materially help. Root resolves disagreements and owns the final recommendation.

## Security assurance for AI-generated applications

For software and vibe-coded projects, add an explicit application-security workstream when in scope. Use the fast deterministic local pre-audit (`hif security scan .`) when connected runtime is available, then delegate architecture/threat-model review and application-security review. Check identity, authorization, tenant isolation, secrets, injection, SSRF, uploads, dependency supply chain, TLS, CORS and deployment hardening. Produce a P0/P1/P2/P3 remediation plan with evidence, owner, corrective action, regression test and retest criteria. Critical/high unresolved risks must be called out as release blockers unless explicitly accepted by an authorized security owner. Do not describe heuristic scanning as complete SAST/DAST or certification. See docs/SECURITY-VIBE-CODING.md.


## Universal high-assurance review

HIF Strong applies to every domain, not only software. For research, verify source quality, freshness, claim-to-source traceability, conflicting evidence and uncertainty. For campaigns, review audience fit, factual claims, brand/compliance constraints, channel formatting and approval status. For reports, validate calculations, dates, citations, data provenance, chart integrity, executive conclusions and consistency between summary and detail. For operations, check ownership, dependencies, feasibility, risks and measurable acceptance criteria.

Use independent review only where it materially reduces risk. Do not equate multiple model opinions with truth; prioritize primary evidence, deterministic checks and domain-specific acceptance criteria. Clearly separate draft, reviewed, validated and published states. A publication is not considered complete until an authorized connector confirms it.

See `docs/HIF-UNIVERSAL-ORCHESTRATOR.md`.
