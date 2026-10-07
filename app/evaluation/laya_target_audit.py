"""Audit suite for Laya training target quality, probabilistic bounds, and causal state integrity."""
from typing import List, Dict, Any
from app.domain.decision_schemas import DecisionRecord
from app.decision.laya_target_policy import LayaTargetPolicy

class LayaTargetAuditor:
    """Performs rigorous quality and integrity checks on Laya target generation."""

    def audit_target_quality(self, records: List[DecisionRecord]) -> Dict[str, Any]:
        missing_gold = 0
        invalid_prob_sums = 0
        nan_inf_counts = 0
        causal_leakage_detected = 0
        
        class_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
        regime_counts = {}
        risk_counts = {}
        permission_counts = {}

        # Forbidden future field keywords inside state representation
        forbidden_state_keys = {"future_return", "ground_truth", "outcome", "post_trade_pnl", "next_bar"}

        for rec in records:
            # 1. State causal integrity check
            state_dict = rec.state.model_dump()
            for key in state_dict.keys():
                if any(forbidden in key.lower() for forbidden in forbidden_state_keys):
                    causal_leakage_detected += 1

            # 2. Target computation
            gold = LayaTargetPolicy.compute_gold_targets(rec)
            soft = LayaTargetPolicy.compute_soft_distribution(rec)

            if not gold or not gold.get("direction_v2"):
                missing_gold += 1
                continue

            dir_target = gold["direction_v2"]
            if dir_target in class_counts:
                class_counts[dir_target] += 1

            regime = gold["market_regime_v2"]
            regime_counts[regime] = regime_counts.get(regime, 0) + 1

            risk = gold["risk_level_v2"]
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

            perm = gold["trade_permission_v2"]
            permission_counts[perm] = permission_counts.get(perm, 0) + 1

            # 3. Soft probability distribution sum & valid bounds check
            dir_dist = soft.get("direction_v2", {})
            prob_sum = sum(dir_dist.values())
            if abs(prob_sum - 1.0) > 1e-5:
                invalid_prob_sums += 1

            for p in dir_dist.values():
                if p < 0.0 or p > 1.0 or not (p == p): # NaN check
                    nan_inf_counts += 1

        total = len(records)
        passed = (missing_gold == 0 and invalid_prob_sums == 0 and nan_inf_counts == 0 and causal_leakage_detected == 0)

        return {
            "audited_records_count": total,
            "missing_gold_count": missing_gold,
            "invalid_probability_sums": invalid_prob_sums,
            "nan_inf_counts": nan_inf_counts,
            "causal_leakage_count": causal_leakage_detected,
            "class_distribution": class_counts,
            "regime_distribution": regime_counts,
            "risk_distribution": risk_counts,
            "permission_distribution": permission_counts,
            "audit_passed": passed
        }
