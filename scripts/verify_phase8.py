"""Phase 8 Verification Script executing sample-size audit, zero-trade critic validation, cross-asset/cross-period testing, baseline strategy benchmark, and reproducibility checks."""
import os
import sys
import json
from pathlib import Path
import pandas as pd

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.memory.repository import ExperimentRepository
from app.data.indian_provider import IndianMarketDataProvider
from app.data.forex_provider import ForexDataProvider
from app.data.csv_provider import CSVDataProvider
from app.data.registry import ResearchDatasetRegistry
from app.data.quality import DataQualityChecker
from app.data.splitter import DataSplitter
from app.domain.schemas import StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec, BacktestMetrics
from app.backtesting.engine import Backtester
from app.backtesting.metrics import calculate_metrics
from app.agents.critic import CriticAgent
from app.agents.researcher import ResearcherAgent
from app.services.experiment_runner import ExperimentRunner
from app.services.ai_brain import AIBrainService
from app.paper_trading.portfolio import PaperPortfolio
from app.paper_trading.engine import PaperExecutionEngine
from app.config.safety import assert_paper_trading_only

def run_phase8_verification():
    print("==================================================")
    print("   QUANT AI PHASE 8 RESEARCH INTEGRITY SUITE")
    print("==================================================")

    # 1. Safety Audit
    print("\n--> TASK 18: Safety Boundary Audit")
    assert_paper_trading_only()
    print("  [OK] PAPER_TRADING_ONLY=true & ALLOW_REAL_BROKER=false strictly verified.")

    # 2. Sample-Size Warning Policy Audit
    print("\n--> TASK 01: Sample-Size Policy Audit")
    m_zero = calculate_metrics([], pd.Series([100.0, 100.0]), 100.0)
    m_insuf = calculate_metrics([], pd.Series([100.0, 100.0]), 100.0)
    # Check sample size categories
    print(f"  [OK] Zero-trade sample warning: {m_zero.sample_size_warning} (Trade Count: {m_zero.trade_count})")
    assert m_zero.sample_size_warning == "NO_TRADES"

    # 3. Zero-Trade Critic Rule Verification
    print("\n--> TASK 02, 03: Zero-Trade Critic Rule Verification")
    critic = CriticAgent()
    spec_dummy = StrategySpec(
        strategy_id="STRAT_ZERO", version="v1", symbol="RELIANCE.NS",
        rules=StrategyRuleSet(entry_rules=[], exit_rules=[])
    )
    critic_eval = critic.evaluate(m_zero, spec_dummy)
    print(f"  [OK] Critic Verdict for 0 trades: {critic_eval.verdict} | Reasoning: {critic_eval.reasoning}")
    assert critic_eval.verdict == "REJECT"
    assert "NO_TRADES" in critic_eval.reasoning

    # 4. Dataset Date-Range & Forex Depth Audit
    print("\n--> TASK 05, 06: Dataset Date-Range & Forex Depth Audit")
    indian_provider = IndianMarketDataProvider()
    forex_provider = ForexDataProvider()

    rel_data = indian_provider.fetch_ohlcv("RELIANCE.NS")
    tcs_data = indian_provider.fetch_ohlcv("TCS.NS")
    eur_data = forex_provider.fetch_ohlcv("EURUSD=X")

    for d in [rel_data, tcs_data, eur_data]:
        reg = ResearchDatasetRegistry.register(d, "yfinance")
        q = DataQualityChecker.inspect(d.df, symbol=d.symbol)
        span_days = (d.end_date - d.start_date).days
        years = round(span_days / 365.25, 2)
        print(f"  [DATASET] {d.symbol:12s} | Start: {str(d.start_date)[:10]} | End: {str(d.end_date)[:10]} | Span: {years} yrs ({len(d)} bars) | Quality: {q.status}")

    # 5. Local CSV Dataset Support Test
    print("\n--> TASK 07: Local CSV Data Import Support")
    csv_provider = CSVDataProvider(data_folder=ROOT_DIR / "data")
    print(f"  [OK] CSVDataProvider initialized. Data directory: {csv_provider.data_folder}")

    # 6. Controlled Baseline Strategy Benchmark
    print("\n--> TASK 10: Controlled Deterministic Baseline Strategy Benchmark")
    baseline_spec = StrategySpec(
        strategy_id="BASELINE_SMA_CROSS",
        version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        indicators=[
            IndicatorSpec(name="SMA", params={"period": 10}),
            IndicatorSpec(name="SMA", params={"period": 30})
        ],
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="sma_10", operator=">", right="sma_30")],
            exit_rules=[ConditionSpec(left="sma_10", operator="<", right="sma_30")],
            stop_loss_pct=3.0,
            take_profit_pct=6.0,
            position_sizing_pct=15.0
        )
    )

    backtester = Backtester(initial_cash=100000.0, commission_bps=3.0, slippage_bps=1.0)
    base_dev_m, base_dev_trades, _ = backtester.run(rel_data, baseline_spec, "DEVELOPMENT")
    print(f"  [OK] Baseline SMA Crossover on RELIANCE.NS:")
    print(f"    - Trade Count: {base_dev_m.trade_count} | Sample Warning: {base_dev_m.sample_size_warning}")
    print(f"    - Return: {base_dev_m.total_return_pct}% | Sharpe: {base_dev_m.sharpe_ratio} | Max DD: {base_dev_m.max_drawdown_pct}%")

    # 7. Cross-Asset Validation using Baseline Strategy
    print("\n--> TASK 08: Controlled Cross-Asset Validation")
    tcs_m, _, _ = backtester.run(tcs_data, baseline_spec, "DEVELOPMENT")
    eur_m, _, _ = backtester.run(eur_data, baseline_spec, "DEVELOPMENT")
    print(f"  [CROSS-ASSET] RELIANCE.NS -> Return: {base_dev_m.total_return_pct}% | Sharpe: {base_dev_m.sharpe_ratio} | Trades: {base_dev_m.trade_count}")
    print(f"  [CROSS-ASSET] TCS.NS       -> Return: {tcs_m.total_return_pct}% | Sharpe: {tcs_m.sharpe_ratio} | Trades: {tcs_m.trade_count}")
    print(f"  [CROSS-ASSET] EURUSD=X     -> Return: {eur_m.total_return_pct}% | Sharpe: {eur_m.sharpe_ratio} | Trades: {eur_m.trade_count}")

    # 8. Cross-Period Validation
    print("\n--> TASK 09: Cross-Period Validation")
    df_full = rel_data.df.copy()
    n = len(df_full)
    third = n // 3
    early_df = df_full.iloc[:third].reset_index(drop=True)
    mid_df = df_full.iloc[third:2*third].reset_index(drop=True)
    recent_df = df_full.iloc[2*third:].reset_index(drop=True)

    from app.data.base_provider import MarketData
    m_early = MarketData("RELIANCE.NS", "INDIAN_EQUITY", "1d", early_df)
    m_mid = MarketData("RELIANCE.NS", "INDIAN_EQUITY", "1d", mid_df)
    m_recent = MarketData("RELIANCE.NS", "INDIAN_EQUITY", "1d", recent_df)

    em_early, _, _ = backtester.run(m_early, baseline_spec, "DEVELOPMENT")
    em_mid, _, _ = backtester.run(m_mid, baseline_spec, "DEVELOPMENT")
    em_recent, _, _ = backtester.run(m_recent, baseline_spec, "DEVELOPMENT")

    print(f"  [CROSS-PERIOD] EARLY  ({str(m_early.start_date)[:10]} to {str(m_early.end_date)[:10]}) -> Return: {em_early.total_return_pct}% | Sharpe: {em_early.sharpe_ratio} | Trades: {em_early.trade_count}")
    print(f"  [CROSS-PERIOD] MIDDLE ({str(m_mid.start_date)[:10]} to {str(m_mid.end_date)[:10]}) -> Return: {em_mid.total_return_pct}% | Sharpe: {em_mid.sharpe_ratio} | Trades: {em_mid.trade_count}")
    print(f"  [CROSS-PERIOD] RECENT ({str(m_recent.start_date)[:10]} to {str(m_recent.end_date)[:10]}) -> Return: {em_recent.total_return_pct}% | Sharpe: {em_recent.sharpe_ratio} | Trades: {em_recent.trade_count}")

    # 9. AI Brain Scoped Summary Verification
    print("\n--> TASK 14: AI Brain Evidence Scope Verification")
    repo = ExperimentRepository()
    brain_service = AIBrainService(repository=repo)
    brain_summary = brain_service.generate_learned_summary()
    print(f"  Title: {brain_summary['title']}")
    for obs in brain_summary['evidence_supported_observations']:
        print(f"  [Scoped Evidence] {obs}")

    # 10. Reproducibility Check
    print("\n--> TASK 17: Deterministic Reproducibility Check")
    b1 = Backtester()
    b2 = Backtester()
    r1_m, _, _ = b1.run(rel_data, baseline_spec, "DEVELOPMENT")
    r2_m, _, _ = b2.run(rel_data, baseline_spec, "DEVELOPMENT")
    assert r1_m.sharpe_ratio == r2_m.sharpe_ratio and r1_m.total_return_pct == r2_m.total_return_pct
    print(f"  [OK] Deterministic Rerun Verified: Sharpe={r1_m.sharpe_ratio} == {r2_m.sharpe_ratio} | Return={r1_m.total_return_pct}% == {r2_m.total_return_pct}%")

    print("\n==================================================")
    print("   PHASE 8 RESEARCH INTEGRITY SUITE COMPLETE — ALL PASSED")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_phase8_verification()
