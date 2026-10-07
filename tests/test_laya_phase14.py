"""Unit tests for Phase 14 Laya Domain Dataset Quality and Readiness."""
import pytest
import json
from pathlib import Path
from app.domain.decision_schemas import DecisionRecord, GroundTruthOutcome, MarketState
from app.decision.laya_target_policy import LayaTargetPolicy, TARGET_POLICY_VERSION
from app.evaluation.laya_target_audit import LayaTargetAuditor
from app.data.laya_dataset_generator import LayaDatasetGenerator

@pytest.fixture
def sample_decision_record():
    return DecisionRecord(
        decision_id="TEST_DEC_001",
        timestamp="2026-01-01T10:00:00Z",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        timeframe="1d",
        dataset_id="DS_TEST",
        dataset_hash="hash123",
        data_split="DEVELOPMENT",
        state=MarketState(
            timestamp="2026-01-01T10:00:00Z",
            symbol="RELIANCE.NS",
            market="INDIAN_EQUITY",
            timeframe="1d",
            dataset_id="DS_TEST",
            dataset_hash="hash123",
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
            regime="TRENDING",
            features={"volatility_20d": 0.015, "rsi_14": 55.0}
        ),
        ground_truth=GroundTruthOutcome(
            decision_id="TEST_DEC_001",
            decision_timestamp="2026-01-01T10:00:00Z",
            future_observation_end_timestamp="2026-01-02T10:00:00Z",
            evaluation_timestamp="2026-01-02T10:00:00Z",
            direction_outcome="BUY",
            realized_return_pct=1.2,
            max_favorable_excursion_pct=1.5,
            max_adverse_excursion_pct=-0.2
        )
    )

def test_laya_target_policy(sample_decision_record):
    gold = LayaTargetPolicy.compute_gold_targets(sample_decision_record)
    soft = LayaTargetPolicy.compute_soft_distribution(sample_decision_record)

    assert gold["direction_v2"] == "BUY"
    assert gold["market_regime_v2"] == "TRENDING"
    assert gold["target_policy_version"] == TARGET_POLICY_VERSION

    dir_dist = soft["direction_v2"]
    assert abs(sum(dir_dist.values()) - 1.0) < 1e-5
    assert dir_dist["BUY"] > dir_dist["SELL"]

def test_laya_target_audit(sample_decision_record):
    auditor = LayaTargetAuditor()
    res = auditor.audit_target_quality([sample_decision_record])
    assert res["audit_passed"] is True
    assert res["causal_leakage_count"] == 0
    assert res["invalid_probability_sums"] == 0

def test_dataset_generator_manifest(tmp_path, sample_decision_record, monkeypatch):
    class MockRepo:
        def list_by_split(self, split):
            if split == "DEVELOPMENT":
                return [sample_decision_record] * 10
            elif split == "VALIDATION":
                return [sample_decision_record] * 3
            elif split == "HOLDOUT":
                return [sample_decision_record] * 2
            return []

    gen = LayaDatasetGenerator(output_dir=tmp_path, repo=MockRepo())
    manifest = gen.generate_all_splits()

    assert manifest["record_counts"]["train"] == 8
    assert manifest["record_counts"]["calibration"] == 2
    assert manifest["record_counts"]["validation"] == 3
    assert manifest["record_counts"]["holdout"] == 2
    assert manifest["fine_tuning_executed"] is False
    assert manifest["decision_authority"] == "SHADOW_ONLY"
