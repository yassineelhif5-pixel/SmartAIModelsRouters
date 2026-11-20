# ADR 0001: Task-level orchestration boundary

- Status: Accepted
- Date: 2026-11-21

## Context

The project aims to dispatch work across Claude, GPT, Gemini and other providers to improve throughput and reduce unnecessary token consumption. Native assistant sessions have provider-specific tools, context, authentication and extension mechanisms. A generic model proxy cannot safely assume it can transparently replace every native session or preserve hidden state.

## Decision

Build HIF as a provider-neutral task orchestrator with native host adapters. A host submits a goal and approved context. HIF plans a task graph, routes tasks to providers, executes independent work in parallel, stores artifacts and returns a consolidated result.

The Claude Code integration exposes `/hif` via a Claude plugin and MCP. Codex and other clients get their own adapters based on their documented extension mechanisms.

## Consequences

- HIF can optimize tasks without owning the entire interactive conversation.
- Context handoff is explicit and auditable.
- Integrations remain host-specific; one plugin is not assumed to work everywhere.
- Model/provider switching may change output quality and tools; validation is required.
- More development is needed than a simple proxy, but the boundary is safer and more portable.
