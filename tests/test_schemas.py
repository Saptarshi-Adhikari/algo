"""Unit tests for domain schemas."""
import pytest
from app.domain.schemas import (
    StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec,
    BacktestMetrics, ExperimentRecord, PortfolioState, CriticEvaluation
)

def test_strategy_spec_validation():
    rule_set = StrategyRuleSet(
        entry_rules=[ConditionSpec(left="rsi_14", operator="<", right="30")],
        exit_rules=[ConditionSpec(left="rsi_14", operator=">", right="70")],
        stop_loss_pct=1.5,
        take_profit_pct=3.0,
        position_sizing_pct=10.0
    )
    strat = StrategySpec(
        strategy_id="EXP_001_RSI",
        version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        indicators=[IndicatorSpec(name="RSI", params={"period": 14})],
        rules=rule_set,
        description="RSI Mean Reversion"
    )
    assert strat.strategy_id == "EXP_001_RSI"
    assert len(strat.rules.entry_rules) == 1
    assert strat.rules.entry_rules[0].operator == "<"

def test_experiment_record_serialization():
    metrics = BacktestMetrics(
        total_return_pct=12.5,
        annualized_return_pct=15.0,
        sharpe_ratio=1.4,
        max_drawdown_pct=-8.2,
        win_rate=0.55,
        trade_count=40,
        average_win=1500.0,
        average_loss=-800.0,
        profit_factor=1.8,
        data_split="DEVELOPMENT"
    )
    record = ExperimentRecord(
        experiment_id="EXP_001",
        hypothesis="RSI oversold entries yield positive returns",
        strategy_version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        timeframe="1d",
        data_period="2022-01-01 to 2023-01-01",
        data_split="DEVELOPMENT",
        metrics=metrics,
        fees_assumed=0.0003,
        slippage_assumed=0.0001,
        critic_verdict="KEEP_FOR_PAPER_TESTING",
        critic_reasoning="Adequate trade count and clean risk profile",
        market_regime="RANGING",
        lesson_learned="Mean reversion works well during ranging regimes",
        status="PASSED"
    )

    data = record.model_dump()
    assert data["experiment_id"] == "EXP_001"
    assert data["metrics"]["sharpe_ratio"] == 1.4

    reconstructed = ExperimentRecord.model_validate(data)
    assert reconstructed.experiment_id == record.experiment_id
