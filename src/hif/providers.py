"""Provider abstractions and concrete model adapters."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelResponse:
    model: str
    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    cost_usd: float | None = None


class ProviderError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool = False,
                 retry_after: float | None = None, status_code: int | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.retry_after = retry_after
        self.status_code = status_code


class ModelProvider(Protocol):
    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse: ...


class LiteLLMProvider:
    """Calls providers supported by LiteLLM using user-provided API credentials."""

    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse:
        try:
            from litellm import acompletion
        except ImportError as exc:
            raise RuntimeError("Install HIF provider dependencies to use real models.") from exc

        started = time.perf_counter()
        try:
            response = await acompletion(
                model=model,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt}],
                max_tokens=max_tokens,
                timeout=timeout,
            )
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            retry_after = getattr(exc, "retry_after", None)
            name, message = type(exc).__name__.lower(), str(exc).lower()
            markers = ("ratelimit", "rate limit", "quota", "timeout", "overloaded",
                       "service unavailable", "connection error", "internal server error",
                       "temporarily unavailable", "capacity")
            retryable = status in {408, 409, 425, 429, 500, 502, 503, 504} or any(
                marker in name or marker in message for marker in markers
            )
            raise ProviderError(str(exc), retryable=retryable,
                                retry_after=retry_after, status_code=status) from exc

        elapsed = int((time.perf_counter() - started) * 1000)
        choice = response.choices[0]
        content = getattr(choice.message, "content", "") or ""
        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        hidden_params = getattr(response, "_hidden_params", None) or {}
        cost = hidden_params.get("response_cost")
        return ModelResponse(
            model=model, content=str(content), input_tokens=input_tokens,
            output_tokens=output_tokens, duration_ms=elapsed,
            cost_usd=float(cost) if cost is not None else None,
        )


class MockProvider:
    """Deterministic test provider; no network or paid credentials required."""

    async def complete(self, *, model: str, system_prompt: str, user_prompt: str,
                       max_tokens: int, timeout: int) -> ModelResponse:
        await asyncio.sleep(0)
        started = time.perf_counter()
        if "RETURN ONLY VALID JSON" in system_prompt.upper():
            import json
            goal = user_prompt.split("USER GOAL:", 1)[-1].split("PROJECT CONTEXT", 1)[0].strip()
            content = json.dumps({
                "goal": goal,
                "nodes": [{
                    "id": "main", "title": "Complete requested task", "role": "generalist",
                    "instructions": goal or "Complete the requested task.",
                    "task_type": "general", "depends_on": [],
                    "acceptance_criteria": ["Provide a useful deliverable."],
                    "context_keys": ["goal"], "max_output_tokens": min(max_tokens, 512),
                }],
                "final_instructions": "Return the completed task result.",
            }, ensure_ascii=False)
        elif "SYNTHESIZER" in system_prompt.upper():
            content = "HIF mock synthesis completed. Review the node outputs for the task result."
        else:
            content = f"Mock result from {model}; received {len(user_prompt)} characters."
        return ModelResponse(
            model=model, content=content, input_tokens=max(1, len(user_prompt) // 4),
            output_tokens=max(1, len(content) // 4),
            duration_ms=int((time.perf_counter() - started) * 1000),
        )


def provider_name(model: str) -> str:
    return model.split("/", 1)[0].lower() if "/" in model else "default"
