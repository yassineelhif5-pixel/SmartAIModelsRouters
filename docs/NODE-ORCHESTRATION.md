# HIF Node Orchestration — /hifnode

## Purpose

The /hifnode mode executes a complex request as a directed acyclic graph (DAG) of specialist nodes. Independent nodes run concurrently; dependent nodes start only after their prerequisites finish. Every node in one run shares the same HIF session ID and durable session memory.

## Execution lifecycle

1. The host creates or resumes one HIF session.
2. The planner creates a bounded node graph with role, task, model preference, dependencies, context references and acceptance criteria.
3. The policy layer validates privacy class, model allowlists, token budgets and required approvals.
4. The scheduler selects nodes whose dependencies are complete.
5. The resource manager calculates a safe concurrency level from configured limits, CPU load, memory pressure and provider-specific concurrency.
6. Ready nodes execute concurrently.
7. Each result is stored with the same session ID, node ID, role, provider/model and usage metadata.
8. Downstream nodes receive only dependency outputs and relevant shared memory.
9. A verifier checks deliverables; a synthesizer returns one consolidated response to the original host session.

## Node contract

Each node has a stable ID, specialist role, bounded task instruction, dependencies, capability requirements, model candidates, memory references, token/cost budgets, deadline, privacy class and acceptance criteria. Nodes return deliverables and artifact references, not claims about tools they did not use.

## Parallelism and write safety

Independent read-only tasks may run concurrently. Tasks that edit the same files or mutable resource must use isolated worktrees/workspaces or serialized merge stages. Do not run conflicting writes in one working directory.

The scheduler uses bounded concurrency. More nodes do not necessarily mean faster execution: providers impose rate limits, models have different latency, and local hardware is finite.

## Shared session memory

Every node carries the same session ID. HIF memory stores approved facts, role definitions, session summaries, outputs and artifact references with provenance. Downstream tasks can reuse prior work instead of asking a new model to repeat it.

This is explicit application-level context sharing, not transfer of a provider's hidden context, private reasoning, internal cache or native conversation state.

## Commands

- /hif: normal orchestration for a bounded goal.
- /hifnode: dependency-aware parallel specialist nodes.
- /hifnode status: inspect active and completed node states where implemented.
- /hifnode cancel: cancel pending/active work where implemented.

Slash-command syntax is host-specific. Claude Code and Gemini CLI provide native command/skill mechanisms; Copilot supports agent skills; ChatGPT connects through a custom MCP app where the user's plan permits it.

## Acceptance criteria

- Independent nodes overlap in time.
- Dependent nodes wait for prerequisites.
- Every node in a run shares one session ID.
- Role definitions and approved memory are reused.
- Outputs and usage metadata are persisted.
- CPU/RAM pressure and provider concurrency bound the scheduler.
- Fallback decisions and errors are auditable.
- Cancellation stops pending tasks and signals running tasks.
