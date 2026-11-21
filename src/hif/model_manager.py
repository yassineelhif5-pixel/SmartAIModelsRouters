"""Centralized model configuration and provider readiness inspection."""

from __future__ import annotations

import os
from dataclasses import dataclass

from hif.config import Settings
from hif.providers import provider_name


PROVIDER_API_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "vertex_ai": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


@dataclass(frozen=True)
class ModelTarget:
    """A configured model and its position in the ordered fallback chain."""

    model: str
    provider: str
    priority: int
    role: str


class AIModelManager:
    """Expose one source of truth for the active model and fallback chain.

    The first configured model is primary. Remaining models are tried in order
    when the current provider reports a retryable availability failure.
    Credentials are never returned; only their presence is reported.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def candidates(self, preferred: tuple[str, ...] = ()) -> tuple[str, ...]:
        pool = self.settings.get_models()
        return tuple(dict.fromkeys((*preferred, *pool)))

    def targets(self) -> tuple[ModelTarget, ...]:
        models = self.settings.get_models()
        return tuple(
            ModelTarget(
                model=model,
                provider=provider_name(model),
                priority=index + 1,
                role="primary" if index == 0 else "fallback",
            )
            for index, model in enumerate(models)
        )

    def status(self) -> dict[str, object]:
        targets = self.targets()
        providers: dict[str, dict[str, object]] = {}
        for target in targets:
            key_name = PROVIDER_API_KEYS.get(target.provider)
            providers[target.provider] = {
                "provider": target.provider,
                "credential_configured": bool(key_name and os.getenv(key_name)),
                "credential_env": key_name,
            }
        return {
            "strategy": "ordered_fallback",
            "primary": targets[0].model,
            "fallbacks": [target.model for target in targets[1:]],
            "models": [
                {
                    "model": target.model,
                    "provider": target.provider,
                    "priority": target.priority,
                    "role": target.role,
                }
                for target in targets
            ],
            "providers": list(providers.values()),
            "usage_fallback_threshold": self.settings.usage_fallback_threshold,
            "usage_window_hours": self.settings.usage_window_hours,
        }
