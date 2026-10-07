"""Unit tests for indicators and StrategyEvaluator."""
import pytest
import pandas as pd
import numpy as np
from app.domain.schemas import StrategySpec, StrategyRuleSet, ConditionSpec, IndicatorSpec
from app.strategies.indicators import enrich_with_indicators, calculate_sma, calculate_rsi
from app.strategies.evaluator import StrategyEvaluator

@pytest.fixture
def sample_ohlcv():
    dates = pd.date_range(start="2023-01-01", periods=50, freq="D")
    prices = np.linspace(100, 200, 50)
    # Add a dip for RSI test
    prices[20:25] = [150, 140, 130, 120, 110]
    return pd.DataFrame({
        "timestamp": dates,
        "open": prices * 0.99,
        "high": prices * 1.01,
        "low": prices * 0.98,
        "close": prices,
        "volume": 1000.0
    })

def test_indicators_calculation(sample_ohlcv):
    sma20 = calculate_sma(sample_ohlcv, 20)
    rsi14 = calculate_rsi(sample_ohlcv, 14)

    assert len(sma20) == 50
    assert pd.isna(sma20.iloc[0])
    assert not pd.isna(sma20.iloc[19])
    assert rsi14.min() >= 0.0 and rsi14.max() <= 100.0

def test_evaluator_signal_generation(sample_ohlcv):
    spec = StrategySpec(
        strategy_id="TEST_SMA_CROSS",
        version="v1",
        market="INDIAN_EQUITY",
        symbol="RELIANCE.NS",
        indicators=[
            IndicatorSpec(name="SMA", params={"period": 5}),
            IndicatorSpec(name="SMA", params={"period": 10})
        ],
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="sma_5", operator=">", right="sma_10")],
            exit_rules=[ConditionSpec(left="sma_5", operator="<", right="sma_10")]
        )
    )

    evaluator = StrategyEvaluator(spec)
    result_df = evaluator.evaluate(sample_ohlcv)

    assert "sma_5" in result_df.columns
    assert "sma_10" in result_df.columns
    assert "entry_signal" in result_df.columns
    assert "exit_signal" in result_df.columns

def test_numeric_constant(sample_ohlcv):
    spec = StrategySpec(
        strategy_id="TEST_NUM", version="v1", market="INDIAN_EQUITY", symbol="RELIANCE.NS",
        rules=StrategyRuleSet(entry_rules=[ConditionSpec(left="close", operator=">", right="1.05")])
    )
    evaluator = StrategyEvaluator(spec)
    df = evaluator.evaluate(sample_ohlcv)
    assert len(df) == 50

def test_normal_column(sample_ohlcv):
    spec = StrategySpec(
        strategy_id="TEST_COL", version="v1", market="INDIAN_EQUITY", symbol="RELIANCE.NS",
        rules=StrategyRuleSet(entry_rules=[ConditionSpec(left="close", operator=">", right="open")])
    )
    evaluator = StrategyEvaluator(spec)
    df = evaluator.evaluate(sample_ohlcv)
    assert len(df) == 50

def test_previous_bar_close_shift(sample_ohlcv):
    spec = StrategySpec(
        strategy_id="TEST_SHIFT_PREV", version="v1", market="INDIAN_EQUITY", symbol="RELIANCE.NS",
        rules=StrategyRuleSet(entry_rules=[ConditionSpec(left="close", operator=">", right="close(-1)")])
    )
    evaluator = StrategyEvaluator(spec)
    df = evaluator.evaluate(sample_ohlcv)
    res_ser = evaluator._resolve_operand("close(-1)", sample_ohlcv)
    assert pd.isna(res_ser.iloc[0])
    assert res_ser.iloc[1] == sample_ohlcv["close"].iloc[0]

