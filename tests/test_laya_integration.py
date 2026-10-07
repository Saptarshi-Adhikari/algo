"""Tests for Phase 13 Laya Shadow Integration."""
import pytest
from app.domain.decision_schemas import MarketState
from app.domain.laya_schemas import LayaPredictionResult
from app.decision.laya_adapter import LayaAdapter
from app.memory.laya_repository import LayaPredictionRepository

def test_laya_prediction_schema():
    res = LayaPredictionResult(
        decision_id="SHADOW_001",
        timestamp="2023-01-10T00:00:00",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        timeframe="1d",
        dataset_id="DS_1",
        dataset_hash="HASH_1",
        state_hash="HASH_1",
        predicted_direction="BUY",
        confidence=0.85,
        confidence_status="UNCALIBRATED",
        decision_authority="SHADOW_ONLY"
    )
    assert res.decision_authority == "SHADOW_ONLY"
    assert res.confidence_status == "UNCALIBRATED"
    assert res.predicted_direction == "BUY"

def test_laya_adapter_predict_isolation():
    state = MarketState(
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        timeframe="1d",
        timestamp="2023-01-10T00:00:00",
        dataset_id="DS_1",
        dataset_hash="HASH_1",
        open=100.0, high=105.0, low=95.0, close=102.0, volume=1000.0
    )
    adapter = LayaAdapter(model_id="convaiinnovations/laya")
    res = adapter.predict(state, decision_id="TEST_DEC_001")

    assert isinstance(res, LayaPredictionResult)
    assert res.decision_authority == "SHADOW_ONLY"
    # Even if model is unavailable or encounters environment error, status is structured, not unhandled crash
    assert res.status in ("SUCCESS", "MODEL_UNAVAILABLE", "MODEL_ERROR")

def test_laya_repository_lifecycle():
    repo = LayaPredictionRepository()
    repo.clear()

    res = LayaPredictionResult(
        decision_id="TEST_SHADOW_101",
        timestamp="2023-01-10T00:00:00",
        symbol="RELIANCE.NS",
        market="INDIAN_EQUITY",
        timeframe="1d",
        dataset_id="DS_1",
        dataset_hash="HASH_1",
        state_hash="HASH_1",
        predicted_direction="HOLD",
        status="SUCCESS"
    )
    repo.save(res)
    assert repo.count() == 1

    all_records = repo.list_all()
    assert len(all_records) == 1
    assert all_records[0].decision_id == "TEST_SHADOW_101"
