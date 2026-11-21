# HIF Quickstart — local MVP 0.3.0

This quickstart installs the HIF runtime and starts its local authenticated REST + Streamable HTTP MCP gateway. Remote clients still need a reachable HTTPS deployment.

## 1. Clone and install

### Windows PowerShell

    git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
    cd SmartAIModelsRouters
    .\scripts\install-hif-runtime.ps1

### Linux

    git clone https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
    cd SmartAIModelsRouters
    bash scripts/install-hif-runtime.sh

Both scripts create a Python 3.12 virtual environment, install dependencies and prepare a local .env file.

## 2. Configure providers

Edit .env. Supply at least one supported LiteLLM model ID and its provider API key. To enable fallback, add two or more eligible models from distinct providers.

Example configuration shape (replace every placeholder with an actual model ID available to your account):

    HIF_MODEL_POOL=anthropic/<model-id>,openai/<model-id>,gemini/<model-id>
    HIF_PLANNER_MODEL=anthropic/<model-id>
    HIF_TASK_MODEL_PREFERENCES={"research":["gemini/<model-id>"],"coding":["anthropic/<model-id>"]}
    HIF_USAGE_FALLBACK_THRESHOLD=0.80
    HIF_USAGE_WINDOW_HOURS=168
    HIF_DEFAULT_MODEL_TOKEN_BUDGET=250000
    HIF_MODEL_TOKEN_BUDGETS={"anthropic/<model-id>":100000,"openai/<model-id>":150000}

Set the API keys required by your selected providers. Never put API keys inside SKILL.md files or commit .env.

The token budgets above are **HIF-measured budgets** for calls made through HIF. They are not an authoritative view of a Claude Pro/Max, ChatGPT Plus/Pro, Gemini Advanced or other consumer subscription quota. API calls may be billed independently.

## 3. Run HIF from the terminal

Normal orchestration (one plan, sequential node processing):

    hif run "Analyse mon application et propose les corrections prioritaires"

Parallel specialist nodes:

    hif node "Analyse, conçois, teste et documente cette fonctionnalité"

Optional project context:

    hif node "Review this project architecture" --context-file .\PROJECT_CONTEXT.md

Every result returns a HIF session ID. Inspect the node status with:

    hif status <session-id>

Display HIF-measured usage:

    hif usage

Return JSON for automation:

    hif run "Prepare a technical plan" --parallel --json

## 4. Connect Claude Code globally for the current OS user

Windows: use the exact hif-mcp.exe path printed by install-hif-runtime.ps1:

    claude mcp add --scope user --transport stdio hif -- "C:\path\to\SmartAIModelsRouters\.venv\Scripts\hif-mcp.exe"
    claude mcp list

Linux:

    claude mcp add --scope user --transport stdio hif -- "$PWD/.venv/bin/hif-mcp"
    claude mcp list

The user scope makes the MCP server available in Claude Code projects for that OS user. Restart or open a new Claude Code session, then invoke /hif or /hifnode. The skills must also be installed; see INSTALLATION.md.

The MCP server currently exposes:
- hif_run: bounded orchestration without parallel specialist dispatch.
- hifnode_run: parallel specialist nodes with one HIF session ID and shared memory.
- hif_session_status: persisted node state.
- hif_usage: measured HIF token usage.


## 5. Start the authenticated gateway

Configure these values in .env:

    HIF_GATEWAY_API_KEY=<random-secret-at-least-32-characters>
    HIF_GATEWAY_HOST=127.0.0.1
    HIF_GATEWAY_PORT=8765
    HIF_GATEWAY_RATE_LIMIT_PER_MINUTE=60
    HIF_GATEWAY_MAX_REQUEST_BYTES=65536

Generate a key:

    python -c "import secrets; print(secrets.token_urlsafe(48))"

Keep the key in a protected secret store or service environment. Do not commit it.

Start the gateway:

    hif gateway

Local endpoints:
- Health: http://127.0.0.1:8765/healthz
- REST API: http://127.0.0.1:8765/v1/run and /v1/node
- MCP Streamable HTTP: http://127.0.0.1:8765/mcp

All endpoints except /healthz require Authorization: Bearer <secret>. See GATEWAY.md for REST examples, remote MCP client configuration and TLS reverse-proxy deployment.

The first gateway is single-tenant and uses one shared bearer secret. Do not expose it to untrusted users or the public internet without a trusted TLS reverse proxy and network restrictions. OAuth/OIDC and tenant isolation are future work.

## 6. Test without spending API credits

Run the test suite:

    python -m pip install -e ".[dev]"
    ruff check . --select E4,E7,E9,F
    python -m compileall -q src tests
    pytest

CI executes these checks on Ubuntu and Windows. Test providers are mocks; these tests do not prove live provider credentials, current model availability, production throughput or billing behavior.

## 7. Current limits

- Text-only provider tasks; the engine does not yet edit project files, run shell commands, browse or deploy.
- Parallel work is dependency-aware but bounded by HIF settings and local CPU/RAM telemetry.
- Provider routing currently uses configured order, task preferences, HIF-measured token budgets and temporary cooldowns. Dynamic price/latency/quality scoring is planned.
- The 80% threshold filters models using the HIF token budget meter. Provider-native subscription quota percentages are used only if a future official integration can obtain them.
- SQLite memory is per OS user by default and shared across projects on that machine. Remote multi-device memory needs the authenticated remote gateway, which is not implemented yet.
- ChatGPT web, Gemini web and Microsoft 365 Copilot can target the new remote MCP endpoint once it is deployed behind HTTPS and configured in the host. Their plan, tenant and remote-MCP permissions still apply.
