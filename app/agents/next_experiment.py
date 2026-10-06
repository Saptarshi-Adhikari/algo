"""Next-Experiment Agent determining lineage direction."""
from typing import Literal, Tuple
from app.domain.schemas import CriticVerdictType, StrategySpec
from app.config.logging import logger

NextActionType = Literal["NEW_HYPOTHESIS", "RETEST_VARIATION", "ROLLBACK_PARENT"]

class NextExperimentAgent:
    """Determines the next strategic decision in the research loop based on critic verdict."""

    def decide_next_step(
        self,
        critic_verdict: CriticVerdictType,
        current_spec: StrategySpec
    ) -> Tuple[NextActionType, str]:
        if critic_verdict == "KEEP_FOR_PAPER_TESTING":
            action: NextActionType = "NEW_HYPOTHESIS"
            reason = f"Strategy {current_spec.version} passed critique! Keep for paper testing and explore next hypothesis."
        elif critic_verdict == "RETEST":
            action: NextActionType = "RETEST_VARIATION"
            reason = f"Strategy {current_spec.version} requires retesting/tuning parameters."
        else:  # REJECT
            if current_spec.parent_version_id:
                action: NextActionType = "ROLLBACK_PARENT"
                reason = f"Strategy {current_spec.version} rejected. Rolling back to parent version {current_spec.parent_version_id}."
            else:
                action: NextActionType = "NEW_HYPOTHESIS"
                reason = f"Baseline Strategy {current_spec.version} rejected. Formulating new baseline hypothesis."

        logger.info(f"NextExperimentAgent decided: {action} ({reason})")
        return action, reason
