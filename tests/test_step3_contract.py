"""Tests for STEP 3 - BacktestMetrics sample_size_warning contract & classification rules."""
import pytest
from app.domain.schemas import BacktestMetrics, CriticEvaluation
from app.agents.critic import CriticAgent

def test_backtest_metrics_has_sample_size_warning():
    m = BacktestMetrics(
        total_return_pct=5.0,
        annualized_return_pct=10.0,
        sharpe_ratio=1.2,
        max_drawdown_pct=-4.0,
        win_rate=0.6,
        trade_count=30,
        average_win=100.0,
        average_loss=-50.0,
        profit_factor=1.5,
        data_split="DEVELOPMENT",
        sample_size_warning="ADEQUATE_SAMPLE"
    )
    assert hasattr(m, "sample_size_warning")
    assert m.sample_size_warning == "ADEQUATE_SAMPLE"

def test_trade_count_classifications():
    def make_metrics(trades: int) -> BacktestMetrics:
        sw = "NO_TRADES" if trades == 0 else ("INSUFFICIENT_SAMPLE" if trades < 5 else ("LIMITED_SAMPLE" if trades < 25 else "ADEQUATE_SAMPLE"))
        return BacktestMetrics(
            total_return_pct=0.0,
            annualized_return_pct=0.0,
            sharpe_ratio=0.0,
            max_drawdown_pct=0.0,
            win_rate=0.0,
            trade_count=trades,
            average_win=0.0,
            average_loss=0.0,
            profit_factor=0.0,
            data_split="DEVELOPMENT",
            sample_size_warning=sw
        )

    m0 = make_metrics(0)
    assert m0.sample_size_warning == "NO_TRADES"

    m3 = make_metrics(3)
    assert m3.sample_size_warning == "INSUFFICIENT_SAMPLE"

    m15 = make_metrics(15)
    assert m15.sample_size_warning == "LIMITED_SAMPLE"

    m30 = make_metrics(30)
    assert m30.sample_size_warning == "ADEQUATE_SAMPLE"

def test_critic_rejects_zero_trades():
    from app.domain.schemas import StrategySpec, StrategyRuleSet
    spec = StrategySpec(
        strategy_id="TEST", version="v1", symbol="TEST", market="INDIAN_EQUITY",
        rules=StrategyRuleSet(entry_rules=[], exit_rules=[])
    )
    critic = CriticAgent()
    m0 = BacktestMetrics(
        total_return_pct=0.0,
        annualized_return_pct=0.0,
        sharpe_ratio=0.0,
        max_drawdown_pct=0.0,
        win_rate=0.0,
        trade_count=0,
        average_win=0.0,
        average_loss=0.0,
        profit_factor=0.0,
        data_split="DEVELOPMENT",
        sample_size_warning="NO_TRADES"
    )
    eval_res = critic.evaluate(m0, spec)
    assert eval_res.verdict == "REJECT"
    assert "0" in eval_res.reasoning or "NO_TRADES" in eval_res.reasoning or "zero" in eval_res.reasoning.lower()
