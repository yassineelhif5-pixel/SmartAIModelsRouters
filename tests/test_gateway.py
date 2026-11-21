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
