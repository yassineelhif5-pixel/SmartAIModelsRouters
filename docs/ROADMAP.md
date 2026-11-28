# HIF Roadmap

## Phase 0 — Repository foundation
- [x] Define product scope and architecture.
- [x] Define security and orchestration boundary.
- [x] Document Windows client, Windows Server and Linux deployment targets.
- [x] Define HIF Node parallel DAG execution and shared session-memory requirements.
- [x] Document CPU/RAM/GPU-aware scheduling and 80% pre-emptive failover policy.
- [x] Add portable \`hif\` and \`hifnode\` skill instructions for Claude, ChatGPT, Gemini, Copilot and Codex targets.
- [x] Add cross-platform skill installation and ZIP packaging scripts.
- [x] Choose and add an explicit open-source license (Apache-2.0, open core: see COMMERCIAL.md).
- [x] Add code-of-conduct policy.

## Phase 1 — Local core MVP
- [x] Python CLI with run, node, status, usage and MCP commands.
- [x] Typed provider protocol and deterministic mock provider.
- [x] Structured task planner and DAG/schema validation.
- [x] Dependency-aware scheduler with bounded parallel node execution.
- [ ] Add cancellation and resumable interrupted runs.
- [x] Ordered model pool, per-task model preferences, HIF token budgets, 80% pre-emptive filtering and cooldown fallback.
- [x] Shared session ID, role definitions and persistent per-user SQLite memory.
- [x] Record per-node and per-session provider-reported input/output token usage and estimated cost when available.
- [ ] Add a durable artifact index and file/content hash references.
- [x] CPU/RAM telemetry through psutil on supported Windows/Linux/macOS hosts.
- [x] Adaptive concurrency with global and per-provider request caps.
- [x] Non-blocking CPU sampling and CPU/RAM-derived default concurrency (capped at eight).
- [x] Lazy bounded local I/O thread pool and CPU helper process pool.
- [x] Lightweight read-only application security pre-audit with JSON findings and remediation plan.
- [x] Deterministic tests and CI that require no paid API credentials.

## Phase 2 — Provider integrations
- [x] Anthropic API adapter (native Messages API).
- [x] OpenAI API adapter (Chat Completions).
- [x] Gemini API adapter (native generateContent).
- [x] OpenRouter, DeepSeek and 25 other provider adapters (docs/PROVIDERS.md).
- [ ] Normalize usage, retry headers, quota errors and reset windows.
- [ ] Implement anticipatory fallback at configurable 80% usage where measurable.
- [x] Per-session budget enforcement and loop detection (spend guard).
- [ ] Add secret redaction and structured logs.

## Phase 3 — Host integrations
- [x] Claude Code local stdio MCP tools (hif_run and hifnode_run).
- [ ] Remote HTTPS MCP host-specific setup and end-to-end validation for Claude Code.
- [ ] Claude web skill ZIP package validation.
- [ ] ChatGPT skill ZIP package and custom MCP app.
- [ ] Gemini web skill package validation.
- [x] Gemini CLI local stdio MCP setup documented.
- [ ] Validate Gemini web custom remote MCP availability and permissions.
- [ ] GitHub Copilot skill/MCP integration.
- [x] Codex local stdio MCP setup documented.
- [ ] Validate Codex remote MCP connection where supported.
- [ ] Cross-host session continuity through explicit HIF memory.

## Phase 4 — Deployment and operations
- [ ] Windows client installer with reversible user-level setup.
- [ ] Windows Server service wrapper, health checks and service recovery.
- [ ] Linux systemd unit, hardening and log rotation.
- [x] Authenticated REST + Streamable HTTP MCP gateway for a single-tenant private pilot (bearer auth, body caps, per-IP rate limit and TLS guard).
- [ ] OAuth/OIDC, tenant isolation, per-user permissions and distributed rate limiting for production multi-tenant use.
- [ ] Docker/Podman image running as non-root.
- [ ] Resource telemetry dashboard and usage reports.
- [ ] Backup, restore and memory-retention controls.

## Phase 5 — Advanced orchestration
- [ ] Isolated Git worktree execution for code changes.
- [ ] Specialist node templates (architect, research, coding, test, review, documentation).
- [ ] Conflict detection and artifact merge stages.
- [ ] Context cache with hash-based invalidation and privacy controls.
- [ ] Prompt/task deduplication.
- [x] Quality/speed/cost evaluation suite (`hif bench`, 30 deterministic tasks).
- [x] Optional local inference through Ollama, LM Studio, vLLM and llama.cpp.

## MVP acceptance criteria
- One user goal creates a validated task graph with stable task IDs.
- Independent nodes overlap; dependencies are respected.
- Every node in one run shares the same HIF session ID and approved memory.
- CPU/RAM pressure and provider limits bound concurrency.
- An observed 80% usage threshold triggers pre-emptive routing to another eligible provider.
- Unreported quota remains unknown; estimates are labelled as estimates.
- A 429 or temporary provider outage triggers bounded fallback.
- Global and per-task budgets prevent overspending.
- Cancellation stops pending work and signals running tasks.
- Host skills fail clearly when the backend/MCP service is missing.
- CI can run without real provider credentials.


## Phase 4.1 — Remote gateway hardening
- [x] Single-tenant bearer-authenticated REST and Streamable HTTP MCP endpoints.
- [x] Health endpoint, request-size limit, per-IP rate limit and no-store/security headers.
- [x] Refuse non-loopback plain-HTTP binds unless direct TLS is configured.
- [x] OAuth 2.1 resource-server integration: external OIDC JWT verification (issuer, JWKS signature, audience, expiry and required scopes) with RFC 9728 discovery.
- [ ] Full user/tenant lifecycle, token revocation/rotation events and fine-grained per-tool authorization.
- [ ] Per-tool permissions, tenant isolation and distributed rate limits.
- [ ] Proxy deployment templates for Caddy, Nginx and IIS ARR.
- [ ] Load, soak, security and failure-injection tests.
- [ ] Production audit events with secret and context redaction.


## Phase 1.1 — Host responsiveness and application security
- [x] Avoid blocking the asyncio event loop during CPU telemetry sampling.
- [x] Derive default task concurrency from available CPU/RAM; preserve explicit operator overrides.
- [x] Bound local I/O threads and local CPU helper processes; instantiate pools lazily.
- [x] Add a fast read-only scanner for common vibe-coding security mistakes.
- [x] Add security CLI output with severity, evidence and prioritized remediation.
- [ ] Add AST-aware and data-flow SAST for supported languages.
- [ ] Add optional dependency vulnerability, secret-history, container and IaC scanners.
- [ ] Add safe test-environment DAST/fuzzing integrations.
- [ ] Add configurable CI release gates and documented risk acceptance.
- [ ] Add Windows Job Object and Linux cgroup deployment examples with measured resource caps.


## Universal Orchestration roadmap

### Phase U1 — Domain-neutral core contracts
- [ ] Define versioned run, orchestrator, task, event, handoff, artifact and report schemas.
- [ ] Add domain classification and configurable domain packs beyond software engineering.
- [ ] Implement fast-first triage and progressive milestone delivery without fabricated background progress.
- [ ] Add priority/deadline scheduling separate from complexity classification.
- [ ] Record truthful queue, execution, validation and retry telemetry; estimate P50/P90 only from sufficient comparable history.

### Phase U2 — Research and information collection
- [ ] Add authorized source/connectors abstraction and evidence ledger.
- [ ] Track source provenance, publication/retrieval dates, freshness, claim links and conflicts.
- [ ] Add source-grounded research synthesis and coverage/uncertainty reporting.
- [ ] Add privacy-aware collection, retention and connector scope enforcement.

### Phase U3 — Professional reporting and artifacts
- [ ] Add report specification, audience profiles and reusable modern templates.
- [ ] Add executive summary, methodology, evidence, recommendations, risks and source register sections.
- [ ] Add chart/table generation from verified data with reproducible calculations.
- [ ] Add DOCX/PDF/PPTX/XLSX artifact adapters and validation when supported.
- [ ] Add preview, versioning, artifact references and export status.

### Phase U4 — Campaign and publication orchestration
- [ ] Add campaign objectives, audience/brand constraints and channel-specific content variants.
- [ ] Add editorial calendar, draft/review/approval/schedule/publish state machine.
- [ ] Add authorized CMS/social/email connectors with platform-compliant rate limits.
- [ ] Require explicit approval for external publication and outbound communication by default.
- [ ] Track confirmed publication IDs/status and real campaign metrics only when connectors return them.

### Phase U5 — Visual orchestration and event API
- [ ] Publish structured, append-only run/task/handoff/artifact events with stable correlation IDs.
- [ ] Add graph projection for orchestrators, agents, tools, dependencies, handoffs and artifacts.
- [ ] Add responsive dashboard: run timeline, graph, status filters, report preview, blockers and approvals.
- [ ] Add text/table accessibility alternative and prevent secrets/chain-of-thought in visual event payloads.
- [ ] Add graph/event consistency tests against actual execution traces.

### Universal acceptance criteria
- A non-software task can be classified and routed to an appropriate domain pack.
- A useful first triage is returned before optional deep work when execution mode allows progressive delivery.
- All displayed agent states, elapsed times, ETAs and provider usage are backed by actual host/runtime data or explicitly labelled estimates.
- Research claims link to source evidence and disclose gaps/conflicts.
- Publication cannot be marked complete without a confirmed authorized connector result.
- Reports distinguish verified data from assumptions and never invent chart values.
- The visual graph is a faithful projection of structured execution events, not a decorative simulation.
- All external, paid, destructive or production actions respect explicit approval and permission scopes.
