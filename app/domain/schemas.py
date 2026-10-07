"""Pydantic schemas and domain data contracts for the AI Quant Research System."""
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

MarketType = Literal["INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"]
DataMode = Literal["REAL", "HISTORICAL", "DELAYED", "SYNTHETIC", "REPLAY", "DEMO", "LIVE_PAPER"]
DataSplitName = Literal["DEVELOPMENT", "VALIDATION", "HOLDOUT"]
MarketRegimeType = Literal["TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY", "UNKNOWN"]
CriticVerdictType = Literal["REJECT", "RETEST", "KEEP_FOR_PAPER_TESTING"]
ExperimentStatus = Literal["RUNNING", "PASSED", "REJECTED", "FAILED", "ROLLED_BACK"]

class IndicatorSpec(BaseModel):
    name: str = Field(..., description="Indicator name e.g. SMA, EMA, RSI, MACD, BB, ATR")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters e.g. {'period': 14}")

class ConditionSpec(BaseModel):
    left: str = Field(..., description="Left field/indicator e.g. 'close', 'rsi_14', 'sma_20'")
    operator: Literal[">", "<", ">=", "<=", "==", "cross_above", "cross_below"] = Field(...)
    right: str = Field(..., description="Right field/indicator/numeric string e.g. 'sma_50', '70', '30'")

class StrategyRuleSet(BaseModel):
    entry_rules: List[ConditionSpec] = Field(default_factory=list)
    exit_rules: List[ConditionSpec] = Field(default_factory=list)
    stop_loss_pct: Optional[float] = Field(default=2.0, ge=0.0, description="Stop loss percentage e.g. 2.0 for 2%")
    take_profit_pct: Optional[float] = Field(default=4.0, ge=0.0, description="Take profit percentage e.g. 4.0 for 4%")
    position_sizing_pct: float = Field(default=10.0, gt=0.0, le=100.0, description="Capital allocation % per trade")

class StrategySpec(BaseModel):
    strategy_id: str = Field(..., description="Unique strategy identifier e.g. STRAT_V1_RSI_CROSS")
    version: str = Field(..., description="Version tag e.g. v1, v2")
    parent_version_id: Optional[str] = Field(default=None, description="Parent strategy version ID if derived")
    hypothesis_id: Optional[str] = Field(default=None, description="Associated hypothesis ID")
    market: MarketType = Field(default="INDIAN_EQUITY")
    symbol: str = Field(..., description="Ticker or currency pair e.g. RELIANCE.NS, EURUSD=X")
    timeframe: str = Field(default="1d", description="Bar timeframe e.g. 1d, 1h")
    indicators: List[IndicatorSpec] = Field(default_factory=list)
    rules: StrategyRuleSet
    description: str = Field(default="")

class TradeRecord(BaseModel):
    trade_id: str
    symbol: str
    side: Literal["LONG", "SHORT"]
    entry_time: str
    exit_time: Optional[str] = None
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    fees: float = 0.0
    slippage: float = 0.0
    pnl: float = 0.0
    return_pct: float = 0.0
    exit_reason: Optional[str] = None

class BacktestMetrics(BaseModel):
    total_return_pct: float
    annualized_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate: float
    trade_count: int
    average_win: float
    average_loss: float
    profit_factor: float
    data_split: DataSplitName
    sortino_ratio: Optional[float] = 0.0
    calmar_ratio: Optional[float] = 0.0
    expectancy_per_trade: Optional[float] = 0.0
    sample_size_warning: Optional[str] = "ADEQUATE_SAMPLE"

class CriticEvaluation(BaseModel):
    verdict: CriticVerdictType
    reasoning: str
    is_overfitted: bool = False
    has_lookahead_bias: bool = False
    has_adequate_trades: bool = True
    parameter_sensitivity_warning: bool = False
    regime_dependence_warning: bool = False

class HypothesisSpec(BaseModel):
    hypothesis_id: str
    title: str
    rationale: str
    cited_experiment_ids: List[str] = Field(default_factory=list)
    differs_from_failures: str

class ExperimentRecord(BaseModel):
    experiment_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    hypothesis: str
    strategy_version: str
    parent_experiment_id: Optional[str] = None
    market: MarketType
    symbol: str
    timeframe: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    data_period: str
    data_split: DataSplitName
    metrics: BacktestMetrics
    fees_assumed: float
    slippage_assumed: float
    critic_verdict: CriticVerdictType
    critic_reasoning: str
    failure_reason: Optional[str] = None
    market_regime: MarketRegimeType = "UNKNOWN"
    lesson_learned: str
    status: ExperimentStatus
    code_version: str = "0.1.0"

class PortfolioPosition(BaseModel):
    position_id: str
    symbol: str
    side: Literal["LONG", "SHORT"]
    entry_price: float
    current_price: float
    quantity: float
    unrealized_pnl: float
    entry_time: str

class PortfolioState(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    virtual_cash: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_equity: float
    max_equity: float
    drawdown_pct: float = 0.0
    open_positions: List[PortfolioPosition] = Field(default_factory=list)
    closed_trades: List[TradeRecord] = Field(default_factory=list)
