---
name: hifnode
description: Run complex work as parallel specialist nodes through HIF, using one shared session ID, role registry and approved session memory.
---

# HIF Node Orchestration

When the user invokes /hifnode or requests parallel specialist execution:

1. Create a concise context brief with the goal, constraints, relevant evidence and acceptance criteria.
2. Call the MCP tool hifnode_run. Do not simulate node execution in the host conversation.
3. HIF creates a dependency-aware graph of specialist nodes such as architect, researcher, implementer, tester, reviewer and writer.
4. Independent nodes execute concurrently; dependent nodes wait for prerequisite results.
5. Every node in the run uses the same HIF session ID and shared SQLite session memory. Role definitions, approved project facts, summaries and node outputs are persisted with provenance.
6. Each node receives only the role definition, relevant memory references and dependency outputs it needs. Do not broadcast the full transcript to every model.
7. HIF bounds concurrency using configured limits, provider concurrency and CPU/RAM telemetry.
8. HIF prefers a different eligible model when HIF-measured usage reaches the configured 80% token budget. Provider subscription quotas are not invented or inferred.
9. Report the returned session ID, node statuses, roles, selected models, elapsed time, token use, fallbacks and final synthesis.
10. If hifnode_run is unavailable, state that the HIF MCP service is not installed or connected. Never claim that parallel work occurred.

The current MVP dispatches text-only tasks. It does not edit files, execute shell commands, browse, deploy or migrate provider-native conversation state. File-writing nodes and isolated worktree execution are later capabilities. Do not request or transfer hidden chain-of-thought.
