# CPU, RAM and parallel resource management

## Goal

HIF maximizes throughput without overwhelming the user's workstation, local inference runtime, provider rate limits or memory. Use adaptive concurrency, not unlimited fan-out.

## Telemetry

The platform adapter may monitor logical CPU count, CPU utilization, available RAM, memory pressure, optional GPU/VRAM usage, queue depth, provider-specific inflight requests, average latency and rate-limit signals.

Local CPU/RAM measurements do not reveal remote provider capacity. Remote API calls are often network-bound; local model inference and file processing are hardware-bound.

## Effective concurrency

The scheduler uses the minimum of:
1. global HIF concurrency;
2. per-provider concurrency ceiling;
3. adaptive local resource ceiling;
4. number of ready DAG nodes.

Use separate pools for remote API requests and local inference. Apply provider pacing and backoff after rate limits. Increase concurrency gradually after sustained healthy operation. Use sampling windows and hysteresis to avoid oscillation.

## Suggested initial defaults

These are starting values, not performance guarantees:
- remote request concurrency: 4;
- local inference concurrency: 1;
- CPU pressure threshold: 85%;
- memory pressure threshold: 88%;
- reserve at least 1.5 GB of free RAM for the host;
- provider-specific concurrency caps must be configurable.

Benchmark on each target machine and provider account. Too much parallelism can increase throttling and costs rather than reduce elapsed time.

## Process priority and CPU affinity

Do not change Windows process priority or processor affinity by default. HIF runs as a normal user process. Optional tuning must be opt-in, reversible and documented. Never elevate privileges or starve the operating system, endpoint protection or other applications.

## Run telemetry

Report active/waiting/completed/failed/cancelled nodes, configured/effective concurrency, sampled CPU/RAM, provider inflight calls, retry counts, queue wait, task duration and wall-clock duration. Never claim GPU telemetry unless the local runtime or supported monitor provides it.
