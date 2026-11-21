from __future__ import annotations

import time
from types import SimpleNamespace

import jwt
import pytest

from hif.oauth import OIDCJWTVerifier


@pytest.fixture
def verifier() -> tuple[OIDCJWTVerifier, str]:
    secret = "test-only-signing-secret-that-is-long-enough"
    instance = OIDCJWTVerifier(
        issuer_url="https://login.example.com/tenant/v2.0",
        jwks_url="https://login.example.com/tenant/keys",
        audience="hif-api-client-id",
        resource_url="https://hif.example.com/mcp",
        required_scopes=("hif.access",),
        algorithms=("HS256",),
    )
    instance._jwks.get_signing_key_from_jwt = lambda token: SimpleNamespace(key=secret)
    return instance, secret


def make_token(secret: str, **overrides) -> str:
    claims = {
        "iss": "https://login.example.com/tenant/v2.0",
        "aud": "hif-api-client-id",
        "exp": int(time.time()) + 300,
        "iat": int(time.time()),
        "scp": "hif.access profile",
        "sub": "user-123",
        "azp": "client-123",
    }
    claims.update(overrides)
    return jwt.encode(claims, secret, algorithm="HS256")


@pytest.mark.asyncio
async def test_oidc_verifier_accepts_valid_token_and_maps_identity(verifier) -> None:
    instance, secret = verifier
    access = await instance.verify_token(make_token(secret))

    assert access is not None
    assert access.client_id == "client-123"
    assert access.subject == "user-123"
    assert access.scopes == ["hif.access", "profile"]
    assert access.resource == "https://hif.example.com/mcp"


@pytest.mark.asyncio
async def test_oidc_verifier_rejects_wrong_audience_and_missing_scope(verifier) -> None:
    instance, secret = verifier
    assert await instance.verify_token(make_token(secret, aud="another-api")) is None
    assert await instance.verify_token(make_token(secret, scp="profile")) is None


@pytest.mark.asyncio
async def test_oidc_verifier_rejects_bad_signature(verifier) -> None:
    instance, _secret = verifier
    assert await instance.verify_token(make_token("wrong-signing-secret")) is None
