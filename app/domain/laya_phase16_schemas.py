"""Domain schemas and typed status models for Phase 16 Laya Shadow Validation."""
from enum import Enum
from typing import List, Dict, Any, Optional
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
    """Calibration status for rolling shadow observations."""
    CALIBRATION_STABLE = "CALIBRATION_STABLE"
    CALIBRATION_DRIFT = "CALIBRATION_DRIFT"
    CALIBRATION_FAILED = "CALIBRATION_FAILED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class ModelHealthStatus(str, Enum):
    """Technical operational health of the Laya inference pipeline."""
    MODEL_OK = "MODEL_OK"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MODEL_INVALID_OUTPUT = "MODEL_INVALID_OUTPUT"
    MODEL_SCHEMA_ERROR = "MODEL_SCHEMA_ERROR"

class DataAvailabilityReport(BaseModel):
    """Report from DataAvailabilityGate auditing fresh market data availability."""
    status: DataAvailabilityStatus
    fresh_symbols: List[str] = Field(default_factory=list)
    fresh_asset_classes: List[str] = Field(default_factory=list)
    fresh_bar_count: int = 0
    latest_timestamp_by_symbol: Dict[str, str] = Field(default_factory=dict)
    stale_symbols: List[str] = Field(default_factory=list)
    unavailable_symbols: List[str] = Field(default_factory=list)
    quality_failures: List[str] = Field(default_factory=list)
    phase15_cutoff_by_symbol: Dict[str, str] = Field(default_factory=dict)

class FreshShadowPredictionRecord(BaseModel):
    """Record of a fresh-shadow prediction produced by ALGO_LAYA_V001."""
    prediction_id: str
    model_id: str = "ALGO_LAYA_V001"
    fresh_shadow: bool = True
    timestamp: str
    symbol: str
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
    latency_ms: float = 0.0
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

class Phase16AssessmentResult(BaseModel):
    """Structured assessment combining independent status dimensions."""
    data_availability_status: DataAvailabilityStatus
    collection_status: CollectionStatus
    evidence_status: EvidenceStatus
    calibration_status: CalibrationStatus
    drift_status: str = "NO_CRITICAL_DRIFT"
    model_health_status: ModelHealthStatus = ModelHealthStatus.MODEL_OK
    economic_shadow_status: str = "HYPOTHETICAL_ONLY"
    
    # Quantitative metrics
    total_fresh_predictions: int = 0
    raw_resolved_predictions: int = 0
    effective_resolved_predictions: int = 0
    direction_accuracy: float = 0.0
    brier_score: float = 0.0
    ece: float = 0.0
    hypothetical_net_return: float = 0.0
    hypothetical_sharpe: float = 0.0
    
    model_id: str = "ALGO_LAYA_V001"
    authority: str = "SHADOW_ONLY"
