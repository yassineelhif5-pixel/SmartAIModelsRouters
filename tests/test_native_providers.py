"""Provider catalog and native adapters, tested with a fake transport (no network)."""

from __future__ import annotations

import asyncio
import json

import pytest

from hif.native_providers import (
    AnthropicProvider,
    AutoProvider,
    GeminiProvider,
    HTTPResult,
    OpenAICompatibleProvider,
)
from hif.provider_catalog import PROVIDERS, configured_providers, get_provider, split_model
from hif.providers import ProviderError


class FakeTransport:
    def __init__(self, status: int = 200, body: dict | None = None,
                 headers: dict[str, str] | None = None):
        self.status, self.body, self.headers = status, body or {}, headers or {}
        self.calls: list[tuple[str, dict, dict]] = []

    def __call__(self, url, headers, payload, timeout):
        self.calls.append((url, headers, payload))
        return HTTPResult(self.status, self.headers, json.dumps(self.body).encode())


def run(coro):
    return asyncio.run(coro)


def call(provider, model):
    return run(provider.complete(model=model, system_prompt="sys", user_prompt="hi",
                                 max_tokens=64, timeout=5))


def test_catalog_ids_are_unique_and_complete():
    ids = [spec.id for spec in PROVIDERS]
    assert len(ids) == len(set(ids))
    for expected in ("openai", "anthropic", "gemini", "mistral", "deepseek", "groq",
                     "openrouter", "azure", "bedrock", "ollama", "vllm"):
        assert expected in ids
    assert len(ids) >= 30


def test_aliases_and_split():
    assert get_provider("google").id == "gemini"
    spec, name = split_model("kimi/kimi-k2")
    assert spec.id == "moonshot" and name == "kimi-k2"
    assert split_model("no-prefix") == (None, "no-prefix")


def test_openai_compatible_request_and_usage(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "k-test")
    transport = FakeTransport(body={"choices": [{"message": {"content": "bonjour"}}],
                                    "usage": {"prompt_tokens": 7, "completion_tokens": 3}})
    response = call(OpenAICompatibleProvider(get_provider("mistral"), transport),
                    "mistral/mistral-small-latest")
    url, headers, payload = transport.calls[0]
    assert url == "https://api.mistral.ai/v1/chat/completions"
    assert headers["Authorization"] == "Bearer k-test"
    assert payload["model"] == "mistral-small-latest"
    assert (response.content, response.input_tokens, response.output_tokens) == ("bonjour", 7, 3)


def test_base_url_override(monkeypatch):
    monkeypatch.setenv("HIF_OLLAMA_BASE_URL", "http://gpu-box:11434/v1")
    transport = FakeTransport(body={"choices": [{"message": {"content": "ok"}}]})
    call(OpenAICompatibleProvider(get_provider("ollama"), transport), "ollama/llama3.1")
    url, headers, _ = transport.calls[0]
    assert url == "http://gpu-box:11434/v1/chat/completions"
    assert "Authorization" not in headers


def test_anthropic_native(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a-test")
    transport = FakeTransport(body={"content": [{"type": "text", "text": "salut"}],
                                    "usage": {"input_tokens": 5, "output_tokens": 2}})
    response = call(AnthropicProvider(get_provider("anthropic"), transport),
                    "anthropic/claude-sonnet")
    url, headers, payload = transport.calls[0]
    assert url.endswith("/v1/messages")
    assert headers["x-api-key"] == "a-test" and payload["system"] == "sys"
    assert response.content == "salut" and response.output_tokens == 2


def test_gemini_native(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    transport = FakeTransport(body={
        "candidates": [{"content": {"parts": [{"text": "hola"}]}}],
        "usageMetadata": {"promptTokenCount": 4, "candidatesTokenCount": 1}})
    response = call(GeminiProvider(get_provider("gemini"), transport), "gemini/gemini-flash")
    assert transport.calls[0][0].endswith("/models/gemini-flash:generateContent")
    assert response.content == "hola" and response.input_tokens == 4


def test_rate_limit_is_retryable_with_retry_after(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "x")
    transport = FakeTransport(status=429, body={"error": {"message": "slow down"}},
                              headers={"retry-after": "12"})
    with pytest.raises(ProviderError) as info:
        call(OpenAICompatibleProvider(get_provider("groq"), transport), "groq/llama")
    assert info.value.retryable and info.value.retry_after == 12.0
    assert info.value.status_code == 429


def test_auth_error_is_not_retryable(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "bad")
    transport = FakeTransport(status=401, body={"error": {"message": "invalid key"}})
    with pytest.raises(ProviderError) as info:
        call(OpenAICompatibleProvider(get_provider("openai"), transport), "openai/gpt")
    assert not info.value.retryable


def test_missing_key_is_reported(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="DEEPSEEK_API_KEY"):
        call(OpenAICompatibleProvider(get_provider("deepseek"), FakeTransport()),
             "deepseek/chat")


def test_auto_provider_dispatch():
    auto = AutoProvider(transport=FakeTransport(), fallback=object())
    assert isinstance(auto.adapter_for("anthropic/x"), AnthropicProvider)
    assert isinstance(auto.adapter_for("gemini/x"), GeminiProvider)
    assert isinstance(auto.adapter_for("together/x"), OpenAICompatibleProvider)
    assert auto.adapter_for("bedrock/x") is auto.fallback
    assert auto.adapter_for("unknown-model") is auto.fallback


def test_configured_providers(monkeypatch):
    for spec in PROVIDERS:
        for name in spec.env_keys:
            monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(spec.base_url_env, raising=False)
    monkeypatch.setenv("MISTRAL_API_KEY", "x")
    monkeypatch.setenv("HIF_ENABLE_OLLAMA", "true")
    assert {spec.id for spec in configured_providers()} == {"mistral", "ollama"}
