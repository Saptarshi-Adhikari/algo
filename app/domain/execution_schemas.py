"""Canonical CostModel and ExecutionModel definitions for Phase 12 Execution Layer."""
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.domain.schemas import MarketType

SlippageType = Literal["FIXED_BPS", "PERCENTAGE"]
ExecutionMode = Literal["IDEALIZED", "BASELINE_REALISTIC", "STRESS"]
DelayMode = Literal["SAME_BAR_SIMULATION", "NEXT_BAR", "N_BAR_DELAY"]
LiquidityMode = Literal["UNLIMITED", "MAX_BAR_VOLUME_PCT", "DISABLED"]

class CostModel(BaseModel):
    """Versioned configuration model for transaction costs per asset class and broker/exchange profile."""
    cost_model_id: str = "COST_V1_BASELINE"
    effective_date: str = "2026-10-01"
    asset_class: MarketType = "INDIAN_EQUITY"
    broker_profile: str = "DEFAULT"

    # Friction parameters
    commission_bps: float = Field(default=3.0, ge=0.0, description="Commission in basis points (3 bps = 0.0003)")
    tax_levy_bps: float = Field(default=0.0, ge=0.0, description="Exchange fees, taxes, STT/levies in bps")
    minimum_charge: float = Field(default=0.0, ge=0.0, description="Minimum order charge")
    cost_model_version: str = "1.0.0"

class ExecutionModel(BaseModel):
    """Versioned execution model configuration specifying latency, spread, slippage, and liquidity."""
    execution_model_id: str = "EXEC_V1_BASELINE"
    execution_mode: ExecutionMode = "BASELINE_REALISTIC"
    delay_mode: DelayMode = "NEXT_BAR"
    latency_bars: int = Field(default=1, ge=0, description="Execution delay in bars (0 for SAME_BAR, 1 for NEXT_BAR)")

    # Slippage & Spread
    slippage_type: SlippageType = "FIXED_BPS"
    slippage_bps: float = Field(default=1.0, ge=0.0, description="Slippage in basis points (1 bps = 0.0001)")
    spread_proxy_bps: float = Field(default=2.0, ge=0.0, description="Bid/Ask spread proxy in bps for OHLCV data")

    # Liquidity
    liquidity_mode: LiquidityMode = "MAX_BAR_VOLUME_PCT"
    max_bar_volume_pct: float = Field(default=10.0, ge=0.0, le=100.0, description="Max allowed order size as % of bar volume")
    execution_model_version: str = "1.0.0"
