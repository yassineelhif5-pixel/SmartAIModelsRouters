"""Benchmark harness: graders and an end-to-end run with mock models."""

from __future__ import annotations

import asyncio
from pathlib import Path

from hif.bench import grade, load_tasks, run_benchmark, write_report
from hif.config import Settings
from hif.engine import HIFEngine
from hif.providers import MockProvider, ModelResponse
from hif.storage import HIFStore

TASKS = Path(__file__).resolve().parents[1] / "bench" / "tasks.jsonl"


def test_task_file_has_thirty_tasks_with_checks():
    tasks = load_tasks(TASKS)
    assert len(tasks) == 30
    assert len({t["id"] for t in tasks}) == 30
    assert all(t["check"] for t in tasks)


def test_graders():
    assert grade('{"invoice_number": "INV-2026-0418", "total": 1284.5, "currency": "EUR"}',
                 {"json_keys": ["invoice_number", "total", "currency"],
                  "contains_all": ["INV-2026-0418", "1284.5"]})[0]
    assert grade("503 /api/v2/orders/77", {"regex": r"^\s*503\s+/api/v2/orders/77\s*$"})[0]
    assert not grade("one two three four five six seven eight nine", {"max_words": 8})[0]
    assert grade("- a\n- b\n- c", {"bullet_count": 3})[0]
    assert grade("Use httponly, secure and samesite.",
                 {"contains_all": ["HttpOnly", "Secure", "SameSite"], "case_insensitive": True})[0]
    assert grade("x", {"python_tests": ["assert True"]})[0] is None  # exec disabled


def test_python_tests_run_isolated_when_allowed():
    good = "```python\ndef double(x):\n    return 2 * x\n```"
    bad = "```python\ndef double(x):\n    return x\n```"
    check = {"python_tests": ["assert double(4) == 8"]}
    assert grade(good, check, allow_code_exec=True)[0] is True
    assert grade(bad, check, allow_code_exec=True)[0] is False


class EchoProvider(MockProvider):
    async def complete(self, **kwargs) -> ModelResponse:
        response = await super().complete(**kwargs)
        return ModelResponse(model=response.model, content=response.content,
                             input_tokens=response.input_tokens,
                             output_tokens=response.output_tokens, cost_usd=0.001)


def test_end_to_end_run_with_mock_models(tmp_path):
    settings = Settings(database_path=tmp_path / "bench.sqlite3", model_pool=("mock/model",),
                        resource_aware_scheduling=False)
    provider = EchoProvider()
    report = asyncio.run(run_benchmark(
        load_tasks(TASKS)[:3], "mock/baseline", provider,
        lambda: HIFEngine(settings=settings, provider=provider,
                          store=HIFStore(settings.database_path)),
        hif_models=["mock/model"],
    ))
    assert len(report.results) == 3
    summary = report.summary()
    assert summary["baseline"]["input_tokens"] > 0 and summary["hif"]["input_tokens"] > 0
    assert summary["hif"]["cost_usd"] is not None
    json_path, md_path = write_report(report, tmp_path / "out")
    assert "Single model" in md_path.read_text() and json_path.exists()
