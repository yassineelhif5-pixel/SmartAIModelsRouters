# HIF 1.0 — Five-Mode Architecture and Integration Specification

Status: Proposed baseline for HIF 1.0  
Target: yassineelhif5-pixel/SmartAIModelsRouters  
Baseline: existing HIF 0.3.0 codebase

## 1. Product decisions

The following decisions are normative:

| Decision | Behavior |
|---|---|
| Default mode | auto |
| Classification | simple, complicated, too_complicated |
| Strong trigger | Every too_complicated task escalates to hifStrong |
| Mode switching | Automatic during execution when material new evidence changes the task profile |
| Runtime | One shared HIF Core, five specialized mode policies |
| Safety | Explicit approval for destructive, external, production or other high-impact actions |

Canonical internal mode identifiers are dev, bd, arc, strong and agent. User-facing aliases are case-insensitive: /hifDev, /hifBD, /hifArc, /hifStrong and /hifAgent. The generic /hif command selects Auto.

## 2. Five modes

### hifDev — Software Engineering
Mission: analyze, implement, test, review and prepare software changes in new or existing repositories.

Specialists: AI Tech Lead, Software Architect, Backend Engineer, Frontend Engineer, Database Engineer, AI/OCR Engineer, QA Engineer, Security Reviewer and DevOps Engineer.

Required behavior:
- Inspect the existing repository, architecture and conventions before changing files.
- Define module ownership and API/schema contracts before parallel implementation.
- Use isolated branches or worktrees for parallel code changes.
- Restrict each agent to its assigned files and tools.
- Run tests, linters, type checks and security checks where available.
- Integrate only after conflict resolution and validation.
- Report changed files, test evidence, known gaps and rollback considerations.

No direct writes to main. Merges, deployments, production migrations, destructive changes and credential operations require approval.

### hifBD — Database Engineering
Mission: design, query, optimize, migrate and validate database systems.

Specialists: Database Architect, SQL Developer, Query Optimizer, Data Modeler, DBA/Reliability Engineer, Data Quality Analyst and Database Security Reviewer.

Required behavior:
- Detect database engine/version and inspect schema before recommendations.
- Account for keys, constraints, indexes, collation, transactions and workload.
- Separate read-only diagnostics from data writes and schema changes.
- Use execution plans and measured benchmarks when available.
- Produce reversible migrations and pre/post validation queries.
- Consider locks, concurrency, backups, recovery and data volume.
- Coordinate schema contracts with hifDev.

Default to read-only analysis. Production writes, destructive DDL, bulk updates/deletes and migrations require approval and a recovery plan. Never invent row counts or benchmark results.

### hifArc — Architecture
Mission: design and review end-to-end technical solutions.

Specialists: Solution Architect, Software Architect, Cloud Architect, Security Architect, Integration/API Architect and Reliability/Performance Architect.

Required behavior:
- Capture functional and non-functional requirements.
- Produce context, container, component and deployment views as appropriate.
- Document data flows, trust boundaries, identity, secrets and network paths.
- Compare options with explicit trade-offs and decision criteria.
- Define API, event, schema and ownership contracts.
- Record important decisions as ADRs.
- Validate scalability, security, resilience, observability, cost and maintainability.

Deliverables may include diagrams, ADRs, API contracts, deployment topology, threat model and roadmap. A proposed design must never be presented as a deployed architecture.

### hifStrong — High-Assurance Orchestration
Mission: deliver the most reliable outcome for every task classified too_complicated, regardless of domain.

Required behavior:
- Become the root orchestrator for every too_complicated task.
- Create bounded child orchestrators and specialist agents.
- Use multiple providers/models when independent expertise or verification justifies it.
- Request independent critique for high-impact assumptions and deliverables.
- Prefer deterministic checks, tests, evidence and policy validation.
- Compare candidate solutions and select the best fit against user constraints.
- Maintain the global budget, deadline, risk register and completion definition.

Strong does not mean calling every model for every task. It should add reviewers and candidate solutions only when expected quality gain justifies cost and latency. It cannot bypass privacy, permissions or approval gates. Domain modes can operate as specialist workstreams under Strong.

### hifAgent — Agent Workforce
Mission: create, configure, supervise, coordinate and retire task-specific logical agents.

Each agent contract contains:
- agent/task ID and parent orchestrator ID;
- role, objective and bounded instructions;
- input references and output schema;
- scoped working memory;
- provider/model preferences and required capabilities;
- token, cost, time and concurrency budgets;
- allowed tools, file scope and side-effect policy;
- acceptance criteria, status, provenance and telemetry.

Lifecycle: create from an approved role template; validate scope, permissions and budget; assign to a parent task; execute; publish structured output; verify; retry/reassign/suspend/cancel under policy; persist a compact summary; retire.

Agents cannot create unlimited agents, expand their own permissions, alter global budgets or invoke ungranted tools. Agents are logical execution units, not necessarily separate OS processes or full HIF installations.

## 3. Shared HIF Core

Shared services:
- IntentAnalyzer: extract outcome, constraints, requested actions and deliverables.
- TaskClassifier: classify complexity and expose a rationale summary and confidence.
- ExecutionTimeEstimator: estimate P50/P90 from historical task, model and queue telemetry.
- ModeResolver: select the initial mode and manage transitions.
- RootOrchestrator: own the user goal, global budget, plan, policy and final result.
- RecursiveTaskPlanner: create validated DAGs and child-orchestrator plans.
- SpecialistAgentFactory: instantiate approved logical agents.
- AdaptiveMultiModelRouter: filter and rank providers/models.
- HierarchicalBudgetManager: allocate tokens, cost, time and concurrency.
- ParallelExecutionScheduler: schedule dependency-ready work.
- AdaptiveMemoryManager: retrieve scoped, provenance-bearing memory.
- QualityScoringEngine and BestSolutionSelector: verify and select outputs.
- ExecutionTelemetry: measure queue, execution, evaluation and total time.
- GlobalResultAggregator: reconcile outputs, contradictions and unresolved risks.

Runtime sequence:
1. Receive request from CLI, MCP, gateway or host skill.
2. Normalize explicit mode alias, if present.
3. Analyze intent, constraints, risk and context.
4. Classify task complexity.
5. Resolve mode; Auto selects a domain mode, and every too_complicated task escalates to Strong.
6. Estimate duration and resources, labelling estimates as indicative if history is insufficient.
7. Build and validate plan, DAG, permissions, budgets and acceptance criteria.
8. Execute independent tasks within global limits.
9. Re-evaluate mode if material evidence changes the task profile.
10. Verify deliverables, score candidates and synthesize the result.
11. Persist telemetry and compact provenance-aware summaries.

## 4. Task classification

Complexity values:

- simple: one bounded outcome, low ambiguity, few/no dependencies, no substantial external research or multi-stage implementation. Prefer one model call or deterministic local logic.
- complicated: multiple meaningful steps, specialist knowledge, dependencies, non-trivial context or validation. Use a DAG and a limited number of specialist nodes.
- too_complicated: broad or uncertain scope, multiple domains, deep dependencies, significant implementation/research, high consequence, conflicting evidence or need for independent verification. Escalate to Strong.

Do not classify by action count alone. Ten independent low-risk simple actions are not automatically too_complicated.

