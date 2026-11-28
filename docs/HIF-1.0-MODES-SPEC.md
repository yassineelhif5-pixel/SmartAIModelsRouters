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
