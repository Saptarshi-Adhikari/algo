"""Laya-Compatible Structured Dataset Exporter."""
import json
from typing import List, Dict, Any
from app.domain.decision_schemas import DecisionRecord

class LayaDatasetExporter:
    """Exports ALGO DecisionRecords into Laya-compatible structured training cases (state, questions, gold)."""

    @staticmethod
    def export_record_to_laya_case(rec: DecisionRecord) -> Dict[str, Any]:
        """Maps a single ALGO DecisionRecord into a typed Laya case format."""
        # Convert state into structured JSON string/dict for state prompt input
        state_dict = rec.state.model_dump(exclude_none=True)

        laya_questions = []
        for q in rec.questions:
            laya_questions.append({
                "id": q.question_id,
                "type": q.question_type,
                "title": q.title,
                "choices": q.choices
            })

        gold_targets = {
            "q_market_regime": rec.state.regime,
            "q_direction": rec.ground_truth.direction_outcome,
            "q_trade_permission": rec.ground_truth.trade_permission_outcome,
            "realized_return_pct": rec.ground_truth.realized_return_pct
        }

        return {
            "case_id": rec.decision_id,
            "metadata": {
                "dataset_version": "1.0.0",
                "algo_schema_version": rec.state_version,
                "label_policy_version": rec.ground_truth.label_policy_version,
                "source_dataset_id": rec.dataset_id,
                "source_dataset_hash": rec.dataset_hash,
                "symbol": rec.symbol,
                "market": rec.market,
                "timeframe": rec.timeframe,
                "timestamp": rec.timestamp,
                "split": rec.data_split
            },
            "state": state_dict,
            "questions": laya_questions,
            "gold": gold_targets
        }

    @classmethod
    def export_dataset_jsonl(cls, records: List[DecisionRecord]) -> str:
        """Exports a list of records into a JSONL string compatible with Laya dataset ingest."""
        lines = []
        for r in records:
            case = cls.export_record_to_laya_case(r)
            lines.append(json.dumps(case))
        return "\n".join(lines)
