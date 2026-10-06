"""Simulated Paper-Trading Portfolio Manager."""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.domain.schemas import PortfolioState, PortfolioPosition, TradeRecord
from app.config.safety import paper_trading_guard, assert_paper_trading_only
from app.config.logging import logger

class PaperPortfolio:
    """Tracks virtual capital, open simulated positions, realized/unrealized P&L, and drawdown."""

    def __init__(self, initial_cash: float = 100000.0):
        assert_paper_trading_only()
        self.initial_cash = initial_cash
        self.virtual_cash = initial_cash
        self.realized_pnl = 0.0
        self.positions: Dict[str, PortfolioPosition] = {}
        self.closed_trades: List[TradeRecord] = []
        self.max_equity = initial_cash
        self.trade_counter = 1

    @paper_trading_guard
    def open_position(
        self,
        symbol: str,
        side: str,
        fill_price: float,
        quantity: float,
        fee: float = 0.0
    ) -> PortfolioPosition:
        """Simulate opening a new paper position."""
        cost = (fill_price * quantity) + fee
        if cost > self.virtual_cash:
            raise ValueError(f"Insufficient virtual cash (INR/${self.virtual_cash:.2f}) for trade cost (INR/${cost:.2f})")

        self.virtual_cash -= cost
        pos_id = f"POS_{symbol}_{int(datetime.utcnow().timestamp())}"

        pos = PortfolioPosition(
            position_id=pos_id,
            symbol=symbol,
            side="LONG" if side.upper() in ["LONG", "BUY"] else "SHORT",
            entry_price=fill_price,
            current_price=fill_price,
            quantity=quantity,
            unrealized_pnl=-fee,
            entry_time=datetime.utcnow().isoformat()
        )
        self.positions[symbol] = pos
        logger.info(f"PAPER TRADE OPENED: {symbol} Qty={quantity} @ {fill_price:.2f}")
        return pos

    @paper_trading_guard
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        fee: float = 0.0,
        exit_reason: str = "PAPER_SIGNAL"
    ) -> TradeRecord:
        """Simulate closing an existing paper position."""
        if symbol not in self.positions:
            raise KeyError(f"No open paper position for symbol {symbol}")

        pos = self.positions.pop(symbol)
        gross_proceeds = pos.quantity * exit_price
        net_proceeds = gross_proceeds - fee
        self.virtual_cash += net_proceeds

        trade_pnl = net_proceeds - (pos.quantity * pos.entry_price)
        self.realized_pnl += trade_pnl
        return_pct = (trade_pnl / (pos.quantity * pos.entry_price)) * 100.0

        trade_rec = TradeRecord(
            trade_id=f"PTRADE_{self.trade_counter:04d}",
            symbol=symbol,
            side=pos.side,
            entry_time=pos.entry_time,
            exit_time=datetime.utcnow().isoformat(),
            entry_price=round(pos.entry_price, 4),
            exit_price=round(exit_price, 4),
            quantity=round(pos.quantity, 4),
            fees=round(fee, 4),
            slippage=0.0,
            pnl=round(trade_pnl, 2),
            return_pct=round(return_pct, 4),
            exit_reason=exit_reason
        )
        self.closed_trades.append(trade_rec)
        self.trade_counter += 1
        logger.info(f"PAPER TRADE CLOSED: {symbol} Exit={exit_price:.2f} PnL=INR/${trade_pnl:.2f}")
        return trade_rec

    @paper_trading_guard
    def update_market_prices(self, price_map: Dict[str, float]) -> PortfolioState:
        """Update unrealized P&L for open positions and calculate total equity."""
        unrealized = 0.0
        for symbol, pos in self.positions.items():
            if symbol in price_map:
                pos.current_price = price_map[symbol]
                if pos.side == "LONG":
                    pos.unrealized_pnl = (pos.current_price - pos.entry_price) * pos.quantity
                else:
                    pos.unrealized_pnl = (pos.entry_price - pos.current_price) * pos.quantity
            unrealized += pos.unrealized_pnl

        total_equity = self.virtual_cash + sum(pos.quantity * pos.current_price for pos in self.positions.values())
        if total_equity > self.max_equity:
            self.max_equity = total_equity

        drawdown_pct = ((self.max_equity - total_equity) / self.max_equity) * 100.0 if self.max_equity > 0 else 0.0

        return PortfolioState(
            virtual_cash=round(self.virtual_cash, 2),
            unrealized_pnl=round(unrealized, 2),
            realized_pnl=round(self.realized_pnl, 2),
            total_equity=round(total_equity, 2),
            max_equity=round(self.max_equity, 2),
            drawdown_pct=round(drawdown_pct, 2),
            open_positions=list(self.positions.values()),
            closed_trades=self.closed_trades
        )
