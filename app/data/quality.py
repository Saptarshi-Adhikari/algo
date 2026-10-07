"""Market Data Quality Checker module."""
from typing import List, Dict, Any, Optional
import pandas as pd
from pydantic import BaseModel
from app.domain.schemas import DataMode

class DataQualityReport(BaseModel):
    symbol: str
    data_mode: DataMode
    total_rows: int
    start_date: str
    end_date: str
    missing_bars: int
    duplicate_bars: int
    invalid_ohlc_count: int
    zero_negative_prices: int
    timezone: str
    completeness_pct: float
    warnings: List[str]
    status: str  # "PASS", "WARN", "FAIL"

class DataQualityChecker:
    """Validates market data health, detecting gaps, OHLC mismatches, and timestamp errors."""

    @staticmethod
    def inspect(
        df: pd.DataFrame,
        symbol: str,
        data_mode: DataMode = "HISTORICAL",
        expected_freq: str = "1D"
    ) -> DataQualityReport:
        warnings = []
        if df.empty:
            return DataQualityReport(
                symbol=symbol,
                data_mode=data_mode,
                total_rows=0,
                start_date="N/A",
                end_date="N/A",
                missing_bars=0,
                duplicate_bars=0,
                invalid_ohlc_count=0,
                zero_negative_prices=0,
                timezone="UTC",
                completeness_pct=0.0,
                warnings=["DataFrame is empty."],
                status="FAIL"
            )

        total_rows = len(df)
        ts_col = df["timestamp"] if "timestamp" in df.columns else df.index
        timestamps = pd.to_datetime(ts_col)
        
        # 1. Duplicate Timestamps
        duplicate_bars = int(timestamps.duplicated().sum())
        if duplicate_bars > 0:
            warnings.append(f"Detected {duplicate_bars} duplicate timestamps.")

        # 2. Out-of-order check
        if not timestamps.is_monotonic_increasing:
            warnings.append("Timestamps are not strictly in chronological order.")

        # 3. Timezone detection
        tz_str = str(timestamps.dt.tz) if getattr(timestamps.dt, "tz", None) is not None else "UTC (naive)"

        # 4. Zero or Negative prices
        zero_neg = 0
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                zero_neg += int((df[col] <= 0).sum())
        if zero_neg > 0:
            warnings.append(f"Found {zero_neg} zero or negative price entries.")

        # 5. Invalid OHLC relationships: high >= open, close, low & low <= open, close, high
        invalid_ohlc = 0
        if all(col in df.columns for col in ["open", "high", "low", "close"]):
            bad_high = (df["high"] < df["open"]) | (df["high"] < df["close"]) | (df["high"] < df["low"])
            bad_low = (df["low"] > df["open"]) | (df["low"] > df["close"]) | (df["low"] > df["high"])
            invalid_ohlc = int((bad_high | bad_low).sum())
            if invalid_ohlc > 0:
                warnings.append(f"Found {invalid_ohlc} bars with impossible OHLC relationships (e.g., High < Low).")

        # 6. Missing bars estimate
        start_dt = timestamps.min()
        end_dt = timestamps.max()
        
        # Approximate expected business days / daily bars
        date_range = pd.date_range(start=start_dt, end=end_dt, freq="B")
        expected_bars = max(1, len(date_range))
        missing_bars = max(0, expected_bars - total_rows)
        completeness_pct = round(min(100.0, (total_rows / expected_bars) * 100.0), 2)

        if completeness_pct < 80.0:
            warnings.append(f"Low completeness: {completeness_pct}% (missing ~{missing_bars} expected daily bars).")

        # Determine overall status
        if invalid_ohlc > 0 or zero_neg > 0 or total_rows < 10:
            status = "FAIL"
        elif warnings:
            status = "WARN"
        else:
            status = "PASS"

        return DataQualityReport(
            symbol=symbol,
            data_mode=data_mode,
            total_rows=total_rows,
            start_date=str(start_dt),
            end_date=str(end_dt),
            missing_bars=missing_bars,
            duplicate_bars=duplicate_bars,
            invalid_ohlc_count=invalid_ohlc,
            zero_negative_prices=zero_neg,
            timezone=tz_str,
            completeness_pct=completeness_pct,
            warnings=warnings,
            status=status
        )
