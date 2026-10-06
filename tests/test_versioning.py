"""Unit tests for StrategyVersionManager."""
import pytest
from app.strategies.versioning import StrategyVersionManager
from app.domain.schemas import StrategySpec, StrategyRuleSet
from app.memory.sqlite_db import Database
from app.memory.repository import ExperimentRepository

@pytest.fixture
def version_manager(temp_dir):
    db = Database(db_path=temp_dir / "version_test.db")
    repo = ExperimentRepository(database=db)
    return StrategyVersionManager(repository=repo)

def test_version_registration_and_rollback(version_manager):
    v1_spec = StrategySpec(
        strategy_id="STRAT_V1",
        version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        rules=StrategyRuleSet()
    )
    version_manager.register_version(v1_spec, "ACTIVE")

    v2_spec = StrategySpec(
        strategy_id="STRAT_V2",
        version="v2",
        parent_version_id="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        rules=StrategyRuleSet()
    )
    version_manager.register_version(v2_spec, "REJECTED")

    # Verify rollback to parent
    parent = version_manager.rollback_to_parent(v2_spec)
    assert parent == "v1"

    # Baseline has no parent
    assert version_manager.rollback_to_parent(v1_spec) is None
