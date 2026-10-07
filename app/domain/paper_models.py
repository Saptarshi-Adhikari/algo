"""Paper Order and Session Schema definitions."""
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from app.domain.schemas import TradeRecord, PortfolioState

class PaperOrder(BaseModel):
    """Simulated Paper Order container (Non-broker execution model)."""
    order_id: str
    experiment_id: str
    strategy_version: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    symbol: str
    side: Literal["PAPER BUY", "PAPER SELL"]
    requested_price: float
    simulated_fill_price: float
    quantity: float
    fees: float = 0.0
    slippage: float = 0.0
    reason: str = "STRATEGY_SIGNAL"

class PaperTradingSession(BaseModel):
    """Persisted Paper Trading Session State."""
    session_id: str
    strategy_version: str
    experiment_id: str
    symbol: str
    data_source: str
    starting_cash: float = 100000.0
    current_equity: float
    open_positions_count: int
    closed_trades_count: int
    session_start: str
    session_end: Optional[str] = None
    assumptions: Dict[str, Any] = Field(default_factory=dict)
    performance_summary: Dict[str, Any] = Field(default_factory=dict)
