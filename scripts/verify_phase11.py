"""Phase 11 System Verification Suite."""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from app.config.settings import settings
from app.config.safety import assert_paper_trading_only
from app.data.indian_provider import IndianMarketDataProvider
from app.data.crypto_provider import CryptoDataProvider
from app.data.forex_provider import ForexDataProvider
from app.data.gold_provider import GoldDataProvider
from app.services.dataset_builder import HistoricalDatasetBuilder
from app.memory.decision_repository import DecisionRepository
from app.evaluation.leakage_auditor import DatasetLeakageAuditor
from app.evaluation.benchmark_engine import BenchmarkEvaluator
from app.evaluation.laya_exporter import LayaDatasetExporter

def main():
    print("=" * 55)
    print("  QUANT AI PHASE 11 VERIFICATION SUITE")
    print("=" * 55)

    # 1. Safety Checks
    print("\n-- [TASK 01] Safety & Paper-Only Constraint Audit")
    assert_paper_trading_only()
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
    print("  [OK] Safety constraints intact (PAPER_TRADING_ONLY=True, ALLOW_REAL_BROKER=False)")

    # 2. Setup Repository
    repo = DecisionRepository()
    repo.clear()
    print("  [OK] DecisionRepository SQLite table initialized and reset")

    # 3. Process Indian Market Data
    print("\n-- [TASK 02] Historical Decision Dataset Building (Indian Equity)")
    p_ind = IndianMarketDataProvider()
    md_ind = p_ind._generate_synthetic("RELIANCE.NS", "1d")
    builder = HistoricalDatasetBuilder(repo=repo)
    recs_ind = builder.build_dataset_for_market_data(md_ind, horizon_bars=4)
    assert len(recs_ind) > 0
    print(f"  [OK] Indian Equity ({md_ind.symbol}): Generated {len(recs_ind)} decision records")

    # 4. Process Crypto Market Data
    print("\n-- [TASK 03] Historical Decision Dataset Building (Crypto)")
    p_cr = CryptoDataProvider()
    md_cr = p_cr._generate_synthetic("BTC/USDT", "1d")
    recs_cr = builder.build_dataset_for_market_data(md_cr, horizon_bars=4)
    assert len(recs_cr) > 0
    print(f"  [OK] Crypto ({md_cr.symbol}): Generated {len(recs_cr)} decision records")

    # 5. Process Forex Market Data
    print("\n-- [TASK 04] Historical Decision Dataset Building (Forex)")
    p_fx = ForexDataProvider()
    md_fx = p_fx._generate_synthetic("EURUSD=X", "1d")
    recs_fx = builder.build_dataset_for_market_data(md_fx, horizon_bars=4)
    assert len(recs_fx) > 0
    print(f"  [OK] Forex ({md_fx.symbol}): Generated {len(recs_fx)} decision records")

    # 6. Data Leakage & Quality Audit
    print("\n-- [TASK 05] Dataset Leakage & Quality Audit")
    all_recs = repo.list_all(limit=5000)
    audit_res = DatasetLeakageAuditor.audit_records(all_recs)
    print(f"  Total Records: {audit_res['total_records']}")
    print(f"  Future Leakage: {audit_res['future_leakage_count']}")
    print(f"  Duplicates: {audit_res['duplicate_record_count']}")
    print(f"  Invalid Labels: {audit_res['invalid_label_count']}")
    assert audit_res["audit_passed"] is True
    print("  [OK] Leakage Audit PASSED: 0 future leakage, 0 duplicates, 0 invalid labels")

    # 7. Benchmark Evaluation Engine
    print("\n-- [TASK 06] Benchmark Evaluation Engine")
    bench_res = BenchmarkEvaluator.evaluate_decisions(all_recs)
    print(f"  Evaluations: {bench_res['total_evaluations']}")
    print(f"  Class Counts: {bench_res['class_counts']}")
    print(f"  Split Counts: {bench_res['split_counts']}")
    assert bench_res["total_evaluations"] > 0
    print("  [OK] Benchmark Engine evaluated decision dataset successfully")

    # 8. Laya Dataset Exporter
    print("\n-- [TASK 07] Laya-Compatible Dataset Exporter")
    jsonl_str = LayaDatasetExporter.export_dataset_jsonl(all_recs[:5])
    lines = [l for l in jsonl_str.split("\n") if l.strip()]
    assert len(lines) == 5
    first_case = LayaDatasetExporter.export_record_to_laya_case(all_recs[0])
    assert "state" in first_case
    assert "questions" in first_case
    assert "gold" in first_case
    print(f"  [OK] Exported {len(lines)} sample Laya cases (state, questions, gold structure verified)")

    print("\n" + "=" * 55)
    print("  PHASE 11 VERIFICATION COMPLETE — ALL PASSED")
    print("=" * 55)

if __name__ == "__main__":
    main()
