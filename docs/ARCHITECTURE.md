# HIF Architecture

> **Implementation status (0.2.0):** the local MVP currently implements SQLite sessions/memory, typed DAG planning, bounded parallel text execution, a LiteLLM provider adapter, ordered model pools, task-type preferences, HIF-measured 80% token-budget filtering, retryable-error cooldown/fallback, per-provider semaphores and CPU/RAM-aware concurrency. Dynamic cost/latency/quality scoring, official provider quota APIs, durable artifact hashing, cancellation, remote HTTP MCP, file/tool execution and cross-host remote memory are still planned. This document describes the target architecture where those capabilities are not yet shipped.

## 1. Purpose

HIF (Hybrid Intelligent Flow) orchestrates a user's work across multiple AI providers. It is not intended to proxy every token in every native assistant conversation. Its central value is task-level delegation: one outcome becomes a graph of small, independently executable tasks.

## 2. Runtime flow

1. A host adapter receives `/hif <goal>`.
2. The CLI sends the goal, project root and explicitly permitted context to the local HIF gateway.
3. The planner produces a structured plan: task IDs, objective, task type, dependencies, required capabilities, expected output, context references, risk level and budget.
4. The policy engine checks privacy, provider allowlists, cost ceilings, parallelism and approval requirements.
5. The scheduler dispatches ready tasks to eligible providers.
6. Executors collect responses and usage metadata. Transient errors are retried with bounded exponential backoff; quota/rate-limit errors trigger provider fallback when allowed.
7. The verifier checks schemas, tests, evidence and task acceptance criteria.
8. The synthesizer merges artifacts and returns a concise result and execution report to the host.

## 3. Task model

A task should carry:
- `id`, `title`, `instruction`, `task_type`
- `depends_on[]`
- `input_artifacts[]` (paths, hashes, excerpts, summaries)
- `required_capabilities[]`
- `privacy_class` (`local_only`, `approved_provider`, `public_data`)
- `max_input_tokens`, `max_output_tokens`, `max_cost`
- `deadline_seconds`, `risk_level`, `acceptance_criteria[]`
- `status`, `provider`, `model`, `usage`, `artifact_refs[]`

The planner must not decompose a simple request into needless agent calls. A single well-selected model is often cheaper and faster.

## 4. Scheduling and parallelism

Use a dependency DAG. Only tasks whose dependencies have succeeded are eligible. Bound concurrency globally and per provider. Add per-provider rate-limit queues. Support cancellation and propagate cancellation to child tasks. Do not run conflicting write tasks concurrently against the same files; use worktrees, file ownership, or serialized merge stages.

## 5. Routing strategy

Candidate scoring should consider:
- capability compatibility and context window
- user-configured model priority
- estimated input/output price
- observed latency and reliability
- provider health and known rate-limit reset time
- data residency and privacy policy
- remaining task and global budget

Hard constraints (privacy, budget, capability) filter candidates first. A weighted score ranks the remaining candidates. Cost and latency weights must be configurable. The router must be transparent and explain selections.

## 6. Context efficiency

- Prefer file references, targeted excerpts and structured artifacts over full transcripts.
- Use compact task contracts and explicit output schemas.
- Reuse a summary only while its source hashes remain current.
- Avoid duplicate analysis by memoizing deterministic, non-sensitive tasks with content-addressed keys.
- Set token budgets per task and reserve output budget.
- Never silently discard relevant constraints to save tokens.

## 7. Provider abstraction

Define a stable internal interface for capabilities, invocation, streaming, cancellation, health, pricing metadata and usage. Keep provider-specific behavior in adapters. Do not assume all providers implement identical tool calling, JSON mode, image support, streaming or usage reporting.

## 8. Host integration

### Claude Code

Implement a Claude Code plugin containing a user-invoked `/hif` skill/command and an MCP server connection to the local HIF service. Keep extension files compliant with the current Claude plugin format. The plugin is an entry point, not the whole router.

### OpenAI Codex

Provide a separate Codex skill/configuration or MCP integration based on the documented Codex extension points. Do not install Claude-specific plugin manifests into Codex.

### Other clients

Provide a standard HTTP API and MCP server so compatible clients can call HIF tools. A generic HTTP/MCP interface does not guarantee arbitrary chat applications can register a native slash command.

## 9. Session continuity

HIF does not claim to migrate a complete live conversation between providers. A handoff package includes the goal, accepted constraints, concise context summary, task state, relevant artifacts and required output format. The host receives the consolidated result. Provider-specific hidden reasoning or private chain-of-thought is never requested or transferred.

## 10. Reliability

Use idempotency keys for task submissions, bounded retries, circuit breakers, provider cooldowns, deadlines, cancellation, durable task state and structured error categories. Do not retry non-idempotent external actions without explicit safeguards.
