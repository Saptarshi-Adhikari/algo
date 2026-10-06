"""Bounded Autonomous AI Experiment Loop Runner."""
from typing import List, Optional, Dict, Any
from app.data.base_provider import BaseDataProvider, MarketData
from app.data.splitter import DataSplitter
from app.data.indian_provider import IndianMarketDataProvider
from app.data.forex_provider import ForexDataProvider
from app.data.replay_provider import ReplayDataProvider
from app.evaluation.regime import RegimeClassifier
from app.backtesting.engine import Backtester
from app.agents.researcher import ResearcherAgent
from app.agents.builder import StrategyBuilderAgent
from app.agents.critic import CriticAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.next_experiment import NextExperimentAgent
from app.memory.repository import ExperimentRepository
from app.domain.schemas import ExperimentRecord, MarketType
from app.config.settings import settings
from app.config.logging import logger

class ExperimentRunner:
    """Orchestrates bounded quantitative AI research loops."""

    def __init__(
        self,
        repository: Optional[ExperimentRepository] = None,
        data_provider: Optional[BaseDataProvider] = None
    ):
        self.repository = repository or ExperimentRepository()
        self.data_provider = data_provider or IndianMarketDataProvider()
        self.researcher = ResearcherAgent(repository=self.repository)
        self.builder = StrategyBuilderAgent()
        self.critic = CriticAgent()
        self.memory_agent = MemoryAgent(repository=self.repository)
        self.next_exp_agent = NextExperimentAgent()
        self.backtester = Backtester()
        self.splitter = DataSplitter()

    def run_experiments(
        self,
        symbol: str = "RELIANCE.NS",
        market: MarketType = "INDIAN_EQUITY",
        timeframe: str = "1d",
        max_experiments: int = 5,
        allow_holdout: bool = False
    ) -> List[ExperimentRecord]:
        """Execute bounded research loop up to max_experiments."""
        bounded_max = min(max_experiments, settings.DEFAULT_MAX_EXPERIMENTS)
        logger.info(f"Starting Bounded Experiment Loop for {symbol} ({market}) - Max Iterations: {bounded_max}")

        # 1. Fetch market data & split chronologically
        raw_data = self.data_provider.fetch_ohlcv(symbol=symbol, timeframe=timeframe)
        splits = self.splitter.split(raw_data)
        dev_data = splits["DEVELOPMENT"]
        val_data = splits["VALIDATION"]

        # 2. Detect regime
        regime = RegimeClassifier.classify_dataset(dev_data)
        logger.info(f"Detected Market Regime for {symbol}: {regime}")

        executed_records: List[ExperimentRecord] = []
        current_version_num = 1
        parent_version_id: Optional[str] = None

        for i in range(1, bounded_max + 1):
            exp_id = f"EXP_{symbol}_{i:03d}"
            version_str = f"v{current_version_num}"
            logger.info(f"--- STARTING EXPERIMENT ITERATION {i}/{bounded_max} ({exp_id}) ---")

            # A. Researcher proposes hypothesis
            hypothesis = self.researcher.propose_hypothesis(symbol=symbol, regime=regime)

            # B. Strategy Builder converts to rules
            spec = self.builder.build_strategy(
                hypothesis=hypothesis,
                strategy_version=version_str,
                parent_version_id=parent_version_id,
                market=market,
                symbol=symbol,
                timeframe=timeframe
            )

            # C. Backtest on DEVELOPMENT split
            dev_metrics, dev_trades, _ = self.backtester.run(dev_data, spec, data_split="DEVELOPMENT")

            # D. Backtest on VALIDATION split
            val_metrics, val_trades, _ = self.backtester.run(val_data, spec, data_split="VALIDATION")

            # E. Critic evaluates backtest evidence (Primary valuation on validation set)
            eval_metrics = val_metrics if val_metrics.trade_count >= 5 else dev_metrics
            critic_eval = self.critic.evaluate(eval_metrics, spec, regime=regime)

            # F. Memory Agent persists experiment record
            record = self.memory_agent.record_experiment(
                experiment_id=exp_id,
                hypothesis=hypothesis,
                spec=spec,
                metrics=eval_metrics,
                evaluation=critic_eval,
                regime=regime,
                parent_experiment_id=parent_version_id
            )
            executed_records.append(record)

            # G. Next-Experiment Agent decides next step
            next_action, reason = self.next_exp_agent.decide_next_step(critic_eval.verdict, spec)
            logger.info(f"Iteration {i} complete. Next Action: {next_action}")

            if next_action == "NEW_HYPOTHESIS":
                parent_version_id = spec.version
                current_version_num += 1
            elif next_action == "RETEST_VARIATION":
                current_version_num += 1
            elif next_action == "ROLLBACK_PARENT":
                # Maintain parent_version_id, do not advance parent
                current_version_num += 1

        logger.info(f"Completed {len(executed_records)} experiments for {symbol}.")
        return executed_records
