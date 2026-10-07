"""Deterministic Causal MarketState Snapshot Generation Service."""
import pandas as pd
from typing import Optional, Dict, Any
from app.data.base_provider import MarketData
from app.domain.decision_schemas import MarketState
from app.strategies.indicators import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_atr
)

class StateSnapshotBuilder:
    """Generates a causal MarketState snapshot for a given bar index T.
    
    Guarantees:
    - Uses only rows <= T. No future data is accessible.
    - Causal indicator calculations.
    """

    @staticmethod
    def build_snapshot(
        data: MarketData,
        bar_index: int,
        dataset_id: str,
        regime: str = "UNKNOWN"
    ) -> MarketState:
        if bar_index < 0 or bar_index >= len(data.df):
            raise ValueError(f"Bar index {bar_index} out of range [0, {len(data.df)-1}].")

        # Causal historical slice up to bar_index
        sub_df = data.df.iloc[: bar_index + 1].copy()
        current_row = sub_df.iloc[-1]
        ts_str = str(current_row["timestamp"])

        # Compute causal indicators on historical slice
        sma_10_val = float(calculate_sma(sub_df, 10).iloc[-1]) if len(sub_df) >= 10 else None
        sma_20_val = float(calculate_sma(sub_df, 20).iloc[-1]) if len(sub_df) >= 20 else None
        sma_50_val = float(calculate_sma(sub_df, 50).iloc[-1]) if len(sub_df) >= 50 else None

        ema_10_val = float(calculate_ema(sub_df, 10).iloc[-1]) if len(sub_df) >= 10 else None
        ema_20_val = float(calculate_ema(sub_df, 20).iloc[-1]) if len(sub_df) >= 20 else None

        rsi_14_val = float(calculate_rsi(sub_df, 14).iloc[-1]) if len(sub_df) >= 15 else None

        macd_line_val, macd_signal_val, macd_hist_val = None, None, None
        if len(sub_df) >= 26:
            macd_dict = calculate_macd(sub_df)
            macd_line_val = float(macd_dict["macd"].iloc[-1])
            macd_signal_val = float(macd_dict["macd_signal"].iloc[-1])
            macd_hist_val = float(macd_dict["macd_hist"].iloc[-1])

        bb_u, bb_m, bb_l = None, None, None
        if len(sub_df) >= 20:
            bb_dict = calculate_bollinger_bands(sub_df, period=20)
            bb_u = float(bb_dict["bb_upper"].iloc[-1])
            bb_m = float(bb_dict["bb_middle"].iloc[-1])
            bb_l = float(bb_dict["bb_lower"].iloc[-1])

        atr_14_val = float(calculate_atr(sub_df, 14).iloc[-1]) if len(sub_df) >= 15 else None
        volatility_pct = (atr_14_val / float(current_row["close"]) * 100.0) if (atr_14_val and float(current_row["close"]) > 0) else None

        trend_dir = "SIDEWAYS"
        if sma_10_val and sma_20_val:
            if sma_10_val > sma_20_val:
                trend_dir = "UP"
            elif sma_10_val < sma_20_val:
                trend_dir = "DOWN"

        return MarketState(
            symbol=data.symbol,
            market=data.market,
            timeframe=data.timeframe,
            timestamp=ts_str,
            dataset_id=dataset_id,
            dataset_hash=data.dataset_hash,
            open=float(current_row["open"]),
            high=float(current_row["high"]),
            low=float(current_row["low"]),
            close=float(current_row["close"]),
            volume=float(current_row["volume"]),
            sma_10=sma_10_val,
            sma_20=sma_20_val,
            sma_50=sma_50_val,
            ema_10=ema_10_val,
            ema_20=ema_20_val,
            rsi_14=rsi_14_val,
            macd_line=macd_line_val,
            macd_signal=macd_signal_val,
            macd_hist=macd_hist_val,
            bb_upper=bb_u,
            bb_middle=bb_m,
            bb_lower=bb_l,
            atr_14=atr_14_val,
            regime=regime,
            volatility_atr_pct=volatility_pct,
            trend_direction=trend_dir,
            state_version="1.0.0"
        )
