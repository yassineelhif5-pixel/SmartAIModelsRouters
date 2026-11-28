# HIF 1.0 — Conversation UX, Token Governance and Progressive Delivery

Status: Normative companion specification for HIF 1.0  
Applies to: all five modes and every entry point (CLI, gateway, MCP and host skills)

## 1. Product principle

HIF must be visibly useful in the conversation, not merely powerful behind the scenes. The user should quickly understand what HIF is doing, which real agents/models are working, how much of the token budget has been consumed, what has been validated and what remains to do.

The discussion is the primary interface. Keep it simple: one run summary, a compact live activity list, a token meter, and a maintained checklist. Detailed traces are expandable and hidden by default.

## 2. Conversation run summary

At run start, display:
- short normalized mission;
- selected mode and complexity classification;
- planned orchestrator/agent count;
- current phase and progress derived from persisted task states;
- actual token usage, allocated budget and remaining amount;
- estimated duration or historical P50/P90, with uncertainty labelled.

Illustrative only:

    HIF · hifStrong · too_complicated
    Mission: Analyze and modernize the application
    Orchestrators: 5 planned · Agents: 10 planned · Models: 10 eligible
    Progress: 2/5 workstreams completed
    Tokens: 18,420 actual / 60,000 allocated · 41,580 remaining

The interface must distinguish planned, eligible, queued, running, completed, failed, cancelled and skipped. A model is not "running" until a real provider request has started. A candidate model is not the same as a model currently executing. All counts and model names must be sourced from runtime state, never hard-coded or simulated.

## 3. Orchestrator and agent activity

Show a compact expandable row for each actual orchestrator/agent:
- display name and specialist role;
- assigned objective;
- provider/model actually used (or "not assigned yet");
- execution state and current phase;
- reported input/output tokens, or clearly marked estimate;
- elapsed time, retry/fallback status;
- result and validation status.

Example rows (illustrative labels only):

    RUNNING  Architecture Lead — defining service boundaries — provider/model
    RUNNING  Database Agent — inspecting schema and indexes — provider/model
    DONE     Project Reader 1 — mapped backend modules — provider/model
    QUEUED   QA Agent — waiting for API contract
    REVIEW   Security Reviewer — checking authentication design

Keep the overall milestone and next action visible. Collapse verbose logs by default.

## 4. Event-driven progress

The backend emits structured, timestamped events:
- run.accepted, run.classified, run.planned;
- orchestrator.created/started/progress/completed/failed;
- agent.created/queued/started/progress/completed/failed/cancelled;
- model.selected, provider.request_started/completed, provider.fallback;
- budget.allocated/updated/warning/exhausted;
- artifact.created, result.validating/validated/rejected;
- mode.transitioned, approval.requested/granted/denied;
- run.synthesizing/completed/failed.

Each event includes run_id, parent_id where relevant, task/agent ID, timestamp, state and applicable usage metadata. Stream events when the host transport supports it; otherwise expose a pollable status endpoint. Persist/replay events so reconnecting clients can rebuild the current view. Never fabricate progress percentages or agent activity.

## 5. Hierarchical token and cost management (critical)

Token management is a first-class subsystem and must precede large fan-out.

### 5.1 Budget ownership

The root owns the global run envelope:
- max input tokens;
- max output tokens;
- optional cost ceiling;
- deadline;
- reserve for final synthesis, verification, retries and recovery.

Root allocates sub-budgets to child orchestrators. Each child allocates bounded budgets to its agents. Each provider call must reserve capacity against the agent allocation and global remaining envelope before dispatch. Reservation and settlement must be atomic under concurrency.

A budget tracks allocated, reserved, consumed, released and remaining amounts. Unused budget may return to the parent. Only the root can reallocate across siblings. No child may exceed its allocation or silently borrow from another.

### 5.2 Actual versus estimated usage

Track separately:
- estimated input tokens before request;
- provider-reported input tokens;
- output token allowance;
- provider-reported output tokens;
- cached input tokens, if supplied;
- tool/context usage where measurable;
- unknown/unreported usage.

Provider-reported usage is authoritative when available. If unavailable, label counts as estimated and store the estimation method. Never display estimates as actual. Track usage by run, orchestrator, agent, task, provider and model. Cost is shown only when trustworthy pricing metadata and usage are available; otherwise show "unknown" or "estimate", never invented charges.

### 5.3 Allocation and runtime controls

