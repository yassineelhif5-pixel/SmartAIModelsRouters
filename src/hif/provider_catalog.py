"""Catalog of AI providers HIF can reach, and how to reach them.

Every entry is data, not code: adding a provider that speaks an OpenAI-compatible
Chat Completions API takes one ``ProviderSpec``. Base URLs can always be overridden
with ``HIF_<ID>_BASE_URL`` (for example ``HIF_MISTRAL_BASE_URL``), so a regional,
private or proxied endpoint works without a code change.

Model identifiers are written ``<provider id>/<provider model name>``, for example
``mistral/mistral-large-latest`` or ``ollama/llama3.1``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

ProviderKind = Literal[
    "openai_compatible",  # POST {base}/chat/completions, Bearer auth
    "azure_openai",       # Azure OpenAI v1 API, api-key header
    "anthropic",          # native Messages API
    "gemini",             # native Gemini generateContent API
    "litellm",            # cloud SDK auth (AWS, GCP, IBM...) delegated to LiteLLM
]

Region = Literal["us", "eu", "cn", "global", "local"]


@dataclass(frozen=True)
class ProviderSpec:
    id: str
    name: str
    kind: ProviderKind
    base_url: str = ""
    env_keys: tuple[str, ...] = ()
    region: Region = "global"
    local: bool = False
    notes: str = ""
    extra_headers: dict[str, str] = field(default_factory=dict)

    @property
    def base_url_env(self) -> str:
        return f"HIF_{self.id.upper().replace('-', '_')}_BASE_URL"

    def resolved_base_url(self) -> str:
        return os.getenv(self.base_url_env, "").strip() or self.base_url

    def api_key(self) -> str | None:
        for name in self.env_keys:
            value = os.getenv(name, "").strip()
            if value:
                return value
        return None

    def is_configured(self) -> bool:
        """True when HIF has what it needs to call this provider."""
        if self.local:
            # Local servers need no key; they count as configured once enabled explicitly
            # or when their base URL is overridden.
            return bool(os.getenv(self.base_url_env, "").strip()) or _truthy(
                os.getenv(f"HIF_ENABLE_{self.id.upper().replace('-', '_')}", "")
            )
        if self.kind == "azure_openai" and not self.resolved_base_url():
            return False
        if self.kind == "litellm":
            return all(os.getenv(name, "").strip() for name in self.env_keys)
        return self.api_key() is not None


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _oa(id: str, name: str, base_url: str, *keys: str, region: Region = "global",
        notes: str = "", headers: dict[str, str] | None = None) -> ProviderSpec:
    return ProviderSpec(id=id, name=name, kind="openai_compatible", base_url=base_url,
                        env_keys=keys, region=region, notes=notes,
                        extra_headers=headers or {})


def _local(id: str, name: str, base_url: str, notes: str = "") -> ProviderSpec:
    return ProviderSpec(id=id, name=name, kind="openai_compatible", base_url=base_url,
                        region="local", local=True, notes=notes)


# Base URLs follow each provider's public documentation at the time of writing.
# Check them against the provider docs before production use; override with HIF_<ID>_BASE_URL.
PROVIDERS: tuple[ProviderSpec, ...] = (
    # Frontier labs with native APIs
    ProviderSpec("anthropic", "Anthropic (Claude)", "anthropic",
                 "https://api.anthropic.com/v1", ("ANTHROPIC_API_KEY",), "us"),
    ProviderSpec("gemini", "Google Gemini (AI Studio)", "gemini",
                 "https://generativelanguage.googleapis.com/v1beta",
                 ("GEMINI_API_KEY", "GOOGLE_API_KEY"), "global"),
    _oa("openai", "OpenAI", "https://api.openai.com/v1", "OPENAI_API_KEY", region="us"),
    _oa("xai", "xAI (Grok)", "https://api.x.ai/v1", "XAI_API_KEY", region="us"),
    # European providers (data residency arguments)
    _oa("mistral", "Mistral AI", "https://api.mistral.ai/v1", "MISTRAL_API_KEY", region="eu"),
    _oa("scaleway", "Scaleway Generative APIs", "https://api.scaleway.ai/v1",
        "SCW_SECRET_KEY", region="eu"),
    _oa("ovhcloud", "OVHcloud AI Endpoints",
        "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
        "OVH_AI_ENDPOINTS_ACCESS_TOKEN", region="eu",
        notes="Check the endpoint in OVHcloud docs; override HIF_OVHCLOUD_BASE_URL if needed."),
    # Chinese labs
    _oa("deepseek", "DeepSeek", "https://api.deepseek.com/v1", "DEEPSEEK_API_KEY", region="cn"),
    _oa("moonshot", "Moonshot (Kimi)", "https://api.moonshot.ai/v1", "MOONSHOT_API_KEY",
        region="cn"),
    _oa("dashscope", "Alibaba DashScope (Qwen)",
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY",
        region="cn"),
    _oa("zai", "Z.AI (GLM)", "https://api.z.ai/api/paas/v4", "ZAI_API_KEY", region="cn"),
    _oa("minimax", "MiniMax", "https://api.minimax.io/v1", "MINIMAX_API_KEY", region="cn"),
    # Fast / open-weight inference clouds
    _oa("groq", "Groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY", region="us"),
    _oa("cerebras", "Cerebras", "https://api.cerebras.ai/v1", "CEREBRAS_API_KEY", region="us"),
    _oa("sambanova", "SambaNova", "https://api.sambanova.ai/v1", "SAMBANOVA_API_KEY",
        region="us"),
    _oa("together", "Together AI", "https://api.together.xyz/v1", "TOGETHER_API_KEY",
        region="us"),
    _oa("fireworks", "Fireworks AI", "https://api.fireworks.ai/inference/v1",
        "FIREWORKS_API_KEY", region="us"),
    _oa("deepinfra", "DeepInfra", "https://api.deepinfra.com/v1/openai", "DEEPINFRA_API_KEY",
        region="us"),
    _oa("nvidia", "NVIDIA NIM", "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
        region="us"),
    _oa("huggingface", "Hugging Face Inference Providers", "https://router.huggingface.co/v1",
        "HF_TOKEN", "HUGGINGFACE_API_KEY"),
    _oa("perplexity", "Perplexity (Sonar)", "https://api.perplexity.ai", "PERPLEXITY_API_KEY",
        region="us"),
    _oa("cohere", "Cohere (compatibility API)", "https://api.cohere.ai/compatibility/v1",
        "COHERE_API_KEY", "CO_API_KEY"),
    _oa("github", "GitHub Models", "https://models.github.ai/inference", "GITHUB_TOKEN",
        region="us"),
    # Aggregators (useful as a last-resort fallback lane)
    _oa("openrouter", "OpenRouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
        headers={"X-Title": "HIF"}),
    # Hyperscalers
    ProviderSpec("azure", "Azure OpenAI / Azure AI Foundry", "azure_openai", "",
                 ("AZURE_OPENAI_API_KEY",), "global",
                 notes="Set HIF_AZURE_BASE_URL to https://<resource>.openai.azure.com/openai/v1 ; "
                       "the model part of the id is your deployment name."),
    ProviderSpec("bedrock", "AWS Bedrock", "litellm", "",
                 ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION_NAME"), "global",
                 notes="Delegated to LiteLLM (SigV4 signing). Install the providers extra."),
    ProviderSpec("vertex_ai", "Google Vertex AI", "litellm", "",
                 ("VERTEXAI_PROJECT", "VERTEXAI_LOCATION"), "global",
                 notes="Delegated to LiteLLM (Google ADC credentials)."),
    ProviderSpec("watsonx", "IBM watsonx.ai", "litellm", "",
                 ("WATSONX_URL", "WATSONX_APIKEY", "WATSONX_PROJECT_ID"), "global",
                 notes="Delegated to LiteLLM."),
    # Local and self-hosted runtimes (no data leaves the machine or the private network)
    _local("ollama", "Ollama", "http://localhost:11434/v1",
           "Enable with HIF_ENABLE_OLLAMA=true or set HIF_OLLAMA_BASE_URL."),
    _local("lmstudio", "LM Studio", "http://localhost:1234/v1"),
    _local("vllm", "vLLM server", "http://localhost:8000/v1"),
    _local("llamacpp", "llama.cpp server", "http://localhost:8080/v1"),
)

_BY_ID: dict[str, ProviderSpec] = {spec.id: spec for spec in PROVIDERS}

# Prefix aliases people already use (LiteLLM spellings and common names).
ALIASES: dict[str, str] = {
    "google": "gemini",
    "claude": "anthropic",
    "kimi": "moonshot",
    "qwen": "dashscope",
    "glm": "zai",
    "azure_openai": "azure",
    "vertex": "vertex_ai",
    "hf": "huggingface",
    "together_ai": "together",
    "fireworks_ai": "fireworks",
    "nvidia_nim": "nvidia",
    "lm_studio": "lmstudio",
    "llama_cpp": "llamacpp",
}


def get_provider(provider_id: str) -> ProviderSpec | None:
    key = provider_id.strip().lower()
    return _BY_ID.get(ALIASES.get(key, key))


def split_model(model: str) -> tuple[ProviderSpec | None, str]:
    """Split ``provider/model`` into its catalog entry and the provider's own model name."""
    if "/" not in model:
        return None, model
    prefix, name = model.split("/", 1)
    return get_provider(prefix), name


def configured_providers() -> tuple[ProviderSpec, ...]:
    return tuple(spec for spec in PROVIDERS if spec.is_configured())


def credential_env_map() -> dict[str, tuple[str, ...]]:
    """Provider id -> credential variables, for providers that use a single API key."""
    return {
        spec.id: spec.env_keys
        for spec in PROVIDERS
        if spec.env_keys and spec.kind not in {"litellm"}
    }
