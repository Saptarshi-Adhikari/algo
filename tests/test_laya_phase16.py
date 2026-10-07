"""Unit and integration tests for Phase 16 Laya Shadow Status Engine and Data Availability Gate."""
import pytest
from app.config.settings import settings
from app.domain.laya_phase16_schemas import (
    DataAvailabilityStatus, CollectionStatus, EvidenceStatus, CalibrationStatus
)
from app.services.data_availability_gate import DataAvailabilityGate
from app.services.laya_shadow_collector import LayaShadowCollectorService

def test_data_availability_gate(tmp_path):
    gate = DataAvailabilityGate()
    report = gate.audit_data_availability()
    assert report.status in list(DataAvailabilityStatus)

def test_status_independence(tmp_path):
    storage_file = tmp_path / "test_shadow_records.json"
    collector = LayaShadowCollectorService(storage_path=storage_file)
    
    # Verify starting state
    assert collector.collection_status == CollectionStatus.NOT_STARTED
    
    # Collect fresh predictions
    collector.collect_fresh_prediction(symbol="INFY.NS", asset_class="INDIAN_EQUITY", timeframe="1d", predicted_direction="BUY")
    assessment = collector.generate_assessment()
    
    # Collection status must become COLLECTING
    assert assessment.collection_status == CollectionStatus.COLLECTING
    
    # Explicitly pause collection and verify evidence status is NOT wiped
    collector.collection_status = CollectionStatus.PAUSED
    collector.evidence_status = EvidenceStatus.LIMITED_EVIDENCE
    
    paused_assessment = collector.generate_assessment()
    assert paused_assessment.collection_status == CollectionStatus.PAUSED
    assert paused_assessment.evidence_status == EvidenceStatus.LIMITED_EVIDENCE

def test_delayed_outcome_resolution(tmp_path):
    storage_file = tmp_path / "test_shadow_records.json"
    collector = LayaShadowCollectorService(storage_path=storage_file)
    
    pred = collector.collect_fresh_prediction(symbol="BTC-USD", asset_class="CRYPTO", timeframe="1h", predicted_direction="SELL")
    res = collector.resolve_delayed_outcome(prediction_id=pred.prediction_id, ground_truth_direction="SELL", raw_return=-0.03, net_return=-0.031)
    
    assert res is not None
    assert res.resolved is True
    assert res.direction_correct is True

def test_safety_audit():
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
