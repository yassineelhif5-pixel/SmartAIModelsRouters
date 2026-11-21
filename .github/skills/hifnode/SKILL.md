---
name: hifnode
description: Execute complex requests as parallel specialist nodes through HIF with one shared session ID, role registry and approved memory.
---

# HIF Node Orchestration
1. Build a concise context brief with the goal, constraints and acceptance criteria.
2. Call the MCP tool hifnode_run. Do not simulate execution in the host conversation.
3. HIF creates a dependency-aware graph of specialist nodes: architect, researcher, implementer, tester, reviewer or writer.
4. Independent nodes run concurrently; dependencies wait for their prerequisite outputs.
5. All nodes share one HIF session ID, SQLite session memory, role registry and artifact references.
6. Each node receives only the relevant role definition, selected memory and dependency results.
7. Concurrency is bounded using configured limits, provider concurrency and CPU/RAM telemetry.
8. New tasks prefer another eligible model at the configured 80% HIF-measured usage threshold. Unreported provider quotas remain unknown.
9. Report node status, role, selected model, elapsed time, token usage, fallback and final synthesis.
10. If hifnode_run is unavailable, explain that the HIF runtime/MCP service is not connected.

Current MVP is text-only; it does not edit files, run shell commands, browse or deploy. Do not claim provider-native sessions or hidden reasoning are transferred.
