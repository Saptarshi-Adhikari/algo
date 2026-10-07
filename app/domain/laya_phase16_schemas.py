"""Domain schemas and typed status models for Phase 16 Laya Shadow Validation (Research Integrity Corrected)."""
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class DataAvailabilityStatus(str, Enum):
    """Answers: Can the system currently obtain sufficiently fresh, valid market data?"""
    DATA_AVAILABLE = "DATA_AVAILABLE"
    DATA_STALE = "DATA_STALE"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    DATA_QUALITY_BLOCKED = "DATA_QUALITY_BLOCKED"
    DATA_PROVIDER_BLOCKED = "DATA_PROVIDER_BLOCKED"
    NO_ELIGIBLE_MARKETS = "NO_ELIGIBLE_MARKETS"

class CollectionStatus(str, Enum):
    """Answers: Is the shadow system successfully collecting and resolving fresh predictions?"""
    NOT_STARTED = "NOT_STARTED"
    WAITING_FOR_DATA = "WAITING_FOR_DATA"
    COLLECTING = "COLLECTING"
    PAUSED = "PAUSED"
    COLLECTION_ERROR = "COLLECTION_ERROR"
    COLLECTION_COMPLETE_FOR_WINDOW = "COLLECTION_COMPLETE_FOR_WINDOW"

class EvidenceStatus(str, Enum):
    """Answers: Is there enough resolved fresh evidence to support a performance conclusion?"""
    NO_EVIDENCE = "NO_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    LIMITED_EVIDENCE = "LIMITED_EVIDENCE"
    ADEQUATE_EVIDENCE = "ADEQUATE_EVIDENCE"
    STRONG_EVIDENCE = "STRONG_EVIDENCE"
    EVIDENCE_DEGRADED = "EVIDENCE_DEGRADED"

class CalibrationStatus(str, Enum):
    """Calibration status for shadow observations."""
    CALIBRATION_STABLE = "CALIBRATION_STABLE"
    CALIBRATION_DRIFT = "CALIBRATION_DRIFT"
    CALIBRATION_FAILED = "CALIBRATION_FAILED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class DriftStatus(str, Enum):
    """Drift status for monitoring dimensions."""
    STABLE = "STABLE"
    DRIFT = "DRIFT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class ModelHealthStatus(str, Enum):
    """Technical operational health of the Laya inference pipeline."""
    MODEL_OK = "MODEL_OK"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MODEL_INVALID_OUTPUT = "MODEL_INVALID_OUTPUT"
    MODEL_SCHEMA_ERROR = "MODEL_SCHEMA_ERROR"

class LatencyStats(BaseModel):
    """Detailed latency measurement statistics."""
    count: int = 0
    mean_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    max_ms: float = 0.0

class Phase15Cutoff(BaseModel):
    """Canonical cutoff timestamp record per symbol/scope."""
    canonical_symbol: str
    source_symbol: str
    asset_class: str
    timeframe: str
    max_training_timestamp: str = "2026-09-20T00:00:00Z"
    max_calibration_timestamp: str = "2026-09-20T00:00:00Z"
    max_validation_timestamp: str = "2026-09-20T00:00:00Z"
    max_holdout_timestamp: str = "2026-09-20T00:00:00Z"
    global_max_timestamp: str = "2026-09-20T00:00:00Z"

class DataAvailabilityReport(BaseModel):
    """Report from DataAvailabilityGate auditing fresh market data availability."""
    data_availability_status: DataAvailabilityStatus
    fresh_data_available: bool = False
    fresh_symbol_count: int = 0
    fresh_asset_class_count: int = 0
    fresh_record_count: int = 0
    fresh_decision_timestamp_count: int = 0
    total_available_records: int = 0
    historical_records: int = 0
    phase15_records: int = 0
    latest_timestamp_by_scope: Dict[str, str] = Field(default_factory=dict)
    phase15_cutoff_by_scope: Dict[str, str] = Field(default_factory=dict)
    stale_scopes: List[str] = Field(default_factory=list)
    quality_blocked_scopes: List[str] = Field(default_factory=list)
    provider_blocked_scopes: List[str] = Field(default_factory=list)

