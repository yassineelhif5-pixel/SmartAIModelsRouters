# HIF Installation Guide

This guide separates installation of the **skill instructions** from installation of the **HIF orchestration service**. They are not the same thing.

## A. Install skill instructions on Windows

Supported targets in the current installer: Claude Code, OpenAI Codex, Gemini CLI and GitHub Copilot.

    git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
    cd SmartAIModelsRouters

    # Install the two skills globally for all supported local hosts
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

The script makes timestamped backups of existing directories. Start a new assistant session after installation.

## C. Create ZIP packages for web assistants

Use Python 3.10+:

    python scripts/package-skills.py

This creates dist/hif.zip and dist/hifnode.zip. Each ZIP contains the skill directory at its root, for example hif/SKILL.md.

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
