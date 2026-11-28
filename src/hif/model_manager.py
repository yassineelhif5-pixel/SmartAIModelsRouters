"""Centralized model configuration and provider readiness inspection."""

from __future__ import annotations

from dataclasses import dataclass

from hif.config import Settings
from hif.provider_catalog import get_provider
from hif.providers import provider_name


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
        try:
            models = self.settings.get_models()
        except RuntimeError:  # no model configured yet: report an empty chain
            models = ()
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
            spec = get_provider(target.provider)
            env_names = list(spec.env_keys) if spec else []
            providers[target.provider] = {
                "provider": target.provider,
                "credential_configured": bool(spec and spec.is_configured()),
                "credential_env": env_names[0] if len(env_names) == 1 else (env_names or None),
            }
        return {
            "strategy": "ordered_fallback",
            "primary": targets[0].model if targets else None,
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
