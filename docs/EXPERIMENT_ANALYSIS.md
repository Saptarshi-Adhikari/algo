# EXPERIMENT ANALYSIS & AI BRAIN SPECIFICATION

## Experiment Memory Database Schema
SQLite database `data/experiments.db` maintains full experimental auditability:
- `experiment_id`: Unique identifier (e.g., `EXP_SYNTHETIC_IND_001`)
- `hypothesis`: Qualitative rationale proposed by `ResearcherAgent`
- `strategy_version`: Version tag and parent lineage
- `critic_verdict`: `KEEP_FOR_PAPER_TESTING`, `RETEST`, or `REJECT`
- `metrics`: Backtest performance JSON (Sharpe, Drawdown, Return, Trade Count)
- `market_regime`: Classified regime (`TRENDING`, `RANGING`, `HIGH_VOLATILITY`, `LOW_VOLATILITY`)

## AI Brain Learned Summary Engine
`AIBrainService` analyzes stored experiment records to synthesize evidence-grounded insights:
- Every observation explicitly cites the corresponding `experiment_id`.
- Unsupported universal trading claims (e.g., "Momentum is always superior") are strictly prohibited.
- Identifies regime-specific performance trends and repeated failure patterns.
