"""Base Data Provider interface and MarketData container."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import pandas as pd
from pydantic import BaseModel
from app.domain.schemas import MarketType

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
        self.symbol = symbol
        self.market = market
        self.timeframe = timeframe
        self.metadata = metadata or {}
        self.df = self._validate_and_format(df)

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

        # Ensure timestamp is datetime and sorted
        formatted_df["timestamp"] = pd.to_datetime(formatted_df["timestamp"])
        formatted_df = formatted_df.sort_values("timestamp").reset_index(drop=True)

        # Numeric conversions
        for col in ["open", "high", "low", "close", "volume"]:
            formatted_df[col] = pd.to_numeric(formatted_df[col], errors="coerce")

        formatted_df = formatted_df.dropna(subset=["close"])
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