Classifier dimensions:
- number of distinct actions/outcomes;
- domain count and specialist capabilities;
- dependency depth and graph complexity;
- ambiguity and missing requirements;
- context size and source artifacts;
- need for browsing, code execution, repository access or other tools;
- verification difficulty and failure impact;
- privacy/security classification;
- estimated duration, token/cost envelope and deadline pressure.

Suggested typed contract:

    class TaskClassification(BaseModel):
        complexity: Literal["simple", "complicated", "too_complicated"]
        confidence: float
        domains: list[str]
        action_count: int
        dependency_depth_estimate: int
        risk_level: Literal["low", "medium", "high", "critical"]
        requires_tools: list[str]
        rationale_summary: str
        signals: dict[str, float]

The model may propose a classification, but deterministic rules enforce safety, budget and Strong escalation. Store classification, confidence, factors and rationale summary; never store hidden chain-of-thought. If confidence is low, ask one focused clarification only when necessary; low confidence alone must not trigger unbounded delegation.

## 5. Auto resolution and runtime transitions

Initial Auto mapping:
- General bounded simple task: shared single-task path, no specialist mode required.
- Software implementation/debugging/repository change: hifDev.
- SQL/schema/database performance/data migration: hifBD.
- System design/cloud topology/technical architecture: hifArc.
- Autonomous team creation/agent lifecycle: hifAgent.
- Any too_complicated classification: hifStrong.

Automatic transitions may occur when new requirements reveal multiple domains, scope expands, verification fails, required capabilities are missing or external constraints materially change the plan.

Every transition must:
- retain root session and global task identity;
- preserve completed validated artifacts;
- pass only relevant scoped context;
- recalculate remaining budgets;
- record source mode, destination mode and reason;
- enforce a transition limit/cooldown to prevent oscillation;
- preserve approval gates.

Escalation to Strong is mandatory when reclassification becomes too_complicated. Strong remains root owner even if it delegates simpler subtasks to cheaper paths. An explicit domain mode selects the domain workstream, but does not suppress mandatory Strong escalation.

## 6. Hierarchical orchestration guardrails

Initial configurable defaults (not performance guarantees):

| Setting | Initial default |
|---|---:|
| Maximum delegation depth (root = 0) | 3 |
| Maximum active child orchestrators per root | 10 |
| Maximum agents per child orchestrator | 3 |
| Maximum global provider calls in flight | 12 |
| Maximum nodes per local DAG | 12 (existing schema limit) |
| Maximum mode transitions | 3 |

Use logical child orchestrators, not a full HIF process per task. Existing HIF_MAX_PARALLEL_TASKS and HIF_MAX_PROVIDER_PARALLEL remain authoritative until the global budget manager is implemented. Effective concurrency is the minimum of all applicable limits.

Each child receives a reserved sub-budget. Root reserves capacity for synthesis, verification and recovery. A child cannot consume another child's allocation without root reallocation.

## 7. Provider/model assignment

Keep three concepts separate:
1. Agent: role, mission, memory and acceptance criteria.
2. Provider/model: inference endpoint, capabilities, context window, pricing and health.
3. Execution runtime: API, MCP, local Python, shell, Git or another explicitly enabled tool.

Apply hard filters before ranking:
- required modality and capabilities;
- privacy/data residency and provider allowlist;
- context window and structured-output support;
- provider health and cooldown;
- remaining budget and configured quota threshold;
- tool/runtime compatibility.

Rank eligible candidates using configurable weights for quality history, reliability, latency and cost. Record measured token usage and latency separately from estimated costs and unofficial quota estimates. Never assume a consumer subscription grants API access.

## 8. Quality evaluation and solution selection

Candidate output should include deliverable, assumptions, evidence/artifact references, tests/checks, limitations and confidence summary.

Suggested initial weights:
- technical correctness: 25%;
- fulfillment of user request: 20%;
- evidence and reliability: 20%;
- implementation quality: 15%;
- security and policy compliance: 10%;
- performance and maintainability: 10%.

A blocking security/policy failure disqualifies a candidate regardless of weighted score. For code/database work, deterministic tests and validation outweigh model self-rating. For architecture/research, evaluate traceability, consistency, trade-offs and source quality. Select the most suitable valid result, not necessarily the longest or highest raw score. Preserve unresolved disagreements.

## 9. Time estimation and telemetry

Record classification/planning duration, queue wait, task type, provider/model, time to first token where available, provider execution duration, retry/fallback duration, verification duration, end-to-end elapsed time, token usage, cost metadata, resource pressure, concurrency, mode transitions, test outcomes and human corrections.

Use historical P50/P90 values by task type, mode and provider/model only when sample size is sufficient. Otherwise label estimates indicative and state that history is insufficient. Never fabricate precise remaining-time values.

## 10. Memory and provenance

Memory layers:
- Working Memory: current node/agent execution.
- Session Memory: current root run and dependencies.
- Project Memory: validated architecture, conventions and decisions.
- Execution Memory: outcomes, latency, failures, tests and corrections.
- Long-Term Memory: durable authorized summaries only.

Each item includes source/provenance, timestamp, confidence, scope, sensitivity and retention. Agents see only the keys required for their assignment. Never share secrets or hidden model reasoning as memory. Keep SQLite as the first persistence backend; add migrations and repository abstractions before introducing another database/cache.

## 11. API and command contracts

All entry points normalize to a shared request:

    {
      "goal": "User request",
      "mode": "auto",
      "context": {},
      "constraints": {
        "deadline_seconds": null,
        "max_cost_usd": null,
        "max_tokens": null,
        "allowed_providers": [],
        "privacy_class": "approved_provider"
      },
      "approval_policy": "required_for_sensitive_actions"
    }

Backward-compatible CLI evolution:

    hif run "Build a REST API" --mode auto
    hif run "Optimize this query" --mode bd
    hif run "Design an Azure architecture" --mode arc
    hif run "Refactor this repository" --mode dev
    hif run "Investigate this complex incident" --mode strong
    hif run "Create a specialist agent team" --mode agent

Host skill aliases: /hifDev, /hifBD, /hifArc, /hifStrong, /hifAgent and /hif for Auto. Slash commands are host integration aliases, not Python CLI syntax. Host adapters map aliases to the same validated request contract. Gateway and MCP expose the same mode enum.

## 12. Proposed package layout

    src/hif/
      core/
        intent.py
        classifier.py
        estimator.py
        mode_resolver.py
        root_orchestrator.py
        recursive_planner.py
        budgets.py
        telemetry.py
        quality.py
      modes/
        base.py
        registry.py
        dev/
        bd/
        arc/
        strong/
        agent/
      agents/
        models.py
        factory.py
        lifecycle.py
        roles/
      execution/
        scheduler.py
        permissions.py
        artifacts.py
        git_workspace.py
      existing:
        cli.py, config.py, engine.py, planner.py, providers.py,
        router.py, resources.py, schemas.py, storage.py, gateway.py,
        mcp_server.py

This is a target layout. Do not create empty placeholder packages or move working modules prematurely. Add modules when they contain tested behavior.

## 13. Integration map against current repository

