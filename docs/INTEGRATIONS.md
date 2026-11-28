# HIF multi-host integrations

**Publisher and connector signature: ZirconAI.fr** ([zirconai.fr](https://zirconai.fr))

HIF provides one provider-neutral orchestration engine and a portable instruction skill. Host products differ in skill support, MCP/tool access, local execution, authentication and subscription entitlements.

## The critical distinction: native subscription vs connected HIF

| Experience | What the user can do | What it does not automatically provide |
|---|---|---|
| Native skill in the current AI product | Ask the host assistant to follow HIF's workflow using its own active model and native tools | No automatic access to other providers, their models, private quotas or cross-provider subscription pooling |
| Skill + HIF MCP runtime | Invoke HIF's backend, share a HIF session, use configured tools/providers and receive structured run status | Does not convert a consumer chat subscription into API credentials |
| HIF local runtime | Run local indexing, file inspection, deterministic preprocessing, memory, scheduler and MCP stdio on the user's machine | Does not grant access to host chat history or provider subscription entitlements |
| HIF remote gateway | Connect supported web clients to a deployed authenticated HTTPS MCP endpoint | Requires deployment, authentication, host support and provider configuration |

**Subscription rule:** HIF can use the current host model inside the native conversation when the host allows it. If HIF itself must call OpenAI, Anthropic, Google or another provider independently, it needs an officially supported authentication path and provider entitlement. API access may be billed separately. Never scrape browser sessions, reuse hidden cookies, automate consumer chat UIs to evade API limits, or claim a subscription quota is available to HIF unless the provider officially exposes it.

## Compatibility and integration matrix

| Product | Portable skill / instructions | Connected HIF path | Important limitation |
|---|---|---|---|
| ChatGPT | Importable Skills where the account/workspace exposes Skills | Custom MCP app to deployed HTTPS HIF endpoint where plan/workspace controls permit | Skill availability and MCP permissions are plan/admin dependent; consumer subscription is not a general API key |
| Claude web/Desktop | Custom Skills upload where enabled | Supported remote connector/MCP path where available; otherwise skill works as workflow guidance | A Skill alone does not launch the independent HIF backend or other providers |
| Claude Code | `.claude/skills` | Local stdio MCP or remote MCP | HIF runtime must be installed/configured; provider APIs still need authorized credentials |
| Gemini web app | Skills feature where available | Supported remote MCP/tool integration if exposed to the account | Skill upload alone does not connect the local runtime |
| Gemini CLI | Agent Skills | Local stdio MCP or supported remote MCP | CLI runs in its own local environment |
| GitHub Copilot (VS Code, CLI and app where supported) | Agent Skills in `.github/skills/` or personal skill locations | Local or remote MCP configured in the host | Native locations and features vary by harness and organization policy |\n| VS Code Agent Skills | `.github/skills/`, `.claude/skills/`, `.agents/skills/`; extensions can contribute `chatSkills` | MCP or extension-provided tools | Extension packaging requires a separate VS Code extension manifest; not bundled in this repo |
| Microsoft 365 Copilot | Copilot Studio agent instructions | Copilot Studio tool/MCP connection to remote HIF gateway | Requires tenant governance and configured Copilot Studio environment; not a simple consumer-app skill install |
| Microsoft Copilot consumer app | No generic portable HIF skill installation is assumed | Only if Microsoft provides an enabled extension/agent path for that user | Do not conflate with GitHub Copilot or Microsoft 365 Copilot Studio |
| OpenAI Codex | `.agents/skills` | Local stdio MCP or supported remote MCP | Separate host/runtime configuration |
| Cursor Agent / Cloud Agents | `.cursor/skills`, also compatible with `.agents/skills` | MCP configured in Cursor; local/remote according to Cursor surface | Cloud Agents require Skills Sync or project-level skills; host model routing remains controlled by Cursor |
| Kimi Code CLI | `.kimi-code/skills` and generic `.agents/skills` | Kimi CLI MCP configuration | Kimi's own model login/API and provider limits remain separate |
| Qwen Code | `.qwen/skills` and generic `.agents/skills` | Qwen Code MCP configuration | Native sub-agents/teams are Qwen harness features; HIF does not claim to control them unless connected |
| NotebookLM | HIF NotebookLM companion workflow and user-provided HIF reference sources | No generic NotebookLM Agent Skill/MCP tool execution is assumed | NotebookLM is treated as a source-grounded research workspace, not as a general HIF host or agent runtime |

A portable skill is an **instruction layer**. A Plugin bundles Skills and optional MCP configuration under a portable manifest. MCP is a **tool connection**. HIF local/remote runtime is the **execution layer**. They are separate and must be installed/configured separately. The repository now includes `plugins/hif-universal/plugin.json` and `.agents/plugins/marketplace.json`; this makes the Skills package discoverable in supported plugin hosts, but does not deploy or authenticate the MCP runtime.

## 1. ChatGPT

Where the ChatGPT Skills feature is available:
1. Package the portable skill with `python scripts/package-skills.py`.
2. Open the Skills area in ChatGPT.
3. Upload the HIF skill ZIP if the workspace allows it.
4. Start a new conversation and ask ChatGPT to use HIF.

For connected orchestration, configure the HIF remote MCP endpoint as a custom app where the account plan and workspace admin controls permit. The endpoint must be reachable over HTTPS and use supported authentication. A local stdio process on a workstation is not directly reachable from ChatGPT web.

The native skill can still guide the current ChatGPT model if MCP is unavailable. In that case it must not claim to have routed work to other providers or read exact token usage unless the host exposes it.

Official documentation:
- https://help.openai.com/en/articles/20001066-skills-in-chatgpt
- https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- https://developers.openai.com/api/docs/guides/custom-mcp-server

## 2. Claude web/Desktop and Claude Code

For Claude web/Desktop, upload the portable skill ZIP in the Skills interface when available and enabled for the account/workspace. The skill guides Claude's current model; it does not itself connect to HIF.

For Claude Code, install the skill under `~/.claude/skills` and register HIF's local stdio MCP executable or supported remote endpoint. Start a new session and verify that the HIF tools appear before expecting connected orchestration.

Official documentation:
- https://support.claude.com/en/articles/12512180-use-skills-in-claude
- https://support.claude.com/en/articles/12512198-create-custom-skills

## 3. Gemini web and Gemini CLI

For Gemini web, import/use the HIF skill only if the Skills feature is exposed to the user's account. Skill instructions alone do not connect a local HIF process; configure a supported remote tool/MCP connection separately if available.

For Gemini CLI, install the user-level skill and register the local HIF stdio MCP server. Verify using the CLI's skill and MCP listing commands.

Official documentation:
- https://support.google.com/gemini/answer/17094296
- https://geminicli.com/docs/cli/skills/
- https://geminicli.com/docs/cli/using-agent-skills/

## 4. GitHub Copilot

Use the Agent Skills locations supported by the selected Copilot host (for example VS Code or a repository's `.github/skills`). Register HIF's local or remote MCP server using that host's MCP configuration. Feature availability depends on the Copilot product, IDE version and organization policy.

Official documentation:
- https://code.visualstudio.com/docs/agent-customization/agent-skills
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills

## 5. Microsoft 365 Copilot

The supported target architecture is a Copilot Studio agent with HIF exposed as a governed remote tool/MCP endpoint. This requires an appropriate tenant, environment, authentication and admin approval. It is not the same as installing a GitHub Copilot Agent Skill and is not assumed to work in the consumer Microsoft Copilot app.

Official documentation:
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-add-mcp-server
- https://learn.microsoft.com/microsoft-365-copilot/extensibility/overview-custom-engine-agent

## 6. Cursor Agent

Cursor supports the Agent Skills format in project `.cursor/skills/` and user `~/.cursor/skills/` locations. It also discovers compatible `.agents/skills/` folders. The repository includes a native `.cursor/skills/` mirror and the installer supports a user-level Cursor installation.

For Cloud Agents, either commit skills in the repository or enable Cursor's Sync Skills for personal skills. Local user skills are not automatically uploaded to Cloud Agents unless synchronized.

Official documentation:
- https://cursor.com/docs/skills

## 7. Kimi Code CLI

Kimi Code CLI supports Agent Skills with a Kimi-specific user directory and the generic Agent Skills directories. The repository includes a `.kimi-code/skills/` mirror. The installer copies Skills to `~/.kimi-code/skills/` for the current Kimi Code CLI layout. Older Kimi CLI distributions may use `~/.kimi/skills/`; verify the active CLI's discovery paths before installation.

Kimi model calls through the HIF runtime use the Moonshot provider adapter (`moonshot/`) and require a Moonshot API key. Installing a Skill does not log in to Kimi or provide access to a Kimi consumer subscription.

Official documentation:
- https://moonshotai.github.io/kimi-code/en/customization/skills
- https://moonshotai.github.io/kimi-cli/en/customization/skills.html

## 8. Qwen Code

Qwen Code supports Agent Skills from `.qwen/skills/` and the generic `.agents/skills/` directory. The repository includes a native `.qwen/skills/` mirror and the installer supports `~/.qwen/skills/`.

Qwen model calls through HIF use the DashScope provider adapter (`dashscope/`) and require a DashScope/Qwen API key. Qwen Code's native sub-agent/team capabilities are controlled by Qwen Code itself; HIF does not claim to orchestrate those features unless the HIF runtime is explicitly connected.

Official documentation:
- https://github.com/QwenLM/qwen-code/blob/main/docs/users/features/skills.md

## 9. NotebookLM — companion workflow, not a native HIF skill

Do not advertise NotebookLM as a generic Agent Skills or MCP host. HIF provides a companion workflow that helps users prepare a research brief and source pack for NotebookLM:
1. Use HIF (in a supported host or local runtime) to identify research questions and gather user-approved documents/sources.
2. Produce a compact source index, glossary, question list and evidence map.
3. Let the user add those source files/URLs to a NotebookLM notebook using NotebookLM's supported source-import UI.
4. Ask NotebookLM to answer questions grounded in the imported sources.
5. Export or copy the resulting notes/claims back into HIF for source verification, synthesis and a remaining-work checklist.

NotebookLM's own source access, sharing, account limits and supported imports remain controlled by Google. HIF does not claim direct NotebookLM API control, notebook creation, source injection or autonomous notebook access unless Google provides a supported integration and it is actually implemented.

## 10. Local installation and remote gateway

Local runtime:
- Install HIF in a per-user virtual environment.
- Install the portable skill into the host's supported skill directory.
- Register the local stdio MCP server only in hosts running on the same machine/environment.
- Keep local indexing and file access behind explicit permissions.

Remote web clients:
- Deploy HIF gateway on an HTTPS-reachable host.
- Configure authentication and least-privilege tool scopes.
- Apply tenant/session isolation, rate limits, audit logs and privacy policy before multi-user production use.
- Do not expose an unauthenticated gateway to the public internet.

See `docs/GATEWAY.md`, `docs/INSTALLATION.md` and `docs/SECURITY.md`.

## 11. Portable skill installation

The current scripts discover and install every local Agent Skill directory under `skills/` for supported local hosts (Claude Code, Codex, Gemini CLI, supported Copilot hosts, Cursor, Kimi Code CLI and Qwen Code). This includes `hif`, `hifnode`, `hif-dev`, `hif-bd`, `hif-arc`, `hif-strong` and `hif-agent`. They do not install HIF's runtime and do not automatically upload skills to web products.

Windows PowerShell:
```powershell
.\scripts\install-hif-skills.ps1 -Hosts Claude,Codex,GeminiCLI,Copilot,Cursor,Kimi,Qwen
```

Linux/macOS:
```bash
bash scripts/install-hif-skills.sh --hosts claude,codex,gemini,copilot,cursor,kimi,qwen
```

Build ZIP packages for supported web skill-upload surfaces:
```bash
python scripts/package-skills.py
```

The package command automatically builds one ZIP for every portable skill folder, including all five specialist modes. It does not package NotebookLM as a native skill.

## 12. Cross-host memory and privacy

HIF can share session memory across hosts only for data explicitly stored in the HIF runtime and permitted by the user. It does not merge native ChatGPT, Claude, Gemini, Copilot or NotebookLM chat histories. The user must be able to inspect, scope and delete HIF-stored session/project data under the runtime's retention policy.


## 13. ZirconAI.fr signature and specialist mode skills

All HIF skills are published under the **ZirconAI.fr** product signature. The portable skill folders are:

- `hif`: Auto classification and mode selection.
- `hif-dev`: AI Tech Lead and software engineering workflow.
- `hif-bd`: Database and data engineering workflow.
- `hif-arc`: Architecture workflow.
- `hif-strong`: high-assurance analysis and verification.
- `hif-agent`: agent workforce design and lifecycle.
- `hifnode`: connected parallel DAG orchestration.

In coding-agent hosts that expose skills as slash commands, names commonly map to `/hif-dev`, `/hif-bd`, `/hif-arc`, `/hif-strong` and `/hif-agent`. The camel-case aliases `/hifDev`, `/hifBD`, `/hifArc`, `/hifStrong` and `/hifAgent` are semantic aliases; not every host accepts custom slash command spellings. ChatGPT, Claude web, Gemini web and NotebookLM may expose a skill picker or natural-language activation instead of a slash-command interface.

The skill adds specialized instructions and task logic to the host assistant. In Native Subscription mode, it uses only the currently active host model and tools available to that user. It does not create independent API calls to other providers or inspect private subscription quotas. Connected HIF mode requires an explicit MCP connection and configured runtime/provider credentials.

## 14. Current implementation status

- Portable HIF and HIF Node instructions exist in the repository and are mirrored for supported coding-agent hosts.
- ZIP packaging and local skill-copy scripts exist as source code.
- HIF 0.3.0 includes local stdio MCP and an authenticated remote HTTP/Streamable HTTP MCP gateway intended for a single-tenant private pilot.
- Existing orchestration is text-task oriented; do not claim full host-native multi-agent UX, project file editing, NotebookLM control or universal consumer-subscription access.
- Host plan eligibility, UI labels and connector availability change over time. Recheck official host documentation before publishing end-user installation instructions.


## 15. Pipeline and architecture advisory roles

All HIF Skills use the common staged pipeline. See [Pipeline Engine and Multi-Model Routing](PIPELINE-AND-MODEL-ROUTING.md) for the lifecycle, default provider catalog, configuration, installation and Skill-only versus connected execution behavior.

The root orchestrator is also the architecture owner. It may assign an Assistant Architect for independent design critique and an Infrastructure Architect for deployment, network, identity, capacity, resilience, observability, backup/recovery and cost recommendations. See docs/HIF-1.0-MODES-SPEC.md section 26 for the normative contract.


## 16. Lightweight runtime and application security

The runtime adapts concurrency to available CPU and RAM, uses non-blocking telemetry, async provider I/O and lazy bounded local worker pools. Skills-only mode does not start local workers or background services.

Run the built-in read-only security pre-audit with `hif security scan .`. It returns evidence, severity and a remediation plan without executing project code or opening .env contents. See [Resource Management](RESOURCE-MANAGEMENT.md) and [Security Review for Vibe-Coded Software](SECURITY-VIBE-CODING.md).
