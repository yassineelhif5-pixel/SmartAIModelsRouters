# Fournisseurs IA pris en charge

HIF parle directement à 32 fournisseurs, sans passer par un agrégateur. Les requêtes partent
de votre machine ou de votre réseau vers le fournisseur choisi : aucune commission, aucune
étape intermédiaire, et les modèles locaux gardent les données sur place.

- **Adaptateurs natifs** : Anthropic (Messages API) et Google Gemini (generateContent).
- **Protocole compatible OpenAI** : tous les autres fournisseurs cloud et les serveurs locaux
  (Ollama, LM Studio, vLLM, llama.cpp).
- **Délégués à LiteLLM** : AWS Bedrock, Google Vertex AI et IBM watsonx, dont l'authentification
  passe par les SDK cloud (`pip install -e ".[providers]"`).

Un modèle s'écrit `<préfixe>/<nom du modèle chez le fournisseur>`, par exemple
`mistral/mistral-small-latest`, `anthropic/claude-sonnet-4-5` ou `ollama/llama3.1`.
Les noms de modèles évoluent souvent : vérifiez-les dans la documentation du fournisseur.

```bash
hif providers               # tous les fournisseurs et leur état
hif providers --configured  # seulement ceux qui sont prêts ici
```

## Configurer un fournisseur

1. Définissez sa clé (voir le tableau), par exemple `MISTRAL_API_KEY=...`.
2. Laissez `HIF_MODEL_POOL` vide pour activer les modèles de départ, ou listez vos modèles :
   `HIF_MODEL_POOL=mistral/mistral-small-latest,anthropic/claude-sonnet-4-5,ollama/llama3.1`.
3. Pour un point d'accès régional, privé ou un proxy d'entreprise, remplacez l'URL :
   `HIF_<PRÉFIXE>_BASE_URL=https://...` (par exemple `HIF_OPENAI_BASE_URL`).

Modèles locaux : `HIF_ENABLE_OLLAMA=true` (ou `HIF_OLLAMA_BASE_URL=http://serveur-gpu:11434/v1`).

Azure OpenAI : `AZURE_OPENAI_API_KEY` et
`HIF_AZURE_BASE_URL=https://<ressource>.openai.azure.com/openai/v1` ; la partie modèle de
l'identifiant est le nom de votre déploiement (`azure/mon-deploiement-gpt`).

## Comportement en cas d'erreur

- Codes 408, 409, 425, 429, 5xx et 529 : erreur temporaire, HIF met le modèle en pause
  (en respectant l'en-tête `Retry-After`) et passe au candidat suivant.
- Codes 401, 403, 400 : erreur définitive, remontée immédiatement (clé invalide, requête refusée).
- Clé absente : message explicite qui nomme la variable à définir.

## Tableau des fournisseurs

Les URL suivent la documentation publique de chaque fournisseur au moment de l'écriture ;
vérifiez-les avant la production (surtout OVHcloud) et remplacez-les si besoin.

| Préfixe | Fournisseur | Protocole | Région | Identifiants |
| --- | --- | --- | --- | --- |
| `anthropic` | Anthropic (Claude) | anthropic | us | `ANTHROPIC_API_KEY` |
| `gemini` | Google Gemini (AI Studio) | gemini | global | `GEMINI_API_KEY`, `GOOGLE_API_KEY` |
| `openai` | OpenAI | openai_compatible | us | `OPENAI_API_KEY` |
| `xai` | xAI (Grok) | openai_compatible | us | `XAI_API_KEY` |
| `mistral` | Mistral AI | openai_compatible | eu | `MISTRAL_API_KEY` |
| `scaleway` | Scaleway Generative APIs | openai_compatible | eu | `SCW_SECRET_KEY` |
| `ovhcloud` | OVHcloud AI Endpoints | openai_compatible | eu | `OVH_AI_ENDPOINTS_ACCESS_TOKEN` |
| `deepseek` | DeepSeek | openai_compatible | cn | `DEEPSEEK_API_KEY` |
| `moonshot` | Moonshot (Kimi) | openai_compatible | cn | `MOONSHOT_API_KEY` |
| `dashscope` | Alibaba DashScope (Qwen) | openai_compatible | cn | `DASHSCOPE_API_KEY` |
| `zai` | Z.AI (GLM) | openai_compatible | cn | `ZAI_API_KEY` |
| `minimax` | MiniMax | openai_compatible | cn | `MINIMAX_API_KEY` |
| `groq` | Groq | openai_compatible | us | `GROQ_API_KEY` |
| `cerebras` | Cerebras | openai_compatible | us | `CEREBRAS_API_KEY` |
| `sambanova` | SambaNova | openai_compatible | us | `SAMBANOVA_API_KEY` |
| `together` | Together AI | openai_compatible | us | `TOGETHER_API_KEY` |
| `fireworks` | Fireworks AI | openai_compatible | us | `FIREWORKS_API_KEY` |
| `deepinfra` | DeepInfra | openai_compatible | us | `DEEPINFRA_API_KEY` |
| `nvidia` | NVIDIA NIM | openai_compatible | us | `NVIDIA_API_KEY` |
| `huggingface` | Hugging Face Inference Providers | openai_compatible | global | `HF_TOKEN`, `HUGGINGFACE_API_KEY` |
| `perplexity` | Perplexity (Sonar) | openai_compatible | us | `PERPLEXITY_API_KEY` |
| `cohere` | Cohere (compatibility API) | openai_compatible | global | `COHERE_API_KEY`, `CO_API_KEY` |
| `github` | GitHub Models | openai_compatible | us | `GITHUB_TOKEN` |
| `openrouter` | OpenRouter | openai_compatible | global | `OPENROUTER_API_KEY` |
| `azure` | Azure OpenAI / Azure AI Foundry | azure_openai | global | `AZURE_OPENAI_API_KEY` |
| `bedrock` | AWS Bedrock | litellm | global | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION_NAME` |
| `vertex_ai` | Google Vertex AI | litellm | global | `VERTEXAI_PROJECT`, `VERTEXAI_LOCATION` |
| `watsonx` | IBM watsonx.ai | litellm | global | `WATSONX_URL`, `WATSONX_APIKEY`, `WATSONX_PROJECT_ID` |
| `ollama` | Ollama | openai_compatible | local | `HIF_OLLAMA_BASE_URL` ou `HIF_ENABLE_OLLAMA=true` |
| `lmstudio` | LM Studio | openai_compatible | local | `HIF_LMSTUDIO_BASE_URL` ou `HIF_ENABLE_LMSTUDIO=true` |
| `vllm` | vLLM server | openai_compatible | local | `HIF_VLLM_BASE_URL` ou `HIF_ENABLE_VLLM=true` |
| `llamacpp` | llama.cpp server | openai_compatible | local | `HIF_LLAMACPP_BASE_URL` ou `HIF_ENABLE_LLAMACPP=true` |