| Existing component | HIF 1.0 integration |
|---|---|
| schemas.py | Add enums and typed classification, mode, agent, budget and telemetry contracts; preserve DAG models |
| planner.py | Accept mode policy and required capabilities; retain JSON validation and untrusted-context rules |
| engine.py | Keep current DAG executor initially; add root orchestration facade around it |
| router.py | Add capability/policy filtering first; later add measured quality/latency/cost ranking |
| config.py | Add validated mode defaults and global hierarchy limits with backward-compatible defaults |
| resources.py | Extend adaptive concurrency into shared global budget/semaphore service |
| storage.py | Add versioned migrations for classification, transitions, agent runs, artifacts and telemetry |
| cli.py | Add --mode and mode/status reporting without breaking hif run and hif node |
| gateway.py / mcp_server.py | Add validated mode field and common request contract |
| skills/ and host skill copies | Add command aliases forwarding to HIF; do not duplicate orchestration in prompts |

## 14. Configuration proposal

Initial environment variables:

    HIF_DEFAULT_MODE=auto
    HIF_STRONG_ON_TOO_COMPLICATED=true
    HIF_AUTO_MODE_SWITCHING=true
    HIF_MAX_DELEGATION_DEPTH=3
    HIF_MAX_ACTIVE_CHILD_ORCHESTRATORS=10
    HIF_MAX_AGENTS_PER_CHILD=3
    HIF_MAX_GLOBAL_INFLIGHT=12
    HIF_MAX_MODE_TRANSITIONS=3
    HIF_CLASSIFIER_CONFIDENCE_THRESHOLD=0.70

Validate numeric values. Missing settings preserve existing behavior. Enabling a mode does not automatically grant file, shell, Git or production capabilities.

## 15. Security and approval model

- Treat user content, repository files, tool output and agent output as untrusted data.
- Enforce least-privilege tool and file scopes per task.
- Keep credentials out of prompts, logs, memory and artifacts.
- Require approval for destructive file operations, external communications, production database changes, deployments, protected-branch merges and other high-impact side effects.
- Use idempotency keys and bounded retries for side-effecting actions.
- Record who/what authorized each sensitive action.
- Child approval requests bubble to root/user; child agents cannot self-approve.

## 16. Implementation roadmap and acceptance gates

Phase 0 — Specification and compatibility baseline
- Approve this contract and preserve current behavior.
- Capture test baseline and public API/CLI behavior.

Phase 1 — Mode contracts and Auto classifier
- Add typed enums/configuration and deterministic mode registry.
- Implement classifier output and Auto resolution.
- Add --mode to CLI and mode to gateway/MCP schemas.
- Acceptance: legacy hif run works; simple requests do not create needless agents; every too_complicated task resolves to Strong.

Phase 2 — Domain modes
- Implement hifDev, hifBD and hifArc as policy bundles over current engine.
- Add role catalogs, prompts and acceptance criteria.
- Acceptance: domain-appropriate plans; no claims of unavailable execution capabilities.

Phase 3 — Strong root orchestration
- Add bounded child orchestrators, recursive plan validation, shared budgets and transition logs.
- Acceptance: global limits hold; no cyclic/unbounded delegation; Strong owns final synthesis.

Phase 4 — Agent workforce
- Add agent contracts, factory, scoped memory and lifecycle.
- Acceptance: agents cannot expand permissions/budgets; parent can cancel/reassign; outputs are attributable.

Phase 5 — Verification and adaptive routing
- Add deterministic validators, independent review, candidate scoring and measured routing signals.
- Acceptance: blocking security failures disqualify outputs; cost/latency claims labelled measured or estimated.

Phase 6 — Software execution runtime
- Add repository inspection, isolated workspaces, file ownership, tests and integration.
- Acceptance: no direct main writes; integrate only after tests/review; sensitive actions require approval.

Phase 7 — Telemetry, benchmarking and hardening
- Add historical P50/P90 estimates, regression benchmarks, failure injection and load tests.
- Acceptance: estimated/measured metrics are distinct; concurrency and budget invariants hold under load.

## 17. Minimum test matrix

- Each complexity class and confidence boundary.
- Ten independent simple actions do not automatically become too_complicated.
- Every too_complicated task escalates to Strong, including explicit domain-mode requests.
- Auto selects Dev, BD, Arc and Agent for matching domain requests.
- Mode transition preserves root session, completed outputs and budget accounting.
- Transition loop protection and maximum delegation depth.
- Child budget exhaustion, cancellation, provider cooldown and fallback.
- Provider capability/privacy filtering before ranking.
- DAG cycle, missing dependency and duplicate ID rejection.
- Concurrent write conflict detection and workspace isolation.
- Sensitive action approval, denial and audit trail.
- Legacy CLI, gateway, MCP and existing tests remain compatible.

## 18. Non-goals for the first increment

- A full OS process/container for every agent by default.
- Calling every provider/model for every task.
- Assuming provider subscription quotas are observable through API usage.
- Unbounded recursion, concurrency, token spending or autonomous tool access.
- Automatic production deployment, database mutation or Git merge without approval.
- Replacing SQLite before requirements and load are measured.
- Claiming native slash-command support in a host without installing the matching skill/plugin.

## 19. Implementation status rule

This document defines the target contract. It does not claim the five modes, recursive orchestrators, coding runtime, scoring engine or automatic transitions are implemented. A capability is shipped only after code, tests and documentation are merged.


## 20. Conversation UX and token governance

The conversation is HIF's primary user interface. The normative requirements for the run header, real-time orchestrator/agent activity, event-driven progress, hierarchical token accounting, actual-versus-estimated usage, fast project intake with bounded block readers, progressive validation and the user-facing remaining-work checklist are defined in [HIF 1.0 — Conversation UX, Token Governance and Progressive Delivery](HIF-1.0-CONVERSATION-UX-TOKEN-MANAGEMENT.md).

These requirements are release-critical: large-scale multi-agent fan-out must not ship before atomic hierarchical budget reservation, per-call usage accounting, truthful progress state and budget-exhaustion behavior are tested.


## 20. Multi-host skills and subscription-aware adapters

HIF 1.0 must be consumable both as a standalone local/remote orchestrator and as a portable workflow skill inside supported AI hosts.

### 20.1 Two execution modes

- Native subscription mode: the host assistant uses its currently selected model and only its own native tools/sub-agents. HIF instructions guide task decomposition, compact context, validation and checklists. Host-native model selection, token accounting, quota and billing remain controlled by the host.
- Connected HIF mode: the host invokes HIF through an explicitly configured MCP/tool connection. HIF controls its own run/session, configured provider adapters, budget, agents, memory and telemetry.

The skill must detect which mode is actually available. It must not pretend connected HIF execution occurred when MCP tools are missing.

### 20.2 Subscription and authentication boundary

A ChatGPT, Claude, Gemini, NotebookLM or Copilot consumer subscription is not automatically a provider API credential. A native skill can guide the current host model under the host's subscription. Independent HIF calls to other providers require a provider-authorized API/OAuth/connector path and may incur separate charges.

Do not scrape browser cookies, automate consumer chat pages to evade API billing, reuse hidden sessions, rotate accounts to bypass quotas or claim access to private subscription limits. Respect host feature availability, organization policies, official authentication and provider terms.

### 20.3 Host adapter contract

Each host adapter should declare:
- host/product and supported versions;
- skill format and installation path;
- available native delegation, tools and MCP transport;
- authentication mechanism and permission scopes;
- whether local runtime or remote HTTPS gateway is required;
- which token/usage metrics the host exposes;
- supported progress streaming or polling behavior;
- known plan, workspace and admin restrictions.

