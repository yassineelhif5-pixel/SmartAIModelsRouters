# Platform support and deployment

## Target platforms

HIF is designed as a Python-based, provider-neutral orchestration service and CLI. Target environments:

| Platform | Target | Deployment model |
|---|---|---|
| Windows 10/11 | Developer workstation | Per-user virtual environment and CLI |
| Windows Server 2019/2022/2025 | Shared or dedicated server | Dedicated service account and supervised service |
| Linux (Ubuntu/Debian/RHEL-compatible) | Workstation/server | Python virtual environment and systemd |
| Docker/Podman | Cross-platform deployment | Containerized HIF gateway |

Core business logic must remain OS-agnostic. Service management, system telemetry, installers and credential storage belong in platform-specific adapters.

## Windows client

1. Install Git and Python 3.12+.
2. Clone the repository.
3. Create an isolated Python virtual environment.
4. Install HIF and optional provider/MCP dependencies.
5. Configure provider API credentials using environment variables or Windows Credential Manager.
6. Install the host-specific skill or plugin.
7. Run diagnostics and mock-provider tests before enabling paid providers.

Do not install HIF into the global Python interpreter if the workstation hosts other Python applications.

## Windows Server

- Use a dedicated non-administrator service account.
- Install HIF in a dedicated virtual environment under a controlled application directory.
- Run the gateway as a Windows Service only after the service wrapper and health/recovery behavior are implemented and tested.
- Bind to loopback for local-only use, or a protected private interface for remote clients.
- Store secrets using Credential Manager, DPAPI-backed storage or an enterprise secrets manager.
- Configure CPU, memory, concurrency, session isolation and provider budgets.
- Enable structured logs, log rotation, health checks and service recovery.
- Never expose an unauthenticated HIF gateway to the public internet.

A centralized server does not automatically attach every user's Claude, ChatGPT, Gemini or Copilot sessions. Each host must explicitly connect to the server's MCP endpoint or supported adapter.

## Linux

- Run HIF under a dedicated system user with no interactive login.
- Use a Python virtual environment.
- Use systemd with a restricted filesystem and protected environment file.
- Bind to localhost by default. For remote use, require TLS, authentication and a reverse proxy/private network.
- Apply CPUQuota, MemoryMax and TasksMax only after benchmarking.
- Use a secrets manager or a service-user-readable secret file.
- Log to journald or structured rotating files.

## Containers

A later container image should run as non-root, mount only the state directory, use read-only root filesystem where practical and receive secrets through the platform's secret manager. Never bake API keys into image layers.

## Resource controls

The resource manager uses one policy across OSes. Platform adapters supply CPU and memory telemetry. If monitoring is unavailable, HIF must use conservative concurrency limits and report that adaptive scheduling is unavailable.

## Current status

This page defines target deployment profiles. Windows service wrappers, Linux systemd packaging, production remote gateway, authentication, container images and fully tested cross-platform resource telemetry are roadmap items until released.
