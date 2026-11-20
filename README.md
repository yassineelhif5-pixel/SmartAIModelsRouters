# SmartAIModelsRouters

**HIF — Hybrid Intelligent Flow** is a multi-provider AI task orchestrator. It is designed to make Claude, ChatGPT, Gemini and Microsoft/GitHub Copilot delegate work to the right models, parallelize independent tasks, reuse shared task memory and reduce unnecessary context/token usage.

HIF is built around two workflows:

- **/hif** — plan and route a goal across suitable providers, then return one consolidated result.
- **/hifnode** — split a complex goal into specialist nodes (architect, researcher, implementer, tester, reviewer, writer), run independent nodes concurrently and share one HIF session ID and approved memory.

> **Project status:** public repository and architecture/MVP foundation. Portable skill instructions and installation scripts are in the repository. The production orchestration service, persistent shared memory, remote MCP gateway, adaptive resource manager and end-to-end host integrations are not yet complete.

## What HIF is intended to do

1. **Task planning:** turn a user goal into a dependency-aware task graph.
2. **Model routing:** choose by task capability, price, measured latency, availability, privacy policy and budget.
3. **Parallel execution:** dispatch independent nodes concurrently with bounded concurrency.
4. **Shared session memory:** reuse role definitions, approved facts, summaries, node outputs and artifact references under one HIF session ID.
5. **Context optimization:** send each model only the relevant task brief and evidence, not the full conversation by default.
6. **Pre-emptive fallback:** prefer another eligible model when a trustworthy usage metric reaches the configured 80% threshold; never invent unavailable quota percentages.
7. **Resource management:** adapt concurrency to CPU/RAM pressure, optional GPU/VRAM telemetry and provider-specific concurrency limits.
8. **Verification and synthesis:** validate results and return one useful answer with routing, usage and timing information.

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
- A remote HIF gateway must use authentication, TLS and access controls.

## License

No open-source license has been selected yet. Until a LICENSE file is added, the repository is public but all rights are reserved by default.