The adapter maps host commands to the common HIF request contract. It must not duplicate planner, token manager or agent orchestration logic.

### 20.4 Target host support

- ChatGPT: portable skill where Skills import is available; connected mode via supported custom MCP app and deployed HTTPS gateway where plan/workspace controls allow.
- Claude: portable custom skill where enabled; Claude Code local skill plus stdio MCP; web/Desktop connected tools only where officially supported.
- Gemini: portable skill where available; Gemini CLI local skills plus stdio MCP; Gemini web requires an explicitly supported remote tool path.
- GitHub Copilot: Agent Skills and MCP configuration in supported IDE/agent harnesses, subject to product and organization policy.
- Microsoft 365 Copilot: Copilot Studio agent/tool integration with authenticated remote HIF gateway and tenant governance; do not conflate with GitHub Copilot or consumer Microsoft Copilot.
- NotebookLM: provide a companion research workflow and source-pack format. Do not call it a native HIF skill, general agent host or MCP client unless Google exposes and HIF implements an official integration.
- Codex: portable Agent Skill and local/remote MCP configuration in the supported host.

### 20.5 User experience

The same /hif, /hifDev, /hifBD, /hifArc, /hifStrong, /hifAgent and /hifnode intent aliases should map to the common request schema where the host supports custom skill instructions. Aliases are not guaranteed native slash commands. The UI should state whether execution is Native subscription or Connected HIF, and distinguish host-reported usage from HIF/provider-reported usage.

### 20.6 Acceptance criteria

- Skill installation works without HIF runtime installation and clearly describes the reduced native mode.
- Connected mode is used only when MCP/tool connectivity is verified.
- The skill never claims a host's subscription gives HIF independent API access.
- Host adapters expose their actual available delegation and usage capabilities.
- NotebookLM workflow is documented as a manual source-grounded handoff until an official integration exists.
- Cross-host session memory contains only information explicitly stored in HIF and approved by the user.


## 21. AI Tech Lead and cross-agent engineering consistency

HIF is accountable for the coherence of the complete software project. Delegating implementation does not delegate away architectural responsibility: the root AI Tech Lead owns the architecture baseline, contracts, integration sequence and final quality gates.

### 21.1 Project constitution and source of truth

Before parallel development, HIF creates or refreshes a versioned Project Constitution containing:
- repository structure and module boundaries;
- chosen languages, frameworks, runtime versions and dependency policy;
- architectural decisions and approved patterns;
- naming, formatting, error-handling, logging and observability conventions;
- API contracts, event schemas and database ownership;
- security, privacy, authentication and authorization requirements;
- testing strategy, quality gates and definition of done.

The constitution is stored as a project artifact (and optionally as repository documentation) with a revision/hash. Agents must reference the same approved revision. Changes require an explicit proposal and approval by the root Tech Lead; agents cannot silently redefine project-wide standards.

### 21.2 Project Structure and Dependency Graph

HIF builds a structural map before assigning development:
- directories, packages, services and module responsibilities;
- imports/references and build dependencies;
- API routes, DTOs, events and integration boundaries;
- database tables, migrations, entities and repositories;
- frontend routes, components, state and service clients;
- tests, deployment manifests, environment/configuration and CI workflows.

Represent module dependencies as a directed graph. Detect cycles, duplicated responsibilities, forbidden dependencies and layer violations. Define allowed dependency direction (for example UI -> application/API contracts -> domain; domain must not depend on infrastructure) according to the project's chosen architecture, not a universal hard-coded pattern.

### 21.3 Developer task contracts and ownership

Every developer agent receives a task contract:
- unique task and owner;
- exact module/file scope and explicit non-goals;
- approved constitution revision;
- interfaces/contracts to consume and produce;
- upstream dependencies and downstream consumers;
- expected files/artifacts and output schema;
- acceptance tests, budget and deadline;
- branch/worktree or workspace isolation instructions.

Maintain a file/module ownership registry. Avoid concurrent writes to the same files. If two tasks need a shared file, appoint one owner or create a separate integration task. Shared contract changes must be proposed to the Tech Lead before implementation.

### 21.4 Contract-first parallel development

Parallel agents must not invent incompatible interfaces independently.

1. Tech Lead defines or approves API, DTO, event, database and module contracts.
2. Backend, frontend, database and integration agents receive the same versioned contract references.
3. Teams may work in parallel against approved contracts or mocks.
4. Contract changes produce a new version and impact analysis.
5. Downstream tasks are notified and revalidated before merge.
6. Integration Manager checks compatibility across implementations.

Contracts should be machine-checkable where possible (OpenAPI, JSON Schema, protobuf, SQL migration metadata, typed interfaces). Store contract version/hash with each task result.

### 21.5 Cross-model normalization and consistency

Agents may use different providers/models, but their outputs must follow common HIF task and artifact schemas. Normalize:
- terminology and identifiers;
- file paths and module names;
- language/framework versions;
- API and schema names;
- assumptions, evidence, risks and uncertainty;
- test reports and completion status.

Model-specific suggestions are proposals, not project decisions. HIF compares them against the Project Constitution, source code and approved contracts. When models disagree, Tech Lead resolves the difference using evidence and project constraints; do not silently blend incompatible designs. Never assume model brand guarantees expertise.

### 21.6 Integration Manager and merge gates

Use an Integration Manager as a dedicated logical role under the root Tech Lead. It:
- collects branch/worktree outputs and change manifests;
- checks file ownership and overlapping edits;
- verifies contract and dependency compatibility;
- runs formatters, linters, type checks, builds and tests;
- inspects migrations and generated artifacts;
- checks secrets, dependency vulnerabilities and policy violations;
- detects duplicated code, circular imports and architectural boundary violations;
- resolves conflicts or returns a precise correction task to the responsible agent.

Merge gates:
- no unreviewed cross-module contract break;
- no unresolved merge conflict;
- all mandatory tests for affected modules pass;
- no blocking security finding or leaked secret;
- database migrations are ordered, reversible where feasible and validated;
- architecture/constitution deviation is documented and approved;
- change set remains within assigned scope.

HIF must not claim consistency merely because every individual agent reports success. Integration validation is a separate required phase.

### 21.7 Continuous architecture and code consistency checks

At intake and after integration, evaluate:
- project tree against approved target structure;
- dependency graph and layer rules;
- duplicate modules and competing implementations;
- naming and type consistency;
- API/DTO/database field compatibility;
- dependency/version drift;
- configuration and environment variable consistency;
- test coverage and test ownership;
- security, error handling, logging and observability conventions.

Use deterministic tools first (AST/parser, compiler, type checker, linter, dependency scanner, schema diff, tests). Use LLM review for semantic issues that static tools cannot establish. Report actual tool output and distinguish not-run from passed.

### 21.8 Change impact and regression routing

When a contract, shared module or schema changes, compute downstream impact from the dependency graph. Reopen only affected tasks/tests, not the whole project. Route regression failures to the owning agent with:
- failing command and exact output;
- relevant diff and source references;
- contract/constitution revision;
- minimal reproduction and acceptance condition.

The root keeps a single project-level status and does not mark a milestone complete until dependent integration gates pass.

### 21.9 Human governance and protected actions

The Tech Lead may plan, inspect, propose and validate within granted permissions. Explicit approval is required for protected branch merges, releases, deployments, production migrations, destructive operations, credential changes and externally visible actions. Preserve diffs, test evidence and rollback instructions.

