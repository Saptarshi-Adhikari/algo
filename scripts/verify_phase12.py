"""Phase 12 Verification Suite."""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from app.config.settings import settings
from app.config.safety import assert_paper_trading_only
from app.domain.execution_schemas import CostModel, ExecutionModel
from app.services.execution_calculator import CanonicalExecutionCalculator
from app.backtesting.engine import Backtester
from app.paper_trading.portfolio import PaperPortfolio
from app.data.indian_provider import IndianMarketDataProvider
from app.evaluation.robustness import StrategyRobustnessTester
from app.domain.schemas import StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec

def main():
    print("=" * 55)
    print("  QUANT AI PHASE 12 VERIFICATION SUITE")
    print("=" * 55)

    # 1. Safety Checks
    print("\n-- [TASK 01] Safety & Paper-Only Constraint Audit")
    assert_paper_trading_only()
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
    print("  [OK] Safety constraints intact (PAPER_TRADING_ONLY=True, ALLOW_REAL_BROKER=False)")

    # 2. CostModel & ExecutionModel Schemas
    print("\n-- [TASK 02] CostModel & ExecutionModel Schemas")
    c_model = CostModel(cost_model_id="COST_V1_TEST", commission_bps=3.0, tax_levy_bps=1.0)
    e_model = ExecutionModel(execution_model_id="EXEC_V1_TEST", slippage_bps=1.5, spread_proxy_bps=2.0)
    assert c_model.commission_bps == 3.0
    assert e_model.spread_proxy_bps == 2.0
    print("  [OK] CostModel and ExecutionModel instantiated cleanly")

    # 3. Canonical Execution Calculator
    print("\n-- [TASK 03] Canonical Execution Calculator")
    fill_p, fee, slip, fill_qty, is_rej = CanonicalExecutionCalculator.calculate_entry_execution(
        raw_price=100.0, quantity=100.0, cost_model=c_model, exec_model=e_model
    )
    assert not is_rej
    assert fill_p > 100.0  # Entry penalty (spread + slippage)
    assert fee > 0.0
    print(f"  [OK] Entry Fill: Raw=100.0 -> Fill={fill_p:.4f}, Fee={fee:.4f}, Slippage={slip:.4f}")

    # 4. Backtester Integration
    print("\n-- [TASK 04] Backtester Execution Integration")
    p_ind = IndianMarketDataProvider()
    md_ind = p_ind._generate_synthetic("RELIANCE.NS", "1d")
    spec = StrategySpec(
        strategy_id="STRAT_PHASE12", version="v1", symbol="RELIANCE.NS", market="INDIAN_EQUITY",
        indicators=[IndicatorSpec(name="SMA", params={"period": 10})],
        rules=StrategyRuleSet(entry_rules=[ConditionSpec(left="close", operator=">", right="sma_10")], exit_rules=[])
    )
    bt = Backtester(cost_model=c_model, exec_model=e_model)
    metrics, trades, _ = bt.run(md_ind, spec)
    assert hasattr(bt, "cost_model")
    assert hasattr(bt, "exec_model")
    print(f"  [OK] Backtester executed strategy with CostModel({bt.cost_model.cost_model_id}): {len(trades)} trades")

    # 5. Stress Testing Framework (Idealized, 1x, 2x, 3x)
    print("\n-- [TASK 05] Cost & Execution Stress-Testing Framework")
    stress_res = StrategyRobustnessTester.test_robustness(spec, md_ind)
    assert "idealized_sharpe" in stress_res
    assert "friction_2x_sharpe" in stress_res
    assert "friction_3x_sharpe" in stress_res
    print(f"  [OK] Stress Scenarios Evaluated:")
    print(f"       Idealized Sharpe:   {stress_res['idealized_sharpe']}")
    print(f"       1x Realistic Sharpe:{stress_res['base_sharpe']}")
    print(f"       2x Stress Sharpe:   {stress_res['friction_2x_sharpe']}")
    print(f"       3x Stress Sharpe:   {stress_res['friction_3x_sharpe']}")
    print(f"       Verdict:            {stress_res['verdict']}")

    # 6. Paper Portfolio Consistency
    print("\n-- [TASK 06] Paper Portfolio Safety & Execution Guard")
    portfolio = PaperPortfolio(initial_cash=100000.0)
    pos = portfolio.open_position("RELIANCE.NS", "LONG", fill_price=fill_p, quantity=10.0, fee=fee)
    assert pos.entry_price == fill_p
    print("  [OK] PaperPortfolio instantiated and updated cleanly")

    print("\n" + "=" * 55)
    print("  PHASE 12 VERIFICATION COMPLETE — ALL PASSED")
    print("=" * 55)

if __name__ == "__main__":
    main()
