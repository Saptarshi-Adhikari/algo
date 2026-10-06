"""Researcher AI Agent proposing hypotheses based on experiment memory."""
from typing import List, Optional
from app.llm.base import BaseLLMProvider
from app.llm.router import LLMRouter
from app.memory.repository import ExperimentRepository
from app.domain.schemas import HypothesisSpec, ExperimentRecord, MarketRegimeType
from app.config.logging import logger

SYSTEM_PROMPT = """You are an elite quantitative finance Researcher Agent.
Your job is to read relevant experiment memory, review previous failures and successes, and propose exactly ONE new structured hypothesis.
You must cite relevant past experiment IDs and explicitly state why your new hypothesis differs from failed experiments.
Never claim guaranteed profitability or invent historical price data."""

class ResearcherAgent:
    """Proposes quantitative trading hypotheses grounded in experiment memory."""

    def __init__(self, llm: Optional[BaseLLMProvider] = None, repository: Optional[ExperimentRepository] = None):
        self.llm = llm or LLMRouter()
        self.repository = repository or ExperimentRepository()

    def propose_hypothesis(
        self,
        symbol: str = "RELIANCE.NS",
        regime: MarketRegimeType = "TRENDING",
        max_memory_items: int = 5
    ) -> HypothesisSpec:
        """Query memory and generate one structured hypothesis."""
        recent = self.repository.get_recent_experiments(limit=max_memory_items)
        failed = self.repository.get_failed_experiments()[:3]
        passed = self.repository.get_successful_experiments()[:3]

        memory_text = "=== PAST EXPERIMENT MEMORY ===\n"
        if not recent:
            memory_text += "No prior experiments recorded yet. Formulate an initial baseline hypothesis.\n"
        else:
            for exp in recent:
                memory_text += (
                    f"ID: {exp.experiment_id} | Verdict: {exp.critic_verdict} | "
                    f"Sharpe: {exp.metrics.sharpe_ratio:.2f} | Lesson: {exp.lesson_learned}\n"
                )

        if failed:
            memory_text += "\n=== FAILED EXPERIMENTS TO AVOID ===\n"
            for f in failed:
                memory_text += f"ID: {f.experiment_id} | Reason: {f.failure_reason or f.critic_reasoning}\n"

        prompt = (
            f"Symbol: {symbol}\n"
            f"Current Market Regime: {regime}\n\n"
            f"{memory_text}\n\n"
            f"Propose ONE new quantitative trading hypothesis tailored for {symbol} in a {regime} regime."
        )

        logger.info(f"ResearcherAgent generating hypothesis for {symbol} in {regime} regime...")
        hypothesis = self.llm.generate_json(prompt, HypothesisSpec, system_prompt=SYSTEM_PROMPT)
        return hypothesis
