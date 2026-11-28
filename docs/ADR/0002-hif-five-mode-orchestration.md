# ADR 0002: HIF 1.0 five-mode orchestration

- Status: Accepted as the implementation baseline
- Date: 2026-11-28
- Related specification: HIF 1.0 Five-Mode Architecture (../rfc/HIF-1.0-MODES-SPEC.md)

## Context

The HIF 0.3.0 baseline provides a typed task DAG, bounded parallel execution, provider fallback, HIF-measured token budgets, SQLite session memory, CLI, gateway and MCP entry points. It does not yet implement recursive multi-orchestrator hierarchy, domain-specific modes, autonomous agent lifecycle, adaptive classification or high-assurance candidate evaluation.

HIF needs five clear operating modes without duplicating the runtime or breaking the existing execution path.

## Decision

Adopt one shared HIF Core with five mode policies:
- hifDev: software engineering;
- hifBD: database engineering;
- hifArc: architecture;
- hifStrong: high-assurance hierarchical orchestration;
- hifAgent: specialist agent workforce lifecycle.

Default mode is auto. Every task classified too_complicated escalates to hifStrong. Runtime mode switching is enabled, bounded and auditable. Domain modes may execute as specialist workstreams under Strong.

Agents are logical scoped execution units, not necessarily separate OS processes. The root orchestrator retains ownership of the global goal, budgets, policy, task graph and final result.

## Consequences

Positive:
- One provider, memory, scheduler, telemetry and policy boundary is shared.
- Domain-specific behavior can evolve independently without duplicating orchestration.
- Strong coordinates cross-domain work while enforcing global budgets and safety.
- Existing engine and interfaces can be migrated incrementally.

Trade-offs:
- Mode resolution, transitions and hierarchical budgets add complexity.
- Current DAG and storage schemas need backward-compatible extensions.
- Some modes initially act as planning/policy profiles until execution runtimes exist.

## Guardrails

- No unbounded recursive delegation or fan-out.
- No direct writes to the protected default branch.
- No sensitive side effects without explicit approval.
- No provider capability or quota assumptions without verified metadata.
- No feature is considered implemented until it has tests and runtime evidence.

## Rollout

Implement in phases: contracts and Auto classifier; domain mode policies; Strong hierarchy; agent lifecycle; verification and adaptive routing; software execution runtime; telemetry and load testing. See the linked specification for acceptance criteria.
