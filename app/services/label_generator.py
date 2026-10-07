"""Deterministic Ground-Truth Decision Label Generator."""
import pandas as pd
from typing import Optional
from app.data.base_provider import MarketData
from app.domain.decision_schemas import GroundTruthOutcome, DirectionChoice, TradePermissionChoice, RiskChoice

class GroundTruthLabelGenerator:
    """Derives deterministic ground-truth outcome labels strictly from future bars (T+1 to T+H)."""

    @staticmethod
    def generate_label(
        data: MarketData,
        bar_index: int,
        horizon_bars: int = 4,
        buy_threshold_pct: float = 0.5,
        sell_threshold_pct: float = -0.5
    ) -> Optional[GroundTruthOutcome]:
        total_bars = len(data.df)
        if bar_index < 0 or bar_index >= total_bars:
            raise ValueError(f"Bar index {bar_index} out of bounds.")

        # Check if full horizon exists in future observations
        end_bar_index = bar_index + horizon_bars
        if end_bar_index >= total_bars:
            return None  # Cannot construct ground truth without full future horizon

        current_row = data.df.iloc[bar_index]
        future_slice = data.df.iloc[bar_index + 1 : end_bar_index + 1]

        t_close = float(current_row["close"])
        future_close = float(future_slice.iloc[-1]["close"])
        future_high_max = float(future_slice["high"].max())
        future_low_min = float(future_slice["low"].min())

        realized_return_pct = ((future_close - t_close) / t_close) * 100.0
        mfe_pct = ((future_high_max - t_close) / t_close) * 100.0
        mae_pct = ((future_low_min - t_close) / t_close) * 100.0

        # Deterministic label policy
        if realized_return_pct >= buy_threshold_pct:
            direction: DirectionChoice = "BUY"
        elif realized_return_pct <= sell_threshold_pct:
            direction: DirectionChoice = "SELL"
        else:
            direction: DirectionChoice = "HOLD"

        risk: RiskChoice = "HIGH" if abs(mae_pct) > 2.0 else ("MEDIUM" if abs(mae_pct) > 1.0 else "LOW")
        permission: TradePermissionChoice = "REJECT" if risk == "HIGH" else "ALLOW"

        return GroundTruthOutcome(
            decision_timestamp=str(current_row["timestamp"]),
            evaluation_horizon_bars=horizon_bars,
            future_observation_end_timestamp=str(future_slice.iloc[-1]["timestamp"]),
            direction_outcome=direction,
            trade_permission_outcome=permission,
            risk_outcome=risk,
            realized_return_pct=round(realized_return_pct, 4),
            max_favorable_excursion_pct=round(mfe_pct, 4),
            max_adverse_excursion_pct=round(mae_pct, 4),
            target_hit=mfe_pct >= abs(buy_threshold_pct * 2.0),
            stop_hit=mae_pct <= -abs(buy_threshold_pct * 2.0),
            label_policy_version="1.0.0"
        )
