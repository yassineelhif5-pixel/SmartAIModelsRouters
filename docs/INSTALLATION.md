# HIF Installation Guide

**ZirconAI.fr distribution:** HIF local runtime, portable Skills and MCP connector. Publisher identity is verified by signed release metadata once the signed-release channel is implemented and published. Until then, source repository branding is not proof of a cryptographic signature.

This guide separates installation of the **skill instructions** from installation of the **HIF orchestration service**. They are not the same thing.

## A. Install skill instructions on Windows

Supported targets in the current installer: Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, Kimi Code CLI and Qwen Code.

    git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
    cd SmartAIModelsRouters

    # Install all HIF skills for all supported local hosts
    .\scripts\install-hif-skills.ps1

    # Or select only the host you use
    .\scripts\install-hif-skills.ps1 -Hosts Claude
    .\scripts\install-hif-skills.ps1 -Hosts GeminiCLI
    .\scripts\install-hif-skills.ps1 -Hosts Copilot
    .\scripts\install-hif-skills.ps1 -Hosts Codex

    # Preview changes without making them
    .\scripts\install-hif-skills.ps1 -WhatIf

The installer backs up an existing HIF skill directory before replacing it. It installs instructions only; it does not install provider API keys, start a router, or create an MCP server.

## B. Install skill instructions on Linux/macOS

    git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
    cd SmartAIModelsRouters

    # Install for all supported local hosts
    bash scripts/install-hif-skills.sh

    # Select one host
    bash scripts/install-hif-skills.sh --hosts claude
    bash scripts/install-hif-skills.sh --hosts gemini
    bash scripts/install-hif-skills.sh --hosts copilot
    bash scripts/install-hif-skills.sh --hosts codex
    bash scripts/install-hif-skills.sh --hosts cursor
    bash scripts/install-hif-skills.sh --hosts kimi
    bash scripts/install-hif-skills.sh --hosts qwen

The script makes timestamped backups of existing directories. Start a new assistant session after installation.

### Additional coding-agent hosts

- **Cursor:** user Skills install to `~/.cursor/skills`; the repository also contains `.cursor/skills`. Enable Sync Skills for Cloud Agents when using personal Skills remotely.
- **Kimi Code CLI:** user Skills install to `~/.kimi-code/skills`; the repository contains `.kimi-code/skills`. The generic `.agents/skills` path is also supported by Kimi Code.
- **Qwen Code:** user Skills install to `~/.qwen/skills`; the repository contains `.qwen/skills`. Qwen Code also discovers `.agents/skills`.

The scripts copy the portable instructions only. They do not authenticate to those products or configure their MCP servers.

## C. Create ZIP packages for web assistants

Use Python 3.10+:

    python scripts/package-skills.py

This creates one ZIP per skill directory discovered under `skills/`, including specialist modes. Each ZIP contains the skill directory at its root.

### Claude web/Desktop

Open Customize > Skills > Create skill > Upload a skill, upload each ZIP and enable the skills. Code execution and file creation must be enabled; organization policy may apply.

### ChatGPT

On eligible ChatGPT Business, Enterprise, Healthcare or Edu workspaces, open Plugins > Skills > Create > Upload from your computer, then upload each ZIP. Availability is controlled by plan and workspace settings.

### Gemini web app

Open Gemini Apps > Skills and use the create/import workflow to upload the HIF skill file. The feature is only available on supported Gemini app surfaces and may be subject to rollout restrictions.

## D. Microsoft Copilot targets

- **GitHub Copilot:** use the user-level installer target Copilot or the repository .github/skills directory in supported agent harnesses.
- **Microsoft 365 Copilot:** use Copilot Studio to register the HIF remote MCP endpoint as an agent tool. Requires a deployed HTTPS MCP service, authentication, environment configuration and tenant governance.
- **Microsoft Copilot consumer app:** there is no generic direct install path for these local Agent Skill files documented by this project.

## E. Windows Server and Linux server deployment

A server deployment is intended to centralize the HIF gateway so remote assistant clients can connect to one shared orchestrator.

### Windows Server

- Use a dedicated non-administrator service account.
- Install the service in a dedicated Python virtual environment.
- Use Windows Credential Manager, DPAPI or an enterprise secret store.
- Bind locally by default; allow remote access only through a protected private network or TLS reverse proxy.
- Add health checks, service recovery, log rotation and resource limits.
- Do not install a production Windows Service until the service wrapper and gateway are implemented and tested.

