"""Objective Gold-Target and Soft-Target Policy for ALGO Laya fine-tuning readiness."""
import math
from typing import Dict, Any, Tuple
from app.domain.decision_schemas import DecisionRecord

TARGET_POLICY_VERSION = "ALGO_LAYA_TARGET_POLICY_V1"
DISTRIBUTION_POLICY_VERSION = "ALGO_LAYA_TARGET_DISTRIBUTION_V1"

class LayaTargetPolicy:
    """Computes deterministic gold targets and soft probability distributions for Laya training cases."""

    @staticmethod
    def compute_gold_targets(record: DecisionRecord) -> Dict[str, Any]:
        ret_pct = record.ground_truth.realized_return_pct
        state = record.state

        # 1. Raw Direction Target
        if ret_pct >= 0.5:
            raw_direction = "BUY"
        elif ret_pct <= -0.5:
            raw_direction = "SELL"
        else:
            raw_direction = "HOLD"

        # 2. Net Direction Target (Cost-adjusted proxy: deduction of 0.10% friction)
        net_ret = ret_pct - 0.10
        if net_ret >= 0.40:
            net_direction = "BUY"
        elif net_ret <= -0.60:
            net_direction = "SELL"
        else:
            net_direction = "HOLD"

        # 3. Objective Risk Target derived from ATR & volatility
        features = getattr(state, "custom_features", {}) or getattr(state, "features", {}) or {}
        vol = features.get("volatility_20d", 0.015)
        rsi = features.get("rsi_14", 50.0)
        
        if vol >= 0.035 or rsi > 80 or rsi < 20:
            risk_level = "HIGH"
        elif vol >= 0.02:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # 4. Objective Trade Permission Target
        if net_direction != "HOLD" and risk_level != "HIGH":
            trade_permission = "ALLOW"
        else:
            trade_permission = "REJECT"

        # 5. Objective Regime Target
        regime = state.regime if state.regime in ["TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY"] else "UNKNOWN"

        return {
            "direction_v2": net_direction,
            "raw_direction": raw_direction,
            "market_regime_v2": regime,
            "trade_permission_v2": trade_permission,
            "risk_level_v2": risk_level,
            "target_policy_version": TARGET_POLICY_VERSION
        }

    @staticmethod
    def compute_soft_distribution(record: DecisionRecord) -> Dict[str, Dict[str, float]]:
        """Generates soft softmax probability distributions summing strictly to 1.0."""
        ret = record.ground_truth.realized_return_pct
        
        # Continuous return scaling for Direction
        # temperature = 1.0
        e_buy = math.exp(clamp(ret, -5.0, 5.0))
        e_sell = math.exp(clamp(-ret, -5.0, 5.0))
        e_hold = math.exp(1.0 - abs(clamp(ret, -5.0, 5.0)))

        tot_dir = e_buy + e_sell + e_hold
        p_buy = round(e_buy / tot_dir, 6)
        p_sell = round(e_sell / tot_dir, 6)
        p_hold = round(1.0 - p_buy - p_sell, 6) # guarantees sum == 1.0 Exactly

        # Soft distribution for Risk
        features = getattr(record.state, "custom_features", {}) or getattr(record.state, "features", {}) or {}
        vol = features.get("volatility_20d", 0.015)
        e_low = math.exp(clamp(0.03 - vol, -2.0, 2.0) * 50)
        e_med = math.exp(clamp(vol - 0.015, -2.0, 2.0) * 30)
        e_high = math.exp(clamp(vol - 0.03, -2.0, 2.0) * 50)
        tot_risk = e_low + e_med + e_high
        
        pr_low = round(e_low / tot_risk, 6)
        pr_med = round(e_med / tot_risk, 6)
        pr_high = round(1.0 - pr_low - pr_med, 6)

        return {
            "direction_v2": {
                "BUY": p_buy,
                "SELL": p_sell,
                "HOLD": p_hold
            },
            "risk_level_v2": {
                "LOW": pr_low,
                "MEDIUM": pr_med,
                "HIGH": pr_high
            },
            "distribution_policy_version": DISTRIBUTION_POLICY_VERSION
        }

def clamp(val: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, val))
