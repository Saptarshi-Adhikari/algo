"""Unit tests for RegimeClassifier."""
import pytest
from app.data.replay_provider import ReplayDataProvider
from app.evaluation.regime import RegimeClassifier

def test_regime_classification():
    for target_regime in ["TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY"]:
        provider = ReplayDataProvider(regime=target_regime, num_bars=200)
        data = provider.fetch_ohlcv("SYNTHETIC_IND", "1d")
        detected = RegimeClassifier.classify_dataset(data)

        assert detected in ["TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY"]
        assert isinstance(detected, str)
