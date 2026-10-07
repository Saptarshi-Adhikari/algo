"""Canonical Cost and Execution Calculator for Phase 12."""
import math
from typing import Tuple, Dict, Any, Optional
import pandas as pd
from app.domain.execution_schemas import CostModel, ExecutionModel

class CanonicalExecutionCalculator:
    """Calculates net execution price, transaction costs, fees, slippage, and liquidity fills cleanly across backtest, replay, and paper portfolio."""

    @staticmethod
    def calculate_entry_execution(
        raw_price: float,
        quantity: float,
        cost_model: CostModel,
        exec_model: ExecutionModel,
        bar_volume: Optional[float] = None
    ) -> Tuple[float, float, float, float, bool]:
        """Calculates entry fill details: (fill_price, fee, slippage_val, fill_qty, is_rejected)."""
        if raw_price <= 0 or quantity <= 0:
            return 0.0, 0.0, 0.0, 0.0, True

        # Liquidity / Fill Constraint Check
        fill_qty = quantity
        is_rejected = False
        if exec_model.liquidity_mode == "MAX_BAR_VOLUME_PCT" and bar_volume is not None and bar_volume > 0:
            max_qty = bar_volume * (exec_model.max_bar_volume_pct / 100.0)
            if fill_qty > max_qty:
                fill_qty = max_qty
                if fill_qty <= 0:
                    is_rejected = True

        if is_rejected:
            return 0.0, 0.0, 0.0, 0.0, True

        # Calculate Spread + Slippage penalty on entry (Buying at Ask price)
        half_spread_bps = exec_model.spread_proxy_bps / 2.0
        total_entry_penalty_bps = half_spread_bps + exec_model.slippage_bps
        penalty_rate = total_entry_penalty_bps / 10000.0

        fill_price = raw_price * (1.0 + penalty_rate)
        slippage_val = raw_price * penalty_rate * fill_qty

        # Calculate Commission + Tax Fee
        gross_value = fill_price * fill_qty
        total_fee_bps = cost_model.commission_bps + cost_model.tax_levy_bps
        fee = max(gross_value * (total_fee_bps / 10000.0), cost_model.minimum_charge)

        return round(fill_price, 4), round(fee, 4), round(slippage_val, 4), round(fill_qty, 4), False

    @staticmethod
    def calculate_exit_execution(
        entry_price: float,
        raw_exit_price: float,
        quantity: float,
        cost_model: CostModel,
        exec_model: ExecutionModel,
        bar_volume: Optional[float] = None
    ) -> Tuple[float, float, float, float, float, float]:
        """Calculates exit fill details: (fill_price, fee, slippage_val, gross_pnl, net_pnl, return_pct)."""
        if raw_exit_price <= 0 or quantity <= 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        # Calculate Spread + Slippage penalty on exit (Selling at Bid price)
        half_spread_bps = exec_model.spread_proxy_bps / 2.0
        total_exit_penalty_bps = half_spread_bps + exec_model.slippage_bps
        penalty_rate = total_exit_penalty_bps / 10000.0

        fill_price = raw_exit_price * (1.0 - penalty_rate)
        slippage_val = raw_exit_price * penalty_rate * quantity

        # Calculate Commission + Tax Fee on Exit
        gross_exit_value = fill_price * quantity
        total_fee_bps = cost_model.commission_bps + cost_model.tax_levy_bps
        fee = max(gross_exit_value * (total_fee_bps / 10000.0), cost_model.minimum_charge)

        entry_gross_cost = entry_price * quantity
        gross_pnl = (fill_price - entry_price) * quantity
        net_pnl = gross_pnl - fee

        return_pct = (net_pnl / entry_gross_cost * 100.0) if entry_gross_cost > 0 else 0.0

        return (
            round(fill_price, 4),
            round(fee, 4),
            round(slippage_val, 4),
            round(gross_pnl, 2),
            round(net_pnl, 2),
            round(return_pct, 4)
        )
