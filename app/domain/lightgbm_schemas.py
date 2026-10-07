"""Domain schemas for Phase 17 LightGBM Numerical Prediction Foundation."""
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class LightGBMModelStatus(str, Enum):
    """Validation status for registered LightGBM candidate models."""
    EXPERIMENTAL = "EXPERIMENTAL"
    VALIDATED_FOR_RESEARCH = "VALIDATED_FOR_RESEARCH"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    REJECTED = "REJECTED"
    TRAINING_FAILED = "TRAINING_FAILED"

class LightGBMTargetPolicy(BaseModel):
    """Immutable versioned target policy definition for LightGBM."""
    target_policy_version: str = "LIGHTGBM_TARGET_POLICY_V1"
    target_name: str = "future_return_4bar"
    horizon_bars: int = 4
    return_type: str = "raw_close_ratio_minus_1"
    price_field: str = "close"
    timestamp_convention: str = "bar_close_timestamp"
    missing_target_behavior: str = "drop_unresolved_horizon_rows"
    minimum_available_future_bars: int = 4

class LightGBMFeatureSchema(BaseModel):
    """Immutable versioned feature schema for LightGBM."""
    feature_schema_version: str = "LIGHTGBM_FEATURE_SCHEMA_V1"
    price_returns: List[str] = Field(default_factory=lambda: ["return_1", "return_2", "return_4", "return_8", "return_16"])
    moving_averages: List[str] = Field(default_factory=lambda: ["sma_5", "sma_10", "sma_20", "sma_50"])
    relative_positions: List[str] = Field(default_factory=lambda: ["close_vs_sma_10", "close_vs_sma_20", "close_vs_sma_50"])
    volatility_indicators: List[str] = Field(default_factory=lambda: ["rolling_std_5", "rolling_std_10", "rolling_std_20", "atr_14"])
    momentum_indicators: List[str] = Field(default_factory=lambda: ["rsi_14", "momentum_5", "momentum_10", "ema_12", "ema_26", "macd", "macd_signal"])
    volume_indicators: List[str] = Field(default_factory=lambda: ["volume_change", "volume_sma_ratio"])

    def all_feature_names(self) -> List[str]:
        """Returns flattened list of all feature names."""
        return (
            self.price_returns + self.moving_averages + self.relative_positions +
            self.volatility_indicators + self.momentum_indicators + self.volume_indicators
        )

class LightGBMSplitPolicy(BaseModel):
    """Immutable versioned chronological split policy."""
    split_policy_version: str = "LIGHTGBM_SPLIT_POLICY_V1"
    train_ratio: float = 0.70
    validation_ratio: float = 0.15
    holdout_ratio: float = 0.15
    split_method: str = "strictly_chronological"

class NumericalEvaluationMetrics(BaseModel):
    """Comprehensive numerical prediction evaluation metrics."""
    rmse: float
    mae: float
    r2_score: float
    directional_accuracy: float
    correlation: float
    sample_size: int

class LightGBMModelManifest(BaseModel):
    """Permanent manifest record for a LightGBM candidate model."""
    model_id: str = "ALGO_LGBM_V001"
    model_type: str = "LightGBM_Regressor"
    run_id: str = "ALGO_LGBM_TRAIN_RUN_001"
    lightgbm_version: str = "4.7.0"
    python_version: str = "3.11.0"
    dataset_version: str = "ALGO_DECISION_DATASET_V1"
    dataset_manifest_hash: str = "HASH_LGBM_DATASET_V1"
    feature_schema_version: str = "LIGHTGBM_FEATURE_SCHEMA_V1"
    target_policy_version: str = "LIGHTGBM_TARGET_POLICY_V1"
    split_policy_version: str = "LIGHTGBM_SPLIT_POLICY_V1"
    training_config_hash: str = "HASH_LGBM_CONFIG_V1"
    seed: int = 42
    best_iteration: int = 0
    training_range: Dict[str, str] = Field(default_factory=dict)
    validation_range: Dict[str, str] = Field(default_factory=dict)
    holdout_range: Dict[str, str] = Field(default_factory=dict)
    validation_metrics: Dict[str, Any] = Field(default_factory=dict)
    holdout_metrics: Dict[str, Any] = Field(default_factory=dict)
    baseline_metrics: Dict[str, Any] = Field(default_factory=dict)
    subgroup_metrics: Dict[str, Any] = Field(default_factory=dict)
    checkpoint_hash: str = "HASH_LGBM_MODEL_V001"
    status: LightGBMModelStatus = LightGBMModelStatus.EXPERIMENTAL
    decision_authority: str = "OFFLINE_RESEARCH_ONLY"
    created_at: str = ""
