"""Cross-platform resource telemetry and bounded concurrency decisions."""

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
    def snapshot(self) -> ResourceSnapshot:
        logical_cpus = max(1, os.cpu_count() or 1)
        try:
            import psutil
        except ImportError:
            return ResourceSnapshot(None, None, None, logical_cpus)
        try:
            memory = psutil.virtual_memory()
            return ResourceSnapshot(
                cpu_percent=float(psutil.cpu_percent(interval=0.05)),
                memory_percent=float(memory.percent),
                available_memory_mb=int(memory.available / (1024 * 1024)),
                logical_cpus=logical_cpus,
            )
        except Exception:
            return ResourceSnapshot(None, None, None, logical_cpus)


class AdaptiveConcurrency:
    """Conservative resource-aware cap; never changes OS process priority or affinity."""

    def __init__(self, max_parallel: int, cpu_threshold: float = 85.0,
                 memory_threshold: float = 88.0, min_free_memory_mb: int = 1536):
        self.max_parallel = max(1, max_parallel)
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.min_free_memory_mb = min_free_memory_mb
        self.monitor = ResourceMonitor()

    def effective_limit(self) -> tuple[int, ResourceSnapshot]:
        snapshot = self.monitor.snapshot()
        limit = min(self.max_parallel, max(1, snapshot.logical_cpus))
        if snapshot.cpu_percent is not None and snapshot.cpu_percent >= self.cpu_threshold:
            limit = max(1, limit // 2)
        if snapshot.memory_percent is not None and snapshot.memory_percent >= self.memory_threshold:
            limit = 1
        if snapshot.available_memory_mb is not None and snapshot.available_memory_mb < self.min_free_memory_mb:
            limit = 1
        return max(1, limit), snapshot
