"""Full End-to-End System Integration Test."""
import pytest
from app.memory.sqlite_db import Database
from app.memory.repository import ExperimentRepository
from app.data.replay_provider import ReplayDataProvider
from app.data.splitter import DataSplitter
from app.evaluation.regime import RegimeClassifier
from app.agents.researcher import ResearcherAgent
from app.agents.builder import StrategyBuilderAgent
from app.agents.critic import CriticAgent
from app.agents.memory_agent import MemoryAgent
from app.backtesting.engine import Backtester
from app.paper_trading.portfolio import PaperPortfolio
from app.paper_trading.engine import PaperExecutionEngine
from app.llm.mock_provider import MockLLMProvider

def test_full_e2e_research_and_paper_trading_pipeline(temp_dir):
    # 1. Memory DB
    db = Database(db_path=temp_dir / "e2e.db")
    repo = ExperimentRepository(database=db)

    # 2. Data Provider & Splitter
    provider = ReplayDataProvider(regime="TRENDING", num_bars=200)
    data = provider.fetch_ohlcv("SYNTHETIC_IND", "1d")
    splits = DataSplitter().split(data)
    dev_data = splits["DEVELOPMENT"]
    val_data = splits["VALIDATION"]

    # 3. Regime Classifier
    regime = RegimeClassifier.classify_dataset(dev_data)
    assert regime in ["TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY"]

    # 4. LLM & Agents
    llm = MockLLMProvider()
    researcher = ResearcherAgent(llm=llm, repository=repo)
    builder = StrategyBuilderAgent(llm=llm)
    critic = CriticAgent(llm=llm)
    memory_agent = MemoryAgent(repository=repo)

    # 5. Pipeline Step: Propose Hypothesis & Build Strategy
    hyp = researcher.propose_hypothesis("SYNTHETIC_IND", regime)
    spec = builder.build_strategy(hyp, strategy_version="v1", symbol="SYNTHETIC_IND")

    # 6. Backtest on DEV and VAL sets
    backtester = Backtester()
    dev_metrics, dev_trades, _ = backtester.run(dev_data, spec, "DEVELOPMENT")
    val_metrics, val_trades, _ = backtester.run(val_data, spec, "VALIDATION")

    assert dev_metrics.data_split == "DEVELOPMENT"
    assert val_metrics.data_split == "VALIDATION"

    # 7. Critic Evaluation
    evaluation = critic.evaluate(val_metrics, spec, regime)
    assert evaluation.verdict in ["REJECT", "RETEST", "KEEP_FOR_PAPER_TESTING"]

    # 8. Memory Agent Logging
    rec = memory_agent.record_experiment("EXP_E2E_001", hyp, spec, val_metrics, evaluation, regime)
    assert rec.experiment_id == "EXP_E2E_001"
    assert repo.get_experiment("EXP_E2E_001") is not None

    # 9. Paper Portfolio Execution Simulation
    portfolio = PaperPortfolio(initial_cash=100000.0)
    paper_engine = PaperExecutionEngine(portfolio)

    pos = paper_engine.execute_order("SYNTHETIC_IND", "BUY", market_price=100.0, quantity=10.0)
    assert pos.symbol == "SYNTHETIC_IND"

    trade = paper_engine.execute_order("SYNTHETIC_IND", "SELL", market_price=105.0, quantity=10.0)
    assert trade.pnl > 0.0
    assert len(portfolio.closed_trades) == 1
