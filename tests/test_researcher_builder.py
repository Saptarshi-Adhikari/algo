"""Unit tests for ResearcherAgent and StrategyBuilderAgent."""
import pytest
from app.agents.researcher import ResearcherAgent
from app.agents.builder import StrategyBuilderAgent
from app.llm.mock_provider import MockLLMProvider
from app.domain.schemas import HypothesisSpec, StrategySpec

def test_researcher_agent():
    mock_llm = MockLLMProvider()
    researcher = ResearcherAgent(llm=mock_llm)
    hyp = researcher.propose_hypothesis(symbol="RELIANCE.NS", regime="TRENDING")

    assert isinstance(hyp, HypothesisSpec)
    assert hyp.title != ""

def test_strategy_builder_agent():
    mock_llm = MockLLMProvider()
    builder = StrategyBuilderAgent(llm=mock_llm)
    hyp = HypothesisSpec(
        hypothesis_id="HYP_TEST_001",
        title="RSI Cross test",
        rationale="Buy when oversold",
        differs_from_failures="Added stop loss"
    )

    strat = builder.build_strategy(hyp, strategy_version="v1", symbol="EURUSD=X", market="FOREX")
    assert isinstance(strat, StrategySpec)
    assert strat.symbol == "EURUSD=X"
    assert strat.market == "FOREX"
    assert strat.version == "v1"
    assert strat.hypothesis_id == "HYP_TEST_001"
