# HIF module: approval-gated counter-testing

This module takes over after a negative or conditional project review. It is a controlled remediation and falsification workflow, not permission to execute changes.

## Gate 1 — propose
Summarize the negative findings, list recommendations and propose bounded, reversible tests. State tools, data, expected evidence, risks, estimated costs and stop conditions. Ask the user explicitly whether HIF may prepare and run these tests.

## Gate 2 — prepare after approval
Only after an unambiguous affirmative response may the connected HIF tool `hif_countertest_plan` be called with `approved=true`. The tool produces a test protocol only; it does not run commands, change files, access external systems or deploy.

## Gate 3 — execute with least privilege
The host assistant or connected execution tools may execute only the approved test steps. Before any additional side effect, external call, write, installation, data change, spend or deployment, obtain the required separate confirmation. Prefer sandbox, temporary branch, mock data, read-only inspection, dry-run and reversible changes.

## Gate 4 — report and re-evaluate
Capture command/tool evidence, actual outputs, failures and limitations. Do not mark a recommendation as tested if no execution tool was available. Re-run independent reviewers on the revised proposal when useful. Present before/after findings and a new decision.

Never infer approval from silence, a previous unrelated approval, or a generic request to "look into it". Never run a negative review's recommendations automatically. Do not execute arbitrary code produced by a model without inspection, sandboxing and the user's authorization.
