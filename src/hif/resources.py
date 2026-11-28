"""Non-blocking resource telemetry and conservative adaptive concurrency."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSnapshot:
    cpu_percent: float | None
    memory_percent: float | None
    available_memory_mb: int | None
    logical_cpus: int


class ResourceMonitor:
    """Best-effort telemetry. Missing psutil never prevents HIF from running."""

    def __init__(self) -> None:
        self._primed = False

    def snapshot(self) -> ResourceSnapshot:
        logical_cpus = max(1, os.cpu_count() or 1)
        try:
            import psutil
        except ImportError:
            return ResourceSnapshot(None, None, None, logical_cpus)
        try:
            # interval=None is non-blocking. Prime once so later samples represent
            # the interval since the previous call instead of sleeping in the caller.
            cpu = float(psutil.cpu_percent(interval=None))
            was_primed = self._primed
            self._primed = True
            memory = psutil.virtual_memory()
            return ResourceSnapshot(
                cpu_percent=cpu if was_primed else None,
                memory_percent=float(memory.percent),
                available_memory_mb=int(memory.available / (1024 * 1024)),
                logical_cpus=logical_cpus,
            )
        except Exception:
            return ResourceSnapshot(None, None, None, logical_cpus)


def recommended_parallelism() -> int:
    """Choose a conservative default from CPU and available RAM, capped at eight."""
    logical_cpus = max(1, os.cpu_count() or 1)
    cpu_limit = 1 if logical_cpus == 1 else max(2, logical_cpus // 2)
    cpu_limit = min(8, cpu_limit)
    try:
        import psutil
        available_mb = int(psutil.virtual_memory().available / (1024 * 1024))
        memory_limit = max(1, available_mb // 1024)
        return max(1, min(cpu_limit, memory_limit))
    except Exception:
        return max(1, min(cpu_limit, 4))


class AdaptiveConcurrency:
    """Bounded scheduler cap; never changes OS priority or CPU affinity."""

    def __init__(
        self,
        max_parallel: int,
        cpu_threshold: float = 85.0,
        memory_threshold: float = 88.0,
        min_free_memory_mb: int = 1536,
        memory_per_task_mb: int = 512,
    ):
        self.max_parallel = max(1, max_parallel)
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.min_free_memory_mb = min_free_memory_mb
        self.memory_per_task_mb = max(128, memory_per_task_mb)
        self.monitor = ResourceMonitor()

    def effective_limit(self) -> tuple[int, ResourceSnapshot]:
        snapshot = self.monitor.snapshot()
        limit = min(self.max_parallel, max(1, snapshot.logical_cpus))
        if snapshot.cpu_percent is not None and snapshot.cpu_percent >= self.cpu_threshold:
            limit = max(1, limit // 2)
        if snapshot.memory_percent is not None and snapshot.memory_percent >= self.memory_threshold:
            limit = 1
        if snapshot.available_memory_mb is not None:
            free_after_reserve = snapshot.available_memory_mb - self.min_free_memory_mb
            memory_slots = max(1, free_after_reserve // self.memory_per_task_mb)
            limit = min(limit, memory_slots)
            if snapshot.available_memory_mb < self.min_free_memory_mb:
                limit = 1
        return max(1, limit), snapshot
