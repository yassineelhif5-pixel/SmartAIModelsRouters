"""HIF runtime configuration loaded from environment variables."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=False)



# Multi-provider starter catalog. Model IDs are refreshed against provider documentation;
# only providers with configured credentials are activated automatically.
DEFAULT_MODEL_POOL: tuple[str, ...] = (
    "openai/gpt-6-luna",
    "openai/gpt-6.2-sol",
    "openai/gpt-6.2-astra",
    "anthropic/claude-haiku-4-5-20251001",
    "anthropic/claude-sonnet-5",
    "anthropic/claude-opus-5",
    "gemini/gemini-3.5-flash-lite",
    "gemini/gemini-3.8-flash",
    "gemini/gemini-3.1-pro-preview",
    "deepseek/deepseek-flash",
    "deepseek/deepseek-v4-pro",
)

DEFAULT_TASK_MODEL_PREFERENCES: dict[str, tuple[str, ...]] = {
    "analysis": (
        "openai/gpt-6-luna", "gemini/gemini-3.5-flash-lite",
        "deepseek/deepseek-flash", "anthropic/claude-haiku-4-5-20251001",
    ),
    "research": (
        "gemini/gemini-3.8-flash", "openai/gpt-6.2-sol",
        "anthropic/claude-sonnet-5", "deepseek/deepseek-v4-pro",
    ),
    "coding": (
        "openai/gpt-6.2-sol", "anthropic/claude-sonnet-5",
        "deepseek/deepseek-v4-pro", "gemini/gemini-3.8-flash",
    ),
    "testing": (
        "openai/gpt-6-luna", "deepseek/deepseek-flash",
        "anthropic/claude-haiku-4-5-20251001",
    ),
    "review": (
        "openai/gpt-6.2-astra", "anthropic/claude-opus-5",
        "gemini/gemini-3.1-pro-preview", "deepseek/deepseek-v4-pro",
    ),
    "documentation": (
        "openai/gpt-6-luna", "anthropic/claude-sonnet-5",
        "gemini/gemini-3.8-flash",
    ),
    "architecture": (
        "openai/gpt-6.2-astra", "anthropic/claude-opus-5",
        "gemini/gemini-3.1-pro-preview",
    ),
    "infrastructure": (
        "openai/gpt-6.2-sol", "anthropic/claude-sonnet-5",
        "gemini/gemini-3.8-flash",
    ),
    "general": (
        "openai/gpt-6-luna", "gemini/gemini-3.5-flash-lite",
        "deepseek/deepseek-flash",
    ),
}

_PROVIDER_CREDENTIALS: dict[str, tuple[str, ...]] = {
    "openai": ("OPENAI_API_KEY",),
    "anthropic": ("ANTHROPIC_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "deepseek": ("DEEPSEEK_API_KEY",),
}


def _default_models_for_configured_providers() -> tuple[str, ...]:
    """Activate starter models only for providers with a configured API key."""
    enabled = {
        provider
        for provider, env_names in _PROVIDER_CREDENTIALS.items()
        if any(os.getenv(name, "").strip() for name in env_names)
    }
    return tuple(
        model for model in DEFAULT_MODEL_POOL
        if model.split("/", 1)[0] in enabled
    )


def _default_task_preferences(
    active_models: tuple[str, ...],
) -> dict[str, tuple[str, ...]]:
    active = set(active_models)
    return {
        task_type: tuple(model for model in models if model in active)
        for task_type, models in DEFAULT_TASK_MODEL_PREFERENCES.items()
        if any(model in active for model in models)
    }


def default_database_path() -> Path:
    """Return a per-user path shared by every project on this machine."""
    if os.getenv("LOCALAPPDATA"):
        root = Path(os.environ["LOCALAPPDATA"])
    elif os.getenv("XDG_DATA_HOME"):
        root = Path(os.environ["XDG_DATA_HOME"])
    else:
        root = Path.home() / ".local" / "share"
    return root / "HIF" / "hif.sqlite3"


def _parse_csv(value: str | None) -> tuple[str, ...]:
    return tuple(part.strip() for part in (value or "").split(",") if part.strip())


def _parse_json_int_map(value: str | None, setting: str) -> dict[str, int]:
    if not value:
        return {}
    try:
        raw = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{setting} must contain valid JSON.") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"{setting} must be a JSON object.")
    result: dict[str, int] = {}
    for key, amount in raw.items():
        if not isinstance(key, str) or not isinstance(amount, int) or amount <= 0:
            raise ValueError(f"{setting} values must be positive integers.")
        result[key] = amount
    return result


def _parse_json_model_map(value: str | None) -> dict[str, tuple[str, ...]]:
    if not value:
        return {}
    try:
        raw = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("HIF_TASK_MODEL_PREFERENCES must contain valid JSON.") from exc
    if not isinstance(raw, dict):
        raise ValueError("HIF_TASK_MODEL_PREFERENCES must be a JSON object.")
    result: dict[str, tuple[str, ...]] = {}
    for task_type, models in raw.items():
        if not isinstance(task_type, str) or not isinstance(models, list):
            raise ValueError("Task model preferences must map task types to model lists.")
        result[task_type] = tuple(
            str(model).strip() for model in models if str(model).strip()
        )
    return result


@dataclass(frozen=True)
class Settings:
    database_path: Path = field(default_factory=default_database_path)
    model_pool: tuple[str, ...] = field(default_factory=tuple)
    planner_model: str | None = None
    task_model_preferences: dict[str, tuple[str, ...]] = field(default_factory=dict)
    max_parallel_tasks: int = 4
    max_provider_parallel: int = 3
    usage_fallback_threshold: float = 0.80
    usage_window_hours: int = 168
    default_model_token_budget: int = 250_000
    model_token_budgets: dict[str, int] = field(default_factory=dict)
    max_output_tokens_per_task: int = 1800
    request_timeout_seconds: int = 120
    max_context_chars: int = 16_000
    cpu_pressure_threshold: float = 85.0
    memory_pressure_threshold: float = 88.0
    min_free_memory_mb: int = 1536
    resource_aware_scheduling: bool = True
    gateway_api_key: str | None = None
    gateway_host: str = "127.0.0.1"
    gateway_port: int = 8765
    gateway_rate_limit_per_minute: int = 60
    gateway_max_request_bytes: int = 65536
    gateway_tls_certfile: Path | None = None
    gateway_tls_keyfile: Path | None = None
    gateway_allowed_hosts: tuple[str, ...] = field(default_factory=tuple)
    gateway_allowed_origins: tuple[str, ...] = field(default_factory=tuple)
    gateway_oauth_issuer_url: str | None = None
    gateway_oauth_resource_url: str | None = None
    gateway_oauth_audience: str | None = None
    gateway_oauth_jwks_url: str | None = None
    gateway_oauth_required_scopes: tuple[str, ...] = field(default_factory=tuple)
    gateway_oauth_algorithms: tuple[str, ...] = ("RS256",)
    gateway_oauth_allowed_client_ids: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            threshold = float(os.getenv("HIF_USAGE_FALLBACK_THRESHOLD", "0.80"))
            parallel = int(os.getenv("HIF_MAX_PARALLEL_TASKS", "4"))
            provider_parallel = int(os.getenv("HIF_MAX_PROVIDER_PARALLEL", "3"))
            window = int(os.getenv("HIF_USAGE_WINDOW_HOURS", "168"))
            default_budget = int(os.getenv("HIF_DEFAULT_MODEL_TOKEN_BUDGET", "250000"))
            max_output = int(os.getenv("HIF_MAX_OUTPUT_TOKENS_PER_TASK", "1800"))
            timeout = int(os.getenv("HIF_REQUEST_TIMEOUT_SECONDS", "120"))
            max_context = int(os.getenv("HIF_MAX_CONTEXT_CHARS", "16000"))
            cpu_threshold = float(os.getenv("HIF_CPU_PRESSURE_THRESHOLD", "85"))
            memory_threshold = float(os.getenv("HIF_MEMORY_PRESSURE_THRESHOLD", "88"))
            min_free = int(os.getenv("HIF_MIN_FREE_MEMORY_MB", "1536"))
            gateway_port = int(os.getenv("HIF_GATEWAY_PORT", "8765"))
            gateway_rate_limit = int(os.getenv("HIF_GATEWAY_RATE_LIMIT_PER_MINUTE", "60"))
            gateway_max_bytes = int(os.getenv("HIF_GATEWAY_MAX_REQUEST_BYTES", "65536"))
        except ValueError as exc:
            raise ValueError("Invalid numeric HIF setting.") from exc

        positive = {
            "HIF_MAX_PARALLEL_TASKS": parallel,
            "HIF_MAX_PROVIDER_PARALLEL": provider_parallel,
            "HIF_USAGE_WINDOW_HOURS": window,
            "HIF_DEFAULT_MODEL_TOKEN_BUDGET": default_budget,
            "HIF_MAX_OUTPUT_TOKENS_PER_TASK": max_output,
            "HIF_REQUEST_TIMEOUT_SECONDS": timeout,
            "HIF_MAX_CONTEXT_CHARS": max_context,
            "HIF_MIN_FREE_MEMORY_MB": min_free,
            "HIF_GATEWAY_PORT": gateway_port,
            "HIF_GATEWAY_RATE_LIMIT_PER_MINUTE": gateway_rate_limit,
            "HIF_GATEWAY_MAX_REQUEST_BYTES": gateway_max_bytes,
        }
        for name, value in positive.items():
            if value < 1:
                raise ValueError(f"{name} must be greater than zero.")
        if not 0.10 <= threshold <= 1.0:
            raise ValueError("HIF_USAGE_FALLBACK_THRESHOLD must be between 0.10 and 1.0.")
        if gateway_rate_limit < 1 or gateway_max_bytes < 1024:
            raise ValueError("Gateway rate limit must be positive and request size at least 1024 bytes.")
        if not 1 <= gateway_port <= 65535:
            raise ValueError("HIF_GATEWAY_PORT must be between 1 and 65535.")

        oauth_values = (
            os.getenv("HIF_GATEWAY_OAUTH_ISSUER_URL", "").strip(),
            os.getenv("HIF_GATEWAY_OAUTH_RESOURCE_URL", "").strip(),
            os.getenv("HIF_GATEWAY_OAUTH_AUDIENCE", "").strip(),
            os.getenv("HIF_GATEWAY_OAUTH_JWKS_URL", "").strip(),
        )
        oauth_scopes = _parse_csv(os.getenv("HIF_GATEWAY_OAUTH_REQUIRED_SCOPES"))
        oauth_enabled = any(oauth_values) or bool(oauth_scopes)
        if oauth_enabled and (not all(oauth_values) or not oauth_scopes):
            raise ValueError(
                "OAuth gateway requires issuer URL, resource URL, audience, JWKS URL "
                "and at least one required scope."
            )
        if oauth_enabled and not (
            oauth_values[0].startswith("https://")
            and oauth_values[1].startswith("https://")
            and oauth_values[3].startswith("https://")
        ):
            raise ValueError("OAuth issuer, resource and JWKS URLs must use HTTPS.")

        database_setting = os.getenv("HIF_DATABASE_PATH", "").strip()
        database_path = (
            Path(database_setting).expanduser()
            if database_setting
            else default_database_path()
        )

        configured_pool = os.getenv("HIF_MODEL_POOL", "").strip()
        model_pool = (
            _parse_csv(configured_pool)
            if configured_pool
            else _default_models_for_configured_providers()
        )
        configured_preferences = os.getenv("HIF_TASK_MODEL_PREFERENCES", "").strip()
        task_preferences = (
            _parse_json_model_map(configured_preferences)
            if configured_preferences
            else _default_task_preferences(model_pool)
        )

        return cls(
            database_path=database_path,
            model_pool=model_pool,
            planner_model=os.getenv("HIF_PLANNER_MODEL") or None,
            task_model_preferences=task_preferences,
            max_parallel_tasks=parallel,
            max_provider_parallel=provider_parallel,
            usage_fallback_threshold=threshold,
            usage_window_hours=window,
            default_model_token_budget=default_budget,
            model_token_budgets=_parse_json_int_map(
                os.getenv("HIF_MODEL_TOKEN_BUDGETS"), "HIF_MODEL_TOKEN_BUDGETS"
            ),
            max_output_tokens_per_task=max_output,
            request_timeout_seconds=timeout,
            max_context_chars=max_context,
            cpu_pressure_threshold=cpu_threshold,
            memory_pressure_threshold=memory_threshold,
            min_free_memory_mb=min_free,
            resource_aware_scheduling=os.getenv("HIF_RESOURCE_AWARE", "true").lower()
            not in {"0", "false", "no"},
            gateway_api_key=os.getenv("HIF_GATEWAY_API_KEY") or None,
            gateway_host=os.getenv("HIF_GATEWAY_HOST", "127.0.0.1"),
            gateway_port=gateway_port,
            gateway_rate_limit_per_minute=gateway_rate_limit,
            gateway_max_request_bytes=gateway_max_bytes,
            gateway_tls_certfile=Path(os.environ["HIF_GATEWAY_TLS_CERTFILE"]).expanduser()
            if os.getenv("HIF_GATEWAY_TLS_CERTFILE") else None,
            gateway_tls_keyfile=Path(os.environ["HIF_GATEWAY_TLS_KEYFILE"]).expanduser()
            if os.getenv("HIF_GATEWAY_TLS_KEYFILE") else None,
            gateway_allowed_hosts=_parse_csv(os.getenv("HIF_GATEWAY_ALLOWED_HOSTS")),
            gateway_allowed_origins=_parse_csv(os.getenv("HIF_GATEWAY_ALLOWED_ORIGINS")),
            gateway_oauth_issuer_url=os.getenv("HIF_GATEWAY_OAUTH_ISSUER_URL") or None,
            gateway_oauth_resource_url=os.getenv("HIF_GATEWAY_OAUTH_RESOURCE_URL") or None,
            gateway_oauth_audience=os.getenv("HIF_GATEWAY_OAUTH_AUDIENCE") or None,
            gateway_oauth_jwks_url=os.getenv("HIF_GATEWAY_OAUTH_JWKS_URL") or None,
            gateway_oauth_required_scopes=oauth_scopes,
            gateway_oauth_algorithms=_parse_csv(
                os.getenv("HIF_GATEWAY_OAUTH_ALGORITHMS", "RS256")
            ),
            gateway_oauth_allowed_client_ids=_parse_csv(
                os.getenv("HIF_GATEWAY_OAUTH_ALLOWED_CLIENT_IDS")
            ),
        )

    def get_models(self) -> tuple[str, ...]:
        if not self.model_pool:
            raise RuntimeError(
                "No active model configured. Add a provider API key (OpenAI, Anthropic, Gemini "
                "or DeepSeek), or set HIF_MODEL_POOL explicitly. See .env.example."
            )
        return self.model_pool

    def token_budget_for(self, model: str) -> int:
        return self.model_token_budgets.get(model, self.default_model_token_budget)