### 21.10 Acceptance criteria

- HIF creates a project map and constitution before multi-agent coding.
- Every implementation task has explicit ownership, scope, contracts and acceptance tests.
- Agents consume the same approved contract versions.
- Concurrent edits to shared files are prevented or serialized through an integration owner.
- Different model outputs are normalized and checked against project source of truth.
- Integration is a separate phase with deterministic build/test/security/contract checks.
- Breaking contract changes trigger targeted downstream revalidation.
- Final status distinguishes agent-completed work from integrated and validated project work.
- A project is not reported as coherent or complete until required integration gates pass.


## 22. Analyst and Maintenance roles in the AI delivery organization

HIF's software delivery team must include two additional first-class specialist roles: **Business/System Analyst** and **Maintenance & Reliability Engineer**. They work under the root AI Tech Lead and share the Project Constitution, requirements baseline, architecture, contracts and token/resource governance.

### 22.1 Analyst — Business and System Analysis

The Analyst translates user intent and business needs into unambiguous, testable requirements before implementation.

Responsibilities:
- conduct structured requirement discovery and identify ambiguities, assumptions, constraints and stakeholders;
- map business processes, user journeys, use cases, roles and permissions;
- define functional and non-functional requirements, acceptance criteria and edge cases;
- produce user stories, use-case specifications, process flows, data definitions and traceability matrix;
- identify regulatory, privacy, accessibility, audit and operational requirements relevant to the project;
- analyze impact of requirement changes across modules, APIs, data models, tests and documentation;
- validate that proposed technical design satisfies the actual business need;
- maintain a prioritized backlog and flag dependencies or decisions requiring user approval.

Deliverables:
- concise requirements brief and scope boundaries;
- user stories/use cases with Given/When/Then acceptance criteria where appropriate;
- business process diagrams and role/permission matrix;
- functional/non-functional requirements register;
- requirement-to-design-to-test traceability matrix;
- open questions, assumptions, risks and change log.

Rules:
- do not invent business rules where user intent is unclear;
- distinguish confirmed requirements from assumptions and recommendations;
- ask the user only for decisions that materially affect scope or correctness;
- keep requirements linked to acceptance tests and implementation tasks;
- route scope changes to the root Tech Lead for impact analysis before agents change contracts.

### 22.2 Maintenance & Reliability Engineer

The Maintenance Engineer owns operability and long-term maintainability, not just fixing bugs after delivery.

Responsibilities:
- inspect existing codebase health, technical debt, obsolete dependencies and known defects;
- triage incidents and bugs by severity, impact, reproducibility and urgency;
- diagnose logs, traces, metrics, error reports and failed jobs where access is authorized;
- propose safe fixes, patches, upgrades and refactoring with regression coverage;
- maintain dependency and runtime compatibility, vulnerability remediation and patch cadence;
- review backup/restore, recovery, monitoring, alerting, capacity, performance and operational runbooks;
- plan preventive maintenance, recurring checks and lifecycle/upgrade work;
- verify backward compatibility, data migration safety and rollback/recovery paths;
- track recurring defects and root causes rather than repeatedly applying superficial fixes.

Deliverables:
- maintenance assessment and technical-debt register;
- incident/bug triage with severity and impact;
- root-cause analysis and corrective/preventive actions;
- patch/upgrade plan and compatibility matrix;
- regression tests, operational runbooks and recovery/rollback instructions;
- maintenance backlog with owner, priority, dependencies and status.

Rules:
- distinguish diagnosis, proposed fix, implemented fix and production-verified resolution;
- production access, restarts, data changes, migrations, deployment and configuration changes require explicit authorization;
- do not delete logs, data or backups as routine cleanup without approval and retention checks;
- prioritize reversible, observable and tested changes;
- preserve evidence and post-change validation results.

### 22.3 Updated AI software delivery team

The default logical team is now:
- Root AI Tech Lead / Orchestrator — accountable for architecture, coordination and final acceptance;
- Business/System Analyst — requirements, workflows and acceptance criteria;
- Solution Architect — structure, boundaries and technical decisions;
- Backend Developer;
- Frontend Developer;
- Database Engineer;
- AI/OCR Engineer when relevant;
- QA & Test Engineer;
- Security Engineer when risk requires;
- Maintenance & Reliability Engineer;
- Integration Manager — cross-module contracts, merge and system-level validation;
- DevOps/Platform Engineer when deployment/operations are in scope.

This is a role catalogue, not a mandatory fixed-size team. HIF instantiates only roles required by the mission. For a small change, Analyst and Tech Lead may be one logical assignment; Maintenance may be omitted unless the task touches existing behavior, reliability or operations. For a production incident, Maintenance may lead diagnosis while Analyst clarifies business impact and Tech Lead controls remediation.

### 22.4 Lifecycle integration

1. Analyst clarifies the request and defines acceptance criteria.
2. Tech Lead approves scope and assigns architecture/contracts.
3. Developers implement against the approved baseline.
4. QA verifies functional and regression criteria.
5. Maintenance reviews operability, compatibility, observability and recovery when applicable.
6. Integration Manager verifies system-level coherence.
7. Tech Lead accepts or returns work for correction.
8. The user receives completed, validated and remaining items with evidence.

### 22.5 Acceptance criteria

- Analyst outputs confirmed requirements, assumptions, open questions and traceable acceptance criteria.
- Every implementation task links to at least one requirement or explicitly records why it is technical-only.
- Maintenance assessment identifies relevant risks, debt and operational requirements for existing/production systems.
- Production fixes include root cause, regression test and rollback/recovery plan where applicable.
- HIF instantiates these roles selectively and does not inflate agent count for simple tasks.
- User-facing status distinguishes analysis complete, implementation complete, integrated, validated and production verified.


## 23. Technical Leader — real-time cross-channel coordination agent

HIF adds a dedicated **Technical Leader** role for fast operational coordination across parallel specialist workstreams and connected communication channels. This role complements, but does not replace, the root AI Tech Lead.

### 23.1 Role distinction

- Root AI Tech Lead: owns project architecture, technical decisions, scope, contracts, priorities and final acceptance.
- Technical Leader: continuously coordinates incoming specialist updates, detects blockers and inconsistencies, prepares concise actionable responses, and keeps parallel workstreams moving.
- Integration Manager: performs the formal code/contract integration and validation gates.

The Technical Leader may recommend decisions and prepare fixes, but cannot silently override the Project Constitution or approve protected production actions.

### 23.2 Multi-channel intake and parallel response

Where the host/runtime has authorized access to channels (for example task comments, issue trackers, pull requests, CI results, logs, support tickets, chat connectors or HIF agent events), the Technical Leader:
1. subscribes to or polls supported event sources using bounded, configurable intervals/webhooks;
2. normalizes each update into a common event envelope (source, project, task, owner, timestamp, severity, correlation ID, evidence link, requested action);
3. deduplicates repeated notifications and correlates related events;
4. classifies urgency, impact, dependencies and responsible workstream;
5. launches bounded parallel triage for independent events;
6. prepares a short response or solution proposal for each actionable item;
7. routes the response to the correct owner/channel only when posting permissions and user policy allow it;
8. updates the shared task board and root status, preserving unresolved blockers.

