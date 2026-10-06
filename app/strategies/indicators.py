"""Deterministic technical indicator calculations using pandas and numpy."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from app.domain.schemas import IndicatorSpec

def calculate_sma(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    return df[column].rolling(window=period).mean()

def calculate_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    ema_fast = calculate_ema(df, fast)
    ema_slow = calculate_ema(df, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return {"macd": macd_line, "macd_signal": signal_line, "macd_hist": hist}

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
    sma = calculate_sma(df, period)
    std = df["close"].rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return {"bb_upper": upper, "bb_middle": sma, "bb_lower": lower}

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().fillna(0.0)

def enrich_with_indicators(df: pd.DataFrame, indicators: List[IndicatorSpec]) -> pd.DataFrame:
    """Enrich dataframe with required indicators based on strategy specifications."""
    enriched = df.copy()

    for ind in indicators:
        name = ind.name.upper()
        params = ind.params or {}

        if name == "SMA":
            period = params.get("period", 20)
            col_name = f"sma_{period}"
            enriched[col_name] = calculate_sma(enriched, period)
        elif name == "EMA":
            period = params.get("period", 20)
            col_name = f"ema_{period}"
            enriched[col_name] = calculate_ema(enriched, period)
        elif name == "RSI":
            period = params.get("period", 14)
            col_name = f"rsi_{period}"
            enriched[col_name] = calculate_rsi(enriched, period)
        elif name == "MACD":
            fast = params.get("fast", 12)
            slow = params.get("slow", 26)
            sig = params.get("signal", 9)
            res = calculate_macd(enriched, fast, slow, sig)
            for k, v in res.items():
                enriched[k] = v
        elif name in ["BB", "BOLLINGER"]:
            period = params.get("period", 20)
            dev = params.get("std_dev", 2.0)
            res = calculate_bollinger_bands(enriched, period, dev)
            for k, v in res.items():
                enriched[k] = v
        elif name == "ATR":
            period = params.get("period", 14)
            col_name = f"atr_{period}"
            enriched[col_name] = calculate_atr(enriched, period)

    return enriched