### Linux server

- Use a dedicated service account and a Python virtual environment.
- Use systemd with a restricted filesystem, protected environment file, restart policy and journal logging.
- Bind to localhost unless a protected remote endpoint is explicitly required.
- Add TLS, authentication and tenant isolation before remote exposure.

### Remote host integrations

ChatGPT web, Gemini web and Microsoft 365 Copilot cannot reach a private local stdio process. They require an HTTPS-accessible HIF MCP endpoint or another supported cloud connector. The local authenticated REST + Streamable HTTP MCP gateway is now implemented for a single-tenant private pilot. Follow docs/GATEWAY.md to configure it. External OIDC/JWT token validation is supported for MCP when an identity provider is configured; HIF does not issue OAuth tokens. Multi-tenant SaaS controls, fine-grained permissions, Windows Service and Linux systemd packaging are still future work.

## F. Provider setup and costs

HIF will use authorized provider APIs and credentials. API usage can be billed separately from consumer chat subscriptions. Do not paste keys into skill files, source control, screenshots or logs. Use per-provider budgets and global cost ceilings.

## G. Verify availability

- Claude Code: start a new terminal/session and run /skills; test /hif and /hifnode.
- Gemini CLI: run gemini skills list.
- GitHub Copilot: start a new agent session and open the skill picker or slash menu.
- ChatGPT / Claude web / Gemini web: verify each imported skill appears and is enabled in the Skills area.

Remember: skill discovery only installs instructions. Real parallel dispatch, common memory, provider selection and automatic 80% fallback require the HIF runtime and MCP/API integration.


## ChatGPT plan note

Imported ChatGPT Skills are currently documented for eligible Business, Enterprise, Healthcare and Edu accounts; ChatGPT Go is not listed in the eligible-plan documentation. Custom MCP server access has separate requirements: Business and Enterprise/Edu support full MCP according to workspace permissions, while Pro is read/fetch-only. Go is not listed as a supported custom-MCP plan in the current Help Center article. Verify the current availability in the ChatGPT workspace before planning this integration.

Official details:
- https://help.openai.com/fr-fr/articles/20001066-skills-in-chatgpt
- https://help.openai.com/fr-fr/articles/12584461-connecting-custom-mcp-servers-in-chatgpt

## H. Install the HIF runtime (local Windows / Linux)

The skill-only installer copies instructions. To execute tasks against real providers, also install the Python runtime.

### Windows 10/11 or Windows Server

From the repository root in PowerShell:

    .\scripts\install-hif-runtime.ps1

The script creates a Python 3.12 virtual environment, installs the CLI, LiteLLM, MCP and resource-monitoring dependencies, then creates .env from .env.example when needed.

Open .env and configure at least:

- HIF_MODEL_POOL: comma-separated LiteLLM model IDs in preference order.
- The corresponding provider API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, etc.).
- Optional HIF_TASK_MODEL_PREFERENCES and per-model token budgets.

Use model IDs accepted by the provider and current LiteLLM adapter. Do not copy example IDs without verifying availability for your account.

Test the CLI:

    .\.venv\Scripts\hif.exe --help
    .\.venv\Scripts\hif.exe usage

Register MCP at user scope so Claude Code can use HIF across the user's projects. The runtime installer prints the exact executable path; run the displayed command:

    claude mcp add --scope user --transport stdio hif -- "C:\full\path\to\.venv\Scripts\hif-mcp.exe"
    claude mcp list

Start a new Claude Code session and invoke /hif or /hifnode.

### Linux

    bash scripts/install-hif-runtime.sh

Configure .env, then test:

    .venv/bin/hif --help
    .venv/bin/hif usage

Register the local MCP server globally for Claude Code:

    claude mcp add --scope user --transport stdio hif -- "$PWD/.venv/bin/hif-mcp"
    claude mcp list

### Shared memory location

By default, HIF stores SQLite state in a per-user data directory shared across projects:
- Windows: %LOCALAPPDATA%\HIF\hif.sqlite3
- Linux: $XDG_DATA_HOME/HIF/hif.sqlite3, or ~/.local/share/HIF/hif.sqlite3

Set HIF_DATABASE_PATH to an absolute path to override it. Use the same database path only for processes running under the same trusted user/service boundary. Do not put the database on an untrusted network share.

### Current runtime boundaries

