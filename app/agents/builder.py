"""Strategy Builder AI Agent converting hypotheses into deterministic rules."""
from typing import Optional
from app.llm.base import BaseLLMProvider
from app.llm.router import LLMRouter
from app.domain.schemas import HypothesisSpec, StrategySpec, MarketType
from app.config.logging import logger

SYSTEM_PROMPT = """You are a quantitative Strategy Builder Agent.
Your job is to take a qualitative research hypothesis and convert it into deterministic trading rules.
Supported indicators: SMA, EMA, RSI, MACD, BB, ATR.
Supported operators: ONLY '>', '<', '>=', '<=', '==', 'cross_above', 'cross_below'.
CRITICAL: Do NOT use 'above' or 'below'. Use 'cross_above' or 'cross_below' instead.
Output strict structured JSON matching StrategySpec."""

class StrategyBuilderAgent:
    """Converts structured hypotheses into executable strategy specs."""

    def __init__(self, llm: Optional[BaseLLMProvider] = None):
        self.llm = llm or LLMRouter()

    def build_strategy(
        self,
        hypothesis: HypothesisSpec,
        strategy_version: str = "v1",
        parent_version_id: Optional[str] = None,
        market: MarketType = "INDIAN_EQUITY",
        symbol: str = "RELIANCE.NS",
        timeframe: str = "1d"
    ) -> StrategySpec:
        prompt = (
            f"Hypothesis Title: {hypothesis.title}\n"
            f"Rationale: {hypothesis.rationale}\n"
            f"Differs From Failures: {hypothesis.differs_from_failures}\n\n"
            f"Target Market: {market}\n"
            f"Target Symbol: {symbol}\n"
            f"Timeframe: {timeframe}\n"
            f"Strategy Version: {strategy_version}\n"
            f"Parent Version ID: {parent_version_id or 'None'}\n\n"
            f"Convert this hypothesis into deterministic entry rules, exit rules, stop loss %, take profit %, and indicator parameters."
        )

        logger.info(f"StrategyBuilderAgent converting hypothesis {hypothesis.hypothesis_id} into strategy {strategy_version}...")
        spec = self.llm.generate_json(prompt, StrategySpec, system_prompt=SYSTEM_PROMPT)
        # Ensure strategy metadata matches caller specifications
        spec.hypothesis_id = hypothesis.hypothesis_id
        spec.version = strategy_version
        spec.parent_version_id = parent_version_id
        spec.market = market
        spec.symbol = symbol
        spec.timeframe = timeframe
        return spec
