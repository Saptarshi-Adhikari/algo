"""Laya Question-Set V2 Schema definition for ALGO Phase 14."""
from typing import Dict, Any, List

LAYA_QUESTION_SET_V2_VERSION = "LAYA_QUESTION_SET_V2"

LAYA_QUESTION_SET_V2: Dict[str, Dict[str, Any]] = {
    "market_regime_v2": {
        "question_id": "market_regime_v2",
        "type": "choice",
        "instructions": "Determine the prevailing structural market regime based on trend strength, volatility, and price consolidation.",
        "criteria": {
            "TRENDING": "Strong directional move sustained over multiple time periods.",
            "RANGING": "Price bound within defined support and resistance boundaries without clear direction.",
            "HIGH_VOLATILITY": "Rapid, wide price swings with elevated ATR and spread.",
            "LOW_VOLATILITY": "Tight price compression and low historical volatility.",
            "UNKNOWN": "Insufficient structural data to classify regime."
        },
        "ground_truth_source": "Canonical MarketState structural classification engine",
        "suitable_for_training": True,
        "suitable_for_evaluation": True
    },
    "direction_v2": {
        "question_id": "direction_v2",
        "type": "choice",
        "instructions": "Select the optimal net executable trade direction for the next forward evaluation horizon.",
        "criteria": {
            "BUY": "Positive expected net return exceeding transaction costs and slippage threshold.",
            "SELL": "Negative expected net return exceeding transaction costs and slippage threshold.",
            "HOLD": "Neutral or sub-cost return expectation; stay out of market."
        },
        "ground_truth_source": "Execution-cost adjusted forward return policy (NET_DIRECTION_V1)",
        "suitable_for_training": True,
        "suitable_for_evaluation": True
    },
    "trade_permission_v2": {
        "question_id": "trade_permission_v2",
        "type": "choice",
        "instructions": "Determine whether market conditions and execution risk permit taking a new trade position.",
        "criteria": {
            "ALLOW": "Favorable risk-reward, adequate liquidity, and risk within system thresholds.",
            "REJECT": "Excessive volatility, inadequate expected return, or high drawdown risk."
        },
        "ground_truth_source": "Deterministic risk & execution policy (TRADE_PERMISSION_V1)",
        "suitable_for_training": True,
        "suitable_for_evaluation": True
    },
    "risk_level_v2": {
        "question_id": "risk_level_v2",
        "type": "choice",
        "instructions": "Assess the structural tail risk and volatility exposure of the current market state.",
        "criteria": {
            "LOW": "Stable volatility, tight spreads, and low historical drawdown risk.",
            "MEDIUM": "Moderate ATR and normal market volatility.",
            "HIGH": "Extreme ATR relative to price or elevated adverse excursion risk."
        },
        "ground_truth_source": "ATR & Volatility ratio deterministic threshold policy (RISK_LEVEL_V1)",
        "suitable_for_training": True,
        "suitable_for_evaluation": True
    }
}
