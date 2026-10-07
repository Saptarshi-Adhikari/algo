"""Benchmark Evaluation Engine for Decision Datasets."""
from typing import List, Dict, Any
from app.domain.decision_schemas import DecisionRecord

class BenchmarkEvaluator:
    """Evaluates classification accuracy and decision metrics over a set of DecisionRecords."""

    @staticmethod
    def evaluate_decisions(records: List[DecisionRecord]) -> Dict[str, Any]:
        if not records:
            return {
                "total_evaluations": 0,
                "accuracy": 0.0,
                "buy_precision": 0.0,
                "sell_precision": 0.0,
                "hold_precision": 0.0,
                "class_counts": {"BUY": 0, "SELL": 0, "HOLD": 0}
            }

        correct_predictions = 0
        class_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}

        for rec in records:
            gt = rec.ground_truth.direction_outcome
            class_counts[gt] = class_counts.get(gt, 0) + 1

            # Extract predicted direction from questions if present
            pred = None
            for q in rec.questions:
                if q.question_id == "q_direction":
                    pred = q.predicted_value
                    break

            if pred and pred == gt:
                correct_predictions += 1

        acc = (correct_predictions / len(records)) if records else 0.0

        return {
            "total_evaluations": len(records),
            "accuracy": round(acc, 4),
            "class_counts": class_counts,
            "split_counts": {
                "DEVELOPMENT": sum(1 for r in records if r.data_split == "DEVELOPMENT"),
                "VALIDATION": sum(1 for r in records if r.data_split == "VALIDATION"),
                "HOLDOUT": sum(1 for r in records if r.data_split == "HOLDOUT")
            }
        }
