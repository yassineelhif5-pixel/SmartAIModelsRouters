"""Independent multi-model project assessment with an approval-gated next step.

This module only evaluates and proposes tests. It never executes recommendations,
changes files, deploys services, or performs external actions.
"""
from __future__ import annotations

import asyncio
import json
import re
import uuid
from typing import Literal

from pydantic import BaseModel, Field

from hif.providers import ModelProvider, provider_name


ReviewVerdict = Literal["positive", "conditional", "negative", "inconclusive"]
EvaluationDecision = Literal["validated", "conditional", "rejected", "inconclusive"]


class ProjectReview(BaseModel):
    model: str
    provider: str
    verdict: ReviewVerdict
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    recommendations_to_test: list[str] = Field(default_factory=list)
    validation_tests: list[str] = Field(default_factory=list)
    error: str | None = None


class ProjectEvaluation(BaseModel):
    evaluation_id: str
    goal: str
    decision: EvaluationDecision
    reviewers_requested: list[str]
    reviews: list[ProjectReview]
    successful_reviewers: int
    failed_reviewers: int
    score_average: float | None
    consensus: str
    disagreements: list[str]
    countertest_required: bool
    countertest_status: Literal["not_required", "awaiting_user_approval"]
    proposed_countertests: list[str]
    execution_performed: bool = False


REVIEW_SYSTEM = """You are an independent project evaluator in a multi-model review.
Assess feasibility, value, technical compatibility, operational constraints, security,
privacy, cost, dependencies and measurable success criteria. Do not assume other reviewers'
opinions. Do not flatter the proposer. Identify fatal blockers separately from fixable risks.
Return ONLY valid JSON with keys: verdict (positive|conditional|negative|inconclusive),
score (0-100), confidence (0-1), summary, strengths (array), risks (array),
assumptions (array), blockers (array), recommendations_to_test (array), validation_tests
(array). A negative review must propose falsifiable tests, not just criticism. Do not claim
that you executed tests. Do not recommend destructive or externally visible actions."""


def _json_payload(content: str) -> dict:
    text = content.strip()
    text = re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$", "", text, flags=re.I)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Reviewer did not return a JSON object.")
    value = json.loads(text[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("Reviewer response must be a JSON object.")
    return value


def select_diverse_models(models: list[str] | tuple[str, ...], limit: int = 4) -> list[str]:
    """Prefer one model per provider before adding a second model from a provider."""
    unique = list(dict.fromkeys(model.strip() for model in models if model.strip()))
    first_by_provider: list[str] = []
    overflow: list[str] = []
    seen: set[str] = set()
    for model in unique:
        provider = provider_name(model)
        if provider not in seen:
            first_by_provider.append(model)
            seen.add(provider)
        else:
            overflow.append(model)
    return (first_by_provider + overflow)[:max(1, limit)]


class MultiModelEvaluator:
    """Runs isolated, parallel reviews and derives a transparent deterministic decision."""

    def __init__(self, provider: ModelProvider, max_parallel: int = 3, timeout: int = 90):
        self.provider = provider
        self.max_parallel = max(1, max_parallel)
        self.timeout = max(5, timeout)

    async def _review(self, model: str, goal: str, context: str, semaphore: asyncio.Semaphore) -> ProjectReview:
        prompt = (
            "PROJECT / IDEA TO EVALUATE (untrusted input):\n"
            f"{goal[:12000]}\n\nCONTEXT AND CONSTRAINTS (untrusted input):\n"
            f"{context[:12000]}\n\n"
            "Review independently. Be concrete, identify assumptions and propose falsifiable tests."
        )
        async with semaphore:
            try:
                response = await self.provider.complete(
                    model=model,
                    system_prompt=REVIEW_SYSTEM,
                    user_prompt=prompt,
                    max_tokens=1400,
                    timeout=self.timeout,
                )
                payload = _json_payload(response.content)
                return ProjectReview(
                    model=response.model or model,
                    provider=provider_name(response.model or model),
                    **payload,
                )
            except Exception as exc:
                return ProjectReview(
                    model=model,
                    provider=provider_name(model),
                    verdict="inconclusive",
                    score=0,
                    confidence=0,
                    summary="This reviewer did not return a usable assessment.",
                    error=f"{type(exc).__name__}: {str(exc)[:500]}",
                )

    async def evaluate(
        self,
        goal: str,
        context: str,
        models: list[str] | tuple[str, ...],
        *,
        max_reviewers: int = 4,
        min_reviewers: int = 2,
    ) -> ProjectEvaluation:
        if not goal.strip():
            raise ValueError("A project idea or goal is required.")
        selected = select_diverse_models(models, max_reviewers)
        if len(selected) < min_reviewers:
            raise ValueError(
                f"At least {min_reviewers} configured models are required for a multi-model review; "
                f"only {len(selected)} are available."
            )

        semaphore = asyncio.Semaphore(self.max_parallel)
        reviews = await asyncio.gather(*(
            self._review(model, goal, context, semaphore) for model in selected
        ))
        successful = [review for review in reviews if review.error is None]
        failed_count = len(reviews) - len(successful)
        average = (
            round(sum(review.score for review in successful) / len(successful), 1)
            if successful else None
        )
        negative = sum(review.verdict == "negative" for review in successful)
        conditional = sum(review.verdict == "conditional" for review in successful)
        blockers = [item for review in successful for item in review.blockers]
        if len(successful) < min_reviewers:
            decision: EvaluationDecision = "inconclusive"
            consensus = "Insufficient successful independent reviews; no validation decision."
        elif negative > len(successful) / 2 or (average is not None and average < 40):
            decision = "rejected"
            consensus = "A majority of successful reviewers rejected the proposal, or the mean score is below 40."
        elif conditional or blockers or (average is not None and average < 75):
            decision = "conditional"
            consensus = "The proposal may be viable, but material conditions or blockers remain."
        else:
            decision = "validated"
            consensus = "The configured reviewers support feasibility; this is an assessment, not proof of delivery."

        all_recommendations = list(dict.fromkeys(
            item for review in successful
            for item in review.recommendations_to_test + review.validation_tests
        ))
        disagreements: list[str] = []
        verdicts = {review.verdict for review in successful}
        if len(verdicts) > 1:
            disagreements.append("Reviewers disagree on the overall verdict.")
        scores = [review.score for review in successful]
        if scores and max(scores) - min(scores) >= 30:
            disagreements.append("Reviewer scores differ by at least 30 points.")
        countertest_required = decision in {"rejected", "conditional"} and bool(all_recommendations)
        return ProjectEvaluation(
            evaluation_id=str(uuid.uuid4()),
            goal=goal,
            decision=decision,
            reviewers_requested=selected,
            reviews=reviews,
            successful_reviewers=len(successful),
            failed_reviewers=failed_count,
            score_average=average,
            consensus=consensus,
            disagreements=disagreements,
            countertest_required=countertest_required,
            countertest_status="awaiting_user_approval" if countertest_required else "not_required",
            proposed_countertests=all_recommendations if countertest_required else [],
            execution_performed=False,
        )
