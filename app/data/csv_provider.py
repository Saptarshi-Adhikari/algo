"""CSV / Parquet file data provider."""
from typing import List, Optional
from pathlib import Path
import pandas as pd
from app.data.base_provider import BaseDataProvider, MarketData
from app.config.settings import settings

class CSVDataProvider(BaseDataProvider):
    """Loads historical market data from local CSV files."""

    def __init__(self, data_folder: Path = None):
        self.data_folder = data_folder or settings.DATA_DIR

    def get_supported_symbols(self) -> List[str]:
        files = list(self.data_folder.glob("*.csv"))
        return [f.stem for f in files]

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> MarketData:
        file_path = self.data_folder / f"{symbol}.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"CSV data file for {symbol} not found at {file_path}")

        df = pd.read_csv(file_path)
        market_type = "FOREX" if "EUR" in symbol or "USD" in symbol else "INDIAN_EQUITY"
        market_data = MarketData(symbol=symbol, market=market_type, timeframe=timeframe, df=df)

        if start_date or end_date:
            filtered_df = market_data.df.copy()
            if start_date:
                filtered_df = filtered_df[filtered_df["timestamp"] >= pd.to_datetime(start_date)]
            if end_date:
                filtered_df = filtered_df[filtered_df["timestamp"] <= pd.to_datetime(end_date)]
            return MarketData(symbol=symbol, market=market_type, timeframe=timeframe, df=filtered_df)

        return market_data
