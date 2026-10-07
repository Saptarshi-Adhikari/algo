"""Base Data Provider interface and MarketData container."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import pandas as pd
from pydantic import BaseModel
from app.domain.schemas import MarketType

import hashlib

class MarketData:
    """Standardized OHLCV Market Data container."""

    REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

    def __init__(
        self,
        symbol: str,
        market: MarketType,
        timeframe: str,
        df: pd.DataFrame,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.symbol = symbol.strip().upper()
        self.market = market
        self.timeframe = timeframe
        self.metadata = metadata or {}
        self.df = self._validate_and_format(df)
        self.dataset_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Computes a SHA256 checksum of the normalized market data for reproducibility tracking."""
        raw_bytes = self.df.to_json(date_format="iso").encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()[:16]

    def _validate_and_format(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise ValueError(f"MarketData DataFrame for {self.symbol} is empty.")

        formatted_df = df.copy()

        # Lowercase column names
        formatted_df.columns = [str(c).lower().strip() for c in formatted_df.columns]

        # Ensure required columns exist
        missing = [col for col in self.REQUIRED_COLUMNS if col not in formatted_df.columns]
        if missing:
            raise ValueError(f"MarketData missing required columns for {self.symbol}: {missing}")

        # Ensure timestamp is datetime, normalized, and sorted
        formatted_df["timestamp"] = pd.to_datetime(formatted_df["timestamp"])
        
        # Deduplicate identical timestamps
        formatted_df = formatted_df.drop_duplicates(subset=["timestamp"], keep="last")
        formatted_df = formatted_df.sort_values("timestamp").reset_index(drop=True)

        # Numeric conversions
        for col in ["open", "high", "low", "close", "volume"]:
            formatted_df[col] = pd.to_numeric(formatted_df[col], errors="coerce")

        # Fill zero volume if appropriate
        formatted_df["volume"] = formatted_df["volume"].fillna(0.0)

        # Drop rows missing essential price data
        formatted_df = formatted_df.dropna(subset=["close", "open", "high", "low"])

        # Validate strictly positive prices
        if (formatted_df["close"] <= 0).any():
            raise ValueError(f"MarketData for {self.symbol} contains non-positive price values.")

        # Validate OHLC logical relationship
        bad_high = (formatted_df["high"] < formatted_df["open"]) | (formatted_df["high"] < formatted_df["close"])
        bad_low = (formatted_df["low"] > formatted_df["open"]) | (formatted_df["low"] > formatted_df["close"])
        if bad_high.any() or bad_low.any():
            raise ValueError(f"MarketData for {self.symbol} contains invalid OHLC relationships (e.g. High < Open/Close or Low > Open/Close).")

        return formatted_df

    def __len__(self) -> int:
        return len(self.df)

    @property
    def start_date(self) -> pd.Timestamp:
        return self.df["timestamp"].min()

    @property
    def end_date(self) -> pd.Timestamp:
        return self.df["timestamp"].max()


class BaseDataProvider(ABC):
    """Abstract interface for market data providers."""

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> MarketData:
        """Fetch standardized historical or streamed OHLCV market data."""
        pass

    @abstractmethod
    def get_supported_symbols(self) -> List[str]:
        """List symbols supported by this provider."""
        pass
