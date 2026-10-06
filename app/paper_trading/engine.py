"""Simulated Paper Execution Engine."""
from typing import Dict, Any, Optional
from app.paper_trading.portfolio import PaperPortfolio
from app.config.safety import paper_trading_guard, assert_paper_trading_only
from app.config.logging import logger

class PaperExecutionEngine:
    """Executes paper trade intents safely against simulated portfolio."""

    def __init__(self, portfolio: PaperPortfolio, commission_bps: float = 3.0, slippage_bps: float = 1.0):
        assert_paper_trading_only()
        self.portfolio = portfolio
        self.commission_rate = commission_bps / 10000.0
        self.slippage_rate = slippage_bps / 10000.0

    @paper_trading_guard
    def execute_order(
        self,
        symbol: str,
        side: str,  # BUY or SELL
        market_price: float,
        quantity: float,
        reason: str = "SIMULATED_ORDER"
    ):
        """Simulate order execution with fees and slippage."""
        assert_paper_trading_only()

        side_upper = side.upper()
        if side_upper == "BUY":
            fill_price = market_price * (1.0 + self.slippage_rate)
            fee = fill_price * quantity * self.commission_rate
            return self.portfolio.open_position(symbol, side_upper, fill_price, quantity, fee)

        elif side_upper in ["SELL", "CLOSE"]:
            fill_price = market_price * (1.0 - self.slippage_rate)
            fee = fill_price * quantity * self.commission_rate
            return self.portfolio.close_position(symbol, fill_price, fee, exit_reason=reason)

        else:
            raise ValueError(f"Invalid paper order side: {side}")
