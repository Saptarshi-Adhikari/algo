"""Unit tests for DataSplitter and Holdout protection."""
import pytest
import pandas as pd
import numpy as np
from app.data.base_provider import MarketData
from app.data.splitter import DataSplitter, HoldoutProtectionError

@pytest.fixture
def mock_market_data():
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "open": np.linspace(100, 200, 100),
        "high": np.linspace(105, 205, 100),
        "low": np.linspace(95, 195, 100),
        "close": np.linspace(102, 202, 100),
        "volume": 1000.0
    })
    return MarketData(symbol="TEST.NS", market="INDIAN_EQUITY", timeframe="1d", df=df)

def test_splitter_proportions(mock_market_data):
    splitter = DataSplitter(dev_pct=0.6, val_pct=0.2, holdout_pct=0.2)
    splits = splitter.split(mock_market_data)

    assert len(splits["DEVELOPMENT"]) == 60
    assert len(splits["VALIDATION"]) == 20
    assert len(splits["HOLDOUT"]) == 20

    # Ensure chronological order and no overlap
    assert splits["DEVELOPMENT"].end_date < splits["VALIDATION"].start_date
    assert splits["VALIDATION"].end_date < splits["HOLDOUT"].start_date

def test_holdout_protection(mock_market_data):
    splitter = DataSplitter()
    splits = splitter.split(mock_market_data)

    # Allowed access to DEV and VAL
    dev_data = splitter.get_split_data(splits, "DEVELOPMENT")
    assert len(dev_data) == 60

    val_data = splitter.get_split_data(splits, "VALIDATION")
    assert len(val_data) == 20

    # Blocked access to HOLDOUT without flag
    with pytest.raises(HoldoutProtectionError):
        splitter.get_split_data(splits, "HOLDOUT", allow_holdout=False)

    # Explicit access allowed
    holdout_data = splitter.get_split_data(splits, "HOLDOUT", allow_holdout=True)
    assert len(holdout_data) == 20
