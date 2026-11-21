from __future__ import annotations

import asyncio
import json
from datetime import timedelta

import pytest
from pydantic import ValidationError

from hif.config import Settings
from hif.engine import HIFEngine
from hif.planner import PLANNER_SYSTEM, SYNTHESIS_SYSTEM
from hif.providers import ModelResponse, ProviderError
from hif.resources import AdaptiveConcurrency, ResourceSnapshot
from hif.router import ModelRouter
from hif.schemas import ExecutionPlan
from hif.storage import HIFStore, utc_now


class ParallelGraphProvider:
    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0
        self.calls: list[str] = []

    async def complete(
        self, *, model: str, system_prompt: str, user_prompt: str,
        max_tokens: int, timeout: int,
    ) -> ModelResponse:
        self.calls.append(model)
        if system_prompt == PLANNER_SYSTEM:
            content = json.dumps({
                "goal": "Build a tested feature",
                "nodes": [
                    {
                        "id": "design", "title": "Architecture", "role": "architect",
                        "instructions": "Design the component",
                        "task_type": "analysis", "depends_on": [],
                        "acceptance_criteria": ["Architecture is clear"],
                        "context_keys": ["goal", "project_context"],
                    },
                    {
                        "id": "research", "title": "Research", "role": "researcher",
                        "instructions": "Research constraints",
                        "task_type": "research", "depends_on": [],
                        "acceptance_criteria": ["Constraints are listed"],
                        "context_keys": ["goal"],
                    },
                    {
                        "id": "review", "title": "Review", "role": "reviewer",
                        "instructions": "Review the two preceding outputs",
                        "task_type": "review", "depends_on": ["design", "research"],
                        "acceptance_criteria": ["Both outputs are considered"],
                        "context_keys": ["goal"],
                    },
                ],
                "final_instructions": "Combine the node results",
            })
        elif system_prompt == SYNTHESIS_SYSTEM:
            content = "Final consolidated answer"
        else:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            await asyncio.sleep(0.03)
            self.active -= 1
            content = "Node completed: " + user_prompt.split("NODE_ID: ", 1)[-1].splitlines()[0]

        return ModelResponse(
            model=model, content=content, input_tokens=10, output_tokens=5, duration_ms=30
        )


class FallbackProvider(ParallelGraphProvider):
    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse:
        self.calls.append(model)
        if model == "broken/model":
            raise ProviderError("HTTP 429 rate limit", retryable=True, retry_after=0.01)
        return await super().complete(
            model=model, system_prompt=system_prompt, user_prompt=user_prompt,
            max_tokens=max_tokens, timeout=timeout,
        )


def make_settings(tmp_path, **overrides) -> Settings:
    values = dict(
        database_path=tmp_path / "hif-test.sqlite3",
        model_pool=("mock/model",),
        max_parallel_tasks=2,
        max_provider_parallel=2,
        usage_fallback_threshold=0.80,
        default_model_token_budget=100_000,
        resource_aware_scheduling=False,
    )
    values.update(overrides)
    return Settings(**values)


def test_execution_plan_rejects_dependency_cycle() -> None:
    with pytest.raises(ValidationError):
        ExecutionPlan.model_validate({
            "goal": "cycle",
            "nodes": [
                {"id": "a", "title": "A", "role": "architect", "instructions": "A",
                 "depends_on": ["b"]},
                {"id": "b", "title": "B", "role": "reviewer", "instructions": "B",
                 "depends_on": ["a"]},
            ],
        })


def test_store_persists_shared_memory_and_usage(tmp_path) -> None:
    store = HIFStore(tmp_path / "memory.sqlite3")
    session_id = store.create_session("shared goal")
    store.add_memory(session_id, "goal", "user", "shared context")
    store.add_memory(session_id, "role:architect", "system", "architect role definition")
    store.add_usage(session_id, "mock/model", 12, 8)

    memories = store.get_memory(session_id, keys=["goal", "role:architect"])
    assert {item["memory_key"] for item in memories} == {"goal", "role:architect"}
    assert store.model_usage_since("mock/model", utc_now() - timedelta(days=1)) == 20


def test_router_falls_back_at_eighty_percent(tmp_path) -> None:
    settings = make_settings(
        tmp_path,
        model_pool=("alpha/model-a", "beta/model-b"),
        model_token_budgets={"alpha/model-a": 100, "beta/model-b": 100},
    )
    store = HIFStore(settings.database_path)
    session_id = store.create_session("quota test")
    store.add_usage(session_id, "alpha/model-a", 60, 20)

    router = ModelRouter(settings, store)
    assert router.candidates() == ("beta/model-b",)
    assert router.usage_percent("alpha/model-a") == 80.0


def test_resource_scheduler_reduces_parallelism_under_pressure(tmp_path) -> None:
    scheduler = AdaptiveConcurrency(8, cpu_threshold=85, memory_threshold=88)
    scheduler.monitor.snapshot = lambda: ResourceSnapshot(96, 92, 500, 8)
    limit, snapshot = scheduler.effective_limit()
    assert limit == 1
    assert snapshot.logical_cpus == 8


@pytest.mark.asyncio
async def test_hifnode_runs_independent_nodes_in_parallel_and_shares_session(tmp_path) -> None:
    settings = make_settings(tmp_path)
    provider = ParallelGraphProvider()
    engine = HIFEngine(settings=settings, provider=provider, store=HIFStore(settings.database_path))

    result = await engine.run(
        "Build a tested feature",
        context="Project uses Python and SQLite",
        session_id="shared-test-session",
        parallel=True,
    )

    assert result.session_id == "shared-test-session"
    assert [node.node_id for node in result.nodes] == ["design", "research", "review"]
    assert provider.max_active >= 2
    rows = engine.status(result.session_id)["nodes"]
    assert len(rows) == 3
    assert all(row["status"] == "completed" for row in rows)
    memory_keys = {
        item["memory_key"]
        for item in engine.store.get_memory(result.session_id, limit=50)
    }
    assert "node:design" in memory_keys
    assert "node:research" in memory_keys
    assert "session_summary" in memory_keys


@pytest.mark.asyncio
async def test_hif_falls_back_after_retryable_provider_error(tmp_path) -> None:
    settings = make_settings(
        tmp_path,
        model_pool=("broken/model", "healthy/model"),
        planner_model="broken/model",
    )
    provider = FallbackProvider()
    engine = HIFEngine(settings=settings, provider=provider, store=HIFStore(settings.database_path))
    result = await engine.run("Smoke test", parallel=False)

    assert result.nodes
    assert provider.calls[0] == "broken/model"
    assert "healthy/model" in provider.calls
