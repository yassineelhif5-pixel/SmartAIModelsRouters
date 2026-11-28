from __future__ import annotations

from hif.config import Settings


def clear_provider_keys(monkeypatch) -> None:
    for name in (
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
        "GOOGLE_API_KEY", "DEEPSEEK_API_KEY",
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
