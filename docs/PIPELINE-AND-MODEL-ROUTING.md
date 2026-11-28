# HIF Pipeline Engine and Multi-Model Routing

**Product:** HIF — Hybrid Intelligent Flow  
**Publisher:** ZirconAI.fr  
**Repository:** SmartAIModelsRouters

## 1. The same pipeline concept in Skills and the connected runtime

HIF uses one logical pipeline contract in every supported host. A Skill-only installation applies the pipeline as an instruction-driven workflow inside the host assistant. A connected HIF installation executes the same workflow through HIF's DAG engine, provider router, shared SQLite session and measured telemetry.

| Capability | Skill-only mode | Connected HIF runtime |
|---|---|---|
| Request classification | Yes, using the active host model | Yes, persisted with run metadata |
| Pipeline plan and stages | Yes, within the conversation | Yes, validated DAG |
| Specialist roles | Yes, as logical stages | Yes, scheduled nodes |
| Multiple models | Only if the host exposes model selection/delegation | Yes, for configured provider APIs |
| Parallel execution | Only if native host sub-agents are available | Bounded async DAG execution |
| Token usage | Host-reported only, if exposed | HIF records provider-reported usage |
| Shared persistent memory | Host capabilities only | SQLite session memory |
| CPU/RAM-aware scheduling | Not exposed by a Skill alone | Local runtime telemetry |
| Background pipeline / resume | Not guaranteed by a Skill host | Runtime capability, subject to persistence/checkpoint implementation |

A portable Skill cannot independently switch the host's selected model, inspect subscription quotas or create API access to other consumer subscriptions. If the host does not expose sub-agents or model selection, HIF executes stages sequentially with the current model and reports that limitation. Never simulate a multi-model run.

## 2. Standard HIF pipeline

Every non-trivial request follows this lifecycle:

1. **Intake:** normalize the request, output format, constraints, privacy class and acceptance criteria.
2. **Classify:** complexity (simple, complicated, too_complicated) and urgency (critical, high, normal, low) are separate dimensions.
3. **Architect:** the Root Orchestrator performs an initial architecture assessment. For software, infrastructure, cloud and migration work it may assign:
   - **Assistant Architect:** independent design critique, alternatives, consistency checks and architecture risks.
   - **Infrastructure Architect:** hosting, network, identity, security boundaries, capacity, availability, observability, backup/recovery, disaster recovery and infrastructure cost.
4. **Plan:** create a small dependency-aware pipeline with roles, inputs, context references, output schemas, token budgets and acceptance tests.
5. **Select models:** choose the lightest eligible model per stage from the configured pool and role preferences. Use provider capability, actual availability, privacy, historical quality/latency and remaining budget where data exists.
6. **Execute:** run independent stages concurrently only when the host/runtime supports it and resource/provider limits allow it. Dependent stages wait for their prerequisites.
7. **Cross-review:** the Technical Leader and relevant architects reconcile contradictions, detect missing interfaces and identify blockers.
8. **Validate:** use deterministic checks, source evidence, tests, schema checks and build results first; use a reviewer model for semantic gaps.
9. **Synthesize:** return one coherent answer, evidence, actual usage when available and an explicit remaining-work checklist.
10. **Learn:** record permitted telemetry and compact validated summaries. Propose pipeline/model preference improvements without changing security policy or provider permissions.

For simple requests, skip unnecessary delegation and use one inexpensive/fast model or deterministic local logic. For every too_complicated task, Auto escalates to HIF Strong, which may coordinate domain modes under one root orchestrator.

## 3. Default multi-provider model catalog

HIF ships with a starter catalog spanning multiple providers. It does not assume every user has every API account.

