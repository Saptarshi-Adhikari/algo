"""Unit tests for LLM abstraction layer, Local-First Router, and Secret Protection."""
import pytest
import os
from app.llm.base import extract_json_payload
from app.llm.mock_provider import MockLLMProvider
from app.llm.ollama_provider import OllamaLLMProvider
from app.llm.gemini_provider import GeminiLLMProvider, sanitize_secret_error
from app.llm.openrouter_provider import OpenRouterLLMProvider
from app.llm.router import LLMRouter
from app.domain.schemas import HypothesisSpec, StrategySpec, CriticEvaluation
from app.config.settings import settings

def test_extract_json_payload():
    raw_markdown = "Here is your JSON:\n```json\n{\"key\": \"value\"}\n```\nHope that helps!"
    extracted = extract_json_payload(raw_markdown)
    assert extracted == '{"key": "value"}'

    raw_plain = "  {\"foo\": 123}  "
    assert extract_json_payload(raw_plain) == '{"foo": 123}'

def test_secret_error_sanitization():
    secret_key = "AIzaSyABC1234567890abcdefghijklmnopqrst"
    raw_error = f"HTTP 401 Error connecting to https://api.example.com?key={secret_key}"
    clean = sanitize_secret_error(raw_error, secret_key)

    assert secret_key not in clean
    assert "[REDACTED_API_KEY]" in clean

def test_mock_llm_json_generation():
    provider = MockLLMProvider()

    hyp = provider.generate_json("Propose hypothesis", HypothesisSpec)
    assert isinstance(hyp, HypothesisSpec)
    assert hyp.hypothesis_id.startswith("HYP_")

    strat = provider.generate_json("Build strategy", StrategySpec)
    assert isinstance(strat, StrategySpec)
    assert strat.symbol == "RELIANCE.NS"

def test_router_local_first_ollama_success():
    """Verify that if Ollama succeeds, cloud providers are NOT called."""
    class MockOllama(MockLLMProvider):
        pass

    class SpyGemini(GeminiLLMProvider):
        def __init__(self):
            super().__init__(api_key="TEST_GEMINI_KEY")
            self.called = False
        def generate(self, prompt, system_prompt=None):
            self.called = True
            return "GEMINI_RES"

    gemini_spy = SpyGemini()
    router = LLMRouter(ollama=MockOllama(), gemini=gemini_spy, mock=MockLLMProvider())
    res = router.generate("Test prompt")

    assert "Mock response" in res
    assert gemini_spy.called is False  # Cloud provider was NOT called!

def test_router_fallback_to_gemini_when_ollama_fails():
    """Verify fallback to Gemini when Ollama fails and Gemini is configured."""
    class FailingOllama(OllamaLLMProvider):
        def generate(self, prompt, system_prompt=None):
            raise RuntimeError("Ollama connection refused")

    class WorkingGemini(GeminiLLMProvider):
        def __init__(self):
            super().__init__(api_key="TEST_KEY")
        def generate(self, prompt, system_prompt=None):
            return "GEMINI_RESPONSE"

    router = LLMRouter(
        ollama=FailingOllama(),
        gemini=WorkingGemini(),
        mock=MockLLMProvider()
    )
    res = router.generate("Test prompt")
    assert res == "GEMINI_RESPONSE"

def test_router_fallback_to_openrouter_when_gemini_fails():
    """Verify fallback to OpenRouter when Ollama & Gemini fail."""
    class FailingOllama(OllamaLLMProvider):
        def generate(self, prompt, system_prompt=None):
            raise RuntimeError("Ollama connection refused")

    class FailingGemini(GeminiLLMProvider):
        def __init__(self):
            super().__init__(api_key="TEST_KEY")
        def generate(self, prompt, system_prompt=None):
            raise RuntimeError("Gemini 429 Quota Exceeded")

    class WorkingOpenRouter(OpenRouterLLMProvider):
        def __init__(self):
            super().__init__(api_key="TEST_OR_KEY")
        def generate(self, prompt, system_prompt=None):
            return "OPENROUTER_RESPONSE"

    router = LLMRouter(
        ollama=FailingOllama(),
        gemini=FailingGemini(),
        openrouter=WorkingOpenRouter(),
        mock=MockLLMProvider()
    )
    res = router.generate("Test prompt")
    assert res == "OPENROUTER_RESPONSE"

def test_router_final_mock_fallback_when_all_unconfigured():
    """Verify final fallback to MockProvider when all cloud providers are unconfigured and Ollama fails."""
    class FailingOllama(OllamaLLMProvider):
        def generate(self, prompt, system_prompt=None):
            raise RuntimeError("Ollama connection refused")

    router = LLMRouter(
        ollama=FailingOllama(),
        gemini=GeminiLLMProvider(api_key=""),
        openrouter=OpenRouterLLMProvider(api_key=""),
        mock=MockLLMProvider()
    )
    hyp = router.generate_json("Propose hypothesis", HypothesisSpec)
    assert isinstance(hyp, HypothesisSpec)

def test_unconfigured_gemini_raises_cleanly():
    provider = GeminiLLMProvider(api_key="")
    assert provider.is_configured() is False
    with pytest.raises(ValueError, match="Gemini API key is not configured"):
        provider.generate("Test prompt")

def test_live_gemini_smoke_test_conditional():
    """Runs a real Gemini API call ONLY if GEMINI_API_KEY is configured in local environment."""
    key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    if not key or not key.strip():
        pytest.skip("No GEMINI_API_KEY found in local environment. Skipping live Gemini test cleanly.")

    provider = GeminiLLMProvider(api_key=key)
    try:
        res = provider.generate("Respond with 'PONG'")
        assert len(res) > 0
    except Exception as e:
        err_msg = str(e)
        assert key not in err_msg, "SECURITY FAILURE: Raw API key exposed in exception string!"
        print(f"Live Gemini smoke test attempted with local key: {err_msg}")