The current HIF runtime performs text-only model calls, creates DAG nodes, shares explicit session memory, records provider-reported token usage and runs independent nodes concurrently. The authenticated REST + Streamable HTTP MCP gateway is implemented for a single-tenant private pilot. File edits, arbitrary shell/tool execution, browsing, deployment, Windows Service and Linux systemd units are not implemented. Remote assistants can connect only after the gateway is deployed on HTTPS and their host supports remote MCP.

## I. Run the authenticated HTTP/MCP gateway

HIF 0.3.0 includes a local REST API and MCP Streamable HTTP endpoint.

1. Install the runtime and configure provider credentials.
2. Generate a random secret and set HIF_GATEWAY_API_KEY in .env (minimum 32 characters).
3. Keep HIF_GATEWAY_HOST=127.0.0.1 for local use.
4. Run:

       hif gateway

5. Verify:

       curl http://127.0.0.1:8765/healthz

The remote MCP endpoint is http://127.0.0.1:8765/mcp. It requires the bearer secret in the Authorization header. REST endpoints are documented in docs/GATEWAY.md.

For remote access, put the process behind a trusted TLS reverse proxy, restrict inbound access and redact Authorization headers from proxy logs. Do not expose plain HTTP to the internet. Direct TLS binding is also supported by HIF_GATEWAY_TLS_CERTFILE and HIF_GATEWAY_TLS_KEYFILE.

The first gateway is a **single-tenant private pilot**: one shared bearer token, one service identity, one HIF memory database and one provider credential set. It is not suitable for mutually untrusted users or public SaaS use. OAuth/OIDC, tenant isolation, per-user permissions, distributed rate limits and audit exports remain future work.

The gateway does not yet enable file edits, arbitrary shell execution, browsing, deployments or automatic tool execution on behalf of remote assistants.


## I. Fast install and update design (HIF 1.0 target)

The product target is a fast, per-user installation with three selectable levels:
- **Skills only:** copies portable workflow instructions into supported local assistant hosts.
- **Local Core:** adds the lightweight Python runtime, SQLite state, CLI and local stdio MCP connector.
- **Connected:** Local Core plus explicitly configured provider adapters/API credentials or a remote HIF gateway.

The default installation must not download local LLM weights, GPU frameworks or start one process per agent. It should reuse compatible runtime/cache artifacts, install only selected components, and run `hif doctor` plus a local self-test. Provider API keys are not required for skills-only use or deterministic local utilities; they are required for independent remote model calls.

### Signed release verification

The planned ZirconAI.fr release channel will publish a signed manifest containing version, platform, source commit, artifact SHA-256 digests and compatibility metadata. The installer must verify the manifest signature against a trusted public key before running or extracting artifacts, then verify every artifact hash. Windows native binaries should use Authenticode signing when distributed as executables/installers.

**Current limitation:** until a ZirconAI.fr signing key/certificate, public verification key distribution and signed release artifacts are published, do not describe repository downloads as cryptographically signed. The product name/signature in documentation is branding only.

### Dynamic updates

The updater target is staged, verified and rollback-capable:
1. check the signed manifest on startup or a configurable schedule;
2. download only changed files/artifacts where safe;
3. verify signatures and hashes;
4. stage a side-by-side version and run smoke tests;
5. switch atomically at a safe restart boundary;
6. keep the previous known-good version and roll back on health failure;
7. preserve config, credentials, SQLite state and user project data.

Never overwrite a running Python module in place. Skill files can be updated on disk, but host assistants may cache instructions until a new session/reload. Auto-update must be configurable, with stable/preview channels, version pinning and deferral for enterprise users.

### Adaptive in-memory pipelines

The local Core will maintain bounded in-memory queues for active pipeline scheduling, while persisting checkpoints and critical state in SQLite. Each run receives complexity, urgency, priority, dependency graph, deadlines, token/resource budget and safe-resume metadata. Complexity and urgency are separate dimensions. Priority aging prevents low-priority starvation. No pipeline may bypass provider, concurrency, CPU/RAM, privacy or approval limits.

See the HIF 1.0 specification for pipeline classification, scheduling, controlled self-improvement and release acceptance criteria.


## J. Multi-model pipeline configuration

HIF includes a starter catalog across OpenAI, Anthropic, Google Gemini and DeepSeek. It activates only the providers for which an API key is configured. You do not need to configure every provider.

1. Copy .env.example to .env.
2. Add one or more provider API keys to the corresponding environment variables.
3. Leave HIF_MODEL_POOL empty to activate the built-in catalog for configured providers.
4. Leave HIF_TASK_MODEL_PREFERENCES empty to use task-specific defaults.
5. Set explicit values only when you want to override the defaults.

