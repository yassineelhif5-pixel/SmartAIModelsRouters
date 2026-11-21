"""Model selection, local usage budgets, cooldowns and fallback policy."""

from __future__ import annotations

import time
from datetime import timedelta

from hif.config import Settings
from hif.model_manager import AIModelManager
from hif.storage import HIFStore, utc_now


class ModelRouter:
    def __init__(self, settings: Settings, store: HIFStore):
        self.settings = settings
        self.store = store
        self.model_manager = AIModelManager(settings)
        self._cooldown_until: dict[str, float] = {}

    def candidates(self, preferred: tuple[str, ...] = ()) -> tuple[str, ...]:
        ordered = self.model_manager.candidates(preferred)
        eligible: list[str] = []
        now = time.monotonic()
        since = utc_now() - timedelta(hours=self.settings.usage_window_hours)
        for model in ordered:
            if self._cooldown_until.get(model, 0.0) > now:
                continue
            used = self.store.model_usage_since(model, since)
            budget = self.settings.token_budget_for(model)
            utilization = used / budget if budget > 0 else 1.0
            # Local HIF usage only; this is not an upstream subscription quota reading.
            if utilization >= self.settings.usage_fallback_threshold:
                continue
            eligible.append(model)
        return tuple(eligible)

    def status(self) -> dict[str, object]:
        return self.model_manager.status()

    def mark_unavailable(self, model: str, retry_after: float | None = None) -> None:
        try:
            requested_delay = float(retry_after) if retry_after is not None else 30.0
        except (TypeError, ValueError):
            requested_delay = 30.0
        delay = min(max(requested_delay, 1.0), 900.0)
        self._cooldown_until[model] = time.monotonic() + delay

    def usage_percent(self, model: str) -> float:
        since = utc_now() - timedelta(hours=self.settings.usage_window_hours)
        budget = self.settings.token_budget_for(model)
        if budget <= 0:
            return 100.0
        used = self.store.model_usage_since(model, since)
        return min(100.0, used / budget * 100.0)

    def usage_source(self) -> str:
        return "hif_measured_tokens"
