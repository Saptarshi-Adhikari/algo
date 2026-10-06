"""Mock / Rule-Based Fallback LLM Provider for offline testing and fallback."""
from typing import Optional, Type, TypeVar
import json
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.domain.schemas import (
    HypothesisSpec, StrategySpec, StrategyRuleSet, ConditionSpec,
    IndicatorSpec, CriticEvaluation
)

T = TypeVar("T", bound=BaseModel)

class MockLLMProvider(BaseLLMProvider):
    """Deterministic offline fallback provider returning mock strategy specs and hypotheses."""

    def __init__(self, mode: str = "PASSING"):
        self.mode = mode  # PASSING, CRITIC_REJECT, etc.

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Mock response generated for prompt: " + prompt[:50]

    def generate_json(self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None) -> T:
        name = schema_cls.__name__

        if name == "HypothesisSpec":
            obj = HypothesisSpec(
                hypothesis_id="HYP_MOCK_001",
                title="RSI Oversold Mean Reversion with Trend Filter",
                rationale="In mean-reverting or moderately trending markets, entering when RSI is below 30 produces high win rate entries.",
                cited_experiment_ids=[],
                differs_from_failures="Includes strict stop loss and trend filter to prevent buying falling knives."
            )
            return obj

        elif name == "StrategySpec":
            obj = StrategySpec(
                strategy_id="STRAT_MOCK_V1",
                version="v1",
                market="INDIAN_EQUITY",
                symbol="RELIANCE.NS",
                timeframe="1d",
                indicators=[
                    IndicatorSpec(name="RSI", params={"period": 14}),
                    IndicatorSpec(name="SMA", params={"period": 50})
                ],
                rules=StrategyRuleSet(
                    entry_rules=[
                        ConditionSpec(left="rsi_14", operator="<", right="35"),
                        ConditionSpec(left="close", operator=">", right="sma_50")
                    ],
                    exit_rules=[
                        ConditionSpec(left="rsi_14", operator=">", right="65")
                    ],
                    stop_loss_pct=2.0,
                    take_profit_pct=5.0,
                    position_sizing_pct=15.0
                ),
                description="RSI Oversold Mean Reversion above 50-day SMA"
            )
            return obj

        elif name == "CriticEvaluation":
            if self.mode == "CRITIC_REJECT":
                obj = CriticEvaluation(
                    verdict="REJECT",
                    reasoning="Strategy exhibits low trade count (<5 trades) and parameter sensitivity.",
                    is_overfitted=True,
                    has_adequate_trades=False
                )
            else:
                obj = CriticEvaluation(
                    verdict="KEEP_FOR_PAPER_TESTING",
                    reasoning="Backtest demonstrates robust metrics with adequate trade count and clear risk bounds.",
                    is_overfitted=False,
                    has_adequate_trades=True
                )
            return obj

        # Default schema instantiation fallback
        try:
            return schema_cls.model_construct()
        except Exception:
            raise ValueError(f"MockLLMProvider does not support schema {name}")
