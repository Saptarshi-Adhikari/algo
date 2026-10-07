"""Tests for STEP 4 - Feature preparation and indicator expression evaluation contract."""
import pytest
import pandas as pd
from app.domain.schemas import StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec
from app.strategies.evaluator import StrategyEvaluator
from app.strategies.future_validator import FutureDataReferenceValidator

def create_sample_df():
    dates = pd.date_range("2023-01-01", periods=100)
    prices = [100.0 + i * 0.5 for i in range(100)]
    return pd.DataFrame({
        "timestamp": dates,
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 2.0 for p in prices],
        "close": prices,
        "volume": [1000 + i * 10 for i in range(100)]
    })

def test_sma_and_ema_operands_evaluation():
    df = create_sample_df()
    spec = StrategySpec(
        strategy_id="TEST_IND",
        version="v1",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        indicators=[
            IndicatorSpec(name="SMA", params={"period": 20}),
            IndicatorSpec(name="EMA", params={"period": 10})
        ],
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="sma_20", operator=">", right="ema_10")],
            exit_rules=[ConditionSpec(left="close", operator="<", right="sma_20")]
        )
    )
    evaluator = StrategyEvaluator(spec)
    res_df = evaluator.evaluate(df)
    assert "entry_signal" in res_df.columns
    assert "exit_signal" in res_df.columns
    assert "sma_20" in res_df.columns
    assert "ema_10" in res_df.columns

def test_arithmetic_operand_expression_evaluation():
    df = create_sample_df()
    spec = StrategySpec(
        strategy_id="TEST_MATH",
        version="v1",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        indicators=[IndicatorSpec(name="SMA", params={"period": 20})],
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="1.05 * close(-1)", operator=">", right="sma_20")],
            exit_rules=[ConditionSpec(left="close", operator="<", right="0.98 * close(-1)")]
        )
    )
    evaluator = StrategyEvaluator(spec)
    res_df = evaluator.evaluate(df)
    assert "entry_signal" in res_df.columns
    assert "exit_signal" in res_df.columns

def test_unsupported_indicator_handling():
    df = create_sample_df()
    spec = StrategySpec(
        strategy_id="TEST_UNSUPPORTED",
        version="v1",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="unknown_indicator_999", operator=">", right="50")],
            exit_rules=[]
        )
    )
    evaluator = StrategyEvaluator(spec)
    with pytest.raises(KeyError):
        evaluator.evaluate(df)

def test_future_data_prevention():
    spec = StrategySpec(
        strategy_id="TEST_LOOKAHEAD",
        version="v1",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="close(1)", operator=">", right="close")],  # lookahead close(1)
            exit_rules=[]
        )
    )
    with pytest.raises(ValueError, match="FUTURE DATA LEAKAGE DETECTED"):
        FutureDataReferenceValidator.validate_strategy(spec)