| Provider | Starter model IDs | Intended default use |
|---|---|---|
| OpenAI | openai/gpt-luna-latest, openai/gpt-sol-latest, openai/gpt-astra-latest | Fast triage, general/coding work, complex review |
| Anthropic | anthropic/claude-haiku-latest, anthropic/claude-sonnet-latest, anthropic/claude-opus-latest | Fast extraction, engineering, deep review |
| Google Gemini | gemini/gemini-3.5-flash-lite, gemini/gemini-3.8-flash, gemini/gemini-4-hydrogen, gemini/gemini-4-neon | Low-latency tasks, agentic/research work, advanced reasoning |
| DeepSeek | deepseek/deepseek-flash-latest, deepseek/deepseek-pro-latest | Cost-sensitive tasks and deeper reasoning |
| Moonshot AI (Kimi) | moonshot/kimi-latest | Long-context reasoning and research |
| Alibaba Cloud (Qwen) | dashscope/qwen-max-latest, dashscope/qwen-flash-latest | General reasoning, coding and fast tasks |
| xAI | xai/grok-latest | Alternative reasoning and research |
| Z.AI (GLM) | zai/glm-latest, zai/glm-flash-latest | General and fast tasks |
| MiniMax | minimax/minimax-latest | General-purpose tasks |
| Mistral, Groq, OpenRouter | User-selected LiteLLM model IDs | Additional hosted models and routing options; explicit model IDs required |

Model aliases and provider routes follow LiteLLM documentation and can change with upstream releases. Verify account/region availability and test the selected model before production rollout. These are API model identifiers, not consumer subscription entitlements. Access, regional availability, account limits, pricing and lifecycle can change. Confirm the exact provider model ID and LiteLLM compatibility before production use. Preview models should be pinned deliberately and reviewed for lifecycle changes.

Official model references:
- OpenAI model/API overview: https://platform.openai.com/overview
- Anthropic model lifecycle: https://docs.anthropic.com/en/docs/about-claude/model-deprecations
- Gemini model list: https://ai.google.dev/gemini-api/docs/models
- DeepSeek model list and pricing: https://api-docs.deepseek.com/api/list-models/ and https://api-docs.deepseek.com/quick_start/pricing/
- LiteLLM provider catalog and aliases: https://docs.litellm.ai/docs/providers and https://docs.litellm.ai/docs/model_latest_aliases
- Moonshot/Kimi: https://platform.moonshot.ai/
- Alibaba DashScope/Qwen: https://dashscope.console.aliyun.com/

## 4. Automatic provider activation

The runtime activates starter models only for providers with a configured API key:

- OPENAI_API_KEY activates OpenAI starter models.
- ANTHROPIC_API_KEY activates Anthropic starter models.
- GEMINI_API_KEY or GOOGLE_API_KEY activates Gemini starter models.
- DEEPSEEK_API_KEY activates DeepSeek starter models.
- MOONSHOT_API_KEY activates Moonshot/Kimi.
- DASHSCOPE_API_KEY activates Alibaba DashScope/Qwen.
- XAI_API_KEY, ZAI_API_KEY and MINIMAX_API_KEY activate Grok, GLM and MiniMax.
- MISTRAL_API_KEY, GROQ_API_KEY and OPENROUTER_API_KEY are accepted for explicitly configured model IDs.

If HIF_MODEL_POOL is empty, HIF builds the active pool from configured provider credentials. The Moonshot, DashScope, xAI, Z.AI and MiniMax starters use LiteLLM provider routes. If it is explicitly set, that list overrides the starter catalog.

If HIF_TASK_MODEL_PREFERENCES is empty, HIF uses the default task preferences filtered to active models. Explicit JSON preferences override those defaults.

HIF does not require all four providers. One configured provider is sufficient to start; adding more provider keys expands the eligible fallback pool. Model identifiers are not proof that the user's account has access: provider errors are handled through retry/cooldown/fallback.

## 5. Install and configure

### 5.1 Install portable Skills (Windows)

```powershell
git clone -b main https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
cd SmartAIModelsRouters
.\scripts\install-hif-skills.ps1 -Hosts Claude,Codex,GeminiCLI,Copilot
```

Install one host only if preferred:

```powershell
.\scripts\install-hif-skills.ps1 -Hosts Claude
```

### 5.2 Install portable Skills (Linux/macOS)

```bash
git clone -b feature/hif-1.0-five-modes https://github.com/yassineelhif5-pixel/SmartAIModelsRouters.git
cd SmartAIModelsRouters
bash scripts/install-hif-skills.sh --hosts claude,codex,gemini,copilot,cursor,kimi,qwen
```

Start a new host session and confirm that the HIF Skills are visible. Host-specific command syntax varies.

### 5.3 Install the local HIF runtime

Windows:

```powershell
.\scripts\install-hif-runtime.ps1
Copy-Item .env.example .env
notepad .env
```

Linux/macOS:

