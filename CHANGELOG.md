# Changelog

All notable changes to HIF are listed here. Dates are in ISO format.

## 0.4.0 — 2026-11-28

### Added
- Independent multi-provider project evaluation (`hif_evaluate_project`) and approval-gated
  counter-test planning (`hif_countertest_plan`).
- AI model manager: `hif models`, MCP tool `hif_models` and gateway route `GET /v1/models`
  show the primary model, the fallback chain and which provider credentials are set.
- Execution profiles `auto`, `browser`, `small`, `standard`, `server`.
- Modular root skill (`skills/hif/modules/`) and a portable Agent Plugin under
  `plugins/hif-universal/`.
- Direct connections to 32 AI providers (`hif/provider_catalog.py`, `hif/native_providers.py`):
  native Anthropic Messages and Gemini adapters, an OpenAI-compatible adapter for 26 cloud and
  local providers, LiteLLM delegation for AWS Bedrock, Vertex AI and watsonx. New command
  `hif providers`. Any endpoint can be overridden with `HIF_<PREFIX>_BASE_URL`.
- Agent spend guard (`hif/spend_guard.py`): per-session caps on tokens, model calls and reported
  cost, plus loop detection. Sessions that trip it stop with status `stopped_by_spend_guard`.
- Benchmark harness (`hif/bench.py`, `bench/tasks.jsonl`, `hif bench`): 30 deterministic tasks,
  HIF against a single model, Markdown and JSON reports.
- Apache-2.0 licence, NOTICE, COMMERCIAL.md (open-core boundary), CODE_OF_CONDUCT.md,
  SECURITY.md, PyPI release workflow.

### Changed
- The engine's default provider is now `AutoProvider`, which picks the adapter from the model
  prefix and falls back to LiteLLM for unknown prefixes.
- Default model catalog updated to model IDs checked on 2026-11-28 (pinned IDs instead of
  unverified `-latest` aliases).
- README rewritten; HIF 1.0 specifications moved to `docs/rfc/`.

## 0.3.0

- Authenticated REST and Streamable HTTP MCP gateway for a single-tenant private pilot,
  OIDC/JWT verifier, task planning, parallel nodes, shared SQLite memory, token budgets with
  80 % fallback, CPU/RAM-aware concurrency, read-only security pre-audit.
