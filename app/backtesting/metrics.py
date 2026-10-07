"""Pure deterministic backtest metrics calculation."""
import numpy as np
import pandas as pd
from typing import List
from app.domain.schemas import BacktestMetrics, TradeRecord, DataSplitName

def calculate_metrics(
    trades: List[TradeRecord],
    equity_curve: pd.Series,
    initial_cash: float,
    data_split: DataSplitName = "DEVELOPMENT",
    risk_free_rate: float = 0.05
) -> BacktestMetrics:
    """Calculate quantitative strategy metrics purely from trade history and equity curve."""
    trade_count = len(trades)
    if trade_count == 0 or len(equity_curve) < 2:
        return BacktestMetrics(
            total_return_pct=0.0,
            annualized_return_pct=0.0,
            sharpe_ratio=0.0,
            max_drawdown_pct=0.0,
            win_rate=0.0,
            trade_count=0,
            average_win=0.0,
            average_loss=0.0,
            profit_factor=0.0,
            data_split=data_split,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            expectancy_per_trade=0.0,
            sample_size_warning="NO_TRADES"
        )

    final_equity = equity_curve.iloc[-1]
    total_return_pct = ((final_equity - initial_cash) / initial_cash) * 100.0

    # Calculate trading days
    num_days = max(1, len(equity_curve))
    num_years = num_days / 252.0
    if num_years > 0 and final_equity > 0:
        annualized_return_pct = (((final_equity / initial_cash) ** (1.0 / num_years)) - 1.0) * 100.0
    else:
        annualized_return_pct = 0.0

    # Drawdown calculation
    running_max = equity_curve.cummax()
    drawdown_series = (equity_curve - running_max) / running_max * 100.0
    max_drawdown_pct = float(drawdown_series.min())

    # Sharpe ratio
    daily_returns = equity_curve.pct_change().dropna()
    if len(daily_returns) > 1 and daily_returns.std() > 1e-8:
        rf_daily = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
        excess_returns = daily_returns - rf_daily
        sharpe_ratio = float((excess_returns.mean() / daily_returns.std()) * np.sqrt(252.0))
    else:
        sharpe_ratio = 0.0

    # Trade stats
    wins = [t.pnl for t in trades if t.pnl > 0]
    losses = [t.pnl for t in trades if t.pnl < 0]

    win_count = len(wins)
    loss_count = len(losses)
    win_rate = win_count / trade_count if trade_count > 0 else 0.0

    average_win = float(np.mean(wins)) if wins else 0.0
    average_loss = float(np.mean(losses)) if losses else 0.0

    total_gross_win = sum(wins)
    total_gross_loss = abs(sum(losses))
    profit_factor = float(total_gross_win / total_gross_loss) if total_gross_loss > 0 else (999.0 if total_gross_win > 0 else 0.0)

    # Extended Metrics (Sortino, Calmar, Expectancy, Sample Warning)
    downside_returns = daily_returns[daily_returns < 0]
    if len(downside_returns) > 1 and downside_returns.std() > 1e-8:
        rf_daily = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
        sortino_ratio = float(((daily_returns.mean() - rf_daily) / downside_returns.std()) * np.sqrt(252.0))
    else:
        sortino_ratio = 0.0

    calmar_ratio = float(annualized_return_pct / abs(max_drawdown_pct)) if max_drawdown_pct < 0 else 0.0
    expectancy_per_trade = float((win_rate * average_win) - ((1.0 - win_rate) * abs(average_loss)))

    if trade_count == 0:
        sample_size_warning = "NO_TRADES"
    elif trade_count < 5:
        sample_size_warning = "INSUFFICIENT_SAMPLE"
    elif trade_count < 25:
        sample_size_warning = "LIMITED_SAMPLE"
    else:
        sample_size_warning = "ADEQUATE_SAMPLE"

    return BacktestMetrics(
        total_return_pct=round(total_return_pct, 4),
        annualized_return_pct=round(annualized_return_pct, 4),
        sharpe_ratio=round(sharpe_ratio, 4),
        max_drawdown_pct=round(max_drawdown_pct, 4),
        win_rate=round(win_rate, 4),
        trade_count=trade_count,
        average_win=round(average_win, 4),
        average_loss=round(average_loss, 4),
        profit_factor=round(profit_factor, 4),
        data_split=data_split,
        sortino_ratio=round(sortino_ratio, 4),
        calmar_ratio=round(calmar_ratio, 4),
        expectancy_per_trade=round(expectancy_per_trade, 4),
        sample_size_warning=sample_size_warning
    )
