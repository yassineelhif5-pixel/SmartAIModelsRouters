---
name: hif
description: Use the HIF multi-provider orchestrator for substantial tasks, cost-aware model routing, specialist delegation, shared session memory, or consolidated results.
---

# HIF — Hybrid Intelligent Flow

HIF is a task orchestrator. It is not a silent replacement for the host assistant's native model or conversation.

## Invocation
1. Understand the outcome, constraints and definition of done.
2. Build a concise context brief with only relevant facts, paths, excerpts and decisions. Do not send the full conversation by default.
3. Call the MCP tool hif_run with the goal and context. If the user explicitly requests parallel specialist nodes, use hifnode_run instead.
4. Report the session ID, roles, selected models, measured token usage, elapsed time, fallbacks and synthesis.
5. If the MCP tool is unavailable, explain that HIF is not connected. Never pretend routing happened.
6. Avoid orchestration for trivial requests.

## Efficiency
- Select models by task capability, cost, latency and privacy policy.
- Keep context compact; reuse HIF memory and artifacts.
- Execute dependent tasks sequentially; use hifnode_run for concurrent specialist work.
- Use the configured 80% HIF-measured token-budget threshold for fallback. Do not invent provider subscription quota percentages.
- Respect API billing, rate limits, provider terms and spending budgets.

## Safety
- Current MVP tasks are text-only; no file editing, shell commands, browsing or deployment.
- HIF shares explicit briefs, approved facts, role definitions and task outputs, not provider-native hidden context.
- Do not bypass quotas or rotate accounts to evade restrictions.
- Do not send secrets or confidential data to remote providers without approval.
- Never request hidden chain-of-thought.
