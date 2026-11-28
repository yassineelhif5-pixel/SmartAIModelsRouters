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


## Host auto-sizing and local worker isolation

HIF reads the logical CPU count and available physical memory at startup. Unless HIF_MAX_PARALLEL_TASKS is explicitly set, the initial global task cap is derived conservatively from those measurements and capped at eight. The adaptive scheduler then samples CPU and memory without sleeping in the asyncio event loop and reduces concurrency when pressure or the free-memory reserve is reached.

The scheduler also applies an estimated memory allowance per active task. This is a safety heuristic, not a hard operating-system memory limit. A task with unexpectedly high memory use can still exceed its estimate.

### Separate execution lanes

- **Remote model/API calls:** async I/O, with a per-provider semaphore and request timeout. Do not occupy local worker threads while waiting for remote responses.
- **Local blocking I/O:** a lazily created ThreadPoolExecutor with HIF_MAX_LOCAL_THREADS workers. File scans and blocking file helpers can use this pool instead of blocking the event loop.
- **Local CPU-heavy helpers:** a lazily created ProcessPoolExecutor with HIF_MAX_LOCAL_PROCESSES workers. CPU work must be picklable and explicitly submitted; do not send arbitrary project code to this pool.
- **Skills:** instructions-only installation does not start a runtime, create threads, install background services or consume CPU continuously.

Worker pools are created only on first use. Their defaults are two I/O threads and one CPU process. Override with HIF_MAX_LOCAL_THREADS, HIF_MAX_LOCAL_PROCESSES and HIF_LOCAL_TASK_MEMORY_MB. The local process pool is for bounded trusted helper functions, not an execution sandbox.

### Server and workstation profiles

| Environment | Suggested policy |
|---|---|
| Small workstation / laptop | Leave auto sizing enabled; keep local CPU workers at 1 |
| Developer workstation | Auto global concurrency; 2 I/O threads; 1 CPU process |
| Shared application server | Set an explicit conservative HIF_MAX_PARALLEL_TASKS after load testing; use per-provider limits |
| Dedicated worker server | Increase caps gradually after CPU/RAM, provider throttling and latency benchmarks |

For shared servers, consider running HIF under a dedicated low-privilege OS account and enforce service/container CPU and memory limits externally (systemd slices, cgroups, Windows Job Objects or container limits). HIF's in-process scheduler is cooperative and cannot guarantee hard resource isolation against an untrusted or runaway native process.

### Responsiveness guarantees and limitations

HIF avoids blocking its async event loop for CPU sampling and provides bounded worker pools. This reduces contention; it does not guarantee that the host can never become overloaded. Keep the service under OS-level limits, monitor it, and test under representative load. Do not raise process priority or change CPU affinity by default.
