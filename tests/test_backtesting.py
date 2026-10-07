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

def test_metrics_sample_size_categories():
    equity = pd.Series([100000.0, 100000.0])
    
    # 1. NO_TRADES (0 trades)
    m0 = calculate_metrics([], equity, 100000.0, "DEVELOPMENT")
    assert m0.trade_count == 0
    assert m0.sample_size_warning == "NO_TRADES"

    # 2. INSUFFICIENT_SAMPLE (1-4 trades)
    from app.domain.schemas import TradeRecord
    dummy_trade = TradeRecord(trade_id="T1", symbol="S", side="LONG", entry_time="2023-01-01", exit_time="2023-01-02", entry_price=10.0, exit_price=11.0, quantity=1.0, pnl=1.0)
    m1 = calculate_metrics([dummy_trade] * 3, pd.Series([100.0, 101.0, 102.0, 103.0]), 100.0, "DEVELOPMENT")
    assert m1.sample_size_warning == "INSUFFICIENT_SAMPLE"

    # 3. LIMITED_SAMPLE (5-24 trades)
    m5 = calculate_metrics([dummy_trade] * 10, pd.Series([100.0] * 11), 100.0, "DEVELOPMENT")
    assert m5.sample_size_warning == "LIMITED_SAMPLE"

    # 4. ADEQUATE_SAMPLE (25+ trades)
    m25 = calculate_metrics([dummy_trade] * 30, pd.Series([100.0] * 31), 100.0, "DEVELOPMENT")
    assert m25.sample_size_warning == "ADEQUATE_SAMPLE"
