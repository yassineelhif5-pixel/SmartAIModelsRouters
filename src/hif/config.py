"""HIF runtime configuration loaded from environment variables."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


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


@dataclass(frozen=True)
class Settings:
    database_path: Path = Path(".hif/hif.sqlite3")
    model_pool: tuple[str, ...] = field(default_factory=tuple)
    planner_model: str | None = None
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
    allow_local_only_tasks: bool = False

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
        except ValueError as exc:
            raise ValueError("Invalid numeric HIF setting.") from exc

        if not 0.10 <= threshold <= 1.0:
            raise ValueError("HIF_USAGE_FALLBACK_THRESHOLD must be between 0.10 and 1.0.")
        for name, value in {
            "HIF_MAX_PARALLEL_TASKS": parallel,
            "HIF_MAX_PROVIDER_PARALLEL": provider_parallel,
            "HIF_USAGE_WINDOW_HOURS": window,
            "HIF_DEFAULT_MODEL_TOKEN_BUDGET": default_budget,
            "HIF_MAX_OUTPUT_TOKENS_PER_TASK": max_output,
            "HIF_REQUEST_TIMEOUT_SECONDS": timeout,
            "HIF_MAX_CONTEXT_CHARS": max_context,
            "HIF_MIN_FREE_MEMORY_MB": min_free,
        }.items():
            if value < 1:
                raise ValueError(f"{name} must be greater than zero.")

        return cls(
            database_path=Path(os.getenv("HIF_DATABASE_PATH", ".hif/hif.sqlite3")),
            model_pool=_parse_csv(os.getenv("HIF_MODEL_POOL")),
            planner_model=os.getenv("HIF_PLANNER_MODEL") or None,
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
            allow_local_only_tasks=os.getenv("HIF_ALLOW_LOCAL_ONLY", "false").lower()
            in {"1", "true", "yes"},
        )

    def get_models(self) -> tuple[str, ...]:
        if not self.model_pool:
            raise RuntimeError(
                "No model configured. Set HIF_MODEL_POOL with LiteLLM model identifiers. "
                "See .env.example."
            )
        return self.model_pool

    def token_budget_for(self, model: str) -> int:
        return self.model_token_budgets.get(model, self.default_model_token_budget)
