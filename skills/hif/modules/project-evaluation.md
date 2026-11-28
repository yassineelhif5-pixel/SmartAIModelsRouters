# HIF module: independent project evaluation

Use this module when a user asks whether an idea, product, migration, architecture or project is feasible, compatible, worth pursuing or ready for implementation.

## Required workflow
1. Normalize the proposal, intended users, constraints, budget, deadline, target platforms, data sensitivity and measurable success criteria.
2. Check the actual connected HIF model pool. Request independent reviews from at least two distinct configured providers. Prefer provider diversity before using two models from one provider.
3. Invoke `hif_evaluate_project` when the connected MCP tool exists. Use 2–4 reviewers by default; use up to 6 only when the project warrants it.
4. Give each model the same bounded brief, but request independent assessments before sharing other reviewers' conclusions.
5. Compare feasibility, technical compatibility, security/privacy, operations, costs, dependencies, market/user value and assumptions.
6. Present each model's actual provider/model, verdict, score, confidence, evidence, risks, blockers and testable recommendations.
7. Separate model consensus from objective verification. A model score is not a probability of success.

## Decision semantics
- `validated`: configured reviewers support feasibility; this is an assessment, not proof of implementation.
- `conditional`: plausible but conditions/blockers must be resolved.
- `rejected`: reviewers find material blockers or majority negative judgement.
- `inconclusive`: too few successful independent reviews or evidence is insufficient.

Never turn a negative result into an automatic rejection of the user's ambition. Explain what evidence could change the decision. If only one provider is configured, do not call it multi-model consensus: report that independent cross-provider validation is unavailable and offer a single-model preliminary review.

Do not send sensitive project data to providers that are not authorized by the user's data policy. Do not invent reviewers, scores, token usage, citations or completed tests.
