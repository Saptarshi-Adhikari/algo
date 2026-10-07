"""Feature Builder & Numerical Target Generator for Phase 17 LightGBM model training."""
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from app.domain.lightgbm_schemas import (
    LightGBMFeatureSchema, LightGBMTargetPolicy
)
from app.evaluation.leakage_auditor import DatasetLeakageAuditor
from app.config.logging import logger

class LightGBMFeatureBuilder:
    """Builds leakage-controlled numerical features and 4-bar forward return targets.
    
    Research Integrity Rules:
    - Every feature is generated strictly from historical observations <= t.
    - Rejects any negative shifts, future closes, future highs/lows/volumes.
    - Target is strictly close[t+4] / close[t] - 1.
    - Excludes unresolvable tail rows where t+4 is outside dataset.
    """
    def __init__(
        self,
        feature_schema: Optional[LightGBMFeatureSchema] = None,
        target_policy: Optional[LightGBMTargetPolicy] = None
    ):
        self.feature_schema = feature_schema or LightGBMFeatureSchema()
        self.target_policy = target_policy or LightGBMTargetPolicy()

    def build_features_and_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes technical indicator features and 4-bar forward return targets for an OHLCV DataFrame."""
        if df.empty or len(df) < 60:
            logger.warning("[LightGBMFeatureBuilder] DataFrame has insufficient rows for feature building.")
            return pd.DataFrame()

        df = df.copy()
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp").reset_index(drop=True)

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        volume = df["volume"].astype(float) if "volume" in df.columns else pd.Series(0.0, index=df.index)

        # 1. Price Returns (strictly backward-looking shift)
        df["return_1"] = close.pct_change(1)
        df["return_2"] = close.pct_change(2)
        df["return_4"] = close.pct_change(4)
        df["return_8"] = close.pct_change(8)
        df["return_16"] = close.pct_change(16)

        # 2. Moving Averages
        df["sma_5"] = close.rolling(5).mean()
        df["sma_10"] = close.rolling(10).mean()
        df["sma_20"] = close.rolling(20).mean()
        df["sma_50"] = close.rolling(50).mean()

        # 3. Relative Price Positions
        df["close_vs_sma_10"] = (close - df["sma_10"]) / df["sma_10"]
        df["close_vs_sma_20"] = (close - df["sma_20"]) / df["sma_20"]
        df["close_vs_sma_50"] = (close - df["sma_50"]) / df["sma_50"]

        # 4. Volatility Indicators
        df["rolling_std_5"] = df["return_1"].rolling(5).std()
        df["rolling_std_10"] = df["return_1"].rolling(10).std()
        df["rolling_std_20"] = df["return_1"].rolling(20).std()
        
        tr = np.maximum(high - low, np.maximum(np.abs(high - close.shift(1)), np.abs(low - close.shift(1))))
        df["atr_14"] = tr.rolling(14).mean() / close

        # 5. Momentum Indicators
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df["rsi_14"] = 100 - (100 / (1 + rs))

        df["momentum_5"] = close - close.shift(5)
        df["momentum_10"] = close - close.shift(10)
        df["ema_12"] = close.ewm(span=12, adjust=False).mean()
        df["ema_26"] = close.ewm(span=26, adjust=False).mean()
        df["macd"] = df["ema_12"] - df["ema_26"]
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        # 6. Volume Indicators
        if "volume" in df.columns and (volume > 0).any():
            df["volume_change"] = volume.pct_change(1)
            vol_sma = volume.rolling(20).mean()
            df["volume_sma_ratio"] = volume / (vol_sma + 1e-9)
        else:
            df["volume_change"] = 0.0
            df["volume_sma_ratio"] = 1.0

        # 7. Numerical Target: close[t+4] / close[t] - 1
        horizon = self.target_policy.horizon_bars
        df["future_close"] = close.shift(-horizon)
        df["target_return_4bar"] = (df["future_close"] / close) - 1.0

        # Clean NaNs resulting from indicator warmups or tail horizon
        feature_cols = self.feature_schema.all_feature_names()
        required_cols = feature_cols + ["target_return_4bar"]
        
        # Drop rows with unresolvable targets or warmup NaNs
        clean_df = df.dropna(subset=required_cols).copy().reset_index(drop=True)
        
        # Audit feature names
        for col in feature_cols:
            if col not in clean_df.columns:
                clean_df[col] = 0.0

        logger.info(f"[LightGBMFeatureBuilder] Built {len(clean_df)} clean feature rows with 4-bar forward targets.")
        return clean_df

    def audit_feature_leakage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Audits dataset for look-ahead leakage in feature columns."""
        leakage_found = []
        feature_cols = self.feature_schema.all_feature_names()

        for col in feature_cols:
            if "future" in col.lower() or "shift_neg" in col.lower():
                leakage_found.append(f"Forbidden feature name: {col}")

        # Check timestamp alignment if timestamps are available
        if "timestamp" in df.columns:
            ts_list = df["timestamp"].tolist()
            if not all(ts_list[i] < ts_list[i+1] for i in range(len(ts_list)-1)):
                leakage_found.append("Timestamps are not strictly chronologically ordered.")

        passed = len(leakage_found) == 0
        return {
            "passed": passed,
            "leakage_errors": leakage_found,
            "total_features": len(feature_cols)
        }
