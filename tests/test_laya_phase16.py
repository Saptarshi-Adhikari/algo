"""Unit and integration tests for Phase 16 Laya Shadow Status Engine & Research Integrity Audit."""
import pytest
from app.config.settings import settings
from app.domain.laya_phase16_schemas import (
    DataAvailabilityStatus, CollectionStatus, EvidenceStatus, CalibrationStatus, DriftStatus
)
from app.services.data_availability_gate import DataAvailabilityGate
from app.services.laya_shadow_collector import LayaShadowCollectorService

def test_data_availability_gate_freshness(tmp_path):
    gate = DataAvailabilityGate()
    
    # Test Cases A & B: Phase 15 cutoff timestamp audit
    assert gate.is_timestamp_fresh("2026-09-10T00:00:00Z", "RELIANCE.NS", "INDIAN_EQUITY", "1d") is False
    assert gate.is_timestamp_fresh("2026-10-08T00:00:00Z", "RELIANCE.NS", "INDIAN_EQUITY", "1d") is True
    
    report = gate.audit_data_availability()
    assert report.data_availability_status in list(DataAvailabilityStatus)

def test_instrument_normalization():
    gate = DataAvailabilityGate()
    assert gate.normalize_symbol("BTC/USDT") == "BTC-USD"
    assert gate.normalize_symbol("BTC-USD") == "BTC-USD"
    assert gate.normalize_symbol("RELIANCE.NS") == "RELIANCE.NS"

def test_status_independence_and_sufficiency(tmp_path):
    storage_file = tmp_path / "test_shadow_records.json"
    collector = LayaShadowCollectorService(storage_path=storage_file)
    
    # Single resolved trade setup
    pred = collector.collect_fresh_prediction(
        symbol="BTC/USDT", asset_class="CRYPTO", timeframe="1h",
        predicted_direction="BUY", timestamp="2026-10-08T12:00:00Z"
    )
    collector.resolve_delayed_outcome(
        prediction_id=pred.prediction_id, ground_truth_direction="BUY",
        raw_return=0.02, net_return=0.018
    )
    
    assessment = collector.generate_assessment()
    
    # 1. Instrument Normalization stored
    assert pred.canonical_symbol == "BTC-USD"
    assert pred.source_symbol == "BTC/USDT"
    
    # 2. Metric Sufficiency: Single trade must NOT produce a Sharpe ratio
    assert assessment.trade_count == 1
    assert "NOT_AVAILABLE" in str(assessment.sharpe_ratio)
    
    # 3. Fresh Calibration Status: Single trade must set INSUFFICIENT_EVIDENCE
    assert assessment.fresh_calibration_status == CalibrationStatus.INSUFFICIENT_EVIDENCE
    assert assessment.fresh_calibrated_ece == "NOT_AVAILABLE"
    
    # 4. Drift Status: Single trade must set INSUFFICIENT_EVIDENCE
    assert assessment.data_drift_status == DriftStatus.INSUFFICIENT_EVIDENCE
    assert assessment.prediction_drift_status == DriftStatus.INSUFFICIENT_EVIDENCE
    
    # 5. Independence: Pausing collector preserves evidence state
    collector.collection_status = CollectionStatus.PAUSED
    collector.evidence_status = EvidenceStatus.LIMITED_EVIDENCE
    paused_assessment = collector.generate_assessment()
    assert paused_assessment.collection_status == CollectionStatus.PAUSED
    assert paused_assessment.evidence_status == EvidenceStatus.LIMITED_EVIDENCE

def test_safety_audit():
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
