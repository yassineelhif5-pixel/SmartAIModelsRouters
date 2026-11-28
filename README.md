# HIF — Hybrid Intelligent Flow

**A ZirconAI.fr product** · [zirconai.fr](https://zirconai.fr)

Repository: SmartAIModelsRouters

**HIF — Hybrid Intelligent Flow** is a multi-provider AI task orchestrator. It is designed to make Claude, ChatGPT, Gemini and Microsoft/GitHub Copilot delegate work to the right models, parallelize independent tasks, reuse shared task memory and reduce unnecessary context/token usage.

HIF is built around two workflows:

- **/hif** — plan and route a goal across suitable providers, then return one consolidated result.
- **/hifnode** — split a complex goal into specialist nodes (architect, researcher, implementer, tester, reviewer, writer), run independent nodes concurrently and share one HIF session ID and approved memory.

> **Project status:** HIF 0.3.0 adds an authenticated REST + Streamable HTTP MCP gateway for a single-tenant private pilot, including an external OIDC/JWT resource-server verifier for OAuth 2.1 clients. The local text-only engine, DAG nodes, shared SQLite session memory, measured-token fallback budgets, retry handling and CPU/RAM-aware bounded concurrency remain available. multi-tenant identity isolation, fine-grained tool scopes, file-editing agents, Windows Service/systemd packaging and full end-to-end host integrations remain future work.


## ZirconAI.fr — HIF skills

HIF is published by **ZirconAI.fr**. Install the portable skills in a supported assistant to add specialized workflows on top of that assistant's own subscription and native tools.

| Skill | Workflow |
|---|---|
| `hif` | Auto classification and task routing |
| `hif-dev` | AI Tech Lead, software engineering, repository analysis, implementation and QA |
| `hif-bd` | DBA, SQL, data modeling, optimization and migrations |
| `hif-arc` | Solution, software, cloud and security architecture |
| `hif-strong` | High-assurance analysis, independent verification and risk controls |
| `hif-agent` | Specialist agent design, delegation and lifecycle |
| `hifnode` | Parallel specialist DAG workflow when connected HIF tools are available |

In supported coding-agent hosts, skills are usually invoked by their skill names (for example `/hif-dev` or `/hif-strong`). Other products expose skills through a picker or natural-language activation rather than slash commands. The aliases `/hifDev`, `/hifBD`, `/hifArc`, `/hifStrong` and `/hifAgent` describe the same mode intent; exact command syntax depends on the host.

### Two ways to use HIF

1. **Native subscription mode:** install the skill and use the assistant's currently selected model and native tools. No HIF API key is required for this workflow. The host controls its own subscription, model selection, quota and billing.
2. **Connected HIF mode:** connect the HIF MCP runtime to use HIF-managed sessions, provider adapters, orchestration, shared memory and telemetry. Independent provider API access may require separate credentials and billing.

Installing a skill does not install the HIF runtime or create independent access to other providers' consumer subscriptions. HIF never bypasses provider authentication, quotas or terms.

### Install all HIF skills

The installer and ZIP packager discover every directory under `skills/` containing a `SKILL.md`, so newly added mode skills are included automatically.





## HIF is a universal orchestrator — not only a coding assistant

HIF coordinates domain-specialist workflows for research and information collection, editorial work and professional reporting, marketing/publication campaigns, data analysis, business operations and technology delivery. Software development is one domain pack among several.

Its target interaction is **fast-first, then progressively deeper**: return an initial triage and next action quickly, publish validated milestones as they become available, and finish with a polished evidence-based deliverable. Actual background execution, live progress and multi-agent parallelism require a connected runtime or host tools that explicitly support them.

HIF treats reports as first-class deliverables: executive summaries, methodology, dated sources, findings, evidence, grounded charts/tables, risks, recommendations and limitations. File generation depends on an available artifact tool; it is never claimed without confirmation.

For campaign workflows, HIF can research, draft, adapt content to channels, prepare an editorial calendar and request approvals. Scheduling or publishing requires authorized connectors and explicit approval; HIF never fabricates publication status or engagement.

### Visual orchestration and reporting

The target HIF interface exposes a live timeline and graph of actual orchestrators, agents, tasks, dependencies, tool handoffs and artifacts, alongside a polished report preview, blockers, approvals and evidence. The graph must be generated from real structured runtime events, not simulated agents. This visual dashboard and the full event API are implementation targets, not yet claims of a shipped UI.

See [HIF Universal Orchestrator](docs/HIF-UNIVERSAL-ORCHESTRATOR.md) for domain coverage, fast-first behavior, research provenance, campaign approvals, report structure, graph/event contracts and the implementation sequence.

## HIF pipeline and multi-model routing

Every non-trivial request follows the same staged pipeline in portable Skills and the connected runtime: intake, classification, architecture assessment, specialist planning, model assignment, execution, cross-review, validation, synthesis and remaining-work checklist. Skill-only mode uses the active host model and native sub-agents only when available; connected mode uses HIF's configured multi-provider DAG engine.

The default model catalog covers:
- OpenAI: GPT-6 Luna, GPT-6.1 Sol and GPT-6.2 Astra.
- Anthropic: Claude Haiku 4.5, Sonnet 5 and Opus 5.
- Gemini: Gemini 3.5 Flash-Lite, Gemini 3.8 Flash and Gemini 3.1 Pro Preview.
- DeepSeek: DeepSeek Flash and DeepSeek V4 Pro.

Starter models are activated only when the corresponding provider API key is configured. Leave HIF_MODEL_POOL and HIF_TASK_MODEL_PREFERENCES empty to use the credential-aware defaults, or override them explicitly in .env. Provider API access may be billed separately from consumer subscriptions. See [Pipeline and Model Routing](docs/PIPELINE-AND-MODEL-ROUTING.md).

The Root Orchestrator also acts as the technical architect. It may appoint an Assistant Architect for independent design review and an Infrastructure Architect for hosting, network, identity, capacity, resilience, observability, backup/recovery and cost recommendations.

## Implemented in HIF 0.3.0

1. **Task planning:** create and validate a dependency-aware graph of up to 12 specialist nodes.
2. **Model routing:** use an ordered model pool, task-type preferences, per-model HIF token budgets and retry cooldowns.
3. **Parallel execution:** dispatch independent nodes concurrently and wait for dependencies.
4. **Shared session memory:** store role definitions, approved facts, node outputs, statuses and usage in a per-user SQLite database shared across projects.
5. **Context optimization:** supply each node with a compact brief, selected memory and dependency outputs instead of the full chat history.
6. **Pre-emptive fallback:** filter a model from new tasks when HIF-measured usage reaches the configured 80% budget.
7. **Resource management:** bound concurrency using CPU/RAM telemetry and configured per-provider semaphores.
8. **Local integration:** provide a CLI and stdio MCP server with hif_run and hifnode_run tools.
9. **Local integration:** CLI and stdio MCP server with hif_run and hifnode_run tools.
10. **Remote gateway:** authenticated REST and Streamable HTTP MCP, public minimal health check, bearer auth for private REST mode, optional OIDC/JWT authentication for MCP, request-size caps, per-IP rate limiting, Host/Origin allowlists and TLS guard.
11. **Testing:** mock-provider tests plus gateway security tests; CI runs without paid API keys.

## Planned optimization capabilities

Dynamic price/latency/quality scoring, provider-specific official quota APIs, per-task spending caps, automatic recovery/cancellation, file-editing agents, artifact hashing/cache, GPU/VRAM telemetry, dashboard, OAuth/OIDC, tenant isolation and Windows Service/Linux systemd packaging are not yet implemented. See docs/ROADMAP.md.

## Supported host targets

| Assistant | Distribution method | Target |
|---|---|---|
| Claude web/Desktop | Import skill ZIP in Customize > Skills | Workflow instructions |
| Claude Code | User-level/project Agent Skills | Local skill commands |
| ChatGPT | Import skill ZIP on eligible plans; optional custom MCP app | Workflow + future HIF tools |
| Gemini web app | Import through Gemini Skills | Workflow instructions |
| Gemini CLI | User/workspace Agent Skills | Terminal workflow |
| GitHub Copilot | Agent Skills in supported harnesses | Workspace/user workflow |
| Microsoft 365 Copilot | Copilot Studio agent + remote MCP | Enterprise agent tool |
| OpenAI Codex | Agent Skills under .agents/skills | CLI/IDE workflow |

See docs/INTEGRATIONS.md for exact product prerequisites, supported surfaces and limitations.

## Platform targets

HIF targets Windows 10/11, Windows Server, Linux and later Docker/Podman deployments. See docs/PLATFORM-SUPPORT.md.

## Install local skill instructions

### Windows PowerShell

    git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
    cd SmartAIModelsRouters
    .\scripts\install-hif-skills.ps1

### Linux/macOS

    git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
    cd SmartAIModelsRouters
    bash scripts/install-hif-skills.sh
    bash scripts/install-hif-runtime.sh

### Web assistant ZIP packages

    python scripts/package-skills.py

Creates dist/hif.zip and dist/hifnode.zip. Upload instructions for Claude, ChatGPT and Gemini web are in docs/INSTALLATION.md.

## Core documentation

- Architecture: docs/ARCHITECTURE.md
- Gateway: docs/GATEWAY.md
- Quickstart: docs/QUICKSTART.md
- Installation: docs/INSTALLATION.md
- Integrations: docs/INTEGRATIONS.md
- Node orchestration: docs/NODE-ORCHESTRATION.md
- Shared memory: docs/SHARED-MEMORY.md
- Resource management: docs/RESOURCE-MANAGEMENT.md
- Quota failover at 80%: docs/QUOTA-FAILOVER.md
- Platform support: docs/PLATFORM-SUPPORT.md
- Security: docs/SECURITY.md
- Roadmap: docs/ROADMAP.md

## Important boundaries

- HIF uses authorized provider APIs and obeys provider terms and rate limits.
- API usage may be billed separately from a consumer chat subscription.
- HIF shares explicit task briefs, approved memory and artifacts. It does not transfer another provider's private native conversation state or hidden reasoning.
- The 80% fallback rule uses provider-reported usage or HIF's own metered budget. Estimates are clearly labelled.
- Parallel file-writing tasks require isolated worktrees/workspaces or serialized merge stages.
- Secrets are never stored in skills, committed to Git or printed in logs.
- Local SQLite session memory is shared across projects for the same OS user by default.
- The HIF 0.3 gateway uses a shared bearer secret for a single-tenant private pilot; remote deployments must use TLS and network restrictions. It is not yet a public multi-tenant SaaS.

## License

No open-source license has been selected yet. Until a LICENSE file is added, the repository is public but all rights are reserved by default.


### New HIF 1.0 capabilities

- **Technical Leader:** coordinates connected issues, pull requests, CI events, task comments, logs and support channels; triages updates concurrently and returns actionable solutions with owners and next steps. Access is limited to explicitly connected and authorized channels.
- **Transformation / Migration:** `/hifTransform` and `/hifMigrate` intents inspect the existing project, define a target architecture, launch bounded child orchestrators by workstream and produce a phased migration plan with risks, tests, cutover and rollback before implementation approval.
- **Expanded engineering team:** Business/System Analyst, Maintenance & Reliability Engineer, Integration Manager and specialist developers work under the root AI Tech Lead.

These workflows are documented in `docs/HIF-1.0-MODES-SPEC.md`. Host-specific slash-command availability varies; skills may also be activated via a picker or natural language.


### Local-first ZirconAI runtime, signed updates and adaptive pipelines

HIF 1.0's target distribution is a fast per-user install branded **HIF by ZirconAI.fr**, with separate Skills-only, Local Core and Connected modes. The local Core is designed to stay lightweight: no local LLM weights by default, logical agents rather than resident processes, bounded memory and async execution.

The planned release updater verifies a signed ZirconAI.fr manifest and artifact hashes, stages updates, smoke-tests, switches atomically and rolls back on failure. Cryptographic publisher trust requires an actual published signing key/certificate and signed release artifacts; branding alone is not a signature.

The adaptive Pipeline Engine classifies complexity and urgency separately, creates priority-aware dependency DAGs, runs bounded in-memory queues, persists checkpoints in SQLite and adapts to token/provider/CPU/RAM limits. HIF may propose and test self-improvements, but cannot modify its trust roots, security policy or production installation without approval.

See:
- `docs/HIF-1.0-MODES-SPEC.md` — full local runtime, pipeline, update and controlled self-evolution design.
- `docs/INSTALLATION.md` — install tiers and update workflow.
- `docs/SECURITY.md` — release-signing and update security requirements.

**Implementation status:** these are HIF 1.0 specifications and release requirements. A production ZirconAI signing key, signed release pipeline, atomic updater and adaptive persistent pipeline scheduler must be implemented and tested before claiming these capabilities are available to end users.


## Lightweight local execution and application security

HIF adapts its default concurrency to the host's logical CPU count and available RAM. Resource samples are non-blocking; remote provider calls remain asynchronous and per-provider bounded. Local blocking I/O uses a lazy bounded thread pool, while explicitly submitted CPU-heavy helper functions use a bounded process pool. Skills-only installation starts no runtime service, worker or background monitor.

For a quick read-only security pre-audit of AI-generated/vibe-coded applications:

```bash
hif security scan .
hif security scan . --json
```

The scanner never executes project code and does not read .env contents. It reports heuristic findings, evidence, severity and a prioritized remediation plan. It is not a full SAST/DAST or security certification. See [Security Review for Vibe-Coded Software](docs/SECURITY-VIBE-CODING.md) and [Resource Management](docs/RESOURCE-MANAGEMENT.md).
