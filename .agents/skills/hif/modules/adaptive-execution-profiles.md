# HIF module: adaptive execution profiles

Choose the lightest execution strategy compatible with the host and task. Profile selection is per run; it must not silently change the user's global settings.

| Profile | Use case | Strategy |
|---|---|---|
| `browser` | Browser-only assistant, fragile tab/session, short context, unreliable connection | Sequential calls, compact prompts, one model request at a time, checkpoint after each stage, no local worker assumptions |
| `small` | Low-RAM laptop or small workstation | One active task, one provider call at a time, small context/output, local CPU work disabled or minimal |
| `standard` | Normal developer workstation | Resource-aware concurrency, bounded context and provider semaphores |
| `server` | Dedicated worker with measured capacity | Higher bounded concurrency, explicit CPU/RAM quotas and monitoring |
| `auto` | Unknown environment | Detect CPU/RAM when available; conservative defaults; no assumptions about GPU or browser internals |

Connected runtime supports `HIF_EXECUTION_PROFILE=auto|browser|small|standard|server`. Explicit `HIF_*` settings override profile defaults. Browser-only Skill mode is an instruction-level strategy: it cannot inspect browser RAM, change browser limits, keep a tab alive, or guarantee a network session.

## Degradation ladder
1. Remove optional agents and redundant research.
2. Reduce reviewer count to the minimum of two distinct providers for a cross-provider decision.
3. Run reviewers sequentially instead of concurrently.
4. Reduce context to a short brief and cite source paths/URLs rather than copying large files.
5. Reduce output tokens and save checkpoints between stages.
6. If the browser or connection fails, preserve the last completed result and resume only missing work.
7. If two providers cannot be reached, return `inconclusive`; do not downgrade it silently to a multi-model approval.

Never promise hard RAM/CPU limits from cooperative scheduling alone. Use OS/container limits for isolation, and do not spawn local workers in a browser-only host.
