"""Unit tests for SQLite Memory Repository."""
import pytest
from app.memory.sqlite_db import Database
from app.memory.repository import ExperimentRepository
from app.domain.schemas import ExperimentRecord, BacktestMetrics, StrategySpec, StrategyRuleSet

@pytest.fixture
def repo(temp_dir):
    db_file = temp_dir / "test_exp.db"
    db = Database(db_path=db_file)
    return ExperimentRepository(database=db)

def create_sample_record(exp_id: str, verdict: str = "KEEP_FOR_PAPER_TESTING", regime: str = "TRENDING"):
    metrics = BacktestMetrics(
        total_return_pct=10.0,
        annualized_return_pct=12.0,
        sharpe_ratio=1.5,
        max_drawdown_pct=-5.0,
        win_rate=0.6,
        trade_count=20,
        average_win=100.0,
        average_loss=-50.0,
        profit_factor=2.0,
        data_split="DEVELOPMENT"
    )
    return ExperimentRecord(
        experiment_id=exp_id,
        hypothesis=f"Hypothesis for {exp_id}",
        strategy_version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        timeframe="1d",
        data_period="2023-01-01 to 2023-12-31",
        data_split="DEVELOPMENT",
        metrics=metrics,
        fees_assumed=0.0003,
        slippage_assumed=0.0001,
        critic_verdict=verdict,
        critic_reasoning="Good performance",
        market_regime=regime,
        lesson_learned="Trend following works",
        status="PASSED" if verdict == "KEEP_FOR_PAPER_TESTING" else "REJECTED"
    )

def test_insert_and_get_experiment(repo):
    rec = create_sample_record("EXP_TEST_1")
    repo.insert_experiment(rec)

    fetched = repo.get_experiment("EXP_TEST_1")
    assert fetched is not None
    assert fetched.experiment_id == "EXP_TEST_1"
    assert fetched.metrics.sharpe_ratio == 1.5

def test_filtering_and_stats(repo):
    repo.insert_experiment(create_sample_record("EXP_1", "KEEP_FOR_PAPER_TESTING", "TRENDING"))
    repo.insert_experiment(create_sample_record("EXP_2", "REJECT", "HIGH_VOLATILITY"))
    repo.insert_experiment(create_sample_record("EXP_3", "RETEST", "RANGING"))

    passed = repo.get_successful_experiments()
    assert len(passed) == 1
    assert passed[0].experiment_id == "EXP_1"

    failed = repo.get_failed_experiments()
    assert len(failed) == 1
    assert failed[0].experiment_id == "EXP_2"

    stats = repo.get_summary_statistics()
    assert stats["total_experiments"] == 3
    assert stats["passed_count"] == 1
    assert stats["rejected_count"] == 1
    assert stats["retest_count"] == 1
