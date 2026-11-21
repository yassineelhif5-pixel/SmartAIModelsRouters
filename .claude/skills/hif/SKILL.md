---
name: hif
description: Use the HIF multi-provider orchestrator for substantial tasks, cost-aware model routing, specialist delegation, shared session memory, or consolidated results.
---

# HIF — Hybrid Intelligent Flow

HIF is a task orchestrator. It is not a silent replacement for the host assistant's native model or conversation.

## Invocation

When the user invokes /hif or explicitly asks to orchestrate a substantial task:

1. Identify the desired outcome, constraints and definition of done.
2. Build a concise context brief. Include only relevant facts, file excerpts, project paths, decisions and requirements. Do not send the full conversation or entire repository by default.
3. Call the MCP tool hif_run with the goal and context. If the user explicitly requests parallel specialist nodes, use hifnode_run instead.
4. Report the returned session ID, node roles, selected models, measured token usage, elapsed time, fallbacks and final synthesis.
5. If the MCP tool is unavailable, do not pretend routing happened. Explain that the HIF runtime/MCP server is not installed or connected.
6. Avoid orchestration for trivial requests where a direct response is faster and cheaper.

## Routing and efficiency

- Use task-specific models: fast/low-cost models for classification, extraction and summaries; capable models for complex analysis, coding and verification.
- Execute independent work concurrently only through hifnode_run; respect dependencies.
- Retrieve only role definitions, session facts and artifact references relevant to each task.
- Prefer HIF-shared session memory and prior results over repeating work.
- Use the configured 80% HIF-measured token-budget threshold for pre-emptive fallback. Provider subscription quota percentages are unknown unless the provider exposes an authoritative measurement.
- Respect provider limits, API billing, privacy policies and configured spending budgets.

## Safety and limitations

- HIF tasks are text-only in the current MVP. They do not edit project files, run shell commands, browse the web or deploy code.
- A provider switch does not transfer the host's native conversation state. HIF passes explicit task briefs, approved memory and outputs.
- API access can be billed separately from consumer chat subscriptions.
- Never rotate accounts to evade quotas or provider restrictions.
- Do not send secrets or confidential context to external providers without permission.
- Never request or transfer hidden chain-of-thought.
