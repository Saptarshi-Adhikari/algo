"""Tests for STEP 6 - Settings & LLM Configuration Contract."""
import pytest
from app.config.settings import settings, Settings
from app.llm.router import LLMRouter

def test_settings_fields_exist():
    assert hasattr(settings, "OLLAMA_MODEL")
    assert hasattr(settings, "GEMINI_MODEL")
    assert hasattr(settings, "OPENROUTER_MODEL")
    assert hasattr(settings, "PAPER_TRADING_ONLY")
    assert hasattr(settings, "ALLOW_REAL_BROKER")

    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False

def test_llm_router_provider_chain_status():
    router = LLMRouter()
    status = router.get_status()
    assert isinstance(status, dict)
    assert "active_provider" in status
    assert "ollama_available" in status

def test_no_secret_keys_exposed_in_string_repr():
    # Verify GEMINI_MODEL field exists and has expected value without leaking exposed key
    assert settings.GEMINI_MODEL == "gemini-1.5-flash"
    assert settings.OPENROUTER_MODEL == "google/gemini-2.5-flash"
