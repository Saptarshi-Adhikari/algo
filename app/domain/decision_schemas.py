"""Domain schemas for Phase 11 Decision Dataset & Benchmark Foundation."""
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from app.domain.schemas import MarketType, MarketRegimeType, DataSplitName

QuestionType = Literal["choice", "score", "noul"]
DirectionChoice = Literal["BUY", "SELL", "HOLD"]
StrategyFamilyChoice = Literal["TREND", "MOMENTUM", "MEAN_REVERSION", "BREAKOUT", "PRICE_ACTION", "CANDLESTICK", "VOLATILITY", "NONE"]
TradePermissionChoice = Literal["ALLOW", "REJECT"]
RiskChoice = Literal["LOW", "MEDIUM", "HIGH"]

class MarketState(BaseModel):
    """Causal snapshot of market state at decision timestamp T."""
    symbol: str
    market: MarketType
    timeframe: str = "1d"
    timestamp: str
    dataset_id: str
    dataset_hash: str

    # Causal OHLCV at T
    open: float
    high: float
    low: float
    close: float
    volume: float

    # Causal Indicators at T (Explicitly Optional)
    sma_10: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_10: Optional[float] = None
    ema_20: Optional[float] = None
    rsi_14: Optional[float] = None
    macd_line: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    atr_14: Optional[float] = None

    # Causal Market Context
    regime: MarketRegimeType = "UNKNOWN"
    volatility_atr_pct: Optional[float] = None
    trend_direction: Optional[Literal["UP", "DOWN", "SIDEWAYS"]] = "SIDEWAYS"
    custom_features: Dict[str, Any] = Field(default_factory=dict)
    state_version: str = "1.0.0"

class DecisionQuestion(BaseModel):
    """Typed decision question compatible with future Laya training schema."""
    question_id: str
    title: str
    question_type: QuestionType
    choices: Optional[List[str]] = None
    predicted_value: Optional[str] = None
    confidence: Optional[float] = None

class GroundTruthOutcome(BaseModel):
    """Ground truth label derived strictly from future observation windows after T."""
    decision_timestamp: str
    evaluation_horizon_bars: int = 4
    future_observation_end_timestamp: str
    
    # Ground truth directional decision
    direction_outcome: DirectionChoice
    trade_permission_outcome: TradePermissionChoice = "ALLOW"
    risk_outcome: RiskChoice = "LOW"
    
    # Numeric realization metrics
    realized_return_pct: float
    max_favorable_excursion_pct: float
    max_adverse_excursion_pct: float
    target_hit: bool = False
    stop_hit: bool = False
    label_policy_version: str = "1.0.0"

class DecisionRecord(BaseModel):
    """Durable decision record representing state, question set, ground truth label, and outcome."""
    decision_id: str
    timestamp: str
    symbol: str
    market: MarketType
    timeframe: str = "1d"
    dataset_id: str
    dataset_hash: str
    data_split: DataSplitName = "DEVELOPMENT"

    state_version: str = "1.0.0"
    feature_schema_version: str = "1.0.0"
    state: MarketState
    questions: List[DecisionQuestion] = Field(default_factory=list)
    ground_truth: GroundTruthOutcome

    model_name: Optional[str] = "deterministic_rule_base"
    model_version: Optional[str] = "0.1.0"
    strategy_id: Optional[str] = None
    experiment_id: Optional[str] = None
