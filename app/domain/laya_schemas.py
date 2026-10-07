"""Domain schemas for Laya decision contract (Phase 13)."""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from app.domain.decision_schemas import (
    MarketState, DirectionChoice, StrategyFamilyChoice, TradePermissionChoice, RiskChoice
)

class LayaPredictionResult(BaseModel):
    """ALGO-owned representation of Laya shadow inference prediction."""
    decision_id: str
    timestamp: str
    symbol: str
    market: str
    timeframe: str
    dataset_id: str
    dataset_hash: str
    state_hash: str

    # Typed predictions matching ALGO Laya Contract
    predicted_regime: Optional[str] = "UNKNOWN"
    predicted_direction: Optional[DirectionChoice] = "HOLD"
    predicted_strategy_family: Optional[StrategyFamilyChoice] = "NONE"
    predicted_trade_permission: Optional[TradePermissionChoice] = "REJECT"
    predicted_risk: Optional[RiskChoice] = "HIGH"
    predicted_signal_strength: Optional[float] = 0.0

    raw_predictions: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None
    confidence_status: Literal["UNCALIBRATED"] = "UNCALIBRATED"
    decision_authority: Literal["SHADOW_ONLY"] = "SHADOW_ONLY"

    model_name: str = "convaiinnovations/laya"
    model_version: str = "0.3.5"
    latency_ms: float = 0.0
    status: Literal["SUCCESS", "MODEL_UNAVAILABLE", "MODEL_ERROR", "MODEL_TIMEOUT", "INVALID_OUTPUT"] = "SUCCESS"
    error_message: Optional[str] = None
    contract_version: str = "LAYA_DECISION_SCHEMA_V1"
