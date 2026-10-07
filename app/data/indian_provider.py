"""Indian Equity and Index Data Provider (NSE/BSE)."""
from typing import List, Optional
import pandas as pd
import numpy as np
import yfinance as yf
from app.data.base_provider import BaseDataProvider, MarketData
from app.config.logging import logger

# Phase 10 expanded market universe — Indian Equities
INDIA_EQUITY_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "HINDUNILVR.NS", "MARUTI.NS", "SUNPHARMA.NS", "BAJFINANCE.NS",
]

# Phase 10 expanded market universe — Indian Indices
INDIA_INDEX_SYMBOLS = [
    "^NSEI",      # Nifty 50
    "^NSEBANK",   # Nifty Bank
]

ALL_INDIA_SYMBOLS = INDIA_EQUITY_SYMBOLS + INDIA_INDEX_SYMBOLS


def _classify_india_market(symbol: str) -> str:
    """Classify an Indian symbol as equity or index."""
    if symbol.startswith("^"):
        return "INDIAN_INDEX"
    return "INDIAN_EQUITY"


class IndianMarketDataProvider(BaseDataProvider):
    """Fetches NSE/BSE equity and index data using free legitimate APIs with synthetic fallback."""

    DEFAULT_SYMBOLS = ALL_INDIA_SYMBOLS

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
        market_type = _classify_india_market(symbol)
        logger.info(f"Fetching Indian market data for {yf_symbol} ({timeframe}) [class={market_type}]")

        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period="5y" if not start_date else None, start=start_date, end=end_date, interval=timeframe)

            if df.empty:
                logger.warning(f"No yfinance data returned for {yf_symbol}, generating synthetic dataset.")
                return self._generate_synthetic(symbol, timeframe, market_type)

            df = df.reset_index()
            # Normalize column names
            df = df.rename(columns={
                "Date": "timestamp", "Datetime": "timestamp",
                "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
            })
            return MarketData(
                symbol=symbol,
                market=market_type,
                timeframe=timeframe,
                df=df,
                metadata={"data_mode": "HISTORICAL", "provider": "yfinance"}
            )

        except Exception as e:
            logger.error(f"Error fetching data for {yf_symbol}: {e}. Falling back to synthetic generator.")
            return self._generate_synthetic(symbol, timeframe, market_type)

    def _generate_synthetic(self, symbol: str, timeframe: str, market_type: str = "INDIAN_EQUITY") -> MarketData:
        dates = pd.date_range(start="2023-01-01", periods=250, freq="D")
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
        return MarketData(symbol=symbol, market=market_type, timeframe=timeframe, df=df, metadata={"is_synthetic": True})
