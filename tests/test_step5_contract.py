"""Tests for STEP 5 - ResearchDatasetRegistry contract."""
import pytest
import pandas as pd
from app.data.base_provider import MarketData
from app.data.registry import ResearchDatasetRegistry, ResearchDatasetEntry

def setup_function():
    ResearchDatasetRegistry.clear()

def test_registry_lifecycle():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2023-01-01", periods=10),
        "open": [100.0] * 10,
        "high": [105.0] * 10,
        "low": [95.0] * 10,
        "close": [102.0] * 10,
        "volume": [1000] * 10
    })
    md_ind = MarketData(symbol="RELIANCE.NS", market="INDIAN_EQUITY", timeframe="1d", df=df)
    md_crypto = MarketData(symbol="BTC/USDT", market="CRYPTO", timeframe="1d", df=df)

    # Register
    e1 = ResearchDatasetRegistry.register(md_ind, provider_name="yfinance", quality_status="PASS")
    e2 = ResearchDatasetRegistry.register(md_crypto, provider_name="ccxt", quality_status="PASS")

    # Get
    retrieved = ResearchDatasetRegistry.get(e1.dataset_id)
    assert retrieved is not None
    assert retrieved.symbol == "RELIANCE.NS"

    # List all
    all_entries = ResearchDatasetRegistry.list_all()
    assert len(all_entries) == 2

    # List by asset class
    ind_entries = ResearchDatasetRegistry.list_by_asset_class("INDIAN_EQUITY")
    assert len(ind_entries) == 1
    assert ind_entries[0].symbol == "RELIANCE.NS"

    # Verify metadata fields
    entry = ind_entries[0]
    assert entry.dataset_id.startswith("DS_RELIANCE.NS_")
    assert entry.dataset_hash == md_ind.dataset_hash
    assert entry.total_bars == 10
    assert entry.quality_status == "PASS"
