"""Tests for STEP 2, 3, 4, 5 decision schemas."""
import pytest
from app.domain.decision_schemas import (
    MarketState, DecisionQuestion, GroundTruthOutcome, DecisionRecord
)

def test_market_state_causal_schema():
    state = MarketState(
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        timeframe="1d",
        timestamp="2023-01-10T00:00:00",
        dataset_id="DS_RELIANCE.NS_3eb48c59",
        dataset_hash="3eb48c5914646b45",
        open=2400.0, high=2450.0, low=2390.0, close=2440.0, volume=500000.0,
        sma_10=2410.0, rsi_14=55.4, regime="TRENDING"
    )
    assert state.symbol == "RELIANCE.NS"
    assert state.close == 2440.0
    assert state.sma_20 is None

def test_ground_truth_outcome_schema():
    outcome = GroundTruthOutcome(
        decision_timestamp="2023-01-10T00:00:00",
        evaluation_horizon_bars=4,
        future_observation_end_timestamp="2023-01-14T00:00:00",
        direction_outcome="BUY",
        realized_return_pct=2.5,
        max_favorable_excursion_pct=3.1,
        max_adverse_excursion_pct=-0.8
    )
    assert outcome.direction_outcome == "BUY"
    assert outcome.realized_return_pct == 2.5

def test_decision_record_schema():
    state = MarketState(
        symbol="RELIANCE.NS", market="INDIAN_EQUITY", timeframe="1d",
        timestamp="2023-01-10T00:00:00", dataset_id="DS_1", dataset_hash="HASH_1",
        open=100.0, high=105.0, low=95.0, close=102.0, volume=1000.0
    )
    outcome = GroundTruthOutcome(
        decision_timestamp="2023-01-10T00:00:00", evaluation_horizon_bars=4,
        future_observation_end_timestamp="2023-01-14T00:00:00",
        direction_outcome="HOLD", realized_return_pct=0.1,
        max_favorable_excursion_pct=0.5, max_adverse_excursion_pct=-0.4
    )
    rec = DecisionRecord(
        decision_id="DEC_001", timestamp="2023-01-10T00:00:00",
        symbol="RELIANCE.NS", market="INDIAN_EQUITY", dataset_id="DS_1", dataset_hash="HASH_1",
        state=state, ground_truth=outcome
    )
    assert rec.decision_id == "DEC_001"
    assert rec.state.symbol == "RELIANCE.NS"
