# HIF Gateway — authenticated REST + Streamable HTTP MCP

The HIF Gateway is the remote transport layer for a central HIF runtime. It exposes the same process-wide engine through a small REST API and the MCP Streamable HTTP transport.

## Status and intended use

- Implemented: REST endpoints, Streamable HTTP MCP endpoint, static bearer authentication for private REST/API-key mode, optional external OIDC/JWT verification for MCP, RFC 9728 protected-resource discovery, request-size checks, per-source-IP fixed-window rate limiting, no-store/security headers, health endpoint, Host/Origin allowlists and non-loopback TLS guard.
- Current security model: **single tenant**. REST operator endpoints use one shared bearer secret; MCP can use an external OIDC provider and required-scope validation. This is a private pilot gateway, not a multi-tenant SaaS control plane.
- Not yet implemented: HIF-hosted authorization server, per-user tenant isolation, fine-grained per-tool scopes, admin UI, distributed rate limiting, audit export, HA deployment or production operations.
- The gateway does not grant file-system or shell access. It dispatches the same text-only HIF tasks as the local MVP.

## 1. Install and configure

Install HIF runtime as described in QUICKSTART.md, then configure .env:

    HIF_MODEL_POOL=provider/model-id,other-provider/model-id
    HIF_GATEWAY_API_KEY=REPLACE_WITH_A_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
    HIF_GATEWAY_HOST=127.0.0.1
    HIF_GATEWAY_PORT=8765
    HIF_GATEWAY_RATE_LIMIT_PER_MINUTE=60
    HIF_GATEWAY_MAX_REQUEST_BYTES=65536
    HIF_GATEWAY_ALLOWED_HOSTS=hif.example.com,hif.example.com:*
    HIF_GATEWAY_ALLOWED_ORIGINS=

Generate a strong secret (do not commit it):

Windows PowerShell:

    python -c "import secrets; print(secrets.token_urlsafe(48))"

Linux/macOS:

    python -c 'import secrets; print(secrets.token_urlsafe(48))'

Store the key in a secret manager or a protected environment file readable only by the HIF service account. Do not put it in a skill, source file, browser-visible prompt, public URL or Git repository.

## 2. Start locally

    hif gateway

The default listener is 127.0.0.1:8765. For local-only access, leave HIF_GATEWAY_ALLOWED_HOSTS empty; the MCP SDK keeps its localhost DNS-rebinding protection enabled. For a remote hostname, explicitly configure HIF_GATEWAY_ALLOWED_HOSTS with both the bare hostname and wildcard-port form (for example hif.example.com,hif.example.com:*). Set HIF_GATEWAY_ALLOWED_ORIGINS only for browser clients that send an Origin header. The MCP SDK validates Host/Origin separately from the gateway bearer token. Health check:

    curl http://127.0.0.1:8765/healthz

The health endpoint is intentionally public and returns only service/version information. REST operator routes require Authorization: Bearer <HIF_GATEWAY_API_KEY>. The /mcp and OAuth protected-resource metadata routes use the configured external OIDC flow when HIF_GATEWAY_OAUTH_* is enabled; otherwise /mcp uses the static HIF bearer key.

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

When OIDC is configured, remote MCP clients must obtain an OAuth access token from the configured identity provider and send it in the Authorization header. When OIDC is not configured, compatible private clients can use the shared HIF bearer key. ChatGPT custom MCP requires OAuth 2.1 authorization-code + PKCE for authenticated connections; the static HIF key is not a substitute. Example generic shape for a non-OIDC private client (client configuration formats differ):

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

Never commit a real token in this file. Some clients do not support static custom authorization headers for remote MCP; use their OAuth flow where available. Do not work around that limitation by putting secrets in query parameters.

Available tools:
- hif_run
- hifnode_run
- hif_session_status
- hif_usage

The REST and MCP interfaces use the same HIF engine instance within the gateway process and therefore share the configured SQLite database and provider concurrency controls.


## 5. OAuth 2.1 / OIDC for ChatGPT and enterprise clients

The gateway can act as an OAuth **resource server** for MCP. It does not implement the identity provider or issue user tokens. Your identity provider (for example Microsoft Entra ID, Auth0 or Keycloak) performs user sign-in, consent and the authorization-code + PKCE flow. HIF validates the resulting signed JWT on each MCP request.

