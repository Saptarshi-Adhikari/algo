"""Evaluates zero-shot Laya shadow inference accuracy against Phase 11 Ground Truth datasets."""
from typing import List, Dict, Any, Optional
from app.domain.decision_schemas import DecisionRecord
from app.decision.laya_adapter import LayaAdapter
from app.memory.laya_repository import LayaPredictionRepository

class LayaBenchmarkEvaluator:
    """Evaluates Laya zero-shot predictions against ground truth without authority."""

    def __init__(self, adapter: Optional[LayaAdapter] = None, repo: Optional[LayaPredictionRepository] = None):
        self.adapter = adapter or LayaAdapter()
        self.repo = repo or LayaPredictionRepository()

    def run_zero_shot_benchmark(self, records: List[DecisionRecord]) -> Dict[str, Any]:
        if not records:
            return {"total_evaluations": 0, "accuracy": 0.0, "status": "NO_RECORDS"}

        correct_direction = 0
        correct_regime = 0
        total_evals = 0
        model_errors = 0
        latencies: List[float] = []

        class_matrix = {
            "BUY": {"BUY": 0, "SELL": 0, "HOLD": 0},
            "SELL": {"BUY": 0, "SELL": 0, "HOLD": 0},
            "HOLD": {"BUY": 0, "SELL": 0, "HOLD": 0}
        }

        per_asset_stats: Dict[str, Dict[str, int]] = {}
        per_regime_stats: Dict[str, Dict[str, int]] = {}

        for rec in records:
            pred = self.adapter.predict(rec.state, decision_id=f"BM_{rec.decision_id}")
            self.repo.save(pred)

            if pred.status != "SUCCESS":
                model_errors += 1
                continue

            total_evals += 1
            latencies.append(pred.latency_ms)

            gt_dir = rec.ground_truth.direction_outcome
            p_dir = pred.predicted_direction or "HOLD"

            if p_dir in class_matrix and gt_dir in class_matrix[p_dir]:
                class_matrix[gt_dir][p_dir] += 1

            if p_dir == gt_dir:
                correct_direction += 1

            # Asset stats
            asset_cls = str(rec.market)
            if asset_cls not in per_asset_stats:
                per_asset_stats[asset_cls] = {"total": 0, "correct_direction": 0}
            per_asset_stats[asset_cls]["total"] += 1
            if p_dir == gt_dir:
                per_asset_stats[asset_cls]["correct_direction"] += 1

            # Regime stats
            regime = rec.state.regime
            if regime not in per_regime_stats:
                per_regime_stats[regime] = {"total": 0, "correct_regime": 0}
            per_regime_stats[regime]["total"] += 1

            if pred.predicted_regime == rec.state.regime:
                correct_regime += 1
                per_regime_stats[regime]["correct_regime"] += 1

        acc = (correct_direction / total_evals) if total_evals > 0 else 0.0
        regime_acc = (correct_regime / total_evals) if total_evals > 0 else 0.0
        avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

        per_asset_accuracy = {
            k: round(v["correct_direction"] / v["total"], 4) if v["total"] > 0 else 0.0
            for k, v in per_asset_stats.items()
        }

        per_regime_accuracy = {
            k: round(v["correct_regime"] / v["total"], 4) if v["total"] > 0 else 0.0
            for k, v in per_regime_stats.items()
        }

        return {
            "total_records_processed": len(records),
            "valid_inference_evaluations": total_evals,
            "model_error_count": model_errors,
            "direction_accuracy": round(acc, 4),
            "regime_accuracy": round(regime_acc, 4),
            "per_asset_accuracy": per_asset_accuracy,
            "per_regime_accuracy": per_regime_accuracy,
            "confusion_matrix": class_matrix,
            "avg_latency_ms": round(avg_latency, 2),
            "confidence_status": "UNCALIBRATED",
            "decision_authority": "SHADOW_ONLY"
        }
