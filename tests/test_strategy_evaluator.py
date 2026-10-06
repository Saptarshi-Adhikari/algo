"""Unit tests for indicators and StrategyEvaluator."""
import pytest
import pandas as pd
import numpy as np
from app.domain.schemas import StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec
from app.strategies.indicators import enrich_with_indicators, calculate_sma, calculate_rsi
from app.strategies.evaluator import StrategyEvaluator

@pytest.fixture
def sample_ohlcv():
    dates = pd.date_range(start="2023-01-01", periods=50, freq="D")
    prices = np.linspace(100, 200, 50)
    # Add a dip for RSI test
    prices[20:25] = [150, 140, 130, 120, 110]
    return pd.DataFrame({
        "timestamp": dates,
        "open": prices * 0.99,
        "high": prices * 1.01,
        "low": prices * 0.98,
        "close": prices,
        "volume": 1000.0
    })

def test_indicators_calculation(sample_ohlcv):
    sma20 = calculate_sma(sample_ohlcv, 20)
    rsi14 = calculate_rsi(sample_ohlcv, 14)

    assert len(sma20) == 50
    assert pd.isna(sma20.iloc[0])
    assert not pd.isna(sma20.iloc[19])
    assert rsi14.min() >= 0.0 and rsi14.max() <= 100.0

def test_evaluator_signal_generation(sample_ohlcv):
    spec = StrategySpec(
        strategy_id="TEST_SMA_CROSS",
        version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        indicators=[
            IndicatorSpec(name="SMA", params={"period": 5}),
            IndicatorSpec(name="SMA", params={"period": 10})
        ],
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="sma_5", operator=">", right="sma_10")],
            exit_rules=[ConditionSpec(left="sma_5", operator="<", right="sma_10")]
        )
    )

    evaluator = StrategyEvaluator(spec)
    result_df = evaluator.evaluate(sample_ohlcv)

    assert "sma_5" in result_df.columns
    assert "sma_10" in result_df.columns
    assert "entry_signal" in result_df.columns
    assert "exit_signal" in result_df.columns
