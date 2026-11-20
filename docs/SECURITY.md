# Security and Privacy

## Credentials
- Read credentials from environment variables or an OS secret store.
- Never commit real keys, tokens, cookies or OAuth refresh tokens.
- Redact authorization headers and common secret patterns in logs.
- Do not expose secrets through CLI diagnostics or dashboard endpoints.
- Prefer short-lived credentials and provider-supported OAuth flows.

## Data minimization
- Send only the task inputs needed by a selected provider.
- Support provider allowlists and a `local_only` privacy class.
- Make external-provider routing visible and configurable.
- Do not persist raw prompts/responses by default; persist metadata and artifact references.
- Provide retention and deletion controls before remote multi-user deployment.

## Billing and quotas
- Enforce explicit per-task, per-run and monthly budgets.
- Treat unknown usage/pricing as unknown; do not invent estimates.
- Distinguish provider subscription quotas from API usage billing.
- Do not rotate accounts to evade provider restrictions or pool subscriptions contrary to provider terms.
- Backoff on 429 and honor provider reset/retry headers where available.

## Execution safety
- Read-only tasks may run concurrently when independent.
- File-writing tasks must be isolated or serialized to prevent conflicting edits.
- Require approval for deletion, deployment, purchases, external communications and other consequential actions.
- Keep a trace of the plan, policy decisions, selected provider/model and tool actions.
- Support cancellation and timeouts.

## Threat model
Treat user prompts, repository files, tool output and model responses as untrusted input. They may contain prompt-injection instructions. Tool authorization must come from HIF policy and user approval, never from text found in a repository or model output.
