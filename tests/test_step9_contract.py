"""Tests for STEP 9 - Phase 10 actual market-data validation."""
import pytest
from app.data.provider_factory import get_provider_for_symbol, get_provider
from app.data.registry import ResearchDatasetRegistry

def test_phase10_asset_classes_and_providers():
    # Indian Equities & Indices
    p_rel = get_provider_for_symbol("RELIANCE.NS")
    md_rel = p_rel.fetch_ohlcv("RELIANCE.NS", "1d")
    assert md_rel.market == "INDIAN_EQUITY"
    assert len(md_rel) > 0
    assert hasattr(md_rel, "dataset_hash")

    p_idx = get_provider_for_symbol("^NSEI")
    md_idx = p_idx.fetch_ohlcv("^NSEI", "1d")
    assert md_idx.market == "INDIAN_INDEX"
    assert len(md_idx) > 0

    # Forex
    p_fx = get_provider_for_symbol("EURUSD=X")
    md_fx = p_fx.fetch_ohlcv("EURUSD=X", "1d")
    assert md_fx.market == "FOREX"
    assert len(md_fx) > 0

    # Crypto
    p_cr = get_provider_for_symbol("BTC/USDT")
    md_cr = p_cr.fetch_ohlcv("BTC/USDT", "1d")
    assert md_cr.market == "CRYPTO"
    assert len(md_cr) > 0

    # Gold
    p_au = get_provider_for_symbol("XAUUSD")
    assert "XAUUSD" in p_au.get_supported_symbols()
