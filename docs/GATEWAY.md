# HIF Gateway — authenticated REST + Streamable HTTP MCP

The HIF Gateway is the remote transport layer for a central HIF runtime. It exposes the same process-wide engine through a small REST API and the MCP Streamable HTTP transport.

## Status and intended use

- Implemented: REST endpoints, Streamable HTTP MCP endpoint, bearer-token authentication, constant-time token comparison, request-size checks, per-source-IP fixed-window rate limiting, no-store/security headers, health endpoint and non-loopback TLS guard.
- Current security model: **single tenant / one shared bearer secret**. This is a private pilot gateway, not a multi-tenant SaaS control plane.
- Not yet implemented: OAuth/OIDC, per-user identities, tenant isolation, per-tool scopes, admin UI, distributed rate limiting, audit export, HA deployment or production operations.
- The gateway does not grant file-system or shell access. It dispatches the same text-only HIF tasks as the local MVP.

## 1. Install and configure

Install HIF runtime as described in QUICKSTART.md, then configure .env:

    HIF_MODEL_POOL=provider/model-id,other-provider/model-id
    HIF_GATEWAY_API_KEY=REPLACE_WITH_A_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
    HIF_GATEWAY_HOST=127.0.0.1
    HIF_GATEWAY_PORT=8765
    HIF_GATEWAY_RATE_LIMIT_PER_MINUTE=60
    HIF_GATEWAY_MAX_REQUEST_BYTES=65536

Generate a strong secret (do not commit it):

Windows PowerShell:

    python -c "import secrets; print(secrets.token_urlsafe(48))"

Linux/macOS:

    python -c 'import secrets; print(secrets.token_urlsafe(48))'

Store the key in a secret manager or a protected environment file readable only by the HIF service account. Do not put it in a skill, source file, browser-visible prompt, public URL or Git repository.

## 2. Start locally

    hif gateway

The default listener is 127.0.0.1:8765. Health check:

    curl http://127.0.0.1:8765/healthz

The health endpoint is intentionally public and returns only service/version information. Every other route, including /mcp, requires Authorization: Bearer <HIF_GATEWAY_API_KEY>.

## 3. REST endpoints

All endpoints except /healthz require the bearer token.

### Health

    GET /healthz

### Sequential HIF run

    POST /v1/run
    Content-Type: application/json
    Authorization: Bearer <secret>

    {
      "goal": "Review this architecture",
      "context": "Only approved project context",
      "session_id": null
    }

### Parallel specialist nodes

    POST /v1/node

Uses the same request shape as /v1/run, but enables HIF specialist-node parallel execution.

### Session status

    GET /v1/sessions/{session_id}

### HIF-measured usage

    GET /v1/usage

Usage reports are HIF-metered provider API usage. They are not authoritative consumer subscription quota percentages.

Example:

    curl -X POST http://127.0.0.1:8765/v1/node ^
      -H "Authorization: Bearer YOUR_SECRET" ^
      -H "Content-Type: application/json" ^
      -d "{\\"goal\\":\\"Analyse the migration plan\\",\\"context\\":\\"Approved summary only\\"}"

On PowerShell, use Invoke-RestMethod if curl quoting is inconvenient:

    $headers = @{ Authorization = "Bearer $env:HIF_GATEWAY_API_KEY" }
    $body = @{ goal = "Analyse the migration plan"; context = "Approved summary only" } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/v1/node -Headers $headers -ContentType "application/json" -Body $body

## 4. Remote MCP endpoint

The Streamable HTTP MCP endpoint is:

    http://127.0.0.1:8765/mcp

Remote clients must send the same bearer token in the HTTP Authorization header. Configure their MCP client using its documented Streamable HTTP transport and secret/header mechanism. Example generic shape (client configuration formats differ):

    {
      "mcpServers": {
        "hif": {
          "type": "http",
          "url": "https://hif.example.com/mcp",
          "headers": {
            "Authorization": "Bearer <secret-from-secret-store>"
          }
        }
      }
    }

Never commit a real token in this file. Some clients do not support custom authorization headers for remote MCP; check the client's current documentation. Do not work around that limitation by putting secrets in query parameters.

Available tools:
- hif_run
- hifnode_run
- hif_session_status
- hif_usage

The REST and MCP interfaces use the same HIF engine instance within the gateway process and therefore share the configured SQLite database and provider concurrency controls.

## 5. TLS and reverse proxy

Never expose the gateway over plain HTTP on a public or untrusted network.

Preferred deployment:
1. Keep HIF bound to 127.0.0.1.
2. Put a maintained reverse proxy (for example Caddy, Nginx or IIS ARR) in front.
3. Terminate TLS with a trusted certificate at the proxy.
4. Restrict inbound firewall access to the proxy/approved network.
5. Configure proxy request-body limits, timeouts and access logs with Authorization headers redacted.
6. Do not forward untrusted client identity headers to HIF. Current rate limiting uses the TCP peer address visible to the app; behind a reverse proxy this is normally the proxy address, so enforce rate limiting at the proxy too.

Direct TLS binding is also supported by setting both:

    HIF_GATEWAY_HOST=0.0.0.0
    HIF_GATEWAY_PORT=8765
    HIF_GATEWAY_TLS_CERTFILE=/secure/path/fullchain.pem
    HIF_GATEWAY_TLS_KEYFILE=/secure/path/privatekey.pem

The private key must be readable only by the service identity. For Windows, use an appropriately ACL-protected certificate/key file or prefer IIS reverse proxy termination.

## 6. Security controls and limitations

- Bearer secret must contain at least 32 characters.
- Authentication uses constant-time comparison.
- /healthz is public; it reveals no session, usage or provider information.
- Other routes require authentication.
- Request bodies are capped by HIF_GATEWAY_MAX_REQUEST_BYTES.
- Rate limiting is a per-process, per-source-IP fixed window; it is not distributed and may be shared across clients behind a proxy.
- One gateway key currently authorizes all exposed tools. There are no separate read/run/admin scopes.
- All clients share the service account's HIF database and provider credentials. Do not use this deployment for mutually untrusted users.
- Use a private network or trusted reverse proxy with TLS. Do not bind to a public interface without TLS.
- Keep provider credentials and the gateway key out of logs and source control.
- Review data residency, provider retention and API billing before sending project context to external models.

## 7. Production hardening still required

Before a public SaaS or multi-customer deployment, implement:
- OAuth 2.1 / OIDC authorization and per-user or per-tenant identity.
- Tenant-scoped databases/memory, provider credentials and encryption keys.
- Fine-grained tool scopes and approval policies.
- Distributed rate limits, concurrency quotas and global spend limits.
- Durable audit trail with secret/context redaction.
- Secret rotation, revocation and key management.
- Reverse-proxy configuration tests, load tests, backup/restore and monitoring.
- Windows Service and Linux systemd deployment units with service hardening.
