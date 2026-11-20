---
name: hif
description: Orchestrate substantial tasks across configured AI providers. Use when the user invokes /hif, asks for multi-provider routing, token or cost optimization, parallel specialist work, or a consolidated result from multiple models.
---

# HIF — Hybrid Intelligent Flow

Use HIF as the central orchestrator when the task benefits from specialist delegation, provider routing, or controlled parallel execution.

## Workflow
1. Understand the outcome, constraints, project context and definition of done.
2. Do not send the entire conversation or repository by default. Build a compact context brief with only relevant facts, paths, excerpts and decisions.
3. Use the configured HIF MCP tool or CLI to submit the goal and context.
4. Let HIF create a dependency-aware task plan, route each task to an eligible configured provider/model, execute independent tasks concurrently, preserve outputs in shared session memory and synthesize one result.
5. Report which tasks actually ran, which provider/model was selected, measured usage, elapsed time, fallbacks and any limitations.
6. Do not claim orchestration happened when the HIF MCP server or CLI is unavailable. State the exact missing prerequisite.

## Efficiency policy
- Do not create agents for trivial tasks.
- Parallelize independent read-only work; serialize dependent work.
- Use task-specific model selection: inexpensive/fast models for simple classification, extraction and summaries; stronger models for complex reasoning, coding and verification.
- Minimize repeated context with shared artifacts, compact summaries and provenance.
- Respect provider limits, rate limits, per-task budgets and the global spending ceiling.
- Prefer another eligible provider when a trustworthy usage metric reaches the configured threshold (default 80%). Label estimates as estimates.

## Safety
- The current HIF repository may still be in development. Check implementation status before claiming tools are available.
- A different provider does not inherit the native conversation state of the previous provider. HIF shares only explicit task briefs, approved session facts, role definitions and artifacts.
- API access is normally billed separately from consumer chat subscriptions.
- Never bypass service limits, rotate accounts to evade restrictions or invent quota percentages.
- Do not send secrets or confidential context to an external provider without permission.
- Do not request or transfer hidden chain-of-thought.
- Obtain approval before destructive or externally visible actions.
