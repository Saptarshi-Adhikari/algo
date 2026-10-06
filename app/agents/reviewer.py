"""Backtest Reviewer AI Agent summarizing quantitative metrics without fabrication."""
from typing import List, Dict, Any
from app.domain.schemas import BacktestMetrics, TradeRecord

class BacktestReviewerAgent:
    """Summarizes actual calculated backtest metrics."""

    def summarize(self, metrics: BacktestMetrics, trades: List[TradeRecord]) -> Dict[str, Any]:
        has_adequate_trades = metrics.trade_count >= 10
        summary = {
            "data_split": metrics.data_split,
            "trade_count": metrics.trade_count,
            "total_return_pct": metrics.total_return_pct,
            "sharpe_ratio": metrics.sharpe_ratio,
            "max_drawdown_pct": metrics.max_drawdown_pct,
            "win_rate": metrics.win_rate,
            "profit_factor": metrics.profit_factor,
            "has_adequate_trades": has_adequate_trades,
            "summary_text": (
                f"Backtest executed on {metrics.data_split} set ({metrics.trade_count} trades). "
                f"Total Return: {metrics.total_return_pct:.2f}%, Sharpe: {metrics.sharpe_ratio:.2f}, "
                f"Max Drawdown: {metrics.max_drawdown_pct:.2f}%, Win Rate: {metrics.win_rate*100:.1f}%."
            )
        }
        return summary
