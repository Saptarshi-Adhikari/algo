"""Market Regime Classifier module detecting TRENDING, RANGING, HIGH_VOLATILITY, and LOW_VOLATILITY."""
import numpy as np
import pandas as pd
from typing import Tuple
from app.data.base_provider import MarketData
from app.domain.schemas import MarketRegimeType
from app.strategies.indicators import calculate_atr, calculate_sma

class RegimeClassifier:
    """Extensible quantitative regime classification engine."""

    @staticmethod
    def classify_dataset(data: MarketData) -> MarketRegimeType:
        """Determine predominant regime for market dataset."""
        df = data.df.copy()
        if len(df) < 20:
            return "UNKNOWN"

        # Calculate Normalized ATR (%)
        atr = calculate_atr(df, period=14)
        natr = (atr / df["close"]) * 100.0
        avg_natr = float(natr.dropna().mean())

        # Calculate 20-bar returns standard deviation (Volatility proxy)
        returns = df["close"].pct_change()
        volatility = float(returns.std() * np.sqrt(252.0) * 100.0)

        # Calculate trend strength via SMA 50 slope or price direction efficiency ratio
        price_change = abs(df["close"].iloc[-1] - df["close"].iloc[0])
        path_length = (df["close"].diff().abs()).sum()
        efficiency_ratio = price_change / path_length if path_length > 0 else 0.0

        # Classification logic
        if avg_natr > 2.2 or volatility > 30.0:
            return "HIGH_VOLATILITY"
        elif avg_natr < 0.8 and volatility < 12.0:
            return "LOW_VOLATILITY"
        elif efficiency_ratio > 0.35:
            return "TRENDING"
        else:
            return "RANGING"
