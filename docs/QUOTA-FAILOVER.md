# Pre-emptive provider fallback at 80% usage

## Policy

The default HIF pre-emptive fallback threshold is 80% of a configured or provider-reported usage window. At or above this threshold, HIF should prefer the next eligible model for new tasks rather than waiting for HTTP 429.

This threshold is an operational routing policy, not a method for bypassing provider limits.

## Usage data sources

1. Provider-reported quota: official endpoint/response header with a defined usage window, source and observation time.
2. HIF-measured usage: provider-reported request token counts or spend accumulated by HIF against a configured budget/window.
3. Estimated usage: HIF estimate when exact metadata is unavailable. It must be labelled as an estimate, never presented as the provider's official quota.

Not every provider exposes remaining subscription quota or comparable reset windows. If no trustworthy percentage exists, do not invent one. Fallback can still occur on a real 429, outage or supported quota error.

## Candidate selection

Exclude a candidate when it is disabled, unhealthy, incapable, disallowed by privacy policy, over budget or at/above its measurable threshold. Choose the highest-priority eligible candidate. On retryable failure, respect Retry-After/reset hints, use bounded backoff, then try the next eligible candidate. Do not retry invalid credentials, permission or billing errors indefinitely.

If every candidate is unavailable or over threshold, report that no eligible capacity remains. Never silently rotate personal accounts to evade subscription limits.

## Configuration

- HIF_USAGE_FALLBACK_THRESHOLD=0.80
- configurable per-model and per-provider budgets;
- optional per-provider concurrency ceilings;
- enable/disable anticipatory fallback;
- display provider-reported, HIF-measured and estimated values separately.

## Billing distinction

Consumer subscriptions are not automatically API credits. API calls may incur separate charges. Use documented APIs and authorized credentials only.
