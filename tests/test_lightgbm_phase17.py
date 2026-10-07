"""Unit and integration tests for Phase 17 LightGBM Numerical Prediction Foundation."""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from app.config.settings import settings
from app.domain.lightgbm_schemas import (
    LightGBMFeatureSchema, LightGBMTargetPolicy, LightGBMSplitPolicy, LightGBMModelStatus
)
from app.evaluation.lightgbm_feature_builder import LightGBMFeatureBuilder
from app.models.lightgbm_model import LightGBMNumericalPredictor
from app.memory.lightgbm_model_registry import LightGBMModelRegistry

def test_lightgbm_feature_builder():
    builder = LightGBMFeatureBuilder()
    dates = pd.date_range("2026-01-01", periods=100, freq="1D")
    df = pd.DataFrame({
        "timestamp": dates.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "open": np.linspace(100, 150, 100),
        "high": np.linspace(102, 152, 100),
        "low": np.linspace(98, 148, 100),
        "close": np.linspace(101, 151, 100),
        "volume": np.random.randint(1000, 5000, 100)
    })

    clean_df = builder.build_features_and_target(df)
    assert not clean_df.empty
    assert "target_return_4bar" in clean_df.columns
    
    # Audit feature leakage
    audit = builder.audit_feature_leakage(clean_df)
    assert audit["passed"] is True

def test_chronological_splits():
    predictor = LightGBMNumericalPredictor()
    dates = pd.date_range("2026-01-01", periods=100, freq="1D")
    df = pd.DataFrame({
        "timestamp": dates.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "close": np.linspace(100, 150, 100),
        "target_return_4bar": np.random.randn(100)
    })

    train_df, val_df, holdout_df = predictor.create_chronological_splits(df)
    assert len(train_df) == 70
    assert len(val_df) == 15
    assert len(holdout_df) == 15
    assert train_df["timestamp"].iloc[-1] < val_df["timestamp"].iloc[0]
    assert val_df["timestamp"].iloc[-1] < holdout_df["timestamp"].iloc[0]

def test_lightgbm_fit_and_evaluate(tmp_path):
    models_dir = tmp_path / "models"
    registry_file = tmp_path / "lgbm_registry.json"
    
    predictor = LightGBMNumericalPredictor(model_dir=models_dir)
    predictor.registry = LightGBMModelRegistry(registry_path=registry_file)

    dates = pd.date_range("2026-01-01", periods=150, freq="1D")
    df = pd.DataFrame({
        "timestamp": dates.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "open": np.sin(np.linspace(0, 10, 150)) + 100,
        "high": np.sin(np.linspace(0, 10, 150)) + 102,
        "low": np.sin(np.linspace(0, 10, 150)) + 98,
        "close": np.sin(np.linspace(0, 10, 150)) + 100,
        "volume": np.random.randint(1000, 5000, 150)
    })

    manifest = predictor.fit_and_evaluate(df)
    assert manifest.model_id == "ALGO_LGBM_V001"
    assert manifest.status in list(LightGBMModelStatus)
    assert "rmse" in manifest.validation_metrics
    assert "rmse" in manifest.holdout_metrics
    assert manifest.decision_authority == "OFFLINE_RESEARCH_ONLY"

def test_safety_audit():
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
