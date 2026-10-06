"""Unit tests for Market Data Adapters."""
import pytest
import pandas as pd
from app.data.indian_provider import IndianMarketDataProvider
from app.data.forex_provider import ForexDataProvider
from app.data.replay_provider import ReplayDataProvider
from app.data.base_provider import MarketData

def test_indian_provider_synthetic_fallback():
    provider = IndianMarketDataProvider()
    # Test synthetic generation
    data = provider._generate_synthetic("RELIANCE.NS", "1d")
    assert isinstance(data, MarketData)
    assert len(data) == 250
    assert data.symbol == "RELIANCE.NS"
    assert data.market == "INDIAN_EQUITY"
    assert "close" in data.df.columns

def test_forex_provider_synthetic_fallback():
    provider = ForexDataProvider()
    data = provider._generate_synthetic("EURUSD=X", "1d")
    assert isinstance(data, MarketData)
    assert len(data) == 250
    assert data.market == "FOREX"
    assert data.symbol == "EURUSD=X"

def test_replay_provider_regimes():
    for regime in ["TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY"]:
        provider = ReplayDataProvider(regime=regime, num_bars=100)
        data = provider.fetch_ohlcv("SYNTHETIC_IND", "1d")
        assert len(data) == 100
        assert data.metadata["regime"] == regime
