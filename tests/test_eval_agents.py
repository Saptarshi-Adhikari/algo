"""Unit tests for Reviewer, Critic, MemoryAgent, and NextExperimentAgent."""
import pytest
from app.agents.reviewer import BacktestReviewerAgent
from app.agents.critic import CriticAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.next_experiment import NextExperimentAgent
from app.llm.mock_provider import MockLLMProvider
from app.domain.schemas import BacktestMetrics, StrategySpec, StrategyRuleSet, HypothesisSpec
from app.memory.sqlite_db import Database
from app.memory.repository import ExperimentRepository

@pytest.fixture
def test_repo(temp_dir):
    db = Database(db_path=temp_dir / "eval_agents.db")
    return ExperimentRepository(database=db)

@pytest.fixture
def sample_metrics():
    return BacktestMetrics(
        total_return_pct=15.0,
        annualized_return_pct=18.0,
        sharpe_ratio=1.6,
        max_drawdown_pct=-7.5,
        win_rate=0.6,
        trade_count=25,
        average_win=120.0,
        average_loss=-60.0,
        profit_factor=2.0,
        data_split="DEVELOPMENT"
    )

@pytest.fixture
def sample_spec():
    return StrategySpec(
        strategy_id="STRAT_EVAL_V1",
        version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        rules=StrategyRuleSet()
    )

def test_reviewer_summary(sample_metrics):
    reviewer = BacktestReviewerAgent()
    summary = reviewer.summarize(sample_metrics, [])
    assert summary["trade_count"] == 25
    assert summary["has_adequate_trades"] is True
    assert "15.00%" in summary["summary_text"]

def test_critic_hard_rules(sample_spec):
    critic = CriticAgent(llm=MockLLMProvider())

    # Low trades hard rule
    low_trade_metrics = BacktestMetrics(
        total_return_pct=5.0, annualized_return_pct=5.0, sharpe_ratio=1.0,
        max_drawdown_pct=-2.0, win_rate=1.0, trade_count=2, average_win=10.0,
        average_loss=0.0, profit_factor=99.0, data_split="DEVELOPMENT"
    )
    eval_res = critic.evaluate(low_trade_metrics, sample_spec)
    assert eval_res.verdict == "REJECT"
    assert eval_res.has_adequate_trades is False

def test_memory_and_next_exp(test_repo, sample_metrics, sample_spec):
    memory_agent = MemoryAgent(repository=test_repo)
    next_exp_agent = NextExperimentAgent()

    mock_hyp = HypothesisSpec(
        hypothesis_id="HYP_001",
        title="Test Hyp",
        rationale="Test rationale",
        differs_from_failures="None"
    )

    mock_llm = MockLLMProvider()
    critic = CriticAgent(llm=mock_llm)
    eval_res = critic.evaluate(sample_metrics, sample_spec)

    rec = memory_agent.record_experiment("EXP_TEST_EV", mock_hyp, sample_spec, sample_metrics, eval_res)
    assert rec.experiment_id == "EXP_TEST_EV"

    action, reason = next_exp_agent.decide_next_step(eval_res.verdict, sample_spec)
    assert action in ["NEW_HYPOTHESIS", "RETEST_VARIATION", "ROLLBACK_PARENT"]