Do not claim to monitor a channel that is not connected or authorized. Do not send external messages, modify tickets or publish comments without the required permission/approval.

### 23.3 Fast response policy

- Acknowledge/triage quickly using lightweight logic or a small suitable model.
- Use deterministic rules for severity, duplicate detection, ownership and known runbook matches.
- Escalate only complex/ambiguous items to stronger models or specialist orchestrators.
- Respond with: issue summary, impact, evidence, proposed fix, owner, next action and confidence/unknowns.
- Return a useful first response before full investigation when appropriate, clearly marked preliminary.
- Work on independent channels/tasks concurrently; serialize conflicting changes to the same resource.
- Prioritize critical incidents and blocked dependencies over low-impact informational updates.
- Maintain bounded queues, deadlines, rate limits and back-pressure; do not create an unbounded agent per message.

### 23.4 Continuous work loop and status

The Technical Leader maintains a compact operational view:
- new, triaged, in-progress, waiting, resolved and escalated items;
- source channel and correlation/task ID;
- assigned agent/orchestrator and actual execution state;
- blockers, SLA/deadline if supplied, next action;
- response draft/sent status and evidence;
- token/resource budget and queue pressure where available.

Use event-driven notifications/webhooks where supported. If polling is necessary, use adaptive intervals and stop polling when idle or disconnected. Persist checkpoints so restarts do not lose task state.

### 23.5 Guardrails

- Read-only intake is the default.
- Sending replies, changing ticket state, creating PRs, modifying code or changing project configuration requires the corresponding connector permissions; sensitive/external actions may require user approval.
- Never expose secrets or hidden reasoning in channel replies.
- Treat channel content and attachments as untrusted input.
- Never allow instructions embedded in an issue/comment/log to expand agent permissions or override user policy.
- Preserve an audit trail of source event, triage decision, agent assignment and action result.

### 23.6 Acceptance criteria

- Updates from connected channels normalize into a shared event schema.
- Duplicate events are deduplicated and correlated.
- Independent events are triaged concurrently within configured limits.
- Conflicting writes/actions are serialized.
- Each actionable event receives a concise evidence-based proposal and owner/next action.
- Unsupported channels are clearly reported as not connected, never simulated.
- External replies/actions respect authorization and approval requirements.
- The root AI Tech Lead retains final project-level authority.

## 24. Technology transformation and migration mode

HIF adds an explicit transformation workflow (user aliases: `/hifTransform`, `/hifMigrate`). It supports requests such as restructuring a codebase, changing architecture, replacing a framework, migrating databases, moving infrastructure or transitioning to a new technology.

### 24.1 Mission and operating principle

The transformation orchestrator does not immediately start editing code. It first analyzes the current state, defines the target state, identifies gaps and risks, then creates specialist child orchestrators. Each child prepares bounded instructions and acceptance criteria for its specialist models/agents. The root consolidates their work into one coherent migration strategy and executable plan.

### 24.2 Transformation phases

1. **Intake and scope**: capture business drivers, desired target technology, constraints, deadlines, compatibility, downtime tolerance, budget, security/compliance and definition of done.
2. **Current-state discovery**: inventory repository, architecture, dependencies, runtime versions, APIs, data model, integrations, tests, deployment, operational practices and known pain points.
3. **Target-state design**: compare viable target patterns and versions; validate official support/lifecycle and compatibility where current facts matter.
4. **Gap and impact analysis**: map source-to-target components, data structures, APIs, auth, configuration, infrastructure, CI/CD, observability and team skills.
5. **Child orchestrator creation**: instantiate only relevant workstreams, for example:
   - application/code structure and refactoring;
   - target framework/language and dependency compatibility;
   - database/data migration and integrity;
   - API/integration and contract migration;
   - frontend/UI migration;
   - cloud/infrastructure/network/identity;
   - security/privacy/compliance;
   - testing/performance/reliability;
   - release, cutover, rollback and maintenance.
6. **Specialist instruction generation**: each child creates a concise context pack, source references, target standards, exact tasks, non-goals, output schema, model capability requirements, token/time budget and acceptance tests. Avoid forwarding the full repository/context to every model.
7. **Parallel analysis and option comparison**: independent children analyze in parallel. Compare at least viable options where a material choice exists, including trade-offs, cost/risk/effort and reversibility.
8. **Root synthesis and dependency plan**: root resolves contradictions, approves a common target architecture and creates a dependency-aware roadmap with milestones, owners, prerequisites and estimates labelled by evidence quality.
9. **Approval gate**: present target architecture, impact, costs/risks, data handling, downtime, rollback and phased plan. Obtain user approval before implementation or production-impacting actions.
10. **Execution and validation**: after approval, implement in bounded increments, use feature flags/parallel run where appropriate, migrate data with reconciliation, run compatibility/security/performance/regression tests and produce cutover evidence.
11. **Handover and maintenance**: update architecture docs, runbooks, monitoring, backup/recovery, ownership and maintenance backlog.

### 24.3 Transformation plan deliverable

The root must produce:
- current-state architecture and inventory;
- target-state architecture and rationale;
- source-to-target component/technology mapping;
- options and trade-off matrix;
- dependency graph and workstream ownership;
- detailed action plan with phases, deliverables and acceptance criteria;
- risk register, mitigations and open decisions;
- migration/data strategy, cutover and rollback;
- test/validation strategy;
- resource/token budget and confidence-labelled timeline;
- post-migration maintenance and knowledge-transfer plan.

### 24.4 Model orchestration and efficiency

Each child orchestrator chooses its own specialist model instructions based on task capability, available tools, quality evidence, latency, privacy and budget. It must not assume a particular vendor is always best. Use lightweight models for inventory, extraction and routine compatibility mapping; advanced models for architecture trade-offs and complex migration design; deterministic tooling for dependency scans, schema diffs, builds and tests.

Root allocates child budgets and limits parallelism based on resource pressure. Child agents return compact structured reports and evidence references, not repeated full-context essays. Escalate only unresolved risks or failed validation.

### 24.5 Safety and approval

- Analysis and planning may run without modifying the project.
- Code edits, schema changes, infrastructure changes, data migration, cutover, deployment and destructive operations require explicit approval at the appropriate stage.
- Never assume a migration is reversible; document irreversible steps and recovery alternatives.
- Preserve source snapshots, backups, checksums, migration logs and reconciliation results where applicable.
- Do not claim migration completion until target behavior and data integrity have been validated.

### 24.6 Acceptance criteria

- Transformation begins with current-state discovery and target-state clarification.
- Child orchestrators are created by workstream, not indiscriminately.
- Each child emits actionable model/agent instructions and acceptance tests.
- Root reconciles cross-workstream architecture and dependencies into one plan.
- User receives a complete phased action plan before code or production changes.
- Execution requires approval and produces evidence for tests, data reconciliation, cutover and rollback readiness.


## 25. ZirconAI Local Runtime, trusted updates and rapid installation

### 25.1 Product identity and publisher trust

The local distribution is published as **HIF by ZirconAI.fr**. Publisher branding is not itself a security signature. Release artifacts must be cryptographically verifiable.

