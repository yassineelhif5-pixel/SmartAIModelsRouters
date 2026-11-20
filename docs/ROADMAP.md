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

## Phase 1 — Core engine
- [ ] Complete and validate Python CLI package.
- [ ] Implement typed provider protocol and mock provider.
- [ ] Implement deterministic task planner and schema validation.
- [ ] Implement dependency DAG scheduler.
- [ ] Implement bounded parallel executor, cancellation and durable run state.
- [ ] Implement provider router with capability, budget, latency, health and usage-threshold filters.
- [ ] Implement shared session ID, role registry and persistent memory/artifact index.
- [ ] Implement per-task and per-session token/cost accounting.
- [ ] Add CPU/RAM telemetry adapters for Windows, Linux and macOS.
- [ ] Add adaptive concurrency with hysteresis and provider-specific caps.
- [ ] Add deterministic tests that require no paid API credentials.

## Phase 2 — Provider integrations
- [ ] Anthropic API adapter.
- [ ] OpenAI API adapter.
- [ ] Gemini API adapter.
- [ ] OpenRouter and DeepSeek adapters.
- [ ] Normalize usage, retry headers, quota errors and reset windows.
- [ ] Implement anticipatory fallback at configurable 80% usage where measurable.
- [ ] Add secret redaction, structured logs and budget enforcement.

## Phase 3 — Host integrations
- [ ] Claude Code skill/plugin + MCP tools.
- [ ] Claude web skill ZIP package validation.
- [ ] ChatGPT skill ZIP package and custom MCP app.
- [ ] Gemini web skill package validation.
- [ ] Gemini CLI extension and MCP setup.
- [ ] GitHub Copilot skill/MCP integration.
- [ ] Codex skill/MCP integration.
- [ ] Cross-host session continuity through explicit HIF memory.

## Phase 4 — Deployment and operations
- [ ] Windows client installer with reversible user-level setup.
- [ ] Windows Server service wrapper, health checks and service recovery.
- [ ] Linux systemd unit, hardening and log rotation.
- [ ] Authenticated remote MCP gateway with TLS and tenant isolation.
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
