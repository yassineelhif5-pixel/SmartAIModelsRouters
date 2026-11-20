# SmartAIModelsRouters

**HIF — Hybrid Intelligent Flow** is a multi-provider AI task orchestrator. It is designed to make Claude, ChatGPT, Gemini and GitHub Copilot delegate work to the right models, parallelize independent tasks, reuse shared task memory and reduce unnecessary context/token usage.

HIF is built around two workflows:

- **\`/hif\`** — plan and route a goal across suitable providers, then return one consolidated result.
- **\`/hifnode\`** — split a complex goal into specialist nodes (architect, researcher, implementer, tester, reviewer, writer), run independent nodes concurrently and share one HIF session ID and approved memory.

> **Project status:** public repository and architecture/MVP foundation. The portable skill instructions and integration guides are being prepared. The production orchestration service, persistent shared memory, remote MCP gateway, adaptive resource manager and end-to-end host integrations are not yet complete. Do not treat a skill file alone as a working multi-provider router.

## What HIF is intended to do

1. **Task planning:** turn a user goal into a dependency-aware task graph.
2. **Model routing:** choose by task capability, price, measured latency, availability, privacy policy and budget.
3. **Parallel execution:** dispatch independent nodes concurrently with bounded concurrency.
4. **Shared session memory:** reuse role definitions, approved facts, summaries, node outputs and artifact references under one HIF session ID.
5. **Context optimization:** send each model only the relevant task brief and evidence, not the full conversation by default.
6. **Pre-emptive fallback:** prefer another eligible model when a trustworthy usage metric reaches the configured 80% threshold; never invent unavailable quota percentages.
7. **Resource management:** adapt concurrency to CPU/RAM pressure, optional GPU/VRAM telemetry and provider-specific concurrency limits.
8. **Verification and synthesis:** validate results and return one useful answer with routing, usage and timing information.

## Example requests

\`\`\`text
/hif Analyse ce dépôt et propose un plan de correction priorisé.
/hifnode Conçois, implémente, teste et documente le module de facturation.
/hif Compare trois architectures et produis une recommandation argumentée.
\`\`\`

Slash-command syntax depends on the host. In Claude Code, local skills can provide \`/hif\` and \`/hifnode\`. Web apps generally import the skill and invoke it by selecting or asking for the HIF workflow; they do not necessarily expose the same slash syntax.

## Supported host targets

| Assistant | Distribution method | Target |
|---|---|---|
| Claude web/Desktop | Import skill ZIP in Customize > Skills | Instructions and workflow |
| Claude Code | User-level/project Agent Skills and optional plugin | Local command/skill + future MCP tools |
| ChatGPT | Import skill ZIP on eligible plans; optional custom MCP app | Instructions + future HIF service tools |
| Gemini web app | Import skill in Gemini Skills | Instructions and workflow |
| Gemini CLI | User/workspace Agent Skills or extension | Terminal skill + future MCP tools |
| GitHub Copilot | Agent Skills in VS Code/Copilot-supported harnesses | User/workspace skill + future MCP tools |
| OpenAI Codex | Agent Skills under \`.agents/skills\` | CLI/IDE skill + future MCP tools |

Read [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) for exact per-product setup and limitations.

## Platform targets

HIF targets:
- Windows 10/11 developer clients.
- Windows Server with a dedicated service account.
- Linux workstations and servers.
- Container deployments (Docker/Podman) as a later packaging target.

The target deployment profiles and their current status are in [docs/PLATFORM-SUPPORT.md](docs/PLATFORM-SUPPORT.md).

## Repository layout

- \`skills/hif/SKILL.md\` — portable main orchestration skill.
- \`skills/hifnode/SKILL.md\` — portable parallel-node workflow.
- \`.claude/skills/\`, \`.gemini/skills/\`, \`.agents/skills/\`, \`.github/skills/\` — host-discoverable copies.
- \`docs/INTEGRATIONS.md\` — Claude, ChatGPT, Gemini and Copilot setup.
- \`docs/NODE-ORCHESTRATION.md\` — shared-session DAG and node design.
- \`docs/SHARED-MEMORY.md\` — shared memory model and retrieval policy.
- \`docs/RESOURCE-MANAGEMENT.md\` — CPU/RAM/GPU and concurrency scheduling.
- \`docs/QUOTA-FAILOVER.md\` — anticipatory fallback policy.
- \`docs/PLATFORM-SUPPORT.md\` — Windows client/server and Linux deployment.
- \`docs/ROADMAP.md\` — implementation status and milestones.

## Install skill instructions

### Windows PowerShell (Claude Code, Codex, Gemini CLI, Copilot)

\`\`\`powershell
git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
cd SmartAIModelsRouters
.\\scripts\\install-hif-skills.ps1
\`\`\`

### Linux/macOS (Claude Code, Codex, Gemini CLI, Copilot)

\`\`\`bash
git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
cd SmartAIModelsRouters
bash scripts/install-hif-skills.sh
\`\`\`

To create uploadable skill packages for Claude web, ChatGPT or Gemini web:

\`\`\`bash
python scripts/package-skills.py
\`\`\`

The ZIP files are written to \`dist/\`. See [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Important architecture and safety boundaries

- HIF uses explicitly authorized provider APIs and obeys provider terms and rate limits.
- An API key and API billing are separate from a consumer chat subscription unless the provider explicitly says otherwise.
- HIF only shares task briefs, approved memory and artifacts. It does not transfer another provider's private native conversation state or hidden reasoning.
- The 80% fallback rule only uses a provider-reported usage measure or HIF's own metered budget. Estimates are clearly labelled.
- Parallel file-writing tasks require isolated worktrees/workspaces or serialized merge stages.
- Secrets are never stored in skills, committed to Git or printed in logs.
- A remote HIF gateway must use authentication, TLS and access controls.

## Documentation

Start with:
- [Architecture](docs/ARCHITECTURE.md)
- [Integrations](docs/INTEGRATIONS.md)
- [Installation](docs/INSTALLATION.md)
- [Node orchestration](docs/NODE-ORCHESTRATION.md)
- [Shared memory](docs/SHARED-MEMORY.md)
- [Resource management](docs/RESOURCE-MANAGEMENT.md)
- [Quota failover](docs/QUOTA-FAILOVER.md)
- [Security](docs/SECURITY.md)
- [Roadmap](docs/ROADMAP.md)

## License

No open-source license has been selected yet. Until a LICENSE file is added, the repository is public but all rights are reserved by default.
