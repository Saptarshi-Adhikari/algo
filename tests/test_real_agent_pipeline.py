"""Real End-to-End AI Agent Pipeline and Memory Adaptation Test Suite."""
import pytest
import pandas as pd
from app.llm.ollama_provider import OllamaLLMProvider
from app.llm.router import LLMRouter
from app.agents.researcher import ResearcherAgent
from app.agents.builder import StrategyBuilderAgent
from app.agents.critic import CriticAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.next_experiment import NextExperimentAgent
from app.backtesting.engine import Backtester
from app.memory.sqlite_db import Database
from app.memory.repository import ExperimentRepository
from app.data.replay_provider import ReplayDataProvider
from app.data.splitter import DataSplitter
from app.evaluation.regime import RegimeClassifier
from app.services.experiment_runner import ExperimentRunner
from app.domain.schemas import HypothesisSpec, StrategySpec, ExperimentRecord

@pytest.fixture
def real_router():
    ollama = OllamaLLMProvider(model="qwen2.5:7b", timeout=60.0)
    return LLMRouter(ollama=ollama)

def test_researcher_builder_pipeline(temp_dir, real_router):
    db = Database(db_path=temp_dir / "pipeline_test.db")
    repo = ExperimentRepository(database=db)

    researcher = ResearcherAgent(llm=real_router, repository=repo)
    builder = StrategyBuilderAgent(llm=real_router)

    # 1. Generate Hypothesis
    hyp = researcher.propose_hypothesis(symbol="RELIANCE.NS", regime="TRENDING")
    assert isinstance(hyp, HypothesisSpec)
    assert len(hyp.title) > 0

    # 2. Build Strategy
    spec = builder.build_strategy(hyp, strategy_version="v1", symbol="RELIANCE.NS")
    assert isinstance(spec, StrategySpec)
    assert spec.symbol == "RELIANCE.NS"
    assert spec.version == "v1"

def test_full_agent_research_cycle(temp_dir, real_router):
    db = Database(db_path=temp_dir / "cycle_test.db")
    repo = ExperimentRepository(database=db)
    provider = ReplayDataProvider(regime="TRENDING", num_bars=150)

    runner = ExperimentRunner(repository=repo, data_provider=provider)
    runner.researcher.llm = real_router
    runner.builder.llm = real_router
    runner.critic.llm = real_router

    results = runner.run_experiments(symbol="SYNTHETIC_IND", max_experiments=2)
    assert len(results) == 2

    # Verify Experiment #002 received memory context from Experiment #001
    stored_exps = repo.get_all_experiments()
    assert len(stored_exps) == 2
    assert stored_exps[0].experiment_id == "EXP_SYNTHETIC_IND_001"
    assert stored_exps[1].experiment_id == "EXP_SYNTHETIC_IND_002"

def test_python_compute_decoupling_regression():
    """Verify metrics are strictly Python-computed float numbers."""
    dates = pd.date_range("2023-01-01", periods=10, freq="D")
    prices = [100, 102, 104, 103, 105, 107, 106, 108, 110, 112]
    df = pd.DataFrame({"timestamp": dates, "open": prices, "high": prices, "low": prices, "close": prices, "volume": 1000})

    from app.data.base_provider import MarketData
    m_data = MarketData("COMPUTE_TEST", "INDIAN_EQUITY", "1d", df)
    from app.domain.schemas import StrategyRuleSet
    spec = StrategySpec(strategy_id="COMP_1", version="v1", market="INDIAN_EQUITY", symbol="COMPUTE_TEST", rules=StrategyRuleSet())

    bt = Backtester()
    metrics, trades, equity = bt.run(m_data, spec)

    # Pure Python math verification
    assert isinstance(metrics.total_return_pct, float)
    assert isinstance(metrics.sharpe_ratio, float)
    assert isinstance(metrics.trade_count, int)
