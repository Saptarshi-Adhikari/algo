"""Unit tests for Backtester engine and metrics."""
import pytest
import pandas as pd
import numpy as np
from app.data.base_provider import MarketData
from app.domain.schemas import StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec
from app.backtesting.engine import Backtester
from app.backtesting.metrics import calculate_metrics

@pytest.fixture
def trending_market_data():
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    prices = np.linspace(100, 200, 100)  # Solid uptrend
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices * 0.99,
        "high": prices * 1.01,
        "low": prices * 0.98,
        "close": prices,
        "volume": 10000.0
    })
    return MarketData(symbol="RELIANCE.NS", market="INDIAN_EQUITY", timeframe="1d", df=df)

def test_backtester_execution(trending_market_data):
    spec = StrategySpec(
        strategy_id="TEST_TREND",
        version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        indicators=[
            IndicatorSpec(name="SMA", params={"period": 5}),
            IndicatorSpec(name="SMA", params={"period": 20})
        ],
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="sma_5", operator=">", right="sma_20")],
            exit_rules=[ConditionSpec(left="sma_5", operator="<", right="sma_20")],
            stop_loss_pct=5.0,
            take_profit_pct=10.0,
            position_sizing_pct=20.0
        )
    )

    backtester = Backtester(initial_cash=100000.0, commission_bps=3.0, slippage_bps=1.0)
    metrics, trades, equity = backtester.run(trending_market_data, spec, "DEVELOPMENT")

    assert metrics.trade_count >= 1
    assert len(trades) == metrics.trade_count
    assert metrics.total_return_pct != 0.0
    assert len(equity) == len(trending_market_data)

def test_metrics_no_trades():
    trades = []
    equity = pd.Series([100000.0, 100000.0])
    metrics = calculate_metrics(trades, equity, 100000.0, "DEVELOPMENT")

    assert metrics.trade_count == 0
    assert metrics.total_return_pct == 0.0
    assert metrics.sharpe_ratio == 0.0
    assert metrics.win_rate == 0.0
