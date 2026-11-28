# HIF Skill Delivery Contract

**Status:** Normative behavior for portable HIF Skills. This contract standardizes Skill-only output; it does not imply that the HIF runtime, connectors, dashboard or artifact generators are installed.

## Purpose

Every HIF Skill should produce a useful, trustworthy and presentation-ready result in the host assistant's normal conversation. The host may render Markdown and Mermaid differently; therefore Markdown is the portable baseline and diagrams are progressive enhancement.

## Universal invariants

1. Be fast-first: provide an initial useful answer before optional deep work.
2. Be capability-honest: use only models, tools, agents and connectors actually available.
3. Be evidence-led: separate verified facts, inference, assumptions and unknowns.
4. Be domain-aware: choose specialists and acceptance criteria for the user's outcome, not for show.
5. Be approval-safe: no external, destructive or production action without authorization.
6. Be deliverable-oriented: optimize the final report for the reader, not for internal orchestration.
7. Be portable: work sequentially with the current host model if delegation or diagrams are unsupported.

## Standard run envelope

When structured execution data is available, represent it with this conceptual envelope:

```json
{
  "schema_version": "1.0",
  "run": {
    "id": "actual-run-id-or-null",
    "title": "short goal",
    "mode": "skill-only | connected-runtime",
    "representation": "proposed-plan | actual-execution",
    "status": "proposed | running | completed | validated | blocked | failed",
    "started_at": null,
    "completed_at": null
  },
  "tasks": [
    {
      "id": "stable-task-id",
      "parent_id": null,
      "role": "specialist role",
      "objective": "bounded outcome",
      "depends_on": [],
      "status": "proposed | ready | running | completed | validated | blocked | failed | skipped | not_run",
      "evidence": [],
      "validation": "not_run"
    }
  ],
  "artifacts": [],
  "events": [],
  "metrics": {}
}
```

This is an illustrative schema shape, not a claim that these fields are persisted or that IDs/events exist. In Skill-only mode, omit unavailable fields or use null/empty values; do not create fictitious telemetry. A proposed workflow must set `representation` to `proposed-plan`.

## Report acceptance checklist

- Executive summary states the outcome and decision.
- Scope, method and limitations are clear.
- Findings are prioritized and traceable to evidence.
- Sources have dates/links where available.
- Tables and charts are based on real inputs.
- Recommendations have owners/dates only when known.
- Validation names actual checks and outcomes.
- Remaining work and blockers are explicit.
- No fabricated execution, model, metric, source or publication claims.

## Host rendering guidance

- **Markdown:** mandatory portable fallback.
- **Mermaid:** optional diagram for non-trivial workflows; label plans vs actual execution.
- **JSON:** optional machine-readable companion only when requested/consumed.
- **DOCX/PDF/PPTX/XLSX/HTML:** only through an available artifact tool with confirmed success.
- **Live dashboard:** requires a separate host UI/runtime and structured events; a Skill alone cannot provide it.

## Lifecycle vocabulary

| State | Meaning |
|---|---|
| proposed | Designed, not dispatched |
| ready | Inputs and dependencies satisfied |
| running | Confirmed active execution |
| completed | Work returned, not yet quality-checked |
| validated | Acceptance checks passed with evidence |
| blocked | Cannot proceed without dependency/decision |
| failed | Attempted and failed |
| skipped | Deliberately not required |
| not_run | Check was not performed |

Do not collapse completed, validated and deployed into one status.

## Domain-specific acceptance

The selected Skill adds its own domain checks (engineering, database, architecture, agent design or assurance) on top of this shared contract. HIF root orchestration remains accountable for integration and final acceptance.
