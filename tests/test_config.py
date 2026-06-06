import pytest

from cli_tool.core import config


def test_required_env_trims_value(monkeypatch):
    config.load_environment.cache_clear()
    monkeypatch.setenv("OPENAI_API_KEY", "  test-key  ")

    assert config.get_openai_api_key() == "test-key"


def test_required_env_rejects_blank_value(monkeypatch):
    config.load_environment.cache_clear()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")

    with pytest.raises(RuntimeError, match="Missing ANTHROPIC_API_KEY"):
        config.get_anthropic_api_key()


def test_model_falls_back_when_blank(monkeypatch):
    config.load_environment.cache_clear()
    monkeypatch.setenv("OPENAI_MODEL", "   ")

    assert config.get_openai_model() == "gpt-4.1-mini"
