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
from collections.abc import Callable
from typing import Any

import uvicorn
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from hif import __version__
from hif.config import Settings
from hif.engine import HIFEngine
from hif.mcp_server import mcp

logger = logging.getLogger("hif.gateway")


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal: str = Field(min_length=1, max_length=8000)
    context: str = Field(default="", max_length=32000)
    session_id: str | None = Field(default=None, max_length=128)


class GatewaySecurityMiddleware(BaseHTTPMiddleware):
    """Enforce bearer auth, request size and a per-client fixed-window limit."""

    def __init__(
        self,
        app: Any,
        *,
        api_key: str,
        requests_per_minute: int,
        max_request_bytes: int,
    ) -> None:
        super().__init__(app)
        self.api_key = api_key
        self.requests_per_minute = requests_per_minute
        self.max_request_bytes = max_request_bytes
        self._lock = threading.Lock()
        self._buckets: dict[str, tuple[int, int]] = {}

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        if request.url.path == "/healthz":
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        scheme, _, supplied = auth.partition(" ")
        if scheme.lower() != "bearer" or not supplied or not hmac.compare_digest(
            supplied, self.api_key
        ):
            return JSONResponse(
                {"error": "unauthorized", "message": "A valid bearer token is required."},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

        length = request.headers.get("content-length")
        if length:
            try:
                if int(length) > self.max_request_bytes:
                    return JSONResponse(
                        {"error": "request_too_large"}, status_code=413
                    )
            except ValueError:
                return JSONResponse({"error": "invalid_content_length"}, status_code=400)

        client_host = request.client.host if request.client else "unknown"
        now = int(time.monotonic() // 60)
        with self._lock:
            window, count = self._buckets.get(client_host, (now, 0))
            if window != now:
                window, count = now, 0
            if count >= self.requests_per_minute:
                return JSONResponse(
                    {"error": "rate_limit_exceeded"},
                    status_code=429,
                    headers={"Retry-After": str(60 - int(time.monotonic() % 60))},
                )
            self._buckets[client_host] = (window, count + 1)
            if len(self._buckets) > 4096:
                self._buckets = {
                    key: value for key, value in self._buckets.items()
                    if value[0] >= now - 1
                }

        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response


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
    if len(api_key) < 32:
        raise RuntimeError(
            "Set HIF_GATEWAY_API_KEY to a random secret of at least 32 characters."
        )

    # FastMCP's streamable HTTP app owns its ASGI lifespan and /mcp endpoint.
    app = mcp.streamable_http_app()
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