Before execution:
1. Estimate task graph size, context size and expected provider calls.
2. Apply global token, cost and deadline ceilings.
3. Reserve a configurable portion for synthesis, verification and recovery.
4. Allocate child budgets by task complexity, priority and expected workload.
5. Allocate agent budgets from the child allocation.
6. Set per-call input/output caps.

During execution:
- settle usage after each provider response;
- warn at configurable thresholds (suggested initial values: 70%, 85%, 95%);
- stop optional fan-out/reviewers before sacrificing mandatory validation;
- return unused allocations to the parent;
- prevent new calls before a hard limit is exceeded;
- preserve enough reserve for a minimal final user status.

On exhaustion, stop creating new work and return partial output, completed work, blockers and remaining requirements. The root chooses whether to reallocate, use a cheaper eligible model, reduce scope or ask the user. Do not silently truncate relevant constraints; use targeted retrieval and summarization.

### 5.4 Token meter in discussion

Show allocated, actual/estimated used and remaining. On expansion, show per-orchestrator breakdown and reserve. Example:

    Run budget: 60k allocated
    Used: 18.4k actual · Remaining: 41.6k
    Strong root: 8.2k · Architecture: 4.1k · DB: 3.6k · QA: 2.5k
    Reserve: 8k for final review and synthesis

Only actual provider calls accrue actual usage. The UI must not imply ten models are consuming tokens concurrently if they are merely selected or queued.

## 6. Fast project intake and block reading

When a project/repository is attached or selected, HIF should understand it quickly using two passes.

Pass A — fast fingerprint:
- inspect repository tree and top-level folders;
- identify languages, frameworks, package managers and project type;
- read README, manifests, solution/project files, dependency manifests, entry points and selected config;
- map tests, deployment descriptors and integrations;
- detect likely secret files without exposing secret values;
- produce a concise project fingerprint, coverage and uncertainty summary.

Pass B — targeted parallel reading:
- partition independent modules or file/page ranges into bounded chunks;
- dispatch reader agents only for independent areas;
- return structured summaries with source path, line/page range, interfaces, dependencies, conventions, risks, uncertainties and relevant excerpts;
- consolidate summaries, remove duplication and preserve source references;
- load only task-relevant excerpts into specialist prompts.

Do not send the entire repository, full conversation history or all files to every model. Use progressive retrieval: index first, inspect relevant files second, expand exact ranges only when needed. Chunk overlap must preserve section boundaries; the consolidator checks missing ranges and conflicting summaries. Exclude sensitive files/secrets unless specifically authorized and protected.

A temporary Project Reader team may be launched for large projects, but it is subject to the same global fan-out and token budgets. Retire it after producing a validated project map and compact reusable summary. The first user-visible update should quickly acknowledge what HIF has identified so far and what it is scanning next; do not wait for exhaustive analysis before giving useful status. Do not claim full understanding until coverage and gaps are reported.

## 7. Validation and progressive delivery

Every agent/orchestrator returns a structured result:
- result ID, parent task and owner;
- concise user-readable summary;
- artifact references;
- acceptance criteria with pass/fail/not-run;
- validation evidence (tests, schema checks, source ranges, checksums or reviewer outcome);
- confidence/uncertainty summary;
- limitations and risks;
- remaining actions, owners and dependencies;
- required user approval, if any.

Result states:
- draft: produced, not checked;
- validating: checks running;
- validated: required acceptance checks passed with evidence;
- needs_revision: check failed or reviewer requested changes;
- blocked: missing dependency, permission, data or user decision;
- partial: useful work completed but task unfinished;
- rejected: unusable or unsafe;
- completed: root accepted the deliverable and all mandatory criteria are satisfied.

A producer's assertion is not proof of validation. Prefer deterministic tests, schema validation, source evidence and reproducible checks. For high-risk work, the producer cannot be the sole validator.

Publish independently useful, validated intermediate deliverables as soon as ready. Clearly label provisional results. A blocked branch must not prevent unrelated branches from progressing, but the user must see the blocker.

## 8. User-facing "what remains" checklist

After each meaningful milestone, update a single run checklist in the conversation. Example:

    HIF progress — Project analysis
    [x] Repository structure indexed
    [x] Backend modules mapped and cross-checked
    [x] Database schema summary validated
    [ ] API contracts reviewed
    [ ] Security review completed
    [ ] Final implementation plan delivered

    Next: review API contracts, then consolidate architecture.
    User action: none currently.

Checklist states come from persisted task and acceptance records, not hand-written guesses. Keep completed items checked, in-progress items distinct, remaining items unchecked and blocked items annotated with reasons. When state changes, update the existing checklist rather than posting contradictory copies. At final completion, list completed work and anything not done, including why it remains open.