def test_positive_shift(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    res_ser = evaluator._resolve_operand("close(1)", sample_ohlcv)
    assert res_ser.iloc[0] == sample_ohlcv["close"].iloc[1]

def test_multiplication_with_shifted_close(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    res_ser = evaluator._resolve_operand("1.05 * close(-1)", sample_ohlcv)
    assert pd.isna(res_ser.iloc[0])
    assert abs(res_ser.iloc[1] - (1.05 * sample_ohlcv["close"].iloc[0])) < 1e-5

def test_reversed_multiplication(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    res_ser = evaluator._resolve_operand("close(-1) * 1.05", sample_ohlcv)
    assert pd.isna(res_ser.iloc[0])
    assert abs(res_ser.iloc[1] - (sample_ohlcv["close"].iloc[0] * 1.05)) < 1e-5

def test_arithmetic_with_indicators(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    sample_ohlcv["sma_20"] = calculate_sma(sample_ohlcv, 20)
    sample_ohlcv["atr_14"] = sample_ohlcv["high"] - sample_ohlcv["low"]
    res_ser = evaluator._resolve_operand("sma_20 - 1.5 * atr_14", sample_ohlcv)
    assert len(res_ser) == 50

def test_nested_supported_expression(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    sample_ohlcv["sma_20"] = 100.0
    sample_ohlcv["atr_14"] = 10.0
    res_ser = evaluator._resolve_operand("1.02 * (sma_20 + atr_14)", sample_ohlcv)
    assert res_ser.iloc[0] == 1.02 * (100.0 + 10.0)

def test_invalid_function_name_rejected(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    with pytest.raises((ValueError, KeyError)):
        evaluator._resolve_operand("invalid_fn(-1)", sample_ohlcv)

def test_malicious_expression_rejected(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    with pytest.raises((ValueError, KeyError)):
        evaluator._resolve_operand("__import__('os').system('dir')", sample_ohlcv)

def test_nonexistent_column_rejected(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    with pytest.raises(KeyError):
        evaluator._resolve_operand("non_existent_column_xyz", sample_ohlcv)

def test_division_by_zero_handled(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    res_ser = evaluator._resolve_operand("close / 0.0", sample_ohlcv)
    assert len(res_ser) == 50
    assert (res_ser == 0.0).all()

def test_no_future_data_leakage_from_shifts(sample_ohlcv):
    evaluator = StrategyEvaluator(StrategySpec(strategy_id="T", version="v1", symbol="S", rules=StrategyRuleSet()))
    res_ser = evaluator._resolve_operand("close(-1)", sample_ohlcv)
    # Ensure index i relies ONLY on index i-1
    assert res_ser.iloc[10] == sample_ohlcv["close"].iloc[9]

def test_future_data_validator_allowed_previous_bar(sample_ohlcv):
    from app.strategies.future_validator import FutureDataReferenceValidator, FutureDataReferenceError
    spec = StrategySpec(
        strategy_id="VALID_LOOKBACK", version="v1", symbol="S",
        rules=StrategyRuleSet(entry_rules=[ConditionSpec(left="close", operator=">", right="close(-1)")])
    )
    # Should pass validation without error
    FutureDataReferenceValidator.validate_strategy(spec)

def test_future_data_validator_rejected_future_bar(sample_ohlcv):
    from app.strategies.future_validator import FutureDataReferenceValidator, FutureDataReferenceError
    spec = StrategySpec(
        strategy_id="INVALID_FUTURE", version="v1", symbol="S",
        rules=StrategyRuleSet(entry_rules=[ConditionSpec(left="close", operator=">", right="close(1)")])
    )
    with pytest.raises(FutureDataReferenceError):
        FutureDataReferenceValidator.validate_strategy(spec)

def test_future_data_validator_nested_arithmetic(sample_ohlcv):
    from app.strategies.future_validator import FutureDataReferenceValidator, FutureDataReferenceError
    spec = StrategySpec(
        strategy_id="INVALID_NESTED", version="v1", symbol="S",
        rules=StrategyRuleSet(entry_rules=[ConditionSpec(left="close", operator=">", right="1.05 * close(2)")])
    )
    with pytest.raises(FutureDataReferenceError):
        FutureDataReferenceValidator.validate_strategy(spec)

def test_future_data_validator_parentheses_and_multiple_rules(sample_ohlcv):
    from app.strategies.future_validator import FutureDataReferenceValidator, FutureDataReferenceError
    spec = StrategySpec(
        strategy_id="INVALID_MULTI", version="v1", symbol="S",
        rules=StrategyRuleSet(
            entry_rules=[ConditionSpec(left="close", operator=">", right="sma_20")],
            exit_rules=[ConditionSpec(left="open(1)", operator="<", right="low")]
        )
    )
    with pytest.raises(FutureDataReferenceError):
        FutureDataReferenceValidator.validate_strategy(spec)