Release requirements:
- publish version, build identifier, source commit, supported platforms and minimum runtime;
- generate a release manifest listing every artifact path, SHA-256 digest, size and version;
- sign the manifest and release metadata using an offline-protected Ed25519 release key (or a platform-native code-signing certificate where applicable);
- distribute the public verification key/fingerprint through an independently trusted ZirconAI.fr channel and pin it in the installer;
- sign Windows executables/installers with an Authenticode certificate when available; sign macOS packages/notarize where distributed as native applications;
- verify publisher signature, manifest signature, hashes, compatibility and rollback policy before installation/update;
- reject unsigned, tampered, expired or downgrade releases unless an explicit recovery procedure is used;
- never embed the private signing key in source code, CI logs, packages or the client installer.

A text footer or displayed brand name must never be represented as proof of cryptographic publisher identity.

### 25.2 Fast, minimal local installation

The default local install should be per-user and require no administrator rights:
1. detect OS, architecture, Python/runtime availability and supported host skill locations;
2. download one small signed bootstrap/manifest;
3. verify signature before executing or extracting release payloads;
4. install a pinned, compatible runtime in an isolated environment (or a self-contained signed binary when packaging is mature);
5. install the HIF CLI, local MCP stdio connector and selected portable skills;
6. create per-user data/config/cache directories with restrictive permissions;
7. run `hif doctor` and a local health/self-test;
8. display the exact features available in skill-only, local-runtime and connected-provider modes.

Keep installation modular: users may install only skills, the local lightweight runtime, or the complete local runtime plus MCP. Do not install GPU frameworks or local LLM weights by default. Provider API credentials are optional for local indexing/planning utilities but required for independent remote provider inference.

Installer performance goals (targets, not claims): small bootstrap, parallel verified downloads where safe, reuse compatible cached wheels/artifacts, avoid reinstalling unchanged files, and complete a normal workstation install in seconds to a few minutes depending on network/runtime availability. Measure cold and warm install time on supported OS images before publishing speed claims.

### 25.3 Dynamic update architecture

Use a signed update channel with stable, preview and rollback-capable release tracks:
- a lightweight updater checks a signed version manifest on startup or an adaptive schedule; users/admins can disable automatic checks;
- verify signature and artifact hashes before applying any update;
- download only changed components when delta updates are supported and safe;
- stage the new version side-by-side, validate dependencies and run smoke tests;
- atomically switch the active version only after successful validation;
- retain the last known-good version and support automatic rollback on failed startup/health checks;
- preserve user configuration, credentials, SQLite state and project data; run explicit versioned database migrations with backup and rollback strategy;
- report release notes, changed skills/runtime components, compatibility and required restart;
- allow enterprise policy to pin versions, defer updates or use an internal mirror.

Do not replace running Python modules in-place. The updater should stage files and restart/reload the service at a safe boundary. For skill files, update atomically; host assistants may cache skills until a new session/reload, so HIF must not promise instantaneous host-side skill reload where the host does not support it.

### 25.4 In-memory adaptive pipeline engine

HIF adds a priority-aware pipeline scheduler. The in-memory representation is an execution cache, not the sole durable source of truth.

Each pipeline has:
- pipeline/run ID, parent/root ID and project/session scope;
- request classification and priority;
- DAG nodes, dependencies and state;
- deadline/SLA when provided;
- estimated token/cost/time budgets and actual usage;
- resource requirements and provider constraints;
- checkpoint/artifact references and retry policy;
- cancellation, pause/resume and idempotency metadata.

Persist critical state and checkpoints in SQLite so a process restart can recover safely. Keep only active scheduling state, small queues and hot metadata in memory. Bound memory by configurable limits and evict completed run objects after durable persistence.

### 25.5 Request classification and priority policy

Classify every incoming task by both complexity and urgency:
- complexity: simple, complicated, too_complicated;
- priority: critical, high, normal, low;
- execution class: deterministic_local, lightweight_model, standard_model, strong_review, human_approval.

Priority must consider explicit user priority, production/customer impact, deadlines, blocked downstream work, severity and safety. Do not equate complexity with urgency: a simple production incident may be critical; a complex research task may be low priority.

Use weighted fair scheduling with priority aging to prevent starvation. Respect dependencies: a high-priority node cannot run before required prerequisites. Reserve capacity for critical tasks and final synthesis, but enforce global/provider/resource budgets. Support bounded preemption only at safe checkpoints; never interrupt a non-idempotent side effect mid-flight.

### 25.6 Pipeline creation and dynamic adaptation

The root orchestrator:
1. classifies intent, complexity, urgency, risk and data sensitivity;
2. selects the smallest suitable workflow/mode;
3. creates a pipeline DAG with explicit dependencies and acceptance criteria;
4. allocates child budgets and resource slots;
5. schedules ready nodes by priority and estimated marginal value;
6. adapts concurrency and model tier from CPU/RAM pressure, provider limits, deadlines, token budgets and observed failures;
7. reprioritizes when new critical events arrive;
8. checkpoints and safely pauses/requeues work when resources or provider access become unavailable;
9. synthesizes validated results and releases transient memory.

Pipeline templates may be reused, but each run must bind current project hashes, policies, contracts and inputs. Do not reuse stale plans after material project changes.

### 25.7 HIF self-improvement and controlled evolution

HIF may continuously analyze its own telemetry, benchmark results, failed tasks, user feedback and issue reports to propose improvements to:
- routing policies and model capability profiles;
- prompt/context templates and token budgets;
- pipeline templates and scheduling weights;
- cache/index strategies;
- skill instructions and documentation;
- tests, diagnostics and resource controls.

Self-evolution must follow a controlled engineering loop:
1. observe and identify a measurable problem;
2. create a change proposal with evidence, expected benefit, risk and token/resource impact;
3. create an isolated branch/worktree and tests;
4. implement only within an explicitly authorized development scope;
5. run unit, integration, security, performance and regression checks;
6. compare against baseline benchmarks;
7. prepare a signed release candidate and changelog;
8. require maintainer/user approval for release publication or production rollout unless a narrowly scoped auto-update policy explicitly authorizes it;
9. monitor rollout and rollback automatically on health regression.

HIF must never modify its own installed executable, signing keys, update trust roots, security policy, provider credentials, user data or production environment without explicit authorization. A model-generated patch is untrusted until tests and policy gates pass. Self-improvement cannot grant itself new tools or permissions.

### 25.8 Skills-first rapid operation

When HIF is installed only as a skill, it must remain useful immediately using the host's current model and native tools. It should:
- classify the task quickly;
- select a specialized workflow;
- create compact plans and role-specific instructions;
- use native sub-agents only when available;
- provide useful partial results and explicit remaining work;
- avoid claiming HIF runtime telemetry, background pipelines, dynamic updates or cross-provider routing that do not exist in skill-only mode.

When connected to local HIF MCP, the skill may delegate pipeline creation, priority scheduling, shared memory and actual telemetry to the local runtime. The UI should distinguish skill-only, local runtime and connected provider modes.

### 25.9 Resource and responsiveness requirements

- No resident local LLM by default.
- No permanent process per agent; agents are logical tasks on bounded workers.
- Keep active queues and pipeline metadata memory-bounded.
- Use async event handling and bounded queues with back-pressure.
- Fast triage uses deterministic rules or lightweight models; deep analysis runs asynchronously.
- Stream progress events when the host supports it; otherwise provide concise phase updates.
- Use cancellation, deadlines, retries, circuit breakers and safe checkpoints.
- Expose measured HIF process RAM/CPU, active/queued pipelines and scheduler priority without claiming whole-machine resource usage.