## 9. Required acceptance tests

- Five orchestrators and ten agents appear with accurate planned/queued/running/completed states and actual model assignment.
- Every provider call updates run, orchestrator, agent, provider and model counters.
- Estimated and provider-reported tokens are never conflated.
- Child allocations plus root reserve never exceed the global allocation.
- Concurrent reservations cannot overspend a budget.
- Threshold warnings fire once per crossing at configured levels.
- Budget exhaustion stops new calls, preserves completed work and permits a minimal final status.
- Large project intake uses bounded chunks and scoped summaries; tests prove unrelated files are not broadcast to every agent.
- A result marked completed has a validation record and user-facing remaining-work checklist.
- Failed, blocked, partial and provisional work is never displayed as fully complete.
- Progress events can be replayed after client reconnect.
- Non-streaming clients still receive a final status and checklist.

## 10. Delivery order

1. Implement atomic hierarchical token accounting and per-call usage capture.
2. Implement persisted run/agent state and event stream/polling contract.
3. Implement conversation run header, live activity list and token meter.
4. Implement fast project fingerprint and bounded block-reader agents.
5. Implement result validation records and maintained remaining-work checklist.
6. Add benchmarks, budget exhaustion tests, concurrency tests and reconnect/replay tests.

The first usable version should favor a small truthful UI and strict accounting over elaborate animations or an oversized agent dashboard.


## 11. Token efficiency engine — target: up to 70% fewer tokens

### 11.1 Objective and honest measurement

Token efficiency is a primary HIF product differentiator. HIF should target **up to 70% fewer billable input/output tokens** than a defined baseline for comparable tasks, while preserving or improving task quality and completion rate.

This is an optimization target, not a universal guarantee. Results depend on provider tokenization, task type, context size, caching support, model behavior and the number of independent reasoning passes required. HIF must never claim a 70% saving unless benchmark evidence supports that claim for the relevant workload.

Benchmark protocol:
- Baseline: same task and source snapshot sent to a capable selected model with full relevant context and no HIF context reuse.
- HIF: same task, acceptance criteria and source material, using routing, retrieval, caching, compression and hierarchical orchestration.
- Report input, output and total tokens separately; provider-reported cached tokens separately; latency, cost (only with trustworthy pricing), completion rate and quality checks.
- Token reduction = (baseline total tokens - HIF total tokens) / baseline total tokens × 100.
- Compare equivalent completed work only. A shorter incomplete answer is not a saving.
- Publish workload, sample size, provider/model, date and variation. Do not generalize a small sample to every task.
- Do not count provider cache discounts as tokens eliminated.

### 11.2 Prompt Compiler

Before every provider call, build the smallest sufficient context:
1. stable system policy and role template;
2. concise task objective and acceptance criteria;
3. only relevant project facts and source excerpts;
4. dependency summaries rather than full transcripts;
5. explicit output schema and token ceiling.

Remove repeated instructions, repeated chat history, irrelevant file content and redundant agent outputs. Preserve user constraints, safety rules, source provenance and uncertainty. Every agent receives a role-specific context package, not the entire project or conversation. Record included context references for traceability.

### 11.3 Project Knowledge Index — read once, reuse many times

On project intake, scan the tree and key manifests, fingerprint files with stable hashes, and create a compact project map of modules, entry points, dependencies, APIs, database schema, tests and configuration.

Maintain:
- compact project index: names, relationships, symbols, routes, tables, interfaces and source references;
- detailed evidence store: targeted excerpts and bounded file/page chunks fetched only when needed.

Store summaries with source hashes and dependency fingerprints. Reuse them across agents/runs only while those fingerprints remain valid. Invalidate affected summaries when source files or dependencies change. Never reuse stale summaries as current facts.

### 11.4 Smart block reading

Divide large projects and documents into bounded, independently readable chunks. Reader agents return concise structured records: source path and line/page range, purpose, key facts, interfaces, dependencies, risks, uncertainty and evidence references.

A consolidator deduplicates overlapping findings and produces a shared project summary. Other agents request relevant chunks by reference. Do not send the same large file to five agents. Parallelize reading only when chunks are independent and the consolidated result is cheaper than repeated full-context calls. Exclude secrets and sensitive files unless explicitly authorized and protected.

### 11.5 Hierarchical context sharing

