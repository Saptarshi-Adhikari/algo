"""Unit tests for LLM abstraction layer."""
import pytest
from app.llm.base import extract_json_payload
from app.llm.mock_provider import MockLLMProvider
from app.llm.router import LLMRouter
from app.domain.schemas import HypothesisSpec, StrategySpec, CriticEvaluation

def test_extract_json_payload():
    raw_markdown = "Here is your JSON:\n```json\n{\"key\": \"value\"}\n```\nHope that helps!"
    extracted = extract_json_payload(raw_markdown)
    assert extracted == '{"key": "value"}'

    raw_plain = "  {\"foo\": 123}  "
    assert extract_json_payload(raw_plain) == '{"foo": 123}'

def test_mock_llm_json_generation():
    provider = MockLLMProvider()

    hyp = provider.generate_json("Propose hypothesis", HypothesisSpec)
    assert isinstance(hyp, HypothesisSpec)
    assert hyp.hypothesis_id.startswith("HYP_")

    strat = provider.generate_json("Build strategy", StrategySpec)
    assert isinstance(strat, StrategySpec)
    assert strat.symbol == "RELIANCE.NS"

def test_router_fallback():
    class FailingProvider(MockLLMProvider):
        def generate(self, prompt: str, system_prompt: str = None) -> str:
            raise RuntimeError("Connection timed out")

    router = LLMRouter(primary=FailingProvider(), fallback=MockLLMProvider())
    hyp = router.generate_json("Propose hypothesis", HypothesisSpec)
    assert isinstance(hyp, HypothesisSpec)