### 25.10 Acceptance criteria

- Local installer verifies publisher signature and all release artifact hashes before execution.
- Per-user installation succeeds without administrator rights on supported platforms.
- Skill-only and full-runtime installation paths are clearly separated.
- Updates are staged, verified, atomic and rollback-capable; user data/configuration are preserved.
- Host skill reload limitations are disclosed; no false promise of live reload.
- Pipeline queue and active state are bounded in memory and recover from durable checkpoints.
- Complexity and urgency are independently classified.
- Priority aging prevents starvation; dependencies and resource budgets are always enforced.
- Critical events can preempt only at safe checkpoints.
- HIF self-improvement produces evidence-backed proposals and cannot bypass release/security approval.
- Installation speed, idle RAM, peak RAM, update duration and pipeline latency are benchmarked before public performance claims.

## 26. Universal pipeline contract for every Skill and model

The pipeline is not exclusive to the connected runtime. Every portable Skill must implement the same logical stages in the host conversation. The execution backend differs by mode.

### 26.1 Skill-native pipeline

In Skill-only mode, the current host assistant follows a visible staged workflow: intake, classification, root architecture assessment, specialist stage planning, model/tool capability check, execution, cross-review, validation, synthesis and remaining-work checklist.

A stage contract contains: stage ID, role, objective, compact input references, output schema, dependencies, acceptance criteria, model identity only when exposed, status, measurable elapsed time and usage only when exposed.

Native host delegation may execute independent stages in parallel only when the host actually exposes sub-agents or parallel tools. If not, the Skill executes stages sequentially using the current host model. A Skill cannot independently switch consumer model selections, inspect private subscription quotas or create API entitlements for other providers. It must never simulate a multi-model run.

### 26.2 Connected runtime pipeline

Connected HIF uses the same stage contracts through the validated DAG engine, active model pool, task preferences, per-provider semaphores, token budgets, shared session memory and runtime telemetry. Each child receives compact role-specific context, not the full chat/repository. Model selection uses actual configured credentials and eligible model IDs.

### 26.3 Model catalog and task routing

The initial starter catalog is configured in src/hif/config.py and documented in docs/PIPELINE-AND-MODEL-ROUTING.md:

- OpenAI: openai/gpt-6-luna, openai/gpt-6.1-sol, openai/gpt-6.2-astra.
- Anthropic: anthropic/claude-haiku-4-5-20251001, anthropic/claude-sonnet-5, anthropic/claude-opus-5.
- Gemini: gemini/gemini-3.5-flash-lite, gemini/gemini-3.8-flash, gemini/gemini-3.1-pro-preview.
- DeepSeek: deepseek/deepseek-flash, deepseek/deepseek-v4-pro.

The catalog is filtered by configured provider credentials. An empty HIF_MODEL_POOL activates only providers whose API key is present. An explicit HIF_MODEL_POOL overrides the starter catalog. Empty HIF_TASK_MODEL_PREFERENCES uses task-specific starter preferences filtered to active models; explicit JSON overrides them.

The starter routing policy is a configurable baseline, not a guaranteed model-quality ranking. Model IDs, API availability, account entitlements and provider lifecycle must be rechecked against official provider documentation before production rollout. API access may be billed separately from consumer subscriptions.

### 26.4 Architecture-owned root orchestrator

The Root Orchestrator is also responsible for architecture analysis. For relevant software, infrastructure, cloud and migration tasks, it:
- maps the current state and constraints;
- identifies architecture boundaries, key dependencies and data/API contracts;
- proposes a target architecture and records assumptions/open decisions;
- assigns advisory roles when the design complexity justifies them;
- reconciles recommendations and freezes a versioned architecture/contract baseline before implementation.

### 26.5 Assistant Architect

The Assistant Architect is an independent advisory role. It challenges the root proposal, compares viable alternatives, checks cohesion/coupling, module/API/data contracts, maintainability, security and technical debt. It provides evidence, trade-offs, risks and recommendations. It cannot silently override the root's approved architecture baseline.

### 26.6 Infrastructure Architect

The Infrastructure Architect reviews:
- cloud, on-premises and hybrid topology;
- compute sizing, CPU/RAM, storage and capacity;
- network, DNS, load balancing, connectivity and trust boundaries;
- identity, authentication, authorization and secrets;
- availability, scaling, resilience and disaster recovery;
- backup/restore, monitoring, logging, alerting and observability;
- data residency, security/compliance and infrastructure cost.

It returns a current-state assessment, target recommendation, alternatives, dependencies, risks, cost assumptions and validation criteria. It is instantiated only when relevant.

### 26.7 Planner/schema extension

Task types include architecture and infrastructure. Planner role guidance includes tech_lead, solution_architect, assistant_architect and infrastructure_architect alongside implementation, analysis, QA and maintenance roles. The root remains accountable for synthesis and final decisions.

### 26.8 Acceptance criteria

- Skill-only and connected runtime follow the same logical pipeline stages.
- Skill-only mode accurately reports when native parallelism/model switching is unavailable.
- The default model catalog covers at least four providers and is filtered by configured credentials.
- Explicit model pool and task preferences override defaults.
- Architecture and infrastructure are first-class task types.
- Root Orchestrator performs architecture assessment for relevant technical tasks.
- Assistant Architect and Infrastructure Architect provide separate advisory outputs when warranted.
- Every specialist instruction includes compact context, dependency, output schema and acceptance criteria.
- The final response separates proposed, implemented, integrated and validated outcomes.


## 27. Host-safe execution and vibe-coding security

### 27.1 Resource-aware local runtime

The runtime must size default concurrency from logical CPUs and available RAM, apply non-blocking telemetry, reserve free memory and bound each task's estimated memory. Remote provider requests remain asynchronous and are capped per provider. Local blocking I/O uses a lazy bounded thread pool; explicitly submitted CPU-heavy trusted helpers use a lazy bounded process pool. No unbounded fan-out, process priority changes or CPU affinity changes are allowed by default.

Skill-only installation must remain instruction-only: no daemon, worker pool, persistent resource monitor or background process.

In-process limits are cooperative. Production server deployments must also use a dedicated least-privilege account and OS/container resource limits.

### 27.2 Application security pre-audit

AI-generated/vibe-coded applications should receive a fast deterministic local scan before release. The initial scanner is read-only, bounded by file count/size/time, skips dependency/build folders, does not execute project code and never opens .env contents. It returns rule ID, severity, path/line evidence, recommendation and a verification-oriented action plan.

The security pipeline includes architecture/threat-model review, deterministic pre-audit, dependency/supply-chain review, application-security reviewer, regression verification and a prioritized release recommendation. Critical/high findings are release blockers unless a named authorized security owner records risk acceptance.

The heuristic scanner is not full SAST/DAST, dependency CVE lookup, penetration testing or certification. External tools and human review are required for those activities.

### 27.3 Acceptance criteria

- CPU sampling never sleeps inside the async scheduler.
- Default parallelism is derived from host CPU/RAM and remains bounded.
- Local worker pools are lazy and have explicit thread/process ceilings.
- Provider calls use async I/O and per-provider limits.
- Skills-only installs do not start runtime workers.
- Security scan does not execute project code, open .env contents or modify project files.
- Security findings contain evidence, severity, recommended correction and verification.
- Documentation clearly states scanner limitations and next-level security tools.