Root creates a compact mission brief and project index. Child orchestrators receive only their domain slice. Agents receive only their task contract and evidence. Agents return compact structured results and artifact references. Parents share only relevant fields with dependent agents.

Examples:
- share API contracts with frontend/backend integration agents;
- share schema summaries with database-dependent developers;
- share test failures only with the responsible implementation agent and reviewer;
- send validated child summaries and essential evidence to root synthesis.

Keep large artifacts in storage; prompts carry references and relevant excerpts, not repeated artifact bodies.

### 11.6 Model routing

Select the least expensive and fastest eligible model that meets quality, capability, privacy and context requirements. Use small capable models or deterministic code for simple extraction, classification, formatting and summarization where reliable. Reserve stronger models for difficult reasoning, ambiguous requirements and independent verification.

Use observed quality and failure rates, not brand assumptions. If a small model fails validation, escalate using a compact failure summary rather than replaying the full conversation. Do not call multiple models when one response plus deterministic validation is sufficient.

### 11.7 Output budgets and progressive synthesis

Every agent has a role-specific output schema and maximum output budget. Request concise findings, evidence references, risks and next actions rather than long essays. Use structured output for machine handoffs and a readable summary only at the user boundary.

Agents return compact findings; child orchestrators deduplicate and resolve local contradictions; root receives child summaries and essential evidence. Preserve full artifacts outside prompts. Do not repeatedly ask models to restate validated information.

### 11.8 Cache and deterministic preprocessing

Cache eligible results with keys including normalized task/instruction version, relevant source hashes, model/provider and generation settings, output schema and validation policy, plus privacy/tenant scope.

Cache only safe reusable work. Do not reuse time-sensitive answers, confidential outputs across scopes, or side-effecting actions as if re-executed. Revalidate cached artifacts and invalidate on source/prompt/schema changes.

Use deterministic code for file inventory, hashing, CSV parsing, simple transformations, schema extraction and duplicate detection. Do not spend LLM tokens on operations that deterministic tooling performs accurately.

### 11.9 Adaptive stopping and delegation

Before creating a child or reviewer, estimate marginal value: what new information or independent validation will it add, is it already available, and does the expected benefit justify tokens, latency and cost?

Do not duplicate an agent's assignment or evidence. Stop optional branches when acceptance criteria are satisfied and more analysis is unlikely to change the result. Keep mandatory safety/security review. Reduce optional fan-out before cutting essential validation.

### 11.10 Live token-efficiency panel

In addition to the budget meter, show HIF tokens used, comparable baseline tokens (if available), tokens saved and reduction percentage, input/output split, reused summaries, cache hits and avoided duplicate reads/calls.

Illustrative only:

    HIF token efficiency
    Comparable baseline: 100,000 tokens (estimated)
    HIF consumption:       30,000 tokens (actual)
    Potential reduction:       70% (provisional)
    Reused summaries: 14 · Cache hits: 8 · Duplicate reads avoided: 6

Show a saving percentage only when a comparable baseline exists. Otherwise show "savings not yet measured". Label measured versus estimated baselines. A provider cache discount is a billing feature, not tokens eliminated.

### 11.11 Benchmark suite and release gate

Benchmark representative workloads: repository onboarding, multi-file code changes, SQL analysis, architecture review, long document analysis, multi-step research and test-failure diagnosis.

Run baseline and HIF multiple times on identical inputs and acceptance criteria. Record total/input/output tokens, cached tokens, cache hit rate, provider calls, duplicated context, latency, retries, completion rate and quality/test outcomes.

HIF 1.0 release gates:
- demonstrate meaningful median token reduction on the benchmark suite;
- pursue up to 70% reduction on workloads with substantial repeated context;
- no regression in mandatory acceptance checks or security controls;
- no hidden reduction in task scope or deliverable completeness;
- accurate budget accounting under concurrency;
- publish per-workload results, including cases where HIF saves little or uses more tokens.

### 11.12 Implementation order

1. Per-call token telemetry and baseline benchmark harness.
2. Prompt compiler and strict role-specific input/output budgets.
3. Project fingerprint, source hashes and reusable summaries.
4. Bounded block reader and context-reference retrieval.
5. Hierarchical context routing and deduplicated synthesis.
6. Deterministic preprocessing and cache.
7. Capability/quality-aware model routing.
8. Marginal-value-based delegation and adaptive stopping.
9. Live token savings panel.

Do not optimize by indiscriminately cutting context, shrinking every output or skipping verification. Remove repeated and irrelevant tokens while retaining the evidence needed for a correct result.
