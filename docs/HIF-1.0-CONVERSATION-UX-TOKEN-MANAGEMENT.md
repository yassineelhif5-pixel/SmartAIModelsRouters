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
