"""Strategy Version Control & Lineage Manager."""
from typing import List, Optional, Dict, Any
from app.domain.schemas import StrategySpec
from app.memory.repository import ExperimentRepository
from app.config.logging import logger

class StrategyVersionManager:
    """Manages strategy specs, version lineage tree, and version rollback functionality."""

    def __init__(self, repository: Optional[ExperimentRepository] = None):
        self.repository = repository or ExperimentRepository()

    def register_version(self, spec: StrategySpec, status: str = "CANDIDATE") -> None:
        """Register a strategy version spec in database memory."""
        self.repository.save_strategy_spec(spec, status=status)
        logger.info(f"Registered Strategy Version: {spec.version} (Parent: {spec.parent_version_id or 'None'})")

    def rollback_to_parent(self, current_spec: StrategySpec) -> Optional[str]:
        """Determine parent version ID for rollback when current strategy is rejected."""
        if not current_spec.parent_version_id:
            logger.warning(f"Strategy {current_spec.version} has no parent version to roll back to.")
            return None
        logger.info(f"Rolling back from strategy {current_spec.version} to parent {current_spec.parent_version_id}")
        return current_spec.parent_version_id

    def get_version_lineage_tree(self) -> List[Dict[str, Any]]:
        """Retrieve complete historical experiment lineage for tree display."""
        all_experiments = self.repository.get_all_experiments()
        tree = []
        for exp in all_experiments:
            tree.append({
                "experiment_id": exp.experiment_id,
                "version": exp.strategy_version,
                "parent_id": exp.parent_experiment_id,
                "hypothesis": exp.hypothesis,
                "verdict": exp.critic_verdict,
                "sharpe": exp.metrics.sharpe_ratio,
                "return_pct": exp.metrics.total_return_pct,
                "regime": exp.market_regime,
                "timestamp": exp.timestamp
            })
        return tree
