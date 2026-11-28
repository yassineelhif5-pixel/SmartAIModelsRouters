"""Agent spend circuit breaker.

Stops a session before it overspends: a cap on tokens, on model calls, on reported cost,
and a loop detector that trips when the same prompt is sent to the same model again and
again (the classic runaway agent). Limits are per HIF session and enforced in the request
path, before each provider call, so a tripped session never reaches the provider again.
"""

from __future__ import annotations

import hashlib
import threading
from collections import Counter
from dataclasses import dataclass, field


class SpendLimitExceeded(RuntimeError):
    """Raised when a session trips the circuit breaker. Never retried."""

    def __init__(self, session_id: str, reason: str):
        super().__init__(f"HIF session {session_id} stopped by the spend guard: {reason}")
        self.session_id = session_id
        self.reason = reason


@dataclass(frozen=True)
class SpendLimits:
    max_tokens: int = 500_000          # input + output tokens for the whole session
    max_calls: int = 100               # provider calls, retries and fallbacks included
    max_cost_usd: float | None = None  # only enforced when providers report a cost
    loop_repeat_limit: int = 3         # identical (model, prompt) calls allowed


@dataclass
class _SessionSpend:
    tokens: int = 0
    calls: int = 0
    cost_usd: float = 0.0
    fingerprints: Counter = field(default_factory=Counter)
    tripped: str | None = None


def _fingerprint(model: str, system_prompt: str, user_prompt: str) -> str:
    digest = hashlib.sha256()
    for part in (model, system_prompt, user_prompt):
        digest.update(part.encode("utf-8", errors="replace"))
        digest.update(b"\x00")
    return digest.hexdigest()


class SpendGuard:
    def __init__(self, limits: SpendLimits | None = None):
        self.limits = limits or SpendLimits()
        self._sessions: dict[str, _SessionSpend] = {}
        self._lock = threading.Lock()

    def _state(self, session_id: str) -> _SessionSpend:
        return self._sessions.setdefault(session_id, _SessionSpend())

    def _trip(self, session_id: str, state: _SessionSpend, reason: str) -> None:
        state.tripped = reason
        raise SpendLimitExceeded(session_id, reason)

    def before_call(self, session_id: str, model: str, system_prompt: str,
                    user_prompt: str) -> None:
        """Check the session before a provider call; raise if it must stop."""
        with self._lock:
            state = self._state(session_id)
            if state.tripped:
                raise SpendLimitExceeded(session_id, state.tripped)
            if state.calls >= self.limits.max_calls:
                self._trip(session_id, state, f"{state.calls} model calls reached the limit "
                                              f"of {self.limits.max_calls}")
            if state.tokens >= self.limits.max_tokens:
                self._trip(session_id, state, f"{state.tokens} tokens reached the limit "
                                              f"of {self.limits.max_tokens}")
            if self.limits.max_cost_usd is not None and state.cost_usd >= self.limits.max_cost_usd:
                self._trip(session_id, state, f"cost ${state.cost_usd:.4f} reached the limit "
                                              f"of ${self.limits.max_cost_usd:.4f}")
            key = _fingerprint(model, system_prompt, user_prompt)
            state.fingerprints[key] += 1
            if state.fingerprints[key] > self.limits.loop_repeat_limit:
                self._trip(session_id, state,
                           f"loop detected: the same prompt was sent to {model} "
                           f"{state.fingerprints[key]} times")
            state.calls += 1

    def record(self, session_id: str, input_tokens: int, output_tokens: int,
               cost_usd: float | None = None) -> None:
        with self._lock:
            state = self._state(session_id)
            state.tokens += max(0, input_tokens) + max(0, output_tokens)
            if cost_usd:
                state.cost_usd += cost_usd

    def snapshot(self, session_id: str) -> dict[str, object]:
        with self._lock:
            state = self._state(session_id)
            return {
                "tokens": state.tokens,
                "calls": state.calls,
                "cost_usd": round(state.cost_usd, 6),
                "tripped": state.tripped,
                "limits": {
                    "max_tokens": self.limits.max_tokens,
                    "max_calls": self.limits.max_calls,
                    "max_cost_usd": self.limits.max_cost_usd,
                    "loop_repeat_limit": self.limits.loop_repeat_limit,
                },
            }
