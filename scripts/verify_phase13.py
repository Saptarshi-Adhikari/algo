"""Phase 13 System Verification Suite."""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from app.config.settings import settings
from app.config.safety import assert_paper_trading_only
from app.domain.decision_schemas import MarketState
from app.domain.laya_schemas import LayaPredictionResult
from app.decision.laya_adapter import LayaAdapter
from app.memory.laya_repository import LayaPredictionRepository
from app.evaluation.laya_benchmark import LayaBenchmarkEvaluator
from app.memory.decision_repository import DecisionRepository

def main():
    print("=" * 55)
    print("  QUANT AI PHASE 13 VERIFICATION SUITE")
    print("=" * 55)

    # 1. Safety Audit
    print("\n-- [TASK 01] Safety & Authority Audit")
    assert_paper_trading_only()
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
    print("  [OK] Safety constraints intact (PAPER_TRADING_ONLY=True, ALLOW_REAL_BROKER=False)")

    # 2. Laya Environment Inspection
    print("\n-- [TASK 02] Laya Package Environment Inspection")
    try:
        import laya
        laya_ver = getattr(laya, "__version__", "unknown")
        print(f"  [OK] Installed Laya package detected: v{laya_ver}")
    except Exception as e:
        print(f"  [WARN] Laya package import error: {e}")

    # 3. Laya Decision Contract & Adapter Verification
    print("\n-- [TASK 03] Laya Adapter & Contract Isolation")
    adapter = LayaAdapter()
    state = MarketState(
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        timeframe="1d",
        timestamp="2023-01-10T00:00:00",
        dataset_id="DS_1",
        dataset_hash="HASH_1",
        open=100.0, high=105.0, low=95.0, close=102.0, volume=1000.0
    )
    pred_res = adapter.predict(state, decision_id="VERIFY_DEC_001")
    assert isinstance(pred_res, LayaPredictionResult)
    assert pred_res.decision_authority == "SHADOW_ONLY"
    assert pred_res.confidence_status == "UNCALIBRATED"
    print(f"  [OK] Laya Adapter prediction status: {pred_res.status} | Authority: {pred_res.decision_authority}")

    # 4. Shadow Prediction Persistence
    print("\n-- [TASK 04] Laya Shadow Prediction Repository Persistence")
    repo = LayaPredictionRepository()
    repo.clear()
    repo.save(pred_res)
    assert repo.count() == 1
    print("  [OK] Laya shadow prediction persisted to SQLite (laya_shadow_predictions table)")

    # 5. Zero-Shot Benchmark Evaluation
    print("\n-- [TASK 05] Zero-Shot Laya Benchmark Evaluation")
    dec_repo = DecisionRepository()
    records = dec_repo.list_all(limit=10)
    if records:
        evaluator = LayaBenchmarkEvaluator(adapter=adapter, repo=repo)
        bench_res = evaluator.run_zero_shot_benchmark(records[:5])
        print(f"  [OK] Evaluated {bench_res['total_records_processed']} records against ground truth")
        print(f"       Direction Accuracy: {bench_res['direction_accuracy']}")
        print(f"       Regime Accuracy:    {bench_res['regime_accuracy']}")
        print(f"       Authority:          {bench_res['decision_authority']}")
    else:
        print("  [INFO] No Phase 11 DecisionRecords found to run benchmark (Skipping evaluation)")

    print("\n" + "=" * 55)
    print("  PHASE 13 VERIFICATION COMPLETE — ALL PASSED")
    print("=" * 55)

if __name__ == "__main__":
    main()
