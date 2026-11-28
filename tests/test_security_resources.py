from __future__ import annotations

from hif.resources import AdaptiveConcurrency, ResourceSnapshot, recommended_parallelism
from hif.security import scan_project


def test_security_scan_finds_vibe_coding_risks_without_opening_env(tmp_path) -> None:
    (tmp_path / ".env").write_text("OPENAI_API_KEY=do-not-read-this-value", encoding="utf-8")
    (tmp_path / "app.py").write_text(
        "import subprocess\n"
        "result = eval(user_input)\n"
        "subprocess.run(command, shell=True)\n"
        "requests.get(url, verify=False)\n",
        encoding="utf-8",
    )
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.py").write_text("eval(x)", encoding="utf-8")

    report = scan_project(tmp_path)
    data = report.to_dict()

    rule_ids = {finding.rule_id for finding in report.findings}
    assert {"SEC003", "SEC004", "SEC007", "SEC011"}.issubset(rule_ids)
    assert "do-not-read-this-value" not in str(data)
    assert report.scanned_files == 1
    assert data["action_plan"]
    assert data["risk"] == "high"


def test_security_scan_is_read_only_and_reports_clean_baseline(tmp_path) -> None:
    (tmp_path / "safe.py").write_text("print('hello')\n", encoding="utf-8")
    report = scan_project(tmp_path)

    assert report.scanned_files == 1
    assert report.findings == ()
    assert report.to_dict()["risk"] == "no_findings"
    assert report.to_dict()["action_plan"][0]["priority"] == "baseline"


def test_adaptive_concurrency_respects_memory_per_task(tmp_path) -> None:
    scheduler = AdaptiveConcurrency(
        8, cpu_threshold=99, memory_threshold=99,
        min_free_memory_mb=1024, memory_per_task_mb=1024,
    )
    scheduler.monitor.snapshot = lambda: ResourceSnapshot(10, 30, 4096, 8)
    limit, _ = scheduler.effective_limit()

    assert limit == 3


def test_adaptive_concurrency_never_returns_zero() -> None:
    scheduler = AdaptiveConcurrency(8, min_free_memory_mb=4096)
    scheduler.monitor.snapshot = lambda: ResourceSnapshot(99, 99, 128, 8)
    limit, _ = scheduler.effective_limit()

    assert limit == 1


def test_recommended_parallelism_is_bounded() -> None:
    assert 1 <= recommended_parallelism() <= 8


def test_resource_monitor_uses_non_blocking_cpu_sampling(monkeypatch) -> None:
    import psutil
    from hif.resources import ResourceMonitor

    calls = []
    monkeypatch.setattr(psutil, "cpu_percent", lambda interval=None: calls.append(interval) or 23.0)
    monitor = ResourceMonitor()

    first = monitor.snapshot()
    second = monitor.snapshot()

    assert calls == [None, None]
    assert first.cpu_percent is None
    assert second.cpu_percent == 23.0


def test_local_io_pool_uses_bounded_worker_thread() -> None:
    import asyncio
    import threading
    from hif.resources import LocalExecutionPool

    pool = LocalExecutionPool(max_threads=1, max_processes=1)
    try:
        result = asyncio.run(pool.run_io(lambda: threading.current_thread().name))
    finally:
        pool.close()

    assert result.startswith("hif-io")


def test_adaptive_concurrency_recovers_gradually_after_pressure() -> None:
    scheduler = AdaptiveConcurrency(8, cpu_threshold=85, memory_threshold=88)
    samples = iter([
        ResourceSnapshot(96, 40, 8192, 8),
        ResourceSnapshot(20, 40, 8192, 8),
        ResourceSnapshot(20, 40, 8192, 8),
        ResourceSnapshot(20, 40, 8192, 8),
    ])
    scheduler.monitor.snapshot = lambda: next(samples)

    assert scheduler.effective_limit()[0] == 4
    assert scheduler.effective_limit()[0] == 4
    assert scheduler.effective_limit()[0] == 4
    assert scheduler.effective_limit()[0] == 5


def test_security_scan_redacts_inline_private_key_material(tmp_path) -> None:
    secret = "-----BEGIN PRIVATE KEY-----VERY_SECRET_PRIVATE_KEY_PAYLOAD"
    (tmp_path / "settings.py").write_text(f'PRIVATE_KEY = "{secret}"\\n', encoding="utf-8")

    report = scan_project(tmp_path)

    assert any(item.rule_id == "SEC001" for item in report.findings)
    assert secret not in str(report.to_dict())
    assert "line contents redacted" in str(report.to_dict())
