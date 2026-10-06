"""Critic AI Agent evaluating strategy backtest evidence for overfitting and bias."""
from typing import Optional
from app.llm.base import BaseLLMProvider
from app.llm.router import LLMRouter
from app.domain.schemas import BacktestMetrics, CriticEvaluation, StrategySpec, CriticVerdictType
from app.config.logging import logger

SYSTEM_PROMPT = """You are a skeptical, adversarial quantitative Risk & Overfitting Critic Agent.
Your job is to rigorously critique backtest evidence and attempt to DISPROVE the strategy.
Check for:
1. Low trade count (< 10 trades)
2. Excessive drawdown (> 20%)
3. Negative or poor Sharpe ratio (< 0.5)
4. Parameter over-tuning or look-ahead bias
5. Regime fragility

Possible Verdicts:
- REJECT: Unacceptable risk, low trade count, severe drawdown, or negative Sharpe.
- RETEST: Mixed results needing parameter adjustment or testing on Validation set.
- KEEP_FOR_PAPER_TESTING: Robust metrics, adequate trade count (>= 10), healthy Sharpe ratio (> 1.0), and controlled drawdown."""

class CriticAgent:
    """Evaluates backtest metrics and decides REJECT, RETEST, or KEEP_FOR_PAPER_TESTING."""

    def __init__(self, llm: Optional[BaseLLMProvider] = None):
        self.llm = llm or LLMRouter()

    def evaluate(
        self,
        metrics: BacktestMetrics,
        spec: StrategySpec,
        regime: str = "UNKNOWN"
    ) -> CriticEvaluation:
        # Rule-based hard checks first for deterministic safety
        if metrics.trade_count < 5:
            logger.info("Critic hard-rule triggered: Trade count < 5 -> REJECT")
            return CriticEvaluation(
                verdict="REJECT",
                reasoning=f"Sample size too small ({metrics.trade_count} trades). Minimum 5 trades required for statistical validity.",
                is_overfitted=True,
                has_adequate_trades=False
            )

        if metrics.sharpe_ratio < 0.2 or metrics.max_drawdown_pct < -25.0:
            logger.info(f"Critic hard-rule triggered: Sharpe ({metrics.sharpe_ratio:.2f}) or Drawdown ({metrics.max_drawdown_pct:.2f}%) poor -> REJECT")
            return CriticEvaluation(
                verdict="REJECT",
                reasoning=f"Poor risk-adjusted return (Sharpe: {metrics.sharpe_ratio:.2f}, Max DD: {metrics.max_drawdown_pct:.2f}%).",
                is_overfitted=False,
                has_adequate_trades=metrics.trade_count >= 10
            )

        # Use LLM for nuanced synthesis if initial criteria passed
        prompt = (
            f"Strategy ID: {spec.strategy_id} ({spec.symbol} {spec.timeframe})\n"
            f"Market Regime: {regime}\n"
            f"Data Split: {metrics.data_split}\n\n"
            f"=== METRICS ===\n"
            f"Trade Count: {metrics.trade_count}\n"
            f"Total Return: {metrics.total_return_pct:.2f}%\n"
            f"Annualized Return: {metrics.annualized_return_pct:.2f}%\n"
            f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}\n"
            f"Max Drawdown: {metrics.max_drawdown_pct:.2f}%\n"
            f"Win Rate: {metrics.win_rate*100:.1f}%\n"
            f"Profit Factor: {metrics.profit_factor:.2f}\n\n"
            f"Critique this strategy and issue a final verdict (REJECT, RETEST, or KEEP_FOR_PAPER_TESTING)."
        )

        logger.info(f"CriticAgent evaluating backtest metrics for {spec.strategy_id}...")
        evaluation = self.llm.generate_json(prompt, CriticEvaluation, system_prompt=SYSTEM_PROMPT)
        return evaluation
