"""Unit tests for PaperPortfolio and PaperExecutionEngine."""
import pytest
from app.paper_trading.portfolio import PaperPortfolio
from app.paper_trading.engine import PaperExecutionEngine
from app.config.safety import RealMoneyExecutionForbiddenError
from app.config.settings import settings

def test_paper_portfolio_lifecycle():
    portfolio = PaperPortfolio(initial_cash=100000.0)

    # Open simulated position
    pos = portfolio.open_position("RELIANCE.NS", "LONG", fill_price=2000.0, quantity=10.0, fee=6.0)
    assert pos.symbol == "RELIANCE.NS"
    assert portfolio.virtual_cash == 100000.0 - (2000.0 * 10.0 + 6.0)

    # Update prices
    state = portfolio.update_market_prices({"RELIANCE.NS": 2100.0})
    assert state.unrealized_pnl == (2100.0 - 2000.0) * 10.0
    assert state.total_equity == 100000.0 - 6.0 + 1000.0

    # Close simulated position
    trade = portfolio.close_position("RELIANCE.NS", exit_price=2100.0, fee=6.3)
    assert trade.pnl == pytest.approx(993.7)
    assert len(portfolio.closed_trades) == 1

def test_paper_execution_engine():
    portfolio = PaperPortfolio(initial_cash=50000.0)
    engine = PaperExecutionEngine(portfolio)

    pos = engine.execute_order("EURUSD=X", "BUY", market_price=1.1000, quantity=1000.0)
    assert "EURUSD=X" in portfolio.positions

    trade = engine.execute_order("EURUSD=X", "SELL", market_price=1.1050, quantity=1000.0)
    assert len(portfolio.closed_trades) == 1
    assert trade.symbol == "EURUSD=X"

def test_broker_execution_forbidden_guard():
    original = settings.PAPER_TRADING_ONLY
    try:
        settings.PAPER_TRADING_ONLY = False
        with pytest.raises(RealMoneyExecutionForbiddenError):
            PaperPortfolio(initial_cash=10000.0)
    finally:
        settings.PAPER_TRADING_ONLY = original
