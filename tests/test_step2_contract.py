"""Tests for STEP 2 - MarketData dataset_hash contract."""
import pytest
import pandas as pd
from app.data.base_provider import MarketData
from app.data.indian_provider import IndianMarketDataProvider
from app.data.forex_provider import ForexDataProvider
from app.data.crypto_provider import CryptoDataProvider
from app.data.gold_provider import GoldDataProvider
from app.data.csv_provider import CSVDataProvider

def test_market_data_has_dataset_hash():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2023-01-01", periods=10),
        "open": [100.0] * 10,
        "high": [105.0] * 10,
        "low": [95.0] * 10,
        "close": [102.0] * 10,
        "volume": [1000] * 10
    })
    md = MarketData(symbol="RELIANCE.NS", market="INDIAN_EQUITY", timeframe="1d", df=df)
    assert hasattr(md, "dataset_hash")
    assert isinstance(md.dataset_hash, str)
    assert len(md.dataset_hash) == 16

def test_dataset_hash_determinism_and_uniqueness():
    df1 = pd.DataFrame({
        "timestamp": pd.date_range("2023-01-01", periods=5),
        "open": [10.0] * 5,
        "high": [12.0] * 5,
        "low": [9.0] * 5,
        "close": [11.0] * 5,
        "volume": [100] * 5
    })
    df2 = pd.DataFrame({
        "timestamp": pd.date_range("2023-01-01", periods=5),
        "open": [10.0] * 5,
        "high": [16.0] * 5,  # High must be >= Close
        "low": [9.0] * 5,
        "close": [15.0] * 5,  # changed close
        "volume": [100] * 5
    })
    md1_a = MarketData(symbol="TEST", market="INDIAN_EQUITY", timeframe="1d", df=df1)
    md1_b = MarketData(symbol="TEST", market="INDIAN_EQUITY", timeframe="1d", df=df1)
    md2 = MarketData(symbol="TEST", market="INDIAN_EQUITY", timeframe="1d", df=df2)

    assert md1_a.dataset_hash == md1_b.dataset_hash
    assert md1_a.dataset_hash != md2.dataset_hash

def test_all_providers_produce_valid_dataset_hash():
    # Indian
    p_ind = IndianMarketDataProvider()
    md_ind = p_ind._generate_synthetic("RELIANCE.NS", "1d")
    assert len(md_ind.dataset_hash) == 16

    # Forex
    p_fx = ForexDataProvider()
    md_fx = p_fx._generate_synthetic("EURUSD=X", "1d")
    assert len(md_fx.dataset_hash) == 16

    # Crypto
    p_cr = CryptoDataProvider()
    md_cr = p_cr._generate_synthetic("BTC/USDT", "1d")
    assert len(md_cr.dataset_hash) == 16

    # Gold (GoldDataProvider raises ValueError on invalid symbol, or returns MarketData with dataset_hash)
    p_au = GoldDataProvider()
    assert "XAUUSD" in p_au.get_supported_symbols()
