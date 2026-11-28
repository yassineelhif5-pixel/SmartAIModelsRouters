from __future__ import annotations

import json
from datetime import timedelta

import pytest

from hif.config import Settings
from hif.engine import HIFEngine
from hif.evaluation import MultiModelEvaluator, select_diverse_models
from hif.providers import ModelResponse
from hif.storage import HIFStore, utc_now


class ReviewProvider:
    async def complete(self, *, model, system_prompt, user_prompt, max_tokens, timeout):
        if "counter-test lead" in system_prompt.lower():
            payload = {
                "steps": ["Run a reversible local prototype test"],
                "required_tools": ["pytest"],
                "expected_evidence": ["test report"],
                "pass_criteria": ["all acceptance checks pass"],
                "stop_conditions": ["data loss or unexpected external side effects"],
                "risks": ["test environment differs from production"],
            }
        else:
            payload = {
                "verdict": "negative",
                "score": 30,
                "confidence": 0.9,
                "summary": "The proposal has unresolved feasibility blockers.",
                "strengths": ["Clear user problem"],
                "risks": ["Unverified integration assumptions"],
                "assumptions": ["Required API access is available"],
                "blockers": ["No validated deployment path"],
                "recommendations_to_test": ["Build a reversible proof of concept"],
                "validation_tests": ["Verify the integration against a sandbox"],
            }
        return ModelResponse(
            model=model,
            content=json.dumps(payload),
            input_tokens=100,
            output_tokens=50,
            duration_ms=25,
            cost_usd=0.001,
        )


def test_model_selection_prefers_provider_diversity():
    assert select_diverse_models(
        ["alpha/a", "alpha/b", "beta/c", "gamma/d"], 3
    ) == ["alpha/a", "beta/c", "gamma/d"]


@pytest.mark.asyncio
async def test_evaluation_uses_distinct_providers_and_records_negative_consensus(tmp_path):
    provider = ReviewProvider()
    evaluator = MultiModelEvaluator(provider, max_parallel=2)
    result = await evaluator.evaluate(
        "Build a multi-agent project",
        "Small workstation; limited budget",
        ["alpha/model-a", "beta/model-b", "alpha/model-c"],
        max_reviewers=3,
    )
    assert result.decision == "rejected"
    assert result.successful_reviewers == 3
    assert result.failed_reviewers == 0
    assert result.inconclusive_reviewers == 0
    assert result.countertest_required is True
    assert result.execution_performed is False
    assert result.countertest_status == "awaiting_user_approval"
    assert len({review.provider for review in result.reviews}) == 2
    assert all(review.input_tokens == 100 for review in result.reviews)


@pytest.mark.asyncio
async def test_evaluation_refuses_single_provider_consensus():
    evaluator = MultiModelEvaluator(ReviewProvider())
    with pytest.raises(ValueError, match="distinct configured providers"):
        await evaluator.evaluate(
            "Idea", "", ["alpha/model-a", "alpha/model-b"], max_reviewers=2
        )


@pytest.mark.asyncio
async def test_countertest_requires_approval_and_only_prepares_plan(tmp_path):
    database = tmp_path / "hif.sqlite3"
    settings = Settings(
        database_path=database,
        model_pool=("alpha/model-a", "beta/model-b"),
        task_model_preferences={"testing": ("alpha/model-a",)},
        resource_aware_scheduling=False,
    )
    engine = HIFEngine(settings=settings, provider=ReviewProvider(), store=HIFStore(database))
    result = await engine.evaluate_project("Build a project", "Local sandbox", max_reviewers=2)
    assert result.session_id
    assert engine.store.model_usage_since("alpha/model-a", utc_now() - timedelta(days=1)) > 0
    assert engine.store.model_usage_since("beta/model-b", utc_now() - timedelta(days=1)) > 0
    with pytest.raises(PermissionError, match="explicit user approval"):
        await engine.prepare_countertest_plan(
            result.session_id, result.evaluation_id, approved=False
        )
    plan = await engine.prepare_countertest_plan(
        result.session_id, result.evaluation_id, approved=True
    )
    parsed = json.loads(plan)
    assert parsed["steps"]
    stored = engine.store.get_memory(
        result.session_id, keys=[f"countertest_plan:{result.evaluation_id}"]
    )
    assert len(stored) == 1
    engine.close()


@pytest.mark.asyncio
async def test_evaluation_reviews_are_counted_by_the_spend_guard(tmp_path):
    database = tmp_path / "hif.sqlite3"
    settings = Settings(
        database_path=database,
        model_pool=("alpha/model-a", "beta/model-b"),
        resource_aware_scheduling=False,
        session_max_calls=1,
    )
    engine = HIFEngine(settings=settings, provider=ReviewProvider(), store=HIFStore(database))
    result = await engine.evaluate_project("Build a project", "Local sandbox", max_reviewers=2)
    snapshot = engine.spend_guard.snapshot(result.session_id)
    # Only one review was allowed to reach a provider; the other was stopped by the guard.
    assert snapshot["calls"] == 1
    assert snapshot["tripped"]
    assert snapshot["tokens"] == 150
    engine.close()
