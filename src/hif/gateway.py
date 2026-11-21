"""Authenticated HIF HTTP + Streamable HTTP MCP gateway.

This first gateway release is single-tenant. It is intended for a trusted private
deployment, with bearer-token authentication and TLS when bound beyond loopback.
"""

from __future__ import annotations

import hmac
import logging
import os
import threading
import time
from typing import Any

import uvicorn
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, ValidationError
from mcp.server.auth.settings import AuthSettings
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from hif import __version__
from hif.config import Settings
from hif.engine import HIFEngine
from hif.mcp_server import create_mcp_server
from hif.oauth import OIDCJWTVerifier

logger = logging.getLogger("hif.gateway")


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal: str = Field(min_length=1, max_length=8000)
    context: str = Field(default="", max_length=32000)
    session_id: str | None = Field(default=None, max_length=128)


class GatewaySecurityMiddleware:
    """Pure ASGI auth and limits middleware; preserves MCP streaming responses."""

    def __init__(
        self,
        app: Any,
        *,
        api_key: str,
        requests_per_minute: int,
        max_request_bytes: int,
        oauth_enabled: bool = False,
    ) -> None:
        self.app = app
        self.api_key = api_key
        self.requests_per_minute = requests_per_minute
        self.max_request_bytes = max_request_bytes
        self.oauth_enabled = oauth_enabled
        self._lock = threading.Lock()
        self._buckets: dict[str, tuple[int, int]] = {}

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def secure_send(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing = {key.lower() for key, _ in headers}
                if b"cache-control" not in existing:
                    headers.append((b"cache-control", b"no-store"))
                if b"x-content-type-options" not in existing:
                    headers.append((b"x-content-type-options", b"nosniff"))
                message = {**message, "headers": headers}
            await send(message)

        async def reject(
            status: int,
            body: dict[str, Any],
            headers: dict[str, str] | None = None,
        ) -> None:
            await JSONResponse(body, status_code=status, headers=headers)(
                scope, receive, secure_send
            )

        path = scope.get("path", "")
        if path == "/healthz":
            await self.app(scope, receive, secure_send)
            return

        oauth_mcp_path = (
            self.oauth_enabled
            and (
                path == "/mcp"
                or path.startswith("/.well-known/oauth-protected-resource")
            )
        )
        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }

        # OIDC MCP requests are verified by the MCP SDK; REST and private API-key
        # mode continue to use the HIF operator bearer key.
        if not oauth_mcp_path:
            auth = headers.get("authorization", "")
            scheme, _, supplied = auth.partition(" ")
            if scheme.lower() != "bearer" or not supplied or not hmac.compare_digest(
                supplied.encode("utf-8"), self.api_key.encode("utf-8")
            ):
                await reject(
                    401,
                    {"error": "unauthorized", "message": "A valid bearer token is required."},
                    {"WWW-Authenticate": "Bearer"},
                )
                return

        length = headers.get("content-length")
        if length:
            try:
                if int(length) > self.max_request_bytes:
                    await reject(413, {"error": "request_too_large"})
                    return
            except ValueError:
                await reject(400, {"error": "invalid_content_length"})
                return

        client = scope.get("client")
        client_host = str(client[0]) if client else "unknown"
        now = int(time.monotonic() // 60)
        limited = False
        retry_after = "60"
        with self._lock:
            window, count = self._buckets.get(client_host, (now, 0))
            if window != now:
                window, count = now, 0
            if count >= self.requests_per_minute:
                limited = True
                retry_after = str(60 - int(time.monotonic() % 60))
            else:
                self._buckets[client_host] = (window, count + 1)
            if len(self._buckets) > 4096:
                self._buckets = {
                    key: value for key, value in self._buckets.items()
                    if value[0] >= now - 1
                }
        if limited:
            await reject(
                429,
                {"error": "rate_limit_exceeded"},
                {"Retry-After": retry_after},
            )
            return

        received_bytes = 0
        rejected = False

        async def limited_receive() -> dict[str, Any]:
            nonlocal received_bytes, rejected
            if rejected:
                return {"type": "http.disconnect"}
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_request_bytes:
                    rejected = True
                    await reject(413, {"error": "request_too_large"})
                    return {"type": "http.request", "body": b"", "more_body": False}
            return message

        async def guarded_send(message: dict[str, Any]) -> None:
            if not rejected:
                await secure_send(message)

        await self.app(scope, limited_receive, guarded_send)


def _engine() -> HIFEngine:
    # Reuse the same process-wide engine as the local MCP tools.
    from hif.mcp_server import _engine as get_mcp_engine

    return get_mcp_engine()


async def _read_run_request(request: Request) -> RunRequest:
    raw = await request.body()
    settings = Settings.from_env()
    if len(raw) > settings.gateway_max_request_bytes:
        raise ValueError("Request body exceeds the configured size limit.")
    try:
        return RunRequest.model_validate_json(raw)
    except ValidationError:
        raise


async def _run(request: Request) -> Response:
    try:
        payload = await _read_run_request(request)
    except ValidationError as exc:
        return JSONResponse(
            {"error": "invalid_request", "details": exc.errors(include_input=False)},
            status_code=422,
        )
    except ValueError as exc:
        return JSONResponse({"error": "invalid_request", "message": str(exc)}, status_code=413)

    try:
        result = await _engine().run(
            goal=payload.goal,
            context=payload.context,
            session_id=payload.session_id,
            parallel=False,
        )
        return JSONResponse(result.model_dump(mode="json"))
    except Exception as exc:
        logger.error("HIF gateway run failed (%s).", type(exc).__name__)
        return JSONResponse(
            {"error": "execution_failed", "message": "HIF could not complete this run."},
            status_code=502,
        )


async def _node(request: Request) -> Response:
    try:
        payload = await _read_run_request(request)
    except ValidationError as exc:
        return JSONResponse(
            {"error": "invalid_request", "details": exc.errors(include_input=False)},
            status_code=422,
        )
    except ValueError as exc:
        return JSONResponse({"error": "invalid_request", "message": str(exc)}, status_code=413)

    try:
        result = await _engine().run(
            goal=payload.goal,
            context=payload.context,
            session_id=payload.session_id,
            parallel=True,
        )
        return JSONResponse(result.model_dump(mode="json"))
    except Exception as exc:
        logger.error("HIF gateway node run failed (%s).", type(exc).__name__)
        return JSONResponse(
            {"error": "execution_failed", "message": "HIF could not complete this run."},
            status_code=502,
        )


async def _status(request: Request) -> Response:
    session_id = request.path_params["session_id"]
    if len(session_id) > 128:
        return JSONResponse({"error": "invalid_session_id"}, status_code=400)
    result = _engine().status(session_id)
    if not result["nodes"]:
        return JSONResponse({"error": "session_not_found"}, status_code=404)
    return JSONResponse(result)


async def _usage(request: Request) -> Response:
    engine = _engine()
    return JSONResponse(
        {
            "source": "hif_measured_tokens",
            "window_hours": engine.settings.usage_window_hours,
            "models": engine.usage(),
            "provider_subscription_quota": "not_measured",
        }
    )


async def _health(request: Request) -> Response:
    return JSONResponse({"status": "ok", "service": "hif-gateway", "version": __version__})


def create_app():
    """Build the authenticated Streamable HTTP MCP + REST ASGI application."""
    settings = Settings.from_env()
    api_key = settings.gateway_api_key or ""
    if len(api_key) < 32 or not api_key.isascii():
        raise RuntimeError(
            "Set HIF_GATEWAY_API_KEY to an ASCII random secret of at least 32 characters."
        )
    if bool(settings.gateway_tls_certfile) != bool(settings.gateway_tls_keyfile):
        raise RuntimeError("Configure both gateway TLS certificate and key, or neither.")
    if settings.gateway_tls_certfile and not settings.gateway_tls_certfile.is_file():
        raise RuntimeError("HIF gateway TLS certificate file does not exist.")
    if settings.gateway_tls_keyfile and not settings.gateway_tls_keyfile.is_file():
        raise RuntimeError("HIF gateway TLS key file does not exist.")

    local_hosts = {"127.0.0.1", "localhost", "::1"}
    transport_security = None
    if settings.gateway_allowed_hosts or settings.gateway_allowed_origins:
        if not settings.gateway_allowed_hosts:
            raise RuntimeError("HIF_GATEWAY_ALLOWED_HOSTS is required when origins are configured.")
        transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=list(settings.gateway_allowed_hosts),
            allowed_origins=list(settings.gateway_allowed_origins),
        )
    elif settings.gateway_host not in local_hosts:
        raise RuntimeError(
            "For a non-loopback MCP gateway, configure HIF_GATEWAY_ALLOWED_HOSTS "
            "with the exact public hostname (and wildcard-port form if required)."
        )

    oauth_enabled = bool(settings.gateway_oauth_issuer_url)
    auth_settings = None
    token_verifier = None
    if oauth_enabled:
        verifier = OIDCJWTVerifier(
            issuer_url=settings.gateway_oauth_issuer_url or "",
            jwks_url=settings.gateway_oauth_jwks_url or "",
            audience=settings.gateway_oauth_audience or "",
            resource_url=settings.gateway_oauth_resource_url or "",
            required_scopes=settings.gateway_oauth_required_scopes,
            algorithms=settings.gateway_oauth_algorithms,
        )
        token_verifier = verifier
        auth_settings = AuthSettings(
            issuer_url=AnyHttpUrl(settings.gateway_oauth_issuer_url),
            resource_server_url=AnyHttpUrl(settings.gateway_oauth_resource_url),
            required_scopes=list(settings.gateway_oauth_required_scopes),
            # The verifier checks the provider-specific audience claim directly.
            validate_token_resource=False,
        )

    # FastMCP owns the MCP lifespan and publishes RFC 9728 metadata when OAuth is enabled.
    gateway_mcp = create_mcp_server(auth=auth_settings, token_verifier=token_verifier)
    app = gateway_mcp.streamable_http_app(
        host=settings.gateway_host,
        max_request_body_size=settings.gateway_max_request_bytes,
        transport_security=transport_security,
    )
    app.routes.extend(
        [
            Route("/healthz", _health, methods=["GET"]),
            Route("/v1/run", _run, methods=["POST"]),
            Route("/v1/node", _node, methods=["POST"]),
            Route("/v1/sessions/{session_id:str}", _status, methods=["GET"]),
            Route("/v1/usage", _usage, methods=["GET"]),
        ]
    )
    app.add_middleware(
        GatewaySecurityMiddleware,
        api_key=api_key,
        requests_per_minute=settings.gateway_rate_limit_per_minute,
        max_request_bytes=settings.gateway_max_request_bytes,
        oauth_enabled=oauth_enabled,
    )
    return app


def main() -> None:
    """Start the HIF gateway; non-loopback binds require explicit TLS files."""
    settings = Settings.from_env()
    host = settings.gateway_host
    local_hosts = {"127.0.0.1", "localhost", "::1"}
    ssl_certfile = str(settings.gateway_tls_certfile) if settings.gateway_tls_certfile else None
    ssl_keyfile = str(settings.gateway_tls_keyfile) if settings.gateway_tls_keyfile else None
    if host not in local_hosts and not (ssl_certfile and ssl_keyfile):
        raise SystemExit(
            "Refusing a non-loopback bind without HIF_GATEWAY_TLS_CERTFILE and "
            "HIF_GATEWAY_TLS_KEYFILE. Use a trusted TLS reverse proxy or provide a certificate."
        )

    uvicorn.run(
        create_app(),
        host=host,
        port=settings.gateway_port,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        log_level=os.getenv("HIF_LOG_LEVEL", "info").lower(),
        access_log=False,
    )


if __name__ == "__main__":
    main()
