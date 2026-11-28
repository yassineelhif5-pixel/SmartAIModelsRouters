"""Reproducible benchmark: HIF orchestration against a single model.

Each task in ``bench/tasks.jsonl`` carries deterministic checks (no LLM judge), so two
runs on the same models give comparable numbers. For every task the runner calls the
baseline model once, then runs the same prompt through HIF, and records pass/fail,
tokens, reported cost and wall-clock time for both.

Code tasks execute model-written Python only when ``allow_code_exec`` is true, in a
separate isolated interpreter with a timeout; otherwise they are reported as skipped.
"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from hif.providers import ModelProvider

BASELINE_SYSTEM = "You are a precise assistant. Follow the requested output format exactly."


@dataclass
class Attempt:
    passed: bool | None          # None = skipped (code execution disabled)
    reasons: list[str]
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float | None = None
    elapsed_ms: int = 0
    calls: int = 1
    error: str | None = None


@dataclass
class TaskResult:
    id: str
    domain: str
    baseline: Attempt
    hif: Attempt


@dataclass
class BenchReport:
    baseline_model: str
    hif_models: list[str]
    started_at: str
    results: list[TaskResult] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        def agg(pick: Callable[[TaskResult], Attempt]) -> dict[str, Any]:
            attempts = [pick(result) for result in self.results]
            graded = [a for a in attempts if a.passed is not None]
            costs = [a.cost_usd for a in attempts if a.cost_usd is not None]
            return {
                "graded": len(graded),
                "passed": sum(1 for a in graded if a.passed),
                "pass_rate": round(sum(1 for a in graded if a.passed) / len(graded), 3)
                if graded else None,
                "input_tokens": sum(a.input_tokens for a in attempts),
                "output_tokens": sum(a.output_tokens for a in attempts),
                "cost_usd": round(sum(costs), 6) if costs else None,
                "elapsed_ms": sum(a.elapsed_ms for a in attempts),
                "errors": sum(1 for a in attempts if a.error),
            }

        return {"baseline": agg(lambda r: r.baseline), "hif": agg(lambda r: r.hif)}

    def to_json(self) -> str:
        return json.dumps({**asdict(self), "summary": self.summary()}, indent=2,
                          ensure_ascii=False)

    def to_markdown(self) -> str:
        s = self.summary()
        b, h = s["baseline"], s["hif"]

        def pct(v):
            return "n/a" if v is None else f"{v * 100:.0f} %"

        def cost(v):
            return "not reported" if v is None else f"${v:.4f}"

        lines = [
            "# HIF benchmark",
            "",
            f"Run started {self.started_at}. Baseline model: `{self.baseline_model}`. "
            f"HIF model pool: {', '.join(f'`{m}`' for m in self.hif_models)}.",
            "",
            "| Measure | Single model | HIF |",
            "| --- | --- | --- |",
            f"| Tasks passed | {b['passed']}/{b['graded']} ({pct(b['pass_rate'])}) | "
            f"{h['passed']}/{h['graded']} ({pct(h['pass_rate'])}) |",
            f"| Input tokens | {b['input_tokens']:,} | {h['input_tokens']:,} |",
            f"| Output tokens | {b['output_tokens']:,} | {h['output_tokens']:,} |",
            f"| Reported cost | {cost(b['cost_usd'])} | {cost(h['cost_usd'])} |",
            f"| Total time | {b['elapsed_ms'] / 1000:.1f} s | {h['elapsed_ms'] / 1000:.1f} s |",
            f"| Errors | {b['errors']} | {h['errors']} |",
            "",
            "| Task | Domain | Single model | HIF |",
            "| --- | --- | --- | --- |",
        ]
        mark = {True: "pass", False: "fail", None: "skipped"}
        for r in self.results:
            lines.append(f"| {r.id} | {r.domain} | {mark[r.baseline.passed]} | {mark[r.hif.passed]} |")
        lines += ["", "Checks are deterministic (no model judge). Costs appear only when the "
                  "provider adapter reports them."]
        return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- grading

_CODE_BLOCK = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)


def _extract_json(text: str) -> Any:
    for opener, closer in (("{", "}"), ("[", "]")):
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except ValueError:
                continue
    return None


def _run_python_tests(text: str, tests: list[str], timeout: int = 10) -> tuple[bool, str]:
    match = _CODE_BLOCK.search(text)
    code = match.group(1) if match else text
    program = code + "\n\n" + "\n".join(tests) + "\nprint('HIF_BENCH_OK')\n"
    with tempfile.TemporaryDirectory() as workdir:
        path = Path(workdir) / "candidate.py"
        path.write_text(program, encoding="utf-8")
        try:
            done = subprocess.run([sys.executable, "-I", str(path)], cwd=workdir,
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "code timed out"
    if "HIF_BENCH_OK" in done.stdout:
        return True, "tests passed"
    return False, (done.stderr.strip().splitlines() or ["tests failed"])[-1][:200]


def grade(text: str, check: dict[str, Any], allow_code_exec: bool = False) -> tuple[bool | None, list[str]]:
    reasons: list[str] = []
    ok = True
    flags = re.I if check.get("case_insensitive") else 0
    haystack = text.lower() if check.get("case_insensitive") else text

    def need(cond: bool, reason: str) -> None:
        nonlocal ok
        if not cond:
            ok = False
            reasons.append(reason)

    for word in check.get("contains_all", []):
        w = word.lower() if flags else word
        need(w in haystack or w in haystack.replace(",", ""), f"missing '{word}'")
    if check.get("contains_any"):
        options = check["contains_any"]
        need(any((o.lower() if flags else o) in haystack for o in options),
             f"none of {options}")
    if "regex" in check:
        need(re.search(check["regex"], text, re.I | re.S | re.M) is not None, "format not matched")
    if "json_keys" in check:
        data = _extract_json(text)
        need(isinstance(data, dict) and all(k in data for k in check["json_keys"]),
             f"JSON keys {check['json_keys']} not found")
    if "max_words" in check:
        need(len(text.split()) <= check["max_words"], f"more than {check['max_words']} words")
    if "sentences" in check:
        count = len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()])
        need(count == check["sentences"], f"{count} sentences instead of {check['sentences']}")
    bullets = len(re.findall(r"^\s*[-*•]\s+\S", text, re.M))
    numbered = len(re.findall(r"^\s*\d+[.)]\s+\S", text, re.M))
    if "bullet_count" in check:
        need(bullets == check["bullet_count"], f"{bullets} bullets instead of {check['bullet_count']}")
    if "bullet_count_min" in check:
        need(bullets + numbered >= check["bullet_count_min"],
             f"fewer than {check['bullet_count_min']} items")
    if check.get("min_numbered_steps"):
        need(numbered >= check["min_numbered_steps"],
             f"fewer than {check['min_numbered_steps']} numbered steps")
    if "python_tests" in check:
        if not allow_code_exec:
            return None, ["code execution disabled (use --allow-code-exec)"]
        passed, why = _run_python_tests(text, check["python_tests"])
        need(passed, why)
    return ok, reasons


# --------------------------------------------------------------------------- running

def load_tasks(path: str | Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


async def run_benchmark(
    tasks: list[dict[str, Any]],
    baseline_model: str,
    provider: ModelProvider,
    engine_factory: Callable[[], Any],
    *,
    allow_code_exec: bool = False,
    max_tokens: int = 1800,
    timeout: int = 120,
    hif_models: list[str] | None = None,
) -> BenchReport:
    report = BenchReport(baseline_model=baseline_model, hif_models=hif_models or [],
                         started_at=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
    for task in tasks:
        # Single model
        started = time.perf_counter()
        try:
            response = await provider.complete(model=baseline_model, system_prompt=BASELINE_SYSTEM,
                                               user_prompt=task["prompt"], max_tokens=max_tokens,
                                               timeout=timeout)
            passed, reasons = grade(response.content, task["check"], allow_code_exec)
            baseline = Attempt(passed, reasons, response.input_tokens, response.output_tokens,
                               response.cost_usd)
        except Exception as exc:  # noqa: BLE001 - a failed call is a failed task
            baseline = Attempt(False, ["call failed"], error=f"{type(exc).__name__}: {exc}"[:300])
        baseline.elapsed_ms = int((time.perf_counter() - started) * 1000)

        # HIF orchestration
        engine = engine_factory()
        started = time.perf_counter()
        try:
            result = await engine.run(task["prompt"], session_id=f"bench-{task['id']}-{int(time.time())}")
            passed, reasons = grade(result.synthesis, task["check"], allow_code_exec)
            usage_rows = engine.store.session_usage(result.session_id) \
                if hasattr(engine.store, "session_usage") else []
            costs = [row["cost_usd"] for row in usage_rows if row.get("cost_usd") is not None]
            hif = Attempt(passed, reasons, result.total_input_tokens, result.total_output_tokens,
                          round(sum(costs), 6) if costs else None,
                          calls=len(result.nodes) + 2)
        except Exception as exc:  # noqa: BLE001
            hif = Attempt(False, ["run failed"], error=f"{type(exc).__name__}: {exc}"[:300])
        finally:
            close = getattr(engine, "close", None)
            if close:
                close()
        hif.elapsed_ms = int((time.perf_counter() - started) * 1000)
        report.results.append(TaskResult(task["id"], task["domain"], baseline, hif))
    return report


def write_report(report: BenchReport, out_dir: str | Path) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path, md_path = out / "results.json", out / "report.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    md_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, md_path


def main_sync(**kwargs: Any) -> BenchReport:
    return asyncio.run(run_benchmark(**kwargs))
