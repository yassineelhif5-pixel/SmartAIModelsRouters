# HIF independent multi-model project evaluation

## Purpose

HIF can request independent assessments of an idea, product, architecture, migration or delivery proposal from several configured model providers. The goal is to expose disagreement, hidden assumptions and testable risks before committing engineering time or money.

## Evaluation contract

1. The input brief includes the goal, users, scope, constraints, budget, deadline, target environment and success criteria where known.
2. Reviewers are selected from the configured model pool. HIF prefers different provider families and requires at least two distinct providers for a cross-provider decision.
3. Each reviewer receives the same bounded brief and returns a structured verdict, score, confidence, strengths, risks, assumptions, blockers and falsifiable recommendations.
4. Reviewer calls are bounded by a semaphore and configured request timeout. Failed or invalid responses are recorded as inconclusive rather than fabricated.
5. HIF aggregates only successful reviews and records disagreements. The decision rule is deterministic and visible:
   - rejected: a majority of successful reviewers is negative, or the mean score is below 40;
   - conditional: material conditions/blockers remain, or the mean score is below 75;
   - validated: successful reviewers support feasibility and no conditions/blockers are reported;
   - inconclusive: fewer than two successful independent reviews.
6. A validated verdict is a feasibility assessment, not proof of implementation, security, compliance, market demand or production readiness.

Scores and thresholds are decision aids, not calibrated probabilities. Model outputs can be correlated, incomplete or wrong. For high-stakes decisions, add human domain review and objective evidence.

## Approval-gated counter-testing

A negative or conditional review may produce a set of recommendations and validation tests. HIF stores these proposals with the evaluation session. The user must explicitly authorize the counter-test stage. The MCP tool `hif_countertest_plan` then asks a model to create a bounded, reversible test protocol.

The current tool prepares a plan only. It does not execute shell commands, change files, access external services, spend money or deploy. Actual execution must be performed by the host's authorized tools, with separate confirmation for consequential actions. Test evidence must be captured before re-evaluation.

## Privacy and cost

Every reviewer call sends the project brief to the selected provider. Do not include secrets, personal data or confidential project information unless that provider is approved for the data. Calls may incur provider API charges. HIF reports provider-reported token/cost fields only when available; it does not infer a consumer subscription quota.

## MCP tools

- `hif_evaluate_project(goal, context, max_reviewers)`: independent review, aggregation and session persistence.
- `hif_countertest_plan(session_id, evaluation_id, approved)`: prepares a test protocol only when `approved=true`.

## Known limitations

- No dynamic provider discovery or live model catalog validation is performed by this module.
- Model availability, access, pricing and region restrictions depend on provider accounts and LiteLLM routing.
- Cross-provider diversity does not guarantee statistical independence.
- Tool execution is not included in the evaluation module.