```bash
bash scripts/install-hif-runtime.sh
cp .env.example .env
${EDITOR:-nano} .env
```

Add only the API keys for providers you are authorized to use. Leave HIF_MODEL_POOL empty to activate the starter catalog automatically based on configured keys. Keep secrets in the local environment/OS secret store; never commit .env.

### 5.4 Verify model routing

```bash
hif --help
hif usage
```

If the CLI includes diagnostics in the installed version, use its provider/model diagnostic command. Otherwise, submit a small low-cost test request and verify the returned model name and measured usage. Do not assume every configured model is reachable until a real provider request succeeds.

### 5.5 Connect the Skill to HIF MCP

For Claude Code, the runtime installer prints the exact local executable path. Register it at user scope:

```bash
claude mcp add --scope user --transport stdio hif -- "/absolute/path/to/hif-mcp"
claude mcp list
```

Use the equivalent supported MCP setup for the chosen host. Start a new session and verify that the HIF tools are listed before expecting connected multi-provider execution.

### 5.6 Build Skill ZIPs for supported web hosts

```bash
python scripts/package-skills.py
```

Upload the generated ZIPs through the host's supported Skills import UI. A web Skill without a reachable HIF MCP endpoint runs only the native host workflow.

## 6. Default task-to-model routing

The starter preferences are deliberately multi-provider and ordered for fallback. Additional provider models remain eligible as fallback candidates even when they are not first-choice for a task type:

| Task type | First-choice profile | Fallback profile |
|---|---|---|
| Analysis / triage | GPT-6 Luna, Gemini Flash-Lite | DeepSeek Flash, Claude Haiku |
| Research | Gemini 3.8 Flash, GPT-6.1 Sol | Claude Sonnet 5, DeepSeek V4 Pro |
| Coding | GPT-6.1 Sol, Claude Sonnet 5 | DeepSeek V4 Pro, Gemini 3.8 Flash |
| Testing | GPT-6 Luna, DeepSeek Flash | Claude Haiku |
| Review | GPT-6.2 Astra, Claude Opus 5 | Gemini 3.1 Pro, DeepSeek V4 Pro |
| Architecture | GPT-6.2 Astra, Claude Opus 5 | Gemini 3.1 Pro |
| Infrastructure | GPT-6.1 Sol, Claude Sonnet 5 | Gemini 3.8 Flash |

This is an initial routing policy, not a universal quality ranking. HIF should adapt it using measured task outcomes, latency, failure rates, cost and user-approved feedback. The actual active model pool filters these preferences to providers with configured credentials.

## 7. Architecture roles

The Root Orchestrator must act as an architect during intake, not merely forward prompts. It creates a concise current-state map, identifies constraints and proposes a target architecture when relevant.

- **Root / Solution Architect:** owns the architecture baseline, module boundaries, contracts, ADRs and final technical decision.
- **Assistant Architect:** independently reviews the proposed design, compares alternatives, checks consistency and flags risks or missing requirements.
- **Infrastructure Architect:** reviews deployment topology, compute, storage, network, DNS, identity, secrets, observability, capacity, resilience, backup/recovery, disaster recovery and cost.
- **Integration Manager:** validates that specialist outputs and code fit the approved architecture and contracts.

These are logical roles. HIF instantiates them only when the task benefits from them. A simple question does not need three architect agents.

## 8. Token, memory and resource policy

- Send each stage a compact task brief and only the source excerpts it needs.
- Never broadcast full chat/repository context to every model.
- Reuse cached summaries only while their source hashes and dependency versions remain valid.
- Reserve budget for synthesis and verification.
- Record provider-reported input/output tokens and cost when available; mark missing usage as unavailable.
- Use bounded concurrency and per-provider semaphores.
- Prefer deterministic local parsing, indexing and tests to model calls.
- In Skill-only mode, host token counters are authoritative; HIF must not invent host usage or claim an exact percentage saved.

## 9. Operational boundaries

- API usage may be billed separately from ChatGPT, Claude, Gemini or Copilot consumer subscriptions.
- Native subscription Skills cannot independently call another provider's subscription.
- Parallel multi-model routing requires connected provider APIs or actual host-native sub-agent/model tools.
- HIF does not bypass provider authentication, quotas, rate limits or terms.
- Production changes, external messages, deployments and destructive migrations require approval.
