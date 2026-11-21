# AI Model Manager

## Initial policy

HIF uses one ordered model chain. The first entry is the primary model; subsequent
entries are fallback targets. The initial deployment profile is:

1. Primary: `openai/gpt-6.2-astra` (GPT-6.2 Astra API model ID).
2. Fallback: `anthropic/claude-sonnet-5-5`.
3. Strategy: ordered fallback after a retryable provider availability failure.

The model identifiers are provider API identifiers, not display labels. Check the
provider's model catalog and the LiteLLM integration before changing them.

## Configuration

Set these values in the private `.env` file:

```dotenv
HIF_MODEL_POOL=openai/gpt-6.2-astra,anthropic/claude-sonnet-5-5
HIF_PLANNER_MODEL=openai/gpt-6.2-astra
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

Never commit real credentials. Keep them in environment variables or a secret
manager. The model manager reports whether a credential is configured, but never
returns its value.

## Runtime behavior

- HIF tries the primary model first.
- Retryable errors such as timeouts, connection failures, HTTP 429 and transient
  5xx responses mark that model unavailable for a bounded cooldown and allow the
  next eligible model to be tried.
- Invalid credentials, permission errors, malformed requests and billing errors
  are not retried as transient outages.
- The existing HIF-measured token budget policy can also move new work to the next
  eligible model at the configured threshold (80% by default).
- Task-specific model preferences remain supported and are evaluated before the
  global chain.
- Per-provider semaphores continue to bound concurrent requests.

## Observability

`AIModelManager.status()` returns the primary model, ordered fallbacks, provider
names, priority and a boolean credential-readiness indicator. It never returns
secret values. Router status can be used by a future authenticated administration
endpoint or dashboard.

## Operational notes

OpenAI API billing and Anthropic API billing are separate from consumer chat
subscriptions. Validate that both API keys have active billing and model access
before enabling production fallback. Fallback repeats the same task prompt with
the second provider; it does not transfer hidden reasoning or private provider
conversation state.
