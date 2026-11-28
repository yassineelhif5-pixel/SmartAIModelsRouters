from __future__ import annotations

from hif.config import Settings


def clear_provider_keys(monkeypatch) -> None:
    for name in (
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
        "GOOGLE_API_KEY", "DEEPSEEK_API_KEY", "MOONSHOT_API_KEY",
        "DASHSCOPE_API_KEY", "XAI_API_KEY", "ZAI_API_KEY", "MINIMAX_API_KEY",
        "MISTRAL_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_catalog_activates_only_configured_providers(monkeypatch) -> None:
    clear_provider_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini")
    monkeypatch.delenv("HIF_MODEL_POOL", raising=False)
    monkeypatch.delenv("HIF_TASK_MODEL_PREFERENCES", raising=False)

    settings = Settings.from_env()

    assert settings.model_pool
    assert all(model.startswith(("openai/", "gemini/")) for model in settings.model_pool)
    assert any(model.startswith("openai/") for model in settings.model_pool)
    assert any(model.startswith("gemini/") for model in settings.model_pool)
    assert all(
        model in settings.model_pool
        for models in settings.task_model_preferences.values()
        for model in models
    )


def test_explicit_model_pool_overrides_starter_catalog(monkeypatch) -> None:
    clear_provider_keys(monkeypatch)
    monkeypatch.setenv("HIF_MODEL_POOL", "openai/custom-model,deepseek/custom-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek")
    monkeypatch.delenv("HIF_TASK_MODEL_PREFERENCES", raising=False)

    settings = Settings.from_env()

    assert settings.model_pool == ("openai/custom-model", "deepseek/custom-model")


def test_no_provider_credentials_keeps_default_pool_empty(monkeypatch) -> None:
    clear_provider_keys(monkeypatch)
    monkeypatch.delenv("HIF_MODEL_POOL", raising=False)
    monkeypatch.delenv("HIF_TASK_MODEL_PREFERENCES", raising=False)

    settings = Settings.from_env()

    assert settings.model_pool == ()
    assert settings.task_model_preferences == {}


def test_explicit_task_preferences_override_defaults(monkeypatch) -> None:
    clear_provider_keys(monkeypatch)
    monkeypatch.setenv("HIF_MODEL_POOL", "openai/custom-model,gemini/custom-model")
    monkeypatch.setenv(
        "HIF_TASK_MODEL_PREFERENCES",
        '{"architecture":["gemini/custom-model"],"coding":["openai/custom-model"]}',
    )

    settings = Settings.from_env()

    assert settings.task_model_preferences == {
        "architecture": ("gemini/custom-model",),
        "coding": ("openai/custom-model",),
    }


def test_architecture_and_infrastructure_are_valid_pipeline_types() -> None:
    from hif.schemas import PlannedNode

    architecture = PlannedNode(
        id="architecture", title="Architecture review", role="assistant_architect",
        instructions="Review the target architecture.", task_type="architecture",
    )
    infrastructure = PlannedNode(
        id="infrastructure", title="Infrastructure review", role="infrastructure_architect",
        instructions="Review the hosting and network design.", task_type="infrastructure",
    )

    assert architecture.task_type == "architecture"
    assert infrastructure.task_type == "infrastructure"


def test_kimi_qwen_and_additional_providers_activate_only_with_credentials(monkeypatch) -> None:
    clear_provider_keys(monkeypatch)
    monkeypatch.setenv("MOONSHOT_API_KEY", "test-moonshot")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-dashscope")
    monkeypatch.setenv("XAI_API_KEY", "test-xai")
    monkeypatch.setenv("ZAI_API_KEY", "test-zai")
    monkeypatch.setenv("MINIMAX_API_KEY", "test-minimax")
    monkeypatch.delenv("HIF_MODEL_POOL", raising=False)
    monkeypatch.delenv("HIF_TASK_MODEL_PREFERENCES", raising=False)

    settings = Settings.from_env()

    providers = {model.split("/", 1)[0] for model in settings.model_pool}
    assert providers == {"moonshot", "dashscope", "xai", "zai", "minimax"}
    assert "moonshot/kimi-latest" in settings.model_pool
    assert "dashscope/qwen-max-latest" in settings.model_pool
    assert all(
        model in settings.model_pool
        for models in settings.task_model_preferences.values()
        for model in models
    )


def test_browser_profile_scales_down_parallelism_and_context(monkeypatch) -> None:
    clear_provider_keys(monkeypatch)
    for name in (
        "HIF_MAX_PARALLEL_TASKS", "HIF_MAX_PROVIDER_PARALLEL",
        "HIF_MAX_LOCAL_THREADS", "HIF_MAX_LOCAL_PROCESSES",
        "HIF_LOCAL_TASK_MEMORY_MB", "HIF_MAX_OUTPUT_TOKENS_PER_TASK",
        "HIF_REQUEST_TIMEOUT_SECONDS", "HIF_MAX_CONTEXT_CHARS",
        "HIF_MIN_FREE_MEMORY_MB", "HIF_MODEL_POOL",
        "HIF_TASK_MODEL_PREFERENCES",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("HIF_EXECUTION_PROFILE", "browser")

    settings = Settings.from_env()

    assert settings.execution_profile == "browser"
    assert settings.max_parallel_tasks == 1
    assert settings.max_provider_parallel == 1
    assert settings.max_local_threads == 1
    assert settings.max_context_chars == 6000
    assert settings.max_output_tokens_per_task == 900
