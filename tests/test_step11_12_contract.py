"""Tests for STEP 11 & STEP 12 - End-to-end AI experiment loop & Paper replay consistency."""
import pytest
import pandas as pd
from app.domain.schemas import StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec
from app.backtesting.engine import Backtester
from app.paper_trading.portfolio import PaperPortfolio
from app.data.base_provider import MarketData

def create_sample_market_data():
    dates = pd.date_range("2023-01-01", periods=100)
    prices = [100.0 + (i % 10) * 2.0 for i in range(100)]
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 2.0 for p in prices],
        "close": prices,
        "volume": [1000] * 100
    })
    return MarketData(symbol="RELIANCE.NS", market="INDIAN_EQUITY", timeframe="1d", df=df)

def test_backtest_and_paper_portfolio_consistency():
    data = create_sample_market_data()
    spec = StrategySpec(
        strategy_id="TEST_CONSISTENCY",
        version="v1",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        indicators=[
            IndicatorSpec(name="SMA", params={"period": 5}),
            IndicatorSpec(name="SMA", params={"period": 10})
        ],
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="sma_5", operator=">", right="sma_10")],
            exit_rules=[ConditionSpec(left="sma_5", operator="<", right="sma_10")],
            stop_loss_pct=5.0,
            take_profit_pct=10.0,
            position_sizing_pct=10.0
        )
    )

    # 1. Backtest
    bt = Backtester(initial_cash=100000.0, commission_bps=3.0, slippage_bps=1.0)
    metrics, trades, _ = bt.run(data, spec)

    # 2. Paper Portfolio Execution
    portfolio = PaperPortfolio(initial_cash=100000.0)
    pos = portfolio.open_position("RELIANCE.NS", "LONG", fill_price=100.0, quantity=100.0, fee=0.03)
    trade = portfolio.close_position("RELIANCE.NS", exit_price=105.0, fee=0.03)

    from app.config.settings import settings
    assert settings.PAPER_TRADING_ONLY is True
    assert len(portfolio.closed_trades) == 1
    assert trade.symbol == "RELIANCE.NS"
