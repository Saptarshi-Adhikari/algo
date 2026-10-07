"""Gold Asset Class Data Provider.

Supports XAUUSD (spot Gold in USD) via yfinance.
Indian gold instruments (e.g. GOLDBEES.NS ETF) are attempted where reliably available.

IMPORTANT: Data is for paper-trading research only. No real-money trading.

Provider limitations:
- Free yfinance endpoints may have limited depth for Gold spot data.
- If provider fails, the instrument is marked UNAVAILABLE rather than fabricated.
- Local CSV import is supported as a reliable fallback for deep historical research.
"""
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
import yfinance as yf
from app.data.base_provider import BaseDataProvider, MarketData
from app.config.logging import logger

# Gold instrument registry — maps user-facing name to yfinance symbol and expected price range
GOLD_INSTRUMENTS: Dict[str, Dict] = {
    "XAUUSD": {
        "yf_symbol": "GC=F",       # Gold futures (front month) — widely available
        "description": "Gold Spot / Futures (USD)",
        "price_range": (1200, 3000),
        "currency": "USD",
    },
    "GOLDBEES.NS": {
        "yf_symbol": "GOLDBEES.NS",  # Indian gold ETF traded on NSE
        "description": "Nippon India ETF Gold BeES (NSE)",
        "price_range": (30, 80),
        "currency": "INR",
    },
}

GOLD_SYMBOLS = list(GOLD_INSTRUMENTS.keys())


class GoldDataProvider(BaseDataProvider):
    """Read-only historical Gold data provider.

    Fetches XAUUSD (Gold Futures via GC=F) and Indian gold ETF data.
    Falls back to 'UNAVAILABLE' status if provider cannot supply valid data.
    Does not fabricate Gold prices.
    """

    DEFAULT_SYMBOLS = GOLD_SYMBOLS

    def get_supported_symbols(self) -> List[str]:
        return self.DEFAULT_SYMBOLS

    def fetch_ohlcv(
        self,
        symbol: str = "XAUUSD",
        timeframe: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> MarketData:
        instrument = GOLD_INSTRUMENTS.get(symbol.upper(), GOLD_INSTRUMENTS.get(symbol))
        if not instrument:
            raise ValueError(
                f"Gold instrument '{symbol}' not recognized. "
                f"Supported: {GOLD_SYMBOLS}. "
                f"For custom Gold data, use CSVDataProvider."
            )

        yf_symbol = instrument["yf_symbol"]
        logger.info(f"Fetching Gold data for {symbol} (via {yf_symbol}, {timeframe})")

        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(
                period="5y" if not start_date else None,
                start=start_date,
                end=end_date,
                interval=timeframe
            )

            if df.empty:
                logger.warning(
                    f"Gold provider returned empty data for {yf_symbol}. "
                    f"Marking as UNAVAILABLE. Use CSVDataProvider for local Gold CSV import."
                )
                # Rather than fabricate gold prices, raise a clear error
                raise ValueError(
                    f"Gold data unavailable from provider for '{symbol}' ({yf_symbol}). "
                    f"Provider returned no data. Use CSVDataProvider as fallback."
                )

            df = df.reset_index()
            df = df.rename(columns={
                "Date": "timestamp", "Datetime": "timestamp",
                "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Volume": "volume"
            })

            # Gold futures may have 0 volume on some days — handle explicitly
            if "volume" not in df.columns:
                df["volume"] = 0.0
            df["volume"] = df["volume"].fillna(0.0)

            return MarketData(
                symbol=symbol,
                market="GOLD",
                timeframe=timeframe,
                df=df,
                metadata={
                    "data_mode": "HISTORICAL",
                    "provider": "yfinance",
                    "source_symbol": yf_symbol,
                    "instrument_description": instrument["description"],
                    "currency": instrument["currency"],
                    "note": "Gold futures price (not spot). Paper trading research only."
                }
            )

        except ValueError:
            raise  # Re-raise our own UNAVAILABLE errors
        except Exception as e:
            logger.error(f"Error fetching Gold data for {yf_symbol}: {e}.")
            raise ValueError(
                f"Gold data unavailable: {e}. "
                f"Use CSVDataProvider to import historical Gold data from a local CSV file."
            )
