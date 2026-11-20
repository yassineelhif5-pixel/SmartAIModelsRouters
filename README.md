# SmartAIModelsRouters

**HIF — Hybrid Intelligent Flow** is a provider-agnostic AI orchestration layer designed to make Claude Code, OpenAI/Codex, Gemini and other supported assistants work faster and more efficiently.

The primary user experience is the `/hif` command: describe an outcome once, and HIF plans the work, splits it into independent tasks, routes each task to the most suitable provider/model, executes safe parallel work, and consolidates the results.

> Status: architecture / MVP foundation. This repository does not yet claim a production-ready router or universal session takeover.

## Product goals

- Reduce wall-clock time through dependency-aware parallel execution.
- Reduce token use through task-specific model selection, compact task briefs, context minimization and deduplication.
- Route by capability, latency, price, availability, privacy and user policy.
- Provide explicit fallback on rate limits, transient failures and provider outages.
- Keep a provider-neutral task graph and durable execution state.
- Integrate through native adapters rather than pretending all assistants share one session format.

## The `/hif` experience

Examples:

```text
/hif Analyse ce dépôt, identifie les bugs prioritaires et propose un plan de correction.
/hif Implémente l'écran de connexion, ajoute les tests et prépare la documentation.
/hif --parallel Compare ces trois solutions et produis une recommandation.
/hif status
/hif stop
```

HIF should return a plan before destructive or externally visible actions. Read-only analysis and isolated tasks may run concurrently. File edits must use isolated workspaces/worktrees or explicit conflict coordination.

## Architecture (target)

```text
Claude Code / Codex / other host
          | native skill, command, MCP adapter
          v
       HIF Gateway
          |
   Planner + Task Graph
          |
     Policy Engine
          |
   Model/Provider Router
     /    |     |     \
 Claude OpenAI Gemini OpenRouter ...
          |
 Parallel Executors + Retry/Fallback
          |
 Context/Artifact Store
          |
 Result Validator + Synthesizer
          |
     Host session (/hif)
```

### Core components

1. **CLI and host adapters** — expose `/hif` in supported clients using their documented extension points.
2. **Planner** — converts a user goal into typed tasks, dependencies, acceptance criteria and context budgets.
3. **Router** — selects provider/model per task using capability, configured budget, latency history, availability and privacy rules.
4. **Executor** — runs independent tasks concurrently with bounded concurrency, timeouts, cancellation and retries.
5. **Context manager** — sends only relevant files, summaries and task contracts; avoids forwarding entire transcripts by default.
6. **Artifact store** — stores task inputs/outputs and references so downstream tasks receive concise context.
7. **Verifier/synthesizer** — validates outputs, merges results and returns a concise report with provenance.
8. **Telemetry** — records token usage, estimated cost, duration, retries and routing decisions without logging secrets or sensitive prompt content by default.

## Non-negotiable design principles

- No quota circumvention, credential sharing, account farming or unsupported subscription pooling.
- Use official APIs and user-authorized credentials. Respect provider terms, rate limits and budget limits.
- Distinguish subscription quotas from API billing; never imply API fallback is free.
- Never claim quota visibility where a provider does not expose it.
- Never silently change a user's existing assistant configuration. Installation must be opt-in, reversible and backed up.
- Do not claim that changing provider transfers the native session. HIF passes a task brief, selected context and artifacts; the host remains responsible for its own conversation.
- Require approval for destructive file operations, deployments, purchases, external messages or other high-impact actions.
- Redact API keys and authorization headers; encrypt secrets at rest where persisted.
- Maintain auditability: explain why a model/provider was selected and what data was sent.

## Initial MVP

- Python 3.12+ orchestration service and CLI (implementation decision subject to ADR).
- Provider abstraction with an OpenAI-compatible adapter and explicit provider-specific adapters.
- Task graph with dependencies and bounded parallel execution.
- Heuristic router using task type, capability, configured price/latency and health.
- Token/cost budgets, per-task timeout and global cancellation.
- Mock provider and deterministic tests so CI requires no paid API keys.
- Claude Code plugin exposing `/hif` and MCP tools.
- Codex adapter documented as a separate integration; do not assume Claude plugin files work in Codex.
- Windows-first installation, with macOS/Linux compatibility where practical.

## Repository map

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/ROADMAP.md](docs/ROADMAP.md), [docs/SECURITY.md](docs/SECURITY.md) and [docs/ADR/0001-orchestration-boundary.md](docs/ADR/0001-orchestration-boundary.md).

## Development

The first implementation milestone will establish the Python package, configuration schema, provider protocol, mock adapter, planner/executor interfaces and tests. See the roadmap before adding real provider integrations.

## License

TBD. A license must be selected before external contributions or redistribution; until then, all rights are reserved by default.
