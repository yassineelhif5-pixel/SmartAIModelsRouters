# HIF — Hybrid Intelligent Flow

**Your AI agents, under control: the right model, at the right price, with the proof. On your machines or in Europe.**

[![CI](https://github.com/yassineelhif5-pixel/SmartAIModelsRouters/actions/workflows/ci.yml/badge.svg)](https://github.com/yassineelhif5-pixel/SmartAIModelsRouters/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

HIF splits a goal into specialist tasks, sends each one to the cheapest model able to do it,
runs independent tasks in parallel and returns one consolidated result with its token usage.
It talks directly to **32 AI providers** (OpenAI, Anthropic, Gemini, Mistral, DeepSeek, Azure,
AWS Bedrock, Ollama, vLLM…) with your own keys: no aggregator in the middle, no markup.

A [ZirconAI.fr](https://zirconai.fr) project.

## Why HIF

AI gateways move requests from your app to a model. HIF orchestrates the work itself.

| | Typical AI gateway | HIF |
| --- | --- | --- |
| Unit of work | One request | A goal, split into a graph of specialist tasks |
| Model choice | A list or a price rule | Per task type, with budgets and fallback |
| Runaway agents | Billing alert after the fact | Spend guard stops the session before the next call |
| Where it runs | Often a vendor cloud | Your laptop, your servers, your cloud |
| Providers | Through the vendor | Direct, 32 providers, local models included |

## Try it in five minutes

```bash
git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
cd SmartAIModelsRouters
python -m pip install -e .

export MISTRAL_API_KEY=...        # or OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY…
hif providers --configured        # which providers are ready
hif run "Compare token bucket and fixed window rate limiting, then recommend one"
```

No API key? Run a local model: `HIF_ENABLE_OLLAMA=true HIF_MODEL_POOL=ollama/llama3.1 hif run "..."`.

## What works today (v0.4.0)

| Capability | Command or module |
| --- | --- |
| Task planning into a validated graph of up to 12 specialist nodes | `hif run`, `hif node` |
| Parallel execution of independent nodes, bounded by CPU, RAM and per-provider limits | `hif node` |
| Direct connections to 32 providers, native Anthropic and Gemini adapters | `hif providers`, [docs/PROVIDERS.md](docs/PROVIDERS.md) |
| Model routing by task type, HIF-measured token budgets, fallback on rate limits and outages | [docs/PIPELINE-AND-MODEL-ROUTING.md](docs/PIPELINE-AND-MODEL-ROUTING.md) |
| **Spend guard**: per-session caps on tokens, calls and cost, plus loop detection | `HIF_SESSION_*` settings |
| Shared session memory in SQLite | [docs/SHARED-MEMORY.md](docs/SHARED-MEMORY.md) |
| **Benchmark** against a single model on 30 deterministic tasks | `hif bench --baseline <model>` |
| Independent multi-provider project evaluation (validated, conditional, rejected, inconclusive) and approval-gated counter-test plans | MCP tools `hif_evaluate_project`, `hif_countertest_plan`, [docs/MULTI-MODEL-EVALUATION.md](docs/MULTI-MODEL-EVALUATION.md) |
| Execution profiles `auto`, `browser`, `small`, `standard`, `server` that size concurrency, context and output | `HIF_EXECUTION_PROFILE` |
| Read-only security pre-audit of AI-generated code | `hif security scan .` |
| MCP server (stdio) and authenticated REST + MCP gateway for a single-tenant pilot | `hif mcp`, `hif gateway` |
| Skills for Claude, ChatGPT/Codex, Gemini, Copilot, Cursor, Kimi and Qwen, plus a portable Agent Plugin | `scripts/install-hif-skills.sh`, `plugins/hif-universal/` |

Planned work lives in [docs/ROADMAP.md](docs/ROADMAP.md). Design specifications for later
versions are in [docs/rfc/](docs/rfc/): they describe targets, not shipped features.

## Measure it yourself

```bash
hif bench --baseline openai/gpt-6.2-sol --out bench-results
```

The benchmark runs the same 30 tasks (extraction, coding, security, data, writing, planning)
through one model and through HIF, grades every answer with deterministic checks, and writes
`bench-results/report.md` with pass rates, tokens and reported cost for both. Add
`--allow-code-exec` to run the coding tasks' generated code in an isolated interpreter.

## Stop runaway agents

Every HIF session has a budget, checked before each model call:

```bash
HIF_SESSION_MAX_TOKENS=500000      # input + output tokens per session
HIF_SESSION_MAX_CALLS=100          # model calls, retries included
HIF_SESSION_MAX_COST_USD=2.50      # when the provider reports a cost
HIF_SESSION_LOOP_REPEAT_LIMIT=3    # identical prompt to the same model
```

A session that crosses a limit stops with the status `stopped_by_spend_guard` and makes no
further calls.

## Skills for your assistant

Install the HIF workflows in the assistant you already pay for. No HIF key is needed:
the skills use your assistant's own model and tools.

```bash
bash scripts/install-hif-skills.sh          # Linux / macOS
.\scripts\install-hif-skills.ps1            # Windows PowerShell
python scripts/package-skills.py            # ZIP files for web assistants
```

| Skill | Workflow |
| --- | --- |
| `hif` | Classifies the request and picks a workflow |
| `hif-dev` | Tech lead workflow for repository work, implementation and QA |
| `hif-bd` | SQL, data modeling, optimization, migrations |
| `hif-arc` | Solution, cloud and security architecture |
| `hif-strong` | High-assurance analysis with independent verification |
| `hif-agent` | Specialist agent design and delegation |
| `hifnode` | Parallel specialist graph, when the HIF runtime is connected |

Host support details: [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md).

## Editions

The engine in this repository is open source under Apache-2.0. Team governance (console,
SSO, RBAC, audit log, budgets per team, on-premise packages, SLA) is sold as commercial
editions by ZirconAI.fr. The boundary is described in [COMMERCIAL.md](COMMERCIAL.md).

## Documentation

- [Quickstart](docs/QUICKSTART.md) · [Installation](docs/INSTALLATION.md) · [Architecture](docs/ARCHITECTURE.md)
- [Providers](docs/PROVIDERS.md) · [Routing](docs/PIPELINE-AND-MODEL-ROUTING.md) · [Quota failover](docs/QUOTA-FAILOVER.md)
- [Gateway](docs/GATEWAY.md) · [Security](docs/SECURITY.md) · [Security review for AI-generated code](docs/SECURITY-VIBE-CODING.md)
- [Node orchestration](docs/NODE-ORCHESTRATION.md) · [Shared memory](docs/SHARED-MEMORY.md) · [Resource management](docs/RESOURCE-MANAGEMENT.md)
- [Multi-model evaluation](docs/MULTI-MODEL-EVALUATION.md) · [Plugin and skill packaging](docs/PLUGIN-AND-SKILL-PACKAGING.md)
- [Platform support](docs/PLATFORM-SUPPORT.md) · [Roadmap](docs/ROADMAP.md) · [Changelog](CHANGELOG.md)

## Boundaries

- HIF calls provider APIs with your credentials and follows their terms and rate limits.
  API usage is billed by each provider, separately from consumer chat subscriptions.
- The 80 % fallback rule uses HIF's own token metering, not the provider's private quota.
- The security scan is a heuristic pre-audit, not a SAST/DAST tool or a certification.
- The gateway uses a shared bearer secret for a single-tenant pilot; expose it only behind
  TLS and network restrictions.
- Session memory is a local SQLite file shared across projects for the same OS user.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
