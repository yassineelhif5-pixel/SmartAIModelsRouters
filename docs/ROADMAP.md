# HIF Roadmap

## Phase 0 — Repository foundation
- [x] Define product scope and architecture.
- [x] Define security and orchestration boundary.
- [x] Document Windows client, Windows Server and Linux deployment targets.
- [x] Define HIF Node parallel DAG execution and shared session-memory requirements.
- [x] Document CPU/RAM/GPU-aware scheduling and 80% pre-emptive failover policy.
- [x] Add portable \`hif\` and \`hifnode\` skill instructions for Claude, ChatGPT, Gemini, Copilot and Codex targets.
- [x] Add cross-platform skill installation and ZIP packaging scripts.
- [ ] Choose and add an explicit open-source license.
- [ ] Add code-of-conduct policy.

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
- [x] Deterministic tests and CI that require no paid API credentials.

## Phase 2 — Provider integrations
- [ ] Anthropic API adapter.
- [ ] OpenAI API adapter.
- [ ] Gemini API adapter.
- [ ] OpenRouter and DeepSeek adapters.
- [ ] Normalize usage, retry headers, quota errors and reset windows.
- [ ] Implement anticipatory fallback at configurable 80% usage where measurable.
- [ ] Add secret redaction, structured logs and budget enforcement.

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
- [ ] Quality/speed/cost evaluation suite.
- [ ] Optional local inference through Ollama.

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
- [ ] OAuth 2.1 / OIDC with user identity and token rotation.
- [ ] Per-tool permissions, tenant isolation and distributed rate limits.
- [ ] Proxy deployment templates for Caddy, Nginx and IIS ARR.
- [ ] Load, soak, security and failure-injection tests.
- [ ] Production audit events with secret and context redaction.
