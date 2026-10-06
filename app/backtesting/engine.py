"""Pure deterministic Python backtesting engine."""
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any
from app.data.base_provider import MarketData
from app.domain.schemas import StrategySpec, TradeRecord, BacktestMetrics, DataSplitName
from app.strategies.evaluator import StrategyEvaluator
from app.backtesting.metrics import calculate_metrics

class Backtester:
    """Deterministic event-driven / bar-by-bar Python backtesting engine."""

    def __init__(
        self,
        initial_cash: float = 100000.0,
        commission_bps: float = 3.0,  # 3 bps = 0.0003
        slippage_bps: float = 1.0     # 1 bps = 0.0001
    ):
        self.initial_cash = initial_cash
        self.commission_rate = commission_bps / 10000.0
        self.slippage_rate = slippage_bps / 10000.0

    def run(
        self,
        data: MarketData,
        spec: StrategySpec,
        data_split: DataSplitName = "DEVELOPMENT"
    ) -> Tuple[BacktestMetrics, List[TradeRecord], pd.Series]:
        """Execute strategy deterministically on dataset."""
        evaluator = StrategyEvaluator(spec)
        df = evaluator.evaluate(data.df)

        cash = self.initial_cash
        position_qty = 0.0
        entry_price = 0.0
        entry_time = ""
        trade_id_counter = 1

        trades: List[TradeRecord] = []
        equity_values = []

        stop_loss_pct = spec.rules.stop_loss_pct
        take_profit_pct = spec.rules.take_profit_pct
        position_sizing_pct = spec.rules.position_sizing_pct / 100.0

        for idx, row in df.iterrows():
            current_close = float(row["close"])
            current_high = float(row["high"])
            current_low = float(row["low"])
            timestamp_str = str(row["timestamp"])

            # 1. Manage open position if holding
            if position_qty > 0:
                exit_price = None
                exit_reason = None

                # Check Stop Loss
                if stop_loss_pct and stop_loss_pct > 0:
                    sl_trigger_price = entry_price * (1.0 - (stop_loss_pct / 100.0))
                    if current_low <= sl_trigger_price:
                        exit_price = sl_trigger_price * (1.0 - self.slippage_rate)
                        exit_reason = f"STOP_LOSS ({stop_loss_pct}%)"

                # Check Take Profit
                if exit_price is None and take_profit_pct and take_profit_pct > 0:
                    tp_trigger_price = entry_price * (1.0 + (take_profit_pct / 100.0))
                    if current_high >= tp_trigger_price:
                        exit_price = tp_trigger_price * (1.0 - self.slippage_rate)
                        exit_reason = f"TAKE_PROFIT ({take_profit_pct}%)"

                # Check Exit Signal
                if exit_price is None and row["exit_signal"] == 1:
                    exit_price = current_close * (1.0 - self.slippage_rate)
                    exit_reason = "EXIT_SIGNAL"

                # If exiting trade
                if exit_price is not None:
                    gross_proceeds = position_qty * exit_price
                    fee = gross_proceeds * self.commission_rate
                    net_proceeds = gross_proceeds - fee

                    cash += net_proceeds
                    trade_pnl = net_proceeds - (position_qty * entry_price)
                    return_pct = (trade_pnl / (position_qty * entry_price)) * 100.0

                    trade_rec = TradeRecord(
                        trade_id=f"TRADE_{trade_id_counter:04d}",
                        symbol=spec.symbol,
                        side="LONG",
                        entry_time=entry_time,
                        exit_time=timestamp_str,
                        entry_price=round(entry_price, 4),
                        exit_price=round(exit_price, 4),
                        quantity=round(position_qty, 4),
                        fees=round(fee, 4),
                        slippage=round(self.slippage_rate * position_qty * exit_price, 4),
                        pnl=round(trade_pnl, 2),
                        return_pct=round(return_pct, 4),
                        exit_reason=exit_reason
                    )
                    trades.append(trade_rec)
                    trade_id_counter += 1
                    position_qty = 0.0

            # 2. Check for new entry if not holding position
            if position_qty == 0 and row["entry_signal"] == 1:
                alloc_cash = cash * position_sizing_pct
                if alloc_cash > 10.0:
                    fill_price = current_close * (1.0 + self.slippage_rate)
                    fee = alloc_cash * self.commission_rate
                    net_alloc = alloc_cash - fee
                    position_qty = net_alloc / fill_price
                    cash -= alloc_cash
                    entry_price = fill_price
                    entry_time = timestamp_str

            # Record current bar total equity
            current_equity = cash + (position_qty * current_close)
            equity_values.append(current_equity)

        # Force close any open position at final bar for complete reporting
        if position_qty > 0:
            final_row = df.iloc[-1]
            exit_price = float(final_row["close"]) * (1.0 - self.slippage_rate)
            gross_proceeds = position_qty * exit_price
            fee = gross_proceeds * self.commission_rate
            net_proceeds = gross_proceeds - fee
            cash += net_proceeds
            trade_pnl = net_proceeds - (position_qty * entry_price)
            return_pct = (trade_pnl / (position_qty * entry_price)) * 100.0

            trade_rec = TradeRecord(
                trade_id=f"TRADE_{trade_id_counter:04d}",
                symbol=spec.symbol,
                side="LONG",
                entry_time=entry_time,
                exit_time=str(final_row["timestamp"]),
                entry_price=round(entry_price, 4),
                exit_price=round(exit_price, 4),
                quantity=round(position_qty, 4),
                fees=round(fee, 4),
                slippage=round(self.slippage_rate * position_qty * exit_price, 4),
                pnl=round(trade_pnl, 2),
                return_pct=round(return_pct, 4),
                exit_reason="END_OF_DATA"
            )
            trades.append(trade_rec)
            equity_values[-1] = cash

        equity_curve = pd.Series(equity_values, index=df["timestamp"])
        metrics = calculate_metrics(trades, equity_curve, self.initial_cash, data_split)

        return metrics, trades, equity_curve
