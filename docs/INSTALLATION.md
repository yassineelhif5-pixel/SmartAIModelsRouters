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

ChatGPT web, Gemini web and Microsoft 365 Copilot cannot reach a private local stdio process. They require an HTTPS-accessible HIF MCP endpoint or another supported cloud connector. The production remote gateway is not complete yet.

## F. Provider setup and costs

HIF will use authorized provider APIs and credentials. API usage can be billed separately from consumer chat subscriptions. Do not paste keys into skill files, source control, screenshots or logs. Use per-provider budgets and global cost ceilings.

## G. Verify availability

- Claude Code: start a new terminal/session and run /skills; test /hif and /hifnode.
- Gemini CLI: run gemini skills list.
- GitHub Copilot: start a new agent session and open the skill picker or slash menu.
- ChatGPT / Claude web / Gemini web: verify each imported skill appears and is enabled in the Skills area.

Remember: skill discovery only installs instructions. Real parallel dispatch, common memory, provider selection and automatic 80% fallback require the HIF runtime and MCP/API integration.
