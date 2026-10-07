"""Dataset Quality and Look-Ahead Data Leakage Audit Engine."""
from typing import List, Dict, Any
from app.domain.decision_schemas import DecisionRecord

class DatasetLeakageAuditor:
    """Rigorously audits decision records for future data leakage and record duplicates."""

    @staticmethod
    def audit_records(records: List[DecisionRecord]) -> Dict[str, Any]:
        leakage_count = 0
        duplicate_count = 0
        invalid_label_count = 0
        missing_field_count = 0

        seen_ids = set()
        seen_state_ts = set()

        for rec in records:
            # 1. Duplicate ID Check
            if rec.decision_id in seen_ids:
                duplicate_count += 1
            seen_ids.add(rec.decision_id)

            # 2. Duplicate timestamp check per symbol
            key = (rec.symbol, rec.timestamp, rec.ground_truth.evaluation_horizon_bars)
            if key in seen_state_ts:
                duplicate_count += 1
            seen_state_ts.add(key)

            # 3. Future Data Leakage Check
            # State timestamp T must strictly precede future observation end timestamp
            if rec.state.timestamp >= rec.ground_truth.future_observation_end_timestamp:
                leakage_count += 1

            # Check if any ground truth fields leaked into state custom_features
            if "realized_return" in str(rec.state.custom_features) or "direction_outcome" in str(rec.state.custom_features):
                leakage_count += 1

            # 4. Missing field check
            if not rec.symbol or not rec.timestamp or not rec.dataset_id or not rec.dataset_hash:
                missing_field_count += 1

            # 5. Invalid outcome check
            gt = rec.ground_truth
            if gt.direction_outcome not in ("BUY", "SELL", "HOLD"):
                invalid_label_count += 1

        total = len(records)
        is_clean = (leakage_count == 0) and (duplicate_count == 0) and (invalid_label_count == 0) and (missing_field_count == 0)

        return {
            "total_records": total,
            "future_leakage_count": leakage_count,
            "duplicate_record_count": duplicate_count,
            "invalid_label_count": invalid_label_count,
            "missing_field_count": missing_field_count,
            "audit_passed": is_clean
        }
