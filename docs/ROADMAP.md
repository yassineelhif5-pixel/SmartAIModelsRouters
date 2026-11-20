# HIF Roadmap

## Phase 0 — Repository foundation
- [x] Define product scope and architecture.
- [x] Define security and orchestration boundary.
- [ ] Choose license.
- [ ] Add contribution and code-of-conduct policies.

## Phase 1 — Core engine (MVP)
- [ ] Python package and CLI entry point.
- [ ] Typed configuration and validation.
- [ ] Provider protocol and mock provider.
- [ ] Task and execution data models.
- [ ] Planner interface and deterministic planner for tests.
- [ ] Dependency DAG scheduler.
- [ ] Bounded parallel executor and cancellation.
- [ ] Router with capability, budget, latency and health filters.
- [ ] Token/cost accounting with unknown values represented explicitly.
- [ ] SQLite execution state and artifact references.
- [ ] Unit and integration tests; CI without paid credentials.

## Phase 2 — First integrations
- [ ] OpenAI-compatible API adapter.
- [ ] Anthropic Messages API adapter.
- [ ] Gemini adapter.
- [ ] Provider health, rate limit and retry normalization.
- [ ] Provider configuration examples using environment variables.
- [ ] Secret redaction and structured logs.

## Phase 3 — HIF user experience
- [ ] Claude Code plugin exposing `/hif`.
- [ ] MCP tools: plan, execute, status, cancel, providers.
- [ ] Codex-specific skill/MCP integration.
- [ ] Windows installer and reversible user-level setup.
- [ ] `/hif status`, `/hif providers`, `/hif cancel`.

## Phase 4 — Optimization and reliability
- [ ] Adaptive routing from measured latency and cost.
- [ ] Semantic/context cache with invalidation and privacy controls.
- [ ] Prompt/task deduplication.
- [ ] Parallel task tuning and per-provider concurrency.
- [ ] Evaluation suite for quality, speed and cost trade-offs.
- [ ] Dashboard and usage reports.

## Phase 5 — Advanced orchestration
- [ ] Isolated Git worktree execution for code changes.
- [ ] Specialized agents (research, coding, testing, review, documentation).
- [ ] Output verification and automated test feedback loops.
- [ ] Remote gateway with authentication and tenant isolation.
- [ ] Optional local-model execution through Ollama.

## MVP acceptance criteria
- A single request can be represented as a validated task graph.
- Independent mock tasks execute concurrently; dependent tasks wait.
- A 429/mock quota error triggers eligible fallback and records the reason.
- Global and per-task budgets stop execution before overspend.
- Cancellation stops pending work and signals active executors.
- No API key is required to run the test suite.
- Claude Code can invoke the local service using `/hif`.
- Logs do not expose secrets.
