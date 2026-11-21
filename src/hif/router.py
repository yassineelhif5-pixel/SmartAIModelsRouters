"""Model selection, local usage budgets, cooldowns and fallback policy."""

from __future__ import annotations

import time
from datetime import timedelta

from hif.config import Settings
from hif.storage import HIFStore, utc_now


class ModelRouter:
    def __init__(self, settings: Settings, store: HIFStore):
        self.settings = settings
        self.store = store
        self._cooldown_until: dict[str, float] = {}

    def candidates(self, preferred: tuple[str, ...] = ()) -> tuple[str, ...]:
        pool = self.settings.get_models()
        ordered = tuple(dict.fromkeys((*preferred, *pool)))
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

    def mark_unavailable(self, model: str, retry_after: float | None = None) -> None:
        delay = min(max(float(retry_after or 30.0), 1.0), 900.0)
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
