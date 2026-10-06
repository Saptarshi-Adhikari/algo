"""Unit tests for bounded ExperimentRunner execution."""
import pytest
from app.services.experiment_runner import ExperimentRunner
from app.memory.sqlite_db import Database
from app.memory.repository import ExperimentRepository
from app.data.replay_provider import ReplayDataProvider

@pytest.fixture
def runner(temp_dir):
    db = Database(db_path=temp_dir / "runner_test.db")
    repo = ExperimentRepository(database=db)
    provider = ReplayDataProvider(regime="TRENDING", num_bars=200)
    return ExperimentRunner(repository=repo, data_provider=provider)

def test_bounded_loop_execution(runner):
    results = runner.run_experiments(symbol="SYNTHETIC_IND", max_experiments=3)

    assert len(results) == 3
    for r in results:
        assert r.experiment_id.startswith("EXP_SYNTHETIC_IND_")
        assert r.metrics is not None
        assert r.critic_verdict in ["REJECT", "RETEST", "KEEP_FOR_PAPER_TESTING"]

    # Verify database persistence
    stored = runner.repository.get_all_experiments()
    assert len(stored) == 3
