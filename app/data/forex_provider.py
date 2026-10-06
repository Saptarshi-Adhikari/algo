"""Forex Currency Pair Data Provider."""
from typing import List, Optional
import pandas as pd
import yfinance as yf
from app.data.base_provider import BaseDataProvider, MarketData
from app.config.logging import logger

class ForexDataProvider(BaseDataProvider):
    """Fetches major/minor forex currency pairs using free APIs with synthetic fallback."""

    DEFAULT_PAIRS = [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDINR=X", "AUDUSD=X",
        "USDCAD=X", "USDCHF=X", "EURGBP=X", "GBPJPY=X"
    ]

    def get_supported_symbols(self) -> List[str]:
        return self.DEFAULT_PAIRS

    def fetch_ohlcv(
        self,
        symbol: str = "EURUSD=X",
        timeframe: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> MarketData:
        yf_symbol = symbol if symbol.endswith("=X") else f"{symbol}=X"
        logger.info(f"Fetching Forex data for {yf_symbol} ({timeframe})")

        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period="1y" if not start_date else None, start=start_date, end=end_date, interval=timeframe)

            if df.empty:
                logger.warning(f"No yfinance forex data returned for {yf_symbol}, using synthetic generator.")
                return self._generate_synthetic(symbol, timeframe)

            df = df.reset_index()
            df = df.rename(columns={
                "Date": "timestamp", "Datetime": "timestamp",
                "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
            })
            return MarketData(symbol=symbol, market="FOREX", timeframe=timeframe, df=df)

        except Exception as e:
            logger.error(f"Error fetching forex data for {yf_symbol}: {e}. Falling back to synthetic.")
            return self._generate_synthetic(symbol, timeframe)

    def _generate_synthetic(self, symbol: str, timeframe: str) -> MarketData:
        dates = pd.date_range(start="2023-01-01", periods=250, freq="D")
        import numpy as np
        np.random.seed(100)
        base_rate = 1.08 if "EUR" in symbol else 83.0 if "INR" in symbol else 1.25
        rates = [base_rate]
        for _ in range(len(dates) - 1):
            base_rate *= (1 + np.random.normal(0.0001, 0.005))
            rates.append(base_rate)

        rates = np.array(rates)
        df = pd.DataFrame({
            "timestamp": dates,
            "open": rates * 0.999,
            "high": rates * 1.003,
            "low": rates * 0.997,
            "close": rates,
            "volume": np.random.randint(10000, 500000, size=len(dates))
        })
        return MarketData(symbol=symbol, market="FOREX", timeframe=timeframe, df=df, metadata={"is_synthetic": True})
