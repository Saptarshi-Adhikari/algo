"""Strategy Robustness & Sensitivity Testing Module."""
from typing import Dict, Any, List
import pandas as pd
from app.domain.schemas import StrategySpec
from app.backtesting.engine import Backtester
from app.data.base_provider import MarketData

class StrategyRobustnessTester:
    """Evaluates strategy sensitivity under IDEALIZED, 1X_REALISTIC, 2X_STRESS, and 3X_STRESS friction scenarios."""

    @staticmethod
    def test_robustness(
        spec: StrategySpec,
        data: MarketData,
        base_backtester: Backtester = None
    ) -> Dict[str, Any]:
        from app.domain.execution_schemas import CostModel, ExecutionModel

        # 0. Idealized (0 fees, 0 slippage, 0 spread)
        c0 = CostModel(cost_model_id="COST_IDEAL", commission_bps=0.0)
        e0 = ExecutionModel(execution_model_id="EXEC_IDEAL", execution_mode="IDEALIZED", slippage_bps=0.0, spread_proxy_bps=0.0)
        bt0 = Backtester(cost_model=c0, exec_model=e0)
        m0, _, _ = bt0.run(data, spec, data_split="DEVELOPMENT")

        # 1. Base realistic (1x baseline cost: 3 bps fee, 1 bps slippage, 2 bps spread)
        backtester = base_backtester or Backtester()
        m1, _, _ = backtester.run(data, spec, data_split="DEVELOPMENT")

        # 2. Stress Test A: 2x Friction (6 bps fee, 2 bps slippage, 4 bps spread)
        c2 = CostModel(cost_model_id="COST_2X", commission_bps=6.0)
        e2 = ExecutionModel(execution_model_id="EXEC_2X", execution_mode="STRESS", slippage_bps=2.0, spread_proxy_bps=4.0)
        bt2 = Backtester(cost_model=c2, exec_model=e2)
        m2, _, _ = bt2.run(data, spec, data_split="DEVELOPMENT")

        # 3. Stress Test B: 3x Friction (9 bps fee, 3 bps slippage, 6 bps spread)
        c3 = CostModel(cost_model_id="COST_3X", commission_bps=9.0)
        e3 = ExecutionModel(execution_model_id="EXEC_3X", execution_mode="STRESS", slippage_bps=3.0, spread_proxy_bps=6.0)
        bt3 = Backtester(cost_model=c3, exec_model=e3)
        m3, _, _ = bt3.run(data, spec, data_split="DEVELOPMENT")

        sharpe_drop_2x = m1.sharpe_ratio - m2.sharpe_ratio
        sharpe_drop_3x = m1.sharpe_ratio - m3.sharpe_ratio

        # 1. Friction Stability: Does performance degrade rapidly under cost stress?
        is_friction_stable = (sharpe_drop_2x <= 0.5) and (sharpe_drop_3x <= 1.0)

        # 2. Strategy Quality / Profitability: Is the strategy actually profitable with positive Sharpe?
        is_profitable = (m1.total_return_pct > 0.0) and (m1.sharpe_ratio > 0.5)

        if is_friction_stable and is_profitable:
            verdict = "ROBUST_PROMOTABLE"
        elif is_friction_stable:
            verdict = "FRICTION_STABLE_UNPROFITABLE"
        else:
            verdict = "BRITTLE_SENSITIVE"

        return {
            "strategy_id": spec.strategy_id,
            "idealized_sharpe": round(m0.sharpe_ratio, 2),
            "idealized_return_pct": round(m0.total_return_pct, 2),
            "base_sharpe": round(m1.sharpe_ratio, 2),
            "friction_2x_sharpe": round(m2.sharpe_ratio, 2),
            "friction_3x_sharpe": round(m3.sharpe_ratio, 2),
            "base_return_pct": round(m1.total_return_pct, 2),
            "friction_2x_return_pct": round(m2.total_return_pct, 2),
            "friction_3x_return_pct": round(m3.total_return_pct, 2),
            "sharpe_drop_2x": round(sharpe_drop_2x, 2),
            "sharpe_drop_3x": round(sharpe_drop_3x, 2),
            "is_friction_stable": is_friction_stable,
            "is_profitable": is_profitable,
            "is_brittle": not is_friction_stable,
            "verdict": verdict
        }

