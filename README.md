# SmartAIModelsRouters

**HIF — Hybrid Intelligent Flow** is a multi-provider AI task orchestrator. It is designed to make Claude, ChatGPT, Gemini and Microsoft/GitHub Copilot delegate work to the right models, parallelize independent tasks, reuse shared task memory and reduce unnecessary context/token usage.

HIF is built around two workflows:

- **/hif** — plan and route a goal across suitable providers, then return one consolidated result.
- **/hifnode** — split a complex goal into specialist nodes (architect, researcher, implementer, tester, reviewer, writer), run independent nodes concurrently and share one HIF session ID and approved memory.

> **Project status:** local MVP core is implemented and CI-tested: text-only provider dispatch, DAG nodes, shared SQLite session memory, measured-token fallback budgets, retry handling and CPU/RAM-aware bounded concurrency. The authenticated remote MCP gateway, desktop/web tool execution, file-editing agents, Windows Service/systemd packaging and full end-to-end host integrations remain future work.

## Implemented in local MVP 0.2.0

1. **Task planning:** create and validate a dependency-aware graph of up to 12 specialist nodes.
2. **Model routing:** use an ordered model pool, task-type preferences, per-model HIF token budgets and retry cooldowns.
3. **Parallel execution:** dispatch independent nodes concurrently and wait for dependencies.
4. **Shared session memory:** store role definitions, approved facts, node outputs, statuses and usage in a per-user SQLite database shared across projects.
5. **Context optimization:** supply each node with a compact brief, selected memory and dependency outputs instead of the full chat history.
6. **Pre-emptive fallback:** filter a model from new tasks when HIF-measured usage reaches the configured 80% budget.
7. **Resource management:** bound concurrency using CPU/RAM telemetry and configured per-provider semaphores.
8. **Local integration:** provide a CLI and stdio MCP server with hif_run and hifnode_run tools.
9. **Testing:** exercise the core using mock providers; CI runs without paid API keys.

## Planned optimization capabilities

Dynamic price/latency/quality scoring, provider-specific official quota APIs, per-task spending caps, automatic recovery/cancellation, file-editing agents, artifact hashing/cache, GPU/VRAM telemetry, dashboard, authenticated remote MCP gateway and Windows Service/Linux systemd packaging are not yet implemented. See docs/ROADMAP.md.

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
- A remote HIF gateway must use authentication, TLS and access controls.

## License

No open-source license has been selected yet. Until a LICENSE file is added, the repository is public but all rights are reserved by default.
