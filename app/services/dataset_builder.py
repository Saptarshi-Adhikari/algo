"""Historical Decision Dataset Backfill Builder."""
from typing import List, Optional, Dict
import pandas as pd
from app.data.base_provider import MarketData
from app.data.registry import ResearchDatasetRegistry
from app.domain.decision_schemas import DecisionRecord, DecisionQuestion, DataSplitName
from app.services.state_builder import StateSnapshotBuilder
from app.services.label_generator import GroundTruthLabelGenerator
from app.memory.decision_repository import DecisionRepository
from app.config.logging import logger

class HistoricalDatasetBuilder:
    """Chronologically processes historical MarketData to build and persist DecisionRecords."""

    def __init__(self, repo: Optional[DecisionRepository] = None):
        self.repo = repo or DecisionRepository()

    def build_dataset_for_market_data(
        self,
        data: MarketData,
        horizon_bars: int = 4,
        step_stride: int = 1,
        dev_ratio: float = 0.7,
        val_ratio: float = 0.15
    ) -> List[DecisionRecord]:
        total_bars = len(data)
        if total_bars <= horizon_bars + 15:
            logger.warning(f"MarketData for {data.symbol} has too few bars ({total_bars}) for horizon {horizon_bars}.")
            return []

        # Register dataset metadata canonically
        entry = ResearchDatasetRegistry.register(data, provider_name="HistoricalBuilder", quality_status="PASS")

        # Chronological Train / Validation / Holdout thresholds
        dev_idx = int(total_bars * dev_ratio)
        val_idx = int(total_bars * (dev_ratio + val_ratio))

        records: List[DecisionRecord] = []

        # Start loop after minimum 15 bars to ensure indicator availability
        for i in range(15, total_bars - horizon_bars, step_stride):
            # Chronological split assignment
            if i < dev_idx:
                split_name: DataSplitName = "DEVELOPMENT"
            elif i < val_idx:
                split_name: DataSplitName = "VALIDATION"
            else:
                split_name: DataSplitName = "HOLDOUT"

            # 1. Build Causal Market State at T
            state = StateSnapshotBuilder.build_snapshot(
                data=data,
                bar_index=i,
                dataset_id=entry.dataset_id,
                regime="UNKNOWN"
            )

            # 2. Build Ground Truth Outcome from future bars (T+1 to T+H)
            outcome = GroundTruthLabelGenerator.generate_label(
                data=data,
                bar_index=i,
                horizon_bars=horizon_bars
            )

            if not outcome:
                continue

            # 3. Standard Typed Decision Questions
            questions = [
                DecisionQuestion(
                    question_id="q_market_regime",
                    title="What is the current market regime?",
                    question_type="choice",
                    choices=["TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY", "UNKNOWN"],
                    predicted_value=state.regime
                ),
                DecisionQuestion(
                    question_id="q_direction",
                    title="What is the optimal directional stance for the next horizon?",
                    question_type="choice",
                    choices=["BUY", "SELL", "HOLD"],
                    predicted_value=outcome.direction_outcome
                ),
                DecisionQuestion(
                    question_id="q_trade_permission",
                    title="Should a trade be permitted based on risk?",
                    question_type="choice",
                    choices=["ALLOW", "REJECT"],
                    predicted_value=outcome.trade_permission_outcome
                )
            ]

            dec_id = f"DEC_{data.symbol}_{state.timestamp.replace(':', '-').replace(' ', 'T')}_{i}"

            rec = DecisionRecord(
                decision_id=dec_id,
                timestamp=state.timestamp,
                symbol=data.symbol,
                market=data.market,
                timeframe=data.timeframe,
                dataset_id=entry.dataset_id,
                dataset_hash=entry.dataset_hash,
                data_split=split_name,
                state=state,
                questions=questions,
                ground_truth=outcome
            )

            self.repo.save(rec)
            records.append(rec)

        logger.info(f"Built and persisted {len(records)} DecisionRecords for {data.symbol} ({data.market}).")
        return records
