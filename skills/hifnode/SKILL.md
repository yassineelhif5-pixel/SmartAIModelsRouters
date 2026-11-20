---
name: hifnode
description: Run a complex request as parallel specialist nodes sharing one HIF session ID and approved session memory. Use for multi-workstream tasks with independent subtasks and dependencies.
---

# HIF Node Orchestration

When invoked as /hifnode:

1. Submit one overall goal to HIF and create one shared HIF session ID.
2. Decompose the work into bounded specialist nodes (for example architect, researcher, implementer, tester, reviewer and technical writer).
3. Give each node a role definition, task contract, dependencies, model capabilities, token/cost budget and acceptance criteria.
4. Execute independent nodes concurrently; wait for dependencies before downstream nodes start.
5. Ensure all nodes read/write through the same HIF session memory. Store role definitions, approved project facts, summaries, node outputs and artifact references with provenance.
6. Retrieve only relevant memory and dependency outputs for each node. Never broadcast the entire conversation to every model.
7. Adapt concurrency to CPU/RAM pressure, local-model GPU/VRAM constraints and provider concurrency/rate limits.
8. Use isolated worktrees or serialized execution for conflicting file-writing tasks.
9. Switch to an eligible provider before a configured 80% usage threshold only when provider-reported or HIF-measured usage is available; distinguish estimates clearly.
10. Verify task outputs, consolidate the results and report node status, provider/model, duration, token usage and fallback decisions.

Shared memory is explicit HIF application data. It is not provider-native hidden context, private reasoning or an internal cache. Never claim that a native session has been migrated between providers.
