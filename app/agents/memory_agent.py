"""Memory Agent formatting and persisting complete experiment logs."""
from typing import Optional
from datetime import datetime
from app.domain.schemas import (
    ExperimentRecord, BacktestMetrics, CriticEvaluation, StrategySpec,
    HypothesisSpec, MarketRegimeType
)
from app.memory.repository import ExperimentRepository
from app.config.logging import logger

class MemoryAgent:
    """Persists complete, unedited experiment records into SQLite memory."""

    def __init__(self, repository: Optional[ExperimentRepository] = None):
        self.repository = repository or ExperimentRepository()

    def record_experiment(
        self,
        experiment_id: str,
        hypothesis: HypothesisSpec,
        spec: StrategySpec,
        metrics: BacktestMetrics,
        evaluation: CriticEvaluation,
        regime: MarketRegimeType = "UNKNOWN",
        fees_assumed: float = 0.0003,
        slippage_assumed: float = 0.0001,
        parent_experiment_id: Optional[str] = None
    ) -> ExperimentRecord:
        lesson = (
            f"Verdict: {evaluation.verdict}. "
            f"Sharpe {metrics.sharpe_ratio:.2f}, Return {metrics.total_return_pct:.2f}%, {metrics.trade_count} trades. "
            f"{evaluation.reasoning}"
        )

        status = "PASSED" if evaluation.verdict == "KEEP_FOR_PAPER_TESTING" else "REJECTED"

        record = ExperimentRecord(
            experiment_id=experiment_id,
            timestamp=datetime.utcnow().isoformat(),
            hypothesis=hypothesis.title,
            strategy_version=spec.version,
            parent_experiment_id=parent_experiment_id,
            market=spec.market,
            symbol=spec.symbol,
            timeframe=spec.timeframe,
            parameters={
                "indicators": [i.model_dump() for i in spec.indicators],
                "stop_loss_pct": spec.rules.stop_loss_pct,
                "take_profit_pct": spec.rules.take_profit_pct,
                "position_sizing_pct": spec.rules.position_sizing_pct
            },
            data_period=f"Split: {metrics.data_split}",
            data_split=metrics.data_split,
            metrics=metrics,
            fees_assumed=fees_assumed,
            slippage_assumed=slippage_assumed,
            critic_verdict=evaluation.verdict,
            critic_reasoning=evaluation.reasoning,
            failure_reason=evaluation.reasoning if evaluation.verdict == "REJECT" else None,
            market_regime=regime,
            lesson_learned=lesson,
            status=status
        )

        self.repository.insert_experiment(record)
        logger.info(f"MemoryAgent persisted experiment {experiment_id} (Verdict: {evaluation.verdict})")
        return record
