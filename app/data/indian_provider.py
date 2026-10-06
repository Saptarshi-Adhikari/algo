"""Indian Equity and Index Data Provider (NSE/BSE)."""
from typing import List, Optional
import pandas as pd
import yfinance as yf
from app.data.base_provider import BaseDataProvider, MarketData
from app.config.logging import logger

class IndianMarketDataProvider(BaseDataProvider):
    """Fetches NSE/BSE equity and index data using free legitimate APIs with synthetic fallback."""

    DEFAULT_SYMBOLS = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "TATAMOTORS.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "^NSEI"
    ]

    def get_supported_symbols(self) -> List[str]:
        return self.DEFAULT_SYMBOLS

    def fetch_ohlcv(
        self,
        symbol: str = "RELIANCE.NS",
        timeframe: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> MarketData:
        # Format symbol for yfinance NSE if needed
        yf_symbol = symbol if symbol.startswith("^") or "." in symbol else f"{symbol}.NS"
        logger.info(f"Fetching Indian market data for {yf_symbol} ({timeframe})")

        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period="1y" if not start_date else None, start=start_date, end=end_date, interval=timeframe)

            if df.empty:
                logger.warning(f"No yfinance data returned for {yf_symbol}, generating synthetic dataset.")
                return self._generate_synthetic(symbol, timeframe)

            df = df.reset_index()
            # Normalize column names
            df = df.rename(columns={
                "Date": "timestamp", "Datetime": "timestamp",
                "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
            })
            return MarketData(symbol=symbol, market="INDIAN_EQUITY", timeframe=timeframe, df=df)

        except Exception as e:
            logger.error(f"Error fetching data for {yf_symbol}: {e}. Falling back to synthetic generator.")
            return self._generate_synthetic(symbol, timeframe)

    def _generate_synthetic(self, symbol: str, timeframe: str) -> MarketData:
        dates = pd.date_range(start="2023-01-01", periods=250, freq="D")
        import numpy as np
        np.random.seed(42)
        price = 1000.0
        prices = [price]
        for _ in range(len(dates) - 1):
            price *= (1 + np.random.normal(0.0005, 0.015))
            prices.append(price)

        prices = np.array(prices)
        df = pd.DataFrame({
            "timestamp": dates,
            "open": prices * 0.998,
            "high": prices * 1.012,
            "low": prices * 0.988,
            "close": prices,
            "volume": np.random.randint(100000, 5000000, size=len(dates))
        })
        return MarketData(symbol=symbol, market="INDIAN_EQUITY", timeframe=timeframe, df=df, metadata={"is_synthetic": True})
