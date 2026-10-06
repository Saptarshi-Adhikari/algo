"""Replay & Synthetic Demo Data Provider."""
from typing import List, Optional, Literal
import pandas as pd
import numpy as np
from app.data.base_provider import BaseDataProvider, MarketData
from app.domain.schemas import MarketType, MarketRegimeType

class ReplayDataProvider(BaseDataProvider):
    """Generates synthetic market data tailored to specific market regimes (TRENDING, RANGING, HIGH_VOLATILITY, LOW_VOLATILITY)."""

    def __init__(self, regime: MarketRegimeType = "TRENDING", num_bars: int = 250):
        self.regime = regime
        self.num_bars = num_bars

    def get_supported_symbols(self) -> List[str]:
        return ["SYNTHETIC_IND", "SYNTHETIC_FX"]

    def fetch_ohlcv(
        self,
        symbol: str = "SYNTHETIC_IND",
        timeframe: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> MarketData:
        np.random.seed(42)
        dates = pd.date_range(start="2023-01-01", periods=self.num_bars, freq="D")
        market_type: MarketType = "FOREX" if "FX" in symbol else "INDIAN_EQUITY"

        initial_price = 100.0
        prices = [initial_price]

        drift = 0.0
        vol = 0.01

        if self.regime == "TRENDING":
            drift = 0.0015
            vol = 0.01
        elif self.regime == "RANGING":
            drift = 0.0
            vol = 0.008
        elif self.regime == "HIGH_VOLATILITY":
            drift = 0.0002
            vol = 0.03
        elif self.regime == "LOW_VOLATILITY":
            drift = 0.0005
            vol = 0.004

        price = initial_price
        for i in range(1, self.num_bars):
            if self.regime == "RANGING":
                # Mean reverting pull towards initial_price
                change = (initial_price - price) * 0.05 + np.random.normal(0, vol * price)
            else:
                change = drift * price + np.random.normal(0, vol * price)
            price = max(1.0, price + change)
            prices.append(price)

        prices = np.array(prices)
        df = pd.DataFrame({
            "timestamp": dates,
            "open": prices * (1 - vol * 0.2),
            "high": prices * (1 + vol * 0.8),
            "low": prices * (1 - vol * 0.8),
            "close": prices,
            "volume": np.random.randint(50000, 1000000, size=self.num_bars)
        })

        return MarketData(
            symbol=symbol,
            market=market_type,
            timeframe=timeframe,
            df=df,
            metadata={"regime": self.regime, "is_replay": True}
        )
