"""Crypto Market Data Provider — Read-only historical data via yfinance.

IMPORTANT: This provider is strictly read-only for historical/paper-trading research.
No wallet integration, no API trading keys, no order routing, no live execution.
Only historical OHLCV data is fetched for offline backtesting and paper trading simulation.
"""
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
import yfinance as yf
from app.data.base_provider import BaseDataProvider, MarketData
from app.config.logging import logger

# Phase 10 initial crypto universe — yfinance ticker format (symbol + "-USD")
CRYPTO_SYMBOLS = [
    "BTC-USD",   # Bitcoin / USDT proxy (USD denominated)
    "ETH-USD",   # Ethereum
    "SOL-USD",   # Solana
    "BNB-USD",   # BNB
    "XRP-USD",   # XRP
]

# Mapping from user-friendly names to yfinance symbols
_USER_TO_YF: Dict[str, str] = {
    "BTC/USDT": "BTC-USD",
    "ETH/USDT": "ETH-USD",
    "SOL/USDT": "SOL-USD",
    "BNB/USDT": "BNB-USD",
    "XRP/USDT": "XRP-USD",
    "BTC-USD":  "BTC-USD",
    "ETH-USD":  "ETH-USD",
    "SOL-USD":  "SOL-USD",
    "BNB-USD":  "BNB-USD",
    "XRP-USD":  "XRP-USD",
}

# Canonical symbol names shown to users
USER_FRIENDLY_CRYPTO = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]


def _normalize_crypto_symbol(symbol: str) -> str:
    """Convert user-friendly symbol to yfinance format."""
    return _USER_TO_YF.get(symbol.upper(), symbol.replace("/", "-"))


class CryptoDataProvider(BaseDataProvider):
    """Read-only historical crypto data provider using yfinance (paper trading only).

    Architecture note: This provider is STRICTLY for historical price data ingestion.
    No live trading, no wallet, no exchange keys, no order placement.
    """

    DEFAULT_SYMBOLS = USER_FRIENDLY_CRYPTO

    def get_supported_symbols(self) -> List[str]:
        return self.DEFAULT_SYMBOLS

    def fetch_ohlcv(
        self,
        symbol: str = "BTC/USDT",
        timeframe: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> MarketData:
        yf_symbol = _normalize_crypto_symbol(symbol)
        logger.info(f"Fetching Crypto data for {yf_symbol} ({timeframe}) [read-only/paper-trading mode]")

        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(
                period="5y" if not start_date else None,
                start=start_date,
                end=end_date,
                interval=timeframe
            )

            if df.empty:
                logger.warning(f"No yfinance crypto data returned for {yf_symbol}. Generating synthetic fallback.")
                return self._generate_synthetic(symbol, timeframe)

            df = df.reset_index()
            df = df.rename(columns={
                "Date": "timestamp", "Datetime": "timestamp",
                "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Volume": "volume"
            })

            # Crypto may have 0 volume for certain exchanges — replace with 0 rather than NaN
            if "volume" not in df.columns:
                df["volume"] = 0.0

            return MarketData(
                symbol=symbol,
                market="CRYPTO",
                timeframe=timeframe,
                df=df,
                metadata={
                    "data_mode": "HISTORICAL",
                    "provider": "yfinance",
                    "source_symbol": yf_symbol,
                    "timezone": "UTC",
                    "note": "Paper trading research only. No real trades executed."
                }
            )

        except Exception as e:
            logger.error(f"Error fetching crypto data for {yf_symbol}: {e}. Using synthetic fallback.")
            return self._generate_synthetic(symbol, timeframe)

    def _generate_synthetic(self, symbol: str, timeframe: str) -> MarketData:
        """Generate synthetic crypto OHLCV data with realistic crypto-like volatility."""
        dates = pd.date_range(start="2022-01-01", periods=500, freq="D")
        np.random.seed(99)

        # Higher volatility for crypto
        base_price = 30000.0 if "BTC" in symbol else 2000.0 if "ETH" in symbol else 100.0
        prices = [base_price]
        for _ in range(len(dates) - 1):
            # Crypto is more volatile than equities
            prices.append(prices[-1] * (1 + np.random.normal(0.001, 0.04)))

        prices = np.array(prices)
        opens = prices * np.random.uniform(0.97, 0.999, len(prices))
        closes = prices
        highs = np.maximum(opens, closes) * np.random.uniform(1.01, 1.05, len(prices))
        lows = np.minimum(opens, closes) * np.random.uniform(0.95, 0.99, len(prices))

        df = pd.DataFrame({
            "timestamp": dates,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": np.random.uniform(1e9, 5e10, size=len(dates))  # Crypto volume in USDT
        })
        return MarketData(
            symbol=symbol,
            market="CRYPTO",
            timeframe=timeframe,
            df=df,
            metadata={"is_synthetic": True, "note": "Synthetic fallback — not real market data."}
        )