When OAuth is configured:
- The MCP endpoint /mcp is authenticated by the OIDC JWT verifier.
- The MCP SDK publishes RFC 9728 Protected Resource Metadata at the well-known endpoint and supplies the OAuth challenge on unauthenticated MCP requests.
- The verifier checks JWT signature using the configured JWKS, issuer, audience, expiration and required scopes.
- The REST operator endpoints /v1/* continue to require HIF_GATEWAY_API_KEY.
- The health endpoint remains public and minimal.

This distinction matters for ChatGPT: custom ChatGPT MCP connections use OAuth 2.1 authorization-code + PKCE for authenticated servers. Do not configure the shared HIF API key as a substitute for ChatGPT user authentication. OpenAI's connector documentation also states that ChatGPT does not support customer-provided API keys or machine-to-machine client-credentials grants for this flow. See the official [OpenAI MCP authentication guide](https://developers.openai.com/plugins/build/auth).

### Configure a Microsoft Entra ID resource application

Create an Entra app registration for HIF's API/resource server:

1. Register an application named HIF MCP Resource.
2. Under Expose an API, set the Application ID URI (for example api://<resource-app-client-id>).
3. Add a delegated scope named hif.access and grant the required user/admin consent.
4. Configure the app to issue v2 access tokens.
5. Note the tenant ID and resource app client ID.

Set these HIF values in .env (replace placeholders with the actual Entra values):

    HIF_GATEWAY_OAUTH_ISSUER_URL=https://login.microsoftonline.com/<tenant-id>/v2.0
    HIF_GATEWAY_OAUTH_RESOURCE_URL=https://hif.example.com/mcp
    HIF_GATEWAY_OAUTH_AUDIENCE=<resource-app-client-id>
    HIF_GATEWAY_OAUTH_JWKS_URL=https://login.microsoftonline.com/<tenant-id>/discovery/v2.0/keys
    HIF_GATEWAY_OAUTH_REQUIRED_SCOPES=hif.access
    HIF_GATEWAY_OAUTH_ALGORITHMS=RS256
    HIF_GATEWAY_OAUTH_ALLOWED_CLIENT_IDS=<chatgpt-client-app-id>


**Entra compatibility note:** Microsoft Entra v2 is scope-centric and its token endpoint may accept but ignore the RFC 8707 resource parameter; the requested API scope determines the access-token audience. HIF therefore validates the configured Entra API audience (the resource app ID) rather than assuming the aud claim equals the MCP URL. If your ChatGPT connection or identity-provider policy requires the exact MCP resource URL to be echoed into aud, choose an authorization server with full RFC 8707 resource-indicator support instead. See the [Microsoft identity platform notes on Entra resource indicators](https://microsoft.github.io/identity-spiffe/platform-learnings/agent-id-blueprints-and-users/) and [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html).

The audience must exactly match the aud claim in the access token issued for the HIF resource application. The scope value must match the scp claim. Set HIF_GATEWAY_OAUTH_ALLOWED_CLIENT_IDS to the client application IDs you trust (for example, the ChatGPT OAuth client registration); leaving it empty allows any client in the tenant that can obtain the required delegated scope. HIF also requires a user sub claim. If your identity provider emits a different audience or claim layout, configure those values accordingly; do not weaken signature, issuer, audience or expiry validation.

### Register ChatGPT as an OAuth client

1. Create a separate Entra app registration for the ChatGPT MCP client.
2. Configure it as a web/public client according to the OAuth client credentials supported by your ChatGPT connector setup. Use authorization code + PKCE (S256), not client credentials.
3. Add the exact redirect URI displayed by ChatGPT's custom MCP connection setup to the Entra app registration.
4. Add delegated permission to the HIF resource app's hif.access scope and grant consent as required by your tenant.
5. In ChatGPT, open Plugins, choose Add custom MCP server, set the HTTPS server URL to https://hif.example.com/mcp, choose OAuth and configure a predefined OAuth client with the Entra authorization endpoint, token endpoint, client ID, client secret and the hif.access scope. Use the token endpoint authentication method advertised by Entra and accepted by the ChatGPT connection setup (commonly client_secret_post for a confidential client).
6. Complete the user sign-in/consent flow and test the HIF tools.

Typical Entra endpoints:

    Authorization: https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/authorize
    Token:         https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token

Use the exact callback URI, token authentication method and client type shown by the ChatGPT connector UI. Entra tenant policies and ChatGPT workspace permissions may restrict this configuration.

### Connect other remote MCP clients

For any remote client that supports OAuth 2.1 authorization-code + PKCE, configure its issuer, authorization endpoint, token endpoint, client ID, redirect URI and requested scope according to that client's documentation. Gemini web and Microsoft 365 Copilot support varies by product surface, tenant and rollout; verify their current OAuth/MCP requirements rather than assuming that importing an Agent Skill connects it to HIF.

### Security boundary

OIDC is enabled only when issuer, resource URL, audience, JWKS URL and at least one required scope are configured. If not enabled, /mcp uses the shared HIF bearer key like the REST endpoints. With OIDC enabled, the static HIF key does not bypass OAuth on /mcp; it remains for REST operator endpoints only. Keep both credentials in a secret store and rotate them according to your policy.

## 6. TLS and reverse proxy

Never expose the gateway over plain HTTP on a public or untrusted network.

Preferred deployment:
1. Keep HIF bound to 127.0.0.1.
2. Put a maintained reverse proxy (for example Caddy, Nginx or IIS ARR) in front.
3. Terminate TLS with a trusted certificate at the proxy.
4. Restrict inbound firewall access to the proxy/approved network.
5. Configure proxy request-body limits, timeouts and access logs with Authorization headers redacted.
6. Do not forward untrusted client identity headers to HIF. Current rate limiting uses the TCP peer address visible to the app; behind a reverse proxy this is normally the proxy address, so enforce rate limiting at the proxy too.

Direct TLS binding is also supported by setting both (and configuring the exact public Host allowlist):

    HIF_GATEWAY_HOST=0.0.0.0
    HIF_GATEWAY_PORT=8765
    HIF_GATEWAY_TLS_CERTFILE=/secure/path/fullchain.pem
    HIF_GATEWAY_TLS_KEYFILE=/secure/path/privatekey.pem

The private key must be readable only by the service identity. For Windows, use an appropriately ACL-protected certificate/key file or prefer IIS reverse proxy termination.

## 7. Security controls and limitations

- Bearer secret must contain at least 32 characters.
- Authentication uses constant-time comparison.
- /healthz is public; it reveals no session, usage or provider information.
- REST operator routes require the static operator key. MCP requires the static key in private mode or an OIDC access token when OAuth is configured; the protected-resource metadata route is public for OAuth discovery.
- REST and MCP request bodies are capped by HIF_GATEWAY_MAX_REQUEST_BYTES.
- MCP DNS-rebinding protection is enabled: remote Host values must be explicitly allowlisted with HIF_GATEWAY_ALLOWED_HOSTS; browser Origin values must be explicitly allowlisted with HIF_GATEWAY_ALLOWED_ORIGINS when present.
- Rate limiting is a per-process, per-source-IP fixed window; it is not distributed and may be shared across clients behind a proxy.
- In API-key mode, one gateway key authorizes all exposed tools. In OIDC mode, the MCP endpoint enforces the configured scope set; REST endpoints still use the operator key. Fine-grained read/run/admin scopes are not yet implemented.
- All clients share the service account's HIF database and provider credentials. Do not use this deployment for mutually untrusted users.
- Use a private network or trusted reverse proxy with TLS. Do not bind to a public interface without TLS.
- Keep provider credentials and the gateway key out of logs and source control.
- Review data residency, provider retention and API billing before sending project context to external models.

## 8. Production hardening still required

Before a public SaaS or multi-customer deployment, implement:
- Per-user or per-tenant identity isolation, fine-grained scopes and separate policy enforcement for each tool.
- Tenant-scoped databases/memory, provider credentials and encryption keys.
- Fine-grained tool scopes and approval policies beyond the configured gateway-wide OAuth scope.
- Distributed rate limits, concurrency quotas and global spend limits.
- Durable audit trail with secret/context redaction.
- Secret rotation, revocation and key management.
- Reverse-proxy configuration tests, load tests, backup/restore and monitoring.
- Windows Service and Linux systemd deployment units with service hardening.
