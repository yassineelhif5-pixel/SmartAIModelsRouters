"""Direct HTTP adapters for every provider in the catalog.

No third-party HTTP client is required: requests go through the standard library in a
worker thread, so the async engine is never blocked. Cloud SDK providers (Bedrock,
Vertex AI, watsonx) are delegated to LiteLLM, which handles their signing schemes.

``AutoProvider`` is the default provider of the engine: it reads the ``provider/``
prefix of each model id and picks the matching adapter.
"""

from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from hif.provider_catalog import ProviderSpec, split_model
from hif.providers import LiteLLMProvider, ModelProvider, ModelResponse, ProviderError

RETRYABLE_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}


@dataclass(frozen=True)
class HTTPResult:
    status: int
    headers: dict[str, str]
    body: bytes


class Transport(Protocol):
    def __call__(self, url: str, headers: dict[str, str], payload: dict[str, Any],
                 timeout: int) -> HTTPResult: ...


def urllib_transport(url: str, headers: dict[str, str], payload: dict[str, Any],
                     timeout: int) -> HTTPResult:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return HTTPResult(response.status, {k.lower(): v for k, v in response.headers.items()},
                              response.read())
    except urllib.error.HTTPError as exc:
        return HTTPResult(exc.code, {k.lower(): v for k, v in (exc.headers or {}).items()},
                          exc.read() or b"")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise ProviderError(f"Connection error: {exc}", retryable=True) from exc


def _retry_after(headers: dict[str, str]) -> float | None:
    raw = headers.get("retry-after")
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _raise_for_status(spec: ProviderSpec, result: HTTPResult) -> dict[str, Any]:
    text = result.body.decode("utf-8", errors="replace")
    if result.status >= 400:
        message = text[:500]
        try:
            parsed = json.loads(text)
            error = parsed.get("error", parsed)
            message = error.get("message", message) if isinstance(error, dict) else str(error)
        except (ValueError, AttributeError):
            pass
        raise ProviderError(
            f"{spec.name} HTTP {result.status}: {message}",
            retryable=result.status in RETRYABLE_STATUS,
            retry_after=_retry_after(result.headers),
            status_code=result.status,
        )
    try:
        return json.loads(text)
    except ValueError as exc:
        raise ProviderError(f"{spec.name} returned a non-JSON body", retryable=True) from exc


class _HTTPAdapter:
    def __init__(self, spec: ProviderSpec, transport: Transport | None = None):
        self.spec = spec
        self.transport = transport or urllib_transport

    async def _post(self, url: str, headers: dict[str, str], payload: dict[str, Any],
                    timeout: int) -> tuple[dict[str, Any], int]:
        started = time.perf_counter()
        result = await asyncio.to_thread(self.transport, url, headers, payload, timeout)
        body = _raise_for_status(self.spec, result)
        return body, int((time.perf_counter() - started) * 1000)

    def _key_or_fail(self) -> str:
        key = self.spec.api_key()
        if key is None:
            raise ProviderError(
                f"No API key for {self.spec.name}. Set one of: {', '.join(self.spec.env_keys)}",
                retryable=False,
            )
        return key


class OpenAICompatibleProvider(_HTTPAdapter):
    """Any server that implements POST /chat/completions (most providers and local runtimes)."""

    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse:
        _, name = split_model(model)
        base = self.spec.resolved_base_url().rstrip("/")
        if not base:
            raise ProviderError(f"No base URL for {self.spec.name}; set {self.spec.base_url_env}",
                                retryable=False)
        headers = dict(self.spec.extra_headers)
        if self.spec.kind == "azure_openai":
            headers["api-key"] = self._key_or_fail()
        elif not self.spec.local:
            headers["Authorization"] = f"Bearer {self._key_or_fail()}"
        payload = {
            "model": name,
            "messages": [{"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_prompt}],
            "max_tokens": max_tokens,
        }
        body, elapsed = await self._post(f"{base}/chat/completions", headers, payload, timeout)
        choices = body.get("choices") or [{}]
        content = (choices[0].get("message") or {}).get("content") or ""
        usage = body.get("usage") or {}
        return ModelResponse(
            model=model, content=str(content),
            input_tokens=int(usage.get("prompt_tokens") or 0),
            output_tokens=int(usage.get("completion_tokens") or 0),
            duration_ms=elapsed,
        )


class AnthropicProvider(_HTTPAdapter):
    API_VERSION = "2023-06-01"

    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse:
        _, name = split_model(model)
        headers = {"x-api-key": self._key_or_fail(), "anthropic-version": self.API_VERSION}
        payload = {
            "model": name,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": max_tokens,
        }
        base = self.spec.resolved_base_url().rstrip("/")
        body, elapsed = await self._post(f"{base}/messages", headers, payload, timeout)
        text = "".join(block.get("text", "") for block in body.get("content", [])
                       if block.get("type") == "text")
        usage = body.get("usage") or {}
        return ModelResponse(
            model=model, content=text,
            input_tokens=int(usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("output_tokens") or 0),
            duration_ms=elapsed,
        )


class GeminiProvider(_HTTPAdapter):
    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse:
        _, name = split_model(model)
        headers = {"x-goog-api-key": self._key_or_fail()}
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        base = self.spec.resolved_base_url().rstrip("/")
        body, elapsed = await self._post(f"{base}/models/{name}:generateContent", headers,
                                         payload, timeout)
        candidates = body.get("candidates") or [{}]
        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(part.get("text", "") for part in parts)
        usage = body.get("usageMetadata") or {}
        return ModelResponse(
            model=model, content=text,
            input_tokens=int(usage.get("promptTokenCount") or 0),
            output_tokens=int(usage.get("candidatesTokenCount") or 0),
            duration_ms=elapsed,
        )


AdapterFactory = Callable[[ProviderSpec], ModelProvider]


class AutoProvider:
    """Dispatch each call to the adapter that matches the model's provider prefix."""

    def __init__(self, transport: Transport | None = None,
                 fallback: ModelProvider | None = None):
        self.transport = transport
        self.fallback = fallback or LiteLLMProvider()
        self._adapters: dict[str, ModelProvider] = {}

    def adapter_for(self, model: str) -> ModelProvider:
        spec, _ = split_model(model)
        if spec is None or spec.kind == "litellm":
            return self.fallback
        if spec.id not in self._adapters:
            if spec.kind == "anthropic":
                self._adapters[spec.id] = AnthropicProvider(spec, self.transport)
            elif spec.kind == "gemini":
                self._adapters[spec.id] = GeminiProvider(spec, self.transport)
            else:
                self._adapters[spec.id] = OpenAICompatibleProvider(spec, self.transport)
        return self._adapters[spec.id]

    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse:
        return await self.adapter_for(model).complete(
            model=model, system_prompt=system_prompt, user_prompt=user_prompt,
            max_tokens=max_tokens, timeout=timeout,
        )
