"""Agent spend circuit breaker: unit tests and engine integration."""

from __future__ import annotations

import asyncio

import pytest

import json

from hif.config import Settings
from hif.engine import HIFEngine
from hif.planner import PLANNER_SYSTEM, SYNTHESIS_SYSTEM
from hif.providers import ModelResponse
from hif.spend_guard import SpendGuard, SpendLimitExceeded, SpendLimits
from hif.storage import HIFStore


class ParallelGraphProvider:
    """Returns a three-node plan, then answers every node and the synthesis."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def complete(self, *, model, system_prompt, user_prompt, max_tokens, timeout):
        self.calls.append(model)
        if system_prompt == PLANNER_SYSTEM:
            node = {"title": "T", "role": "generalist", "instructions": "Do it",
                    "task_type": "general", "acceptance_criteria": ["Done"]}
            content = json.dumps({
                "goal": "Build a tested feature",
                "nodes": [{**node, "id": "a", "depends_on": []},
                          {**node, "id": "b", "depends_on": []},
                          {**node, "id": "c", "depends_on": ["a", "b"]}],
                "final_instructions": "Combine",
            })
        elif system_prompt == SYNTHESIS_SYSTEM:
            content = "Final answer"
        else:
            content = "Node done: " + user_prompt.split("NODE_ID: ", 1)[-1].splitlines()[0]
        return ModelResponse(model=model, content=content, input_tokens=10, output_tokens=5)


def make_settings(tmp_path, **overrides) -> Settings:
    values = dict(database_path=tmp_path / "guard.sqlite3", model_pool=("mock/model",),
                  max_parallel_tasks=2, max_provider_parallel=2,
                  default_model_token_budget=100_000, resource_aware_scheduling=False)
    values.update(overrides)
    return Settings(**values)


def test_call_limit_trips_and_stays_tripped():
    guard = SpendGuard(SpendLimits(max_calls=2))
    guard.before_call("s", "m", "sys", "a")
    guard.before_call("s", "m", "sys", "b")
    with pytest.raises(SpendLimitExceeded, match="2 model calls"):
        guard.before_call("s", "m", "sys", "c")
    with pytest.raises(SpendLimitExceeded):
        guard.before_call("s", "m", "sys", "d")
    assert guard.snapshot("s")["tripped"]


def test_token_limit():
    guard = SpendGuard(SpendLimits(max_tokens=100))
    guard.before_call("s", "m", "sys", "a")
    guard.record("s", 80, 30)
    with pytest.raises(SpendLimitExceeded, match="110 tokens"):
        guard.before_call("s", "m", "sys", "b")


def test_cost_limit_only_when_reported():
    guard = SpendGuard(SpendLimits(max_cost_usd=0.05))
    guard.before_call("s", "m", "sys", "a")
    guard.record("s", 10, 10, None)
    guard.before_call("s", "m", "sys", "b")
    guard.record("s", 10, 10, 0.06)
    with pytest.raises(SpendLimitExceeded, match="cost"):
        guard.before_call("s", "m", "sys", "c")


def test_loop_detection_on_identical_prompts():
    guard = SpendGuard(SpendLimits(loop_repeat_limit=2))
    guard.before_call("s", "m", "sys", "same")
    guard.before_call("s", "m", "sys", "same")
    guard.before_call("s", "other-model", "sys", "same")  # another model is not a loop
    with pytest.raises(SpendLimitExceeded, match="loop detected"):
        guard.before_call("s", "m", "sys", "same")


def test_sessions_are_independent():
    guard = SpendGuard(SpendLimits(max_calls=1))
    guard.before_call("a", "m", "sys", "x")
    guard.before_call("b", "m", "sys", "x")
    with pytest.raises(SpendLimitExceeded):
        guard.before_call("a", "m", "sys", "y")


def test_engine_stops_a_session_that_exceeds_its_budget(tmp_path):
    # A 3-node plan needs 5 calls (plan + 3 nodes + synthesis); allow only 3.
    settings = make_settings(tmp_path, session_max_calls=3)
    provider = ParallelGraphProvider()
    store = HIFStore(settings.database_path)
    engine = HIFEngine(settings=settings, provider=provider, store=store)

    with pytest.raises(SpendLimitExceeded):
        asyncio.run(engine.run("Build a tested feature", session_id="guarded"))

    assert len(provider.calls) <= 3
    assert engine.spend_guard.snapshot("guarded")["tripped"]
    engine.close()


def test_engine_runs_normally_within_budget(tmp_path):
    settings = make_settings(tmp_path)
    engine = HIFEngine(settings=settings, provider=ParallelGraphProvider(),
                       store=HIFStore(settings.database_path))
    result = asyncio.run(engine.run("Build a tested feature", session_id="ok"))
    snapshot = engine.spend_guard.snapshot("ok")
    assert snapshot["calls"] == 5 and snapshot["tripped"] is None
    assert snapshot["tokens"] == result.total_input_tokens + result.total_output_tokens
    engine.close()
