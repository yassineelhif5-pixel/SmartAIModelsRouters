from __future__ import annotations

from hif.config import Settings
from hif.model_manager import AIModelManager


def test_model_manager_exposes_primary_and_ordered_fallbacks(tmp_path) -> None:
    settings = Settings(
        database_path=tmp_path / "models.sqlite3",
        model_pool=(
            "openai/gpt-6-astra",
            "anthropic/claude-sonnet-5-5",
        ),
    )

    manager = AIModelManager(settings)
    status = manager.status()

    assert status["strategy"] == "ordered_fallback"
    assert status["primary"] == "openai/gpt-6-astra"
    assert status["fallbacks"] == ["anthropic/claude-sonnet-5-5"]
    assert [item["role"] for item in status["models"]] == ["primary", "fallback"]


def test_model_manager_reports_credential_presence_without_exposing_values(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-secret")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    settings = Settings(
        database_path=tmp_path / "models.sqlite3",
        model_pool=(
            "openai/gpt-6-astra",
            "anthropic/claude-sonnet-5-5",
        ),
    )

    providers = {
        item["provider"]: item for item in AIModelManager(settings).status()["providers"]
    }

    assert providers["openai"]["credential_configured"] is True
    assert providers["anthropic"]["credential_configured"] is False
    assert "test-openai-secret" not in str(providers)