class FreshShadowPredictionRecord(BaseModel):
    """Record of a fresh-shadow prediction produced by ALGO_LAYA_V001."""
    prediction_id: str
    model_id: str = "ALGO_LAYA_V001"
    fresh_shadow: bool = True
    timestamp: str
    symbol: Optional[str] = "RELIANCE.NS"
    canonical_symbol: str = "RELIANCE.NS"
    source_symbol: str = "RELIANCE.NS"
    provider: str = "yfinance"
    asset_class: str
    timeframe: str
    dataset_id: str
    dataset_hash: str
    state_hash: str
    question_schema_version: str = "LAYA_QUESTION_SCHEMA_V2"
    predicted_direction: str = "HOLD"
    predicted_regime: str = "UNKNOWN"
    predicted_strategy_family: str = "NONE"
    predicted_trade_permission: str = "REJECT"
    predicted_risk: str = "HIGH"
    confidence: float = 0.0
    
    # Latency tracking separation
    model_inference_latency_ms: float = 0.0
    end_to_end_prediction_latency_ms: float = 0.0
    storage_latency_ms: float = 0.0
    authority: str = "SHADOW_ONLY"
    
    # Delayed outcome resolution fields
    resolved: bool = False
    ground_truth_direction: Optional[str] = None
    ground_truth_regime: Optional[str] = None
    direction_correct: Optional[bool] = None
    raw_return: Optional[float] = None
    net_return: Optional[float] = None
    cost_model_id: Optional[str] = "QUANT_AI_SLIPPAGE_SPREAD_V1"
    execution_model_id: Optional[str] = "REALISTIC_SIMULATED_EXEC_V1"
    outcome_timestamp: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.canonical_symbol and self.symbol:
            self.canonical_symbol = self.symbol
        if not self.source_symbol and self.symbol:
            self.source_symbol = self.symbol

class Phase16AssessmentResult(BaseModel):
    """Structured assessment combining independent status dimensions (Research Integrity Corrected)."""
    data_availability_status: DataAvailabilityStatus
    collection_status: CollectionStatus
    evidence_status: EvidenceStatus
    
    # Decoupled Baseline vs Fresh Calibration Status
    phase15_baseline_calibration: Dict[str, Any] = Field(default_factory=lambda: {
        "phase": 15,
        "temperature": 1.85,
        "raw_ece": 0.35,
        "calibrated_ece": 0.08,
        "raw_brier": 0.28,
        "calibrated_brier": 0.19
    })
    fresh_calibration_status: CalibrationStatus = CalibrationStatus.INSUFFICIENT_EVIDENCE
    fresh_calibrated_ece: Union[float, str] = "NOT_AVAILABLE"
    fresh_brier_score: Union[float, str] = "NOT_AVAILABLE"
    
    # Drift Status (Independent Sufficiency Rules)
    data_drift_status: DriftStatus = DriftStatus.INSUFFICIENT_EVIDENCE
    prediction_drift_status: DriftStatus = DriftStatus.INSUFFICIENT_EVIDENCE
    calibration_drift_status: DriftStatus = DriftStatus.INSUFFICIENT_EVIDENCE
    regime_drift_status: DriftStatus = DriftStatus.INSUFFICIENT_EVIDENCE
    
    model_health_status: ModelHealthStatus = ModelHealthStatus.MODEL_OK
    economic_shadow_status: str = "HYPOTHETICAL_ONLY"
    
    # Quantitative counts & records
    total_fresh_predictions: int = 0
    raw_resolved_predictions: int = 0
    effective_resolved_predictions: int = 0
    total_available_records: int = 0
    historical_records: int = 0
    phase15_records: int = 0
    fresh_records: int = 0
    fresh_decision_timestamps: int = 0
    
    # Economic Metric Sufficiency Rules (No manufactured numbers for tiny samples)
    trade_count: int = 0
    hypothetical_raw_return: float = 0.0
    hypothetical_net_return: float = 0.0
    sharpe_ratio: Union[float, str] = "NOT_AVAILABLE — insufficient sample"
    profit_factor: Union[float, str] = "NOT_AVAILABLE — insufficient sample"
    max_drawdown: Union[float, str] = "NOT_AVAILABLE — insufficient sample"
    
    # Latency Stats
    model_inference_latency: LatencyStats = Field(default_factory=LatencyStats)
    end_to_end_latency: LatencyStats = Field(default_factory=LatencyStats)
    
    model_id: str = "ALGO_LAYA_V001"
    authority: str = "SHADOW_ONLY"
