"""Strategy Complexity Evaluator Module."""
from typing import Dict, Any
from app.domain.schemas import StrategySpec

class StrategyComplexityEvaluator:
    """Calculates quantitative complexity score for a strategy spec to penalize overfitted / overly intricate rules."""

    @staticmethod
    def evaluate_complexity(spec: StrategySpec) -> Dict[str, Any]:
        indicator_count = len(spec.indicators)
        entry_rule_count = len(spec.rules.entry_rules)
        exit_rule_count = len(spec.rules.exit_rules)
        total_rule_count = entry_rule_count + exit_rule_count

        # Estimate parameters count
        param_count = sum(len(ind.params) for ind in spec.indicators)
        if spec.rules.stop_loss_pct is not None:
            param_count += 1
        if spec.rules.take_profit_pct is not None:
            param_count += 1
        param_count += 1  # position_sizing_pct

        # Complexity Score Formula:
        # Base = (Indicators * 2.0) + (Rules * 1.5) + (Params * 1.0)
        complexity_score = round((indicator_count * 2.0) + (total_rule_count * 1.5) + (param_count * 1.0), 2)

        # Categorize
        if complexity_score <= 7.0:
            category = "LOW"
            penalty = 0.0
        elif complexity_score <= 15.0:
            category = "MODERATE"
            penalty = 0.05
        else:
            category = "HIGH"
            penalty = 0.20

        return {
            "indicator_count": indicator_count,
            "entry_rule_count": entry_rule_count,
            "exit_rule_count": exit_rule_count,
            "total_rules": total_rule_count,
            "total_parameters": param_count,
            "complexity_score": complexity_score,
            "complexity_category": category,
            "sharpe_penalty": penalty
        }
