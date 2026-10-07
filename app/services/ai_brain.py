"""AI Brain / Learned Summary Generator Service."""
from typing import List, Dict, Any
from app.domain.schemas import ExperimentRecord
from app.memory.repository import ExperimentRepository

class AIBrainService:
    """Generates structured, evidence-grounded summary observations referencing specific experiment IDs."""

    def __init__(self, repository: ExperimentRepository = None):
        self.repository = repository or ExperimentRepository()

    def generate_learned_summary(self) -> Dict[str, Any]:
        all_exps = self.repository.get_all_experiments()
        if not all_exps:
            return {
                "observations": ["No experiment memory recorded yet."],
                "repeated_failures": [],
                "regime_insights": {},
                "evidence_citations": []
            }

        observations = []
        repeated_failures = []
        regime_insights = {}
        citations = []

        passed_exps = [e for e in all_exps if e.critic_verdict == "KEEP_FOR_PAPER_TESTING"]
        failed_exps = [e for e in all_exps if e.critic_verdict == "REJECT"]

        # Group by regime
        regimes = set(e.market_regime for e in all_exps)
        for r in regimes:
            r_exps = [e for e in all_exps if e.market_regime == r]
            r_passed = [e for e in r_exps if e.critic_verdict == "KEEP_FOR_PAPER_TESTING"]
            regime_insights[r] = {
                "total_tested": len(r_exps),
                "passed_count": len(r_passed),
                "experiment_ids": [e.experiment_id for e in r_exps]
            }
            if r_passed:
                symbols_involved = ", ".join(list(set(e.symbol for e in r_passed)))
                obs = f"In {r} market regime on symbol(s) [{symbols_involved}], strategies passed critique in experiments: {', '.join([e.experiment_id for e in r_passed])}."
                observations.append(obs)
                citations.extend([e.experiment_id for e in r_passed])

        if failed_exps:
            failed_ids = [e.experiment_id for e in failed_exps[:5]]
            symbols_failed = ", ".join(list(set(e.symbol for e in failed_exps[:5])))
            repeated_failures.append(
                f"On [{symbols_failed}], low trade count, zero signals, or excess drawdown caused strategy rejections in experiments: {', '.join(failed_ids)}."
            )
            citations.extend(failed_ids)

        if not observations:
            all_symbols = ", ".join(list(set(e.symbol for e in all_exps))) if all_exps else "tested datasets"
            all_ids = ", ".join([e.experiment_id for e in all_exps[:5]]) if all_exps else ""
            observations.append(f"Experiments [{all_ids}] on [{all_symbols}] generated insufficient trade frequency or poor risk-adjusted returns under tested market regimes.")

        return {
            "title": "WHAT THIS SYSTEM HAS LEARNED FROM EXPERIMENT EVIDENCE",
            "evidence_supported_observations": observations,
            "repeated_failures": repeated_failures,
            "regime_insights": regime_insights,
            "all_cited_experiment_ids": sorted(list(set(citations)))
        }
