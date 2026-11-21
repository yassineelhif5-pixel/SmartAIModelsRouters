from __future__ import annotations

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from hif.gateway import GatewaySecurityMiddleware


async def protected(request: Request):
    return JSONResponse({"ok": True})


def make_client(*, limit: int = 10, max_bytes: int = 128) -> TestClient:
    app = Starlette(
        routes=[
            Route("/healthz", protected, methods=["GET"]),
            Route("/v1/run", protected, methods=["POST"]),
        ]
    )
    app.add_middleware(
        GatewaySecurityMiddleware,
        api_key="x" * 48,
        requests_per_minute=limit,
        max_request_bytes=max_bytes,
    )
    return TestClient(app)


def test_gateway_rejects_missing_or_invalid_bearer_token() -> None:
    client = make_client()
    assert client.post("/v1/run", json={"goal": "test"}).status_code == 401
    assert client.post(
        "/v1/run", headers={"Authorization": "Bearer wrong"}, json={"goal": "test"}
    ).status_code == 401


def test_gateway_accepts_valid_bearer_token_and_disables_caching() -> None:
    client = make_client()
    response = client.post(
        "/v1/run", headers={"Authorization": "Bearer " + "x" * 48}, json={"goal": "test"}
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_gateway_health_is_public_but_rate_limit_is_enforced() -> None:
    client = make_client(limit=1)
    assert client.get("/healthz").status_code == 200
    headers = {"Authorization": "Bearer " + "x" * 48}
    assert client.post("/v1/run", headers=headers, json={"goal": "one"}).status_code == 200
    response = client.post("/v1/run", headers=headers, json={"goal": "two"})
    assert response.status_code == 429
    assert response.headers["retry-after"]


def test_gateway_rejects_oversized_content_length() -> None:
    client = make_client(max_bytes=32)
    response = client.post(
        "/v1/run",
        headers={"Authorization": "Bearer " + "x" * 48},
        content=b'{"goal":"' + b"a" * 100 + b'"}',
    )
    assert response.status_code == 413


def test_gateway_application_mounts_health_rest_and_mcp_routes(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HIF_GATEWAY_API_KEY", "z" * 48)
    monkeypatch.setenv("HIF_DATABASE_PATH", str(tmp_path / "gateway.sqlite3"))
    monkeypatch.setenv("HIF_GATEWAY_HOST", "127.0.0.1")

    from hif.gateway import create_app

    app = create_app()
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/v1/usage").status_code == 401
        usage = client.get(
            "/v1/usage", headers={"Authorization": "Bearer " + "z" * 48}
        )
        assert usage.status_code == 200
        assert usage.json()["source"] == "hif_measured_tokens"
        assert any(getattr(route, "path", None) == "/mcp" for route in app.routes)


def test_remote_gateway_requires_explicit_mcp_host_allowlist(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HIF_GATEWAY_API_KEY", "r" * 48)
    monkeypatch.setenv("HIF_DATABASE_PATH", str(tmp_path / "remote.sqlite3"))
    monkeypatch.setenv("HIF_GATEWAY_HOST", "0.0.0.0")
    monkeypatch.delenv("HIF_GATEWAY_ALLOWED_HOSTS", raising=False)

    from hif.gateway import create_app

    import pytest

    with pytest.raises(RuntimeError, match="HIF_GATEWAY_ALLOWED_HOSTS"):
        create_app()

    monkeypatch.setenv(
        "HIF_GATEWAY_ALLOWED_HOSTS", "hif.example.com,hif.example.com:*"
    )
    app = create_app()
    assert any(getattr(route, "path", None) == "/mcp" for route in app.routes)


def test_gateway_publishes_oauth_resource_metadata_when_oidc_is_configured(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("HIF_GATEWAY_API_KEY", "o" * 48)
    monkeypatch.setenv("HIF_DATABASE_PATH", str(tmp_path / "oauth-gateway.sqlite3"))
    monkeypatch.setenv("HIF_GATEWAY_HOST", "127.0.0.1")
    monkeypatch.setenv(
        "HIF_GATEWAY_OAUTH_ISSUER_URL", "https://login.example.com/tenant/v2.0"
    )
    monkeypatch.setenv(
        "HIF_GATEWAY_OAUTH_RESOURCE_URL", "https://hif.example.com/mcp"
    )
    monkeypatch.setenv("HIF_GATEWAY_OAUTH_AUDIENCE", "hif-api-client-id")
    monkeypatch.setenv(
        "HIF_GATEWAY_OAUTH_JWKS_URL", "https://login.example.com/tenant/keys"
    )
    monkeypatch.setenv("HIF_GATEWAY_OAUTH_REQUIRED_SCOPES", "hif.access")

    from hif.gateway import create_app

    app = create_app()
    paths = [getattr(route, "path", "") for route in app.routes]
    assert any(path.startswith("/.well-known/oauth-protected-resource") for path in paths)
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        metadata = client.get("/.well-known/oauth-protected-resource/mcp")
        assert metadata.status_code == 200
        assert metadata.json()["authorization_servers"] == [
            "https://login.example.com/tenant/v2.0"
        ]
        protected = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert protected.status_code == 401
        assert "resource_metadata" in protected.headers.get("www-authenticate", "")
        assert client.get("/v1/usage").status_code == 401
        operator_usage = client.get(
            "/v1/usage", headers={"Authorization": "Bearer " + "o" * 48}
        )
        assert operator_usage.status_code == 200


def test_oauth_mcp_path_bypasses_operator_key_but_keeps_rate_limit() -> None:
    app = Starlette(routes=[Route("/mcp", protected, methods=["GET"])])
    app.add_middleware(
        GatewaySecurityMiddleware,
        api_key="x" * 48,
        requests_per_minute=1,
        max_request_bytes=1024,
        oauth_enabled=True,
    )
    client = TestClient(app)

    assert client.get("/mcp").status_code == 200
    assert client.get("/mcp").status_code == 429


def test_mcp_path_requires_operator_key_when_oidc_is_disabled() -> None:
    app = Starlette(routes=[Route("/mcp", protected, methods=["GET"])])
    app.add_middleware(
        GatewaySecurityMiddleware,
        api_key="x" * 48,
        requests_per_minute=10,
        max_request_bytes=1024,
        oauth_enabled=False,
    )
    assert TestClient(app).get("/mcp").status_code == 401


def test_partial_oidc_configuration_is_rejected(monkeypatch) -> None:
    from hif.config import Settings

    monkeypatch.setenv(
        "HIF_GATEWAY_OAUTH_ISSUER_URL", "https://login.example.com/tenant/v2.0"
    )
    monkeypatch.delenv("HIF_GATEWAY_OAUTH_RESOURCE_URL", raising=False)
    monkeypatch.delenv("HIF_GATEWAY_OAUTH_AUDIENCE", raising=False)
    monkeypatch.delenv("HIF_GATEWAY_OAUTH_JWKS_URL", raising=False)
    monkeypatch.delenv("HIF_GATEWAY_OAUTH_REQUIRED_SCOPES", raising=False)

    import pytest

    with pytest.raises(ValueError, match="OAuth gateway requires"):
        Settings.from_env()
