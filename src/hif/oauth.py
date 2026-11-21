"""OIDC/JWT access-token verifier for remote HIF MCP clients."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import jwt
from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger("hif.gateway.oauth")


class OIDCJWTVerifier(TokenVerifier):
    """Validate access JWTs from an external OIDC authorization server.

    The identity provider owns login, authorization-code + PKCE and token issuance.
    HIF validates signature, issuer, audience, expiry and required scopes only.
    """

    def __init__(
        self,
        *,
        issuer_url: str,
        jwks_url: str,
        audience: str,
        resource_url: str,
        required_scopes: tuple[str, ...],
        algorithms: tuple[str, ...] = ("RS256",),
    ) -> None:
        if not algorithms or any(alg.lower() == "none" for alg in algorithms):
            raise ValueError("OIDC JWT algorithms must be explicit and cannot include none.")
        self.issuer_url = issuer_url
        self.jwks_url = jwks_url
        self.audience = audience
        self.resource_url = resource_url
        self.required_scopes = set(required_scopes)
        self.algorithms = list(algorithms)
        self._jwks = jwt.PyJWKClient(
            jwks_url,
            cache_jwk_set=True,
            lifespan=300,
            timeout=5,
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        return await asyncio.to_thread(self._verify_sync, token)

    def _verify_sync(self, token: str) -> AccessToken | None:
        try:
            signing_key = self._jwks.get_signing_key_from_jwt(token)
            claims: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer_url,
                options={"require": ["exp", "iss", "aud"]},
                leeway=30,
            )
            raw_scopes = claims.get("scp", claims.get("scope", ""))
            if isinstance(raw_scopes, str):
                scopes = raw_scopes.split()
            elif isinstance(raw_scopes, list):
                scopes = [str(scope) for scope in raw_scopes]
            else:
                scopes = []

            if not self.required_scopes.issubset(set(scopes)):
                return None

            client_id = (
                claims.get("azp")
                or claims.get("appid")
                or claims.get("client_id")
                or "unknown-client"
            )
            return AccessToken(
                token=token,
                client_id=str(client_id),
                scopes=scopes,
                expires_at=int(claims["exp"]),
                resource=self.resource_url,
                subject=str(claims["sub"]) if claims.get("sub") else None,
                claims=claims,
            )
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
            logger.info("Rejected OAuth access token (%s).", type(exc).__name__)
            return None
        except Exception as exc:
            # JWKS fetch failures and malformed provider responses fail closed.
            logger.warning("OAuth token verification unavailable (%s).", type(exc).__name__)
            return None