Starter API model identifiers:

| Provider | Fast / standard | Advanced |
|---|---|---|
| OpenAI | openai/gpt-6-luna, openai/gpt-6.1-sol | openai/gpt-6.2-astra |
| Anthropic | anthropic/claude-haiku-4-5-20251001, anthropic/claude-sonnet-5 | anthropic/claude-opus-5 |
| Gemini | gemini/gemini-3.5-flash-lite, gemini/gemini-3.8-flash | gemini/gemini-3.1-pro-preview |
| DeepSeek | deepseek/deepseek-flash | deepseek/deepseek-v4-pro |

Check provider documentation, account access, region and LiteLLM support before using any model in production. Model identifiers and availability can change. HIF's starter order is a fallback preference, not a universal quality benchmark.

Example environment setup:

```dotenv
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GEMINI_API_KEY=your-gemini-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# Empty means: auto-activate starter models for configured providers.
HIF_MODEL_POOL=
HIF_PLANNER_MODEL=

# Empty means: use HIF's task-specific defaults.
HIF_TASK_MODEL_PREFERENCES=
```

Do not put real credentials in source control. API calls are billed by providers separately from consumer chat subscriptions. Configure only providers you are authorized to use.

For model routing, task preferences, the Skill-native pipeline and architect roles, see [PIPELINE-AND-MODEL-ROUTING.md](PIPELINE-AND-MODEL-ROUTING.md).

## K. Pipeline behavior in portable Skills

Every HIF Skill follows the same logical pipeline: intake, complexity/urgency classification, architecture assessment when relevant, specialist planning, model/tool capability check, execution, cross-review, validation, synthesis and remaining-work checklist.

- When connected to local HIF MCP, the runtime schedules DAG nodes across configured provider models and reports HIF-measured usage.
- When installed as a Skill only, the host assistant follows the stages using its current model. It can parallelize only if the host explicitly provides native sub-agents.
- A Skill cannot independently switch a consumer model, access other vendors' consumer subscriptions or inspect hidden host quotas.
- If only one model is available, HIF still follows the structured stages with that model; it does not fabricate a multi-model execution report.

The Root Orchestrator is also the architect. It may assign an Assistant Architect for independent design critique and an Infrastructure Architect for deployment, networking, identity, capacity, resilience, observability, backup/recovery and cost recommendations. These advisory roles are activated only when relevant.


## L. Adaptive resource usage on workstations and servers

By default, HIF derives the initial task concurrency from the machine's logical CPU count and available RAM, with a conservative maximum of eight. Runtime sampling is non-blocking. Remote provider requests use async I/O and provider-specific semaphores. Local blocking I/O uses a lazy bounded thread pool; explicitly submitted CPU-heavy helper functions use a lazy bounded process pool.

In .env, leave HIF_MAX_PARALLEL_TASKS unset/commented to use auto sizing. Optional overrides:

```dotenv
HIF_MAX_PROVIDER_PARALLEL=3
HIF_MAX_LOCAL_THREADS=2
HIF_MAX_LOCAL_PROCESSES=1
HIF_LOCAL_TASK_MEMORY_MB=512
HIF_CPU_PRESSURE_THRESHOLD=85
HIF_MEMORY_PRESSURE_THRESHOLD=88
HIF_MIN_FREE_MEMORY_MB=1536
```

For a shared server, benchmark under representative load and set a conservative explicit HIF_MAX_PARALLEL_TASKS. Run HIF under a dedicated least-privilege OS account and apply external OS/container resource limits. In-process adaptive concurrency is cooperative; it is not a hard memory/CPU isolation boundary. A Skills-only installation creates no local runtime, threads, services or background workers.

## M. Vibe-coded application security pre-audit

After installing the HIF runtime, run the local read-only scanner against the project. The provider API extra is not required for this local scan:

```bash
hif security scan .
hif security scan . --json
```

It checks common source/configuration patterns, reports evidence and severity, and produces a prioritized remediation plan. It does not execute application code, does not open .env contents and does not modify files. It is a lightweight heuristic pre-audit, not full SAST/DAST or a security certification.

Use the full [Security Review for Vibe-Coded Software](SECURITY-VIBE-CODING.md) guide for dependency scanning, threat modeling, authentication/authorization checks, tenant isolation, regression tests and release recommendations.
