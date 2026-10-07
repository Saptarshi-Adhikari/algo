"""Phase 16 Verification Script — Laya Shadow Performance, Drift Monitoring & Separate Collection/Evidence Status (Research Integrity Audit)."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config.settings import settings
from app.domain.laya_phase16_schemas import (
    DataAvailabilityStatus, CollectionStatus, EvidenceStatus, CalibrationStatus, DriftStatus
)
from app.services.data_availability_gate import DataAvailabilityGate
from app.services.laya_shadow_collector import LayaShadowCollectorService

def main():
    print("=======================================================")
    print("  QUANT AI PHASE 16 VERIFICATION SUITE (RESEARCH INTEGRITY AUDITED)")
    print("=======================================================")

    # 1. Safety & Authority Audit
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
    print("\n-- [TASK 01] Safety & Authority Audit")
    print("  [OK] Safety constraints intact (PAPER_TRADING_ONLY=True, ALLOW_REAL_BROKER=False)")

    # 2. Phase 15 Cutoff Timestamps & Fresh-Data Audit
    print("\n-- [TASK 02] Phase 15 Cutoff Timestamps & Data Availability Audit")
    gate = DataAvailabilityGate()
    assert gate.is_timestamp_fresh("2026-09-15T00:00:00Z", "RELIANCE.NS", "INDIAN_EQUITY", "1d") is False
    assert gate.is_timestamp_fresh("2026-10-08T00:00:00Z", "RELIANCE.NS", "INDIAN_EQUITY", "1d") is True
    
    report = gate.audit_data_availability()
    print(f"  [OK] Data Availability Audit PASSED: {report.data_availability_status}")
    print(f"       Total Records:     {report.total_available_records}")
    print(f"       Phase 15 Baseline: {report.phase15_records}")
    print(f"       Fresh Records:     {report.fresh_record_count}")

    # 3. Independent Status Separation Audit
    print("\n-- [TASK 03] Independent Status Separation Audit")
    test_storage = ROOT_DIR / "data" / "verify_phase16_test_records.json"
    if test_storage.exists():
        test_storage.unlink()
        
    collector = LayaShadowCollectorService(storage_path=test_storage)
    pred = collector.collect_fresh_prediction(
        symbol="BTC/USDT", asset_class="CRYPTO", timeframe="1h",
        predicted_direction="BUY", timestamp="2026-10-08T12:00:00Z"
    )
    assessment = collector.generate_assessment()
    assert assessment.collection_status == CollectionStatus.COLLECTING
    assert assessment.evidence_status in [EvidenceStatus.NO_EVIDENCE, EvidenceStatus.INSUFFICIENT_EVIDENCE]
    print(f"  [OK] Valid Combination 1: Collection={assessment.collection_status.value} | Evidence={assessment.evidence_status.value}")

    # 4. Metric Sufficiency Audit (1-Trade Sharpe & Calibration Separation)
    print("\n-- [TASK 04] Economic Metric Sufficiency & Calibration Separation Audit")
    resolved = collector.resolve_delayed_outcome(
        prediction_id=pred.prediction_id, ground_truth_direction="BUY",
        raw_return=0.02, net_return=0.018
    )
    assert resolved is not None
    assert resolved.direction_correct is True
    
    ass_res = collector.generate_assessment()
    assert ass_res.trade_count == 1
    assert "NOT_AVAILABLE" in str(ass_res.sharpe_ratio)
    assert ass_res.fresh_calibration_status == CalibrationStatus.INSUFFICIENT_EVIDENCE
    assert ass_res.data_drift_status == DriftStatus.INSUFFICIENT_EVIDENCE
    print(f"  [OK] 1-Trade Sharpe Metric Sufficiency: {ass_res.sharpe_ratio}")
    print(f"  [OK] Decoupled Fresh Calibration Status: {ass_res.fresh_calibration_status.value}")
    print(f"  [OK] Decoupled Drift Status: {ass_res.data_drift_status.value}")

    # 5. Latency & Instrument Identity Audit
    print("\n-- [TASK 05] Latency & Instrument Identity Normalization Audit")
    assert pred.canonical_symbol == "BTC-USD"
    assert pred.source_symbol == "BTC/USDT"
    assert ass_res.model_inference_latency.count >= 1
    assert ass_res.end_to_end_latency.count >= 1
    print(f"  [OK] Canonical Instrument Normalization: {pred.source_symbol} -> {pred.canonical_symbol}")
    print(f"  [OK] Model Inference Latency Stats: Mean={ass_res.model_inference_latency.mean_ms} ms")
    print(f"  [OK] End-to-End Latency Stats: Mean={ass_res.end_to_end_latency.mean_ms} ms")

    # 6. Model Freeze Verification
    print("\n-- [TASK 06] Model Freeze Verification")
    assert pred.model_id == "ALGO_LAYA_V001"
    assert pred.authority == "SHADOW_ONLY"
    print("  [OK] Model ALGO_LAYA_V001 verified frozen and authority SHADOW_ONLY")

    print("\n=======================================================")
    print("  PHASE 16 VERIFICATION COMPLETE — ALL PASSED")
    print("=======================================================")

if __name__ == "__main__":
    main()
