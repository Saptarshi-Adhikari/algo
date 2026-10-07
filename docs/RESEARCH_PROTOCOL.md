# QUANTITATIVE AI RESEARCH PROTOCOL & ANTI-OVERFITTING SPECIFICATION

## Research Loop Workflow
1. **HYPOTHESIS GENERATION**:
   - `ResearcherAgent` queries SQLite memory for past experiment evidence.
   - Requires explicit citations of prior experiment IDs.
   - Enforces deterministic **Anti-Repeat logic** to prevent re-evaluating duplicate or disguised hypotheses.

2. **DETERMINISTIC STRATEGY BUILDING**:
   - `StrategyBuilderAgent` maps qualitative hypotheses to executable `StrategySpec` JSON objects.
   - Employs safe AST expression evaluation for mathematical rule parsing (e.g. `1.05 * close(-1)`).

3. **CHRONOLOGICAL DATA SPLIT**:
   - Data is partitioned chronologically into **DEVELOPMENT (60%)**, **VALIDATION (20%)**, and **HOLDOUT (20%)**.
   - `HoldoutProtectionError` strictly blocks automated strategy optimization or LLM loops from querying HOLDOUT data.

4. **CRITIQUE & COMPLEXITY SCORING**:
   - `CriticAgent` evaluates performance on VALIDATION splits with strict hard rules:
     * Minimum trade count: `trade_count >= 5`
     * Minimum Sharpe ratio: `sharpe_ratio >= 0.5`
     * Maximum drawdown: `max_drawdown_pct <= 25%`
   - `StrategyComplexityEvaluator` penalizes over-engineered strategies with excessive indicators or parameters.

5. **EXPERIMENT MEMORY & LINEAGE**:
   - All outcomes (PASSED, RETEST, REJECTED) are recorded in SQLite `ExperimentRepository`.
   - Rejections trigger `ROLLBACK_PARENT` to preserve baseline strategy lineage.

6. **PAPER-TRADING REPLAY VERIFICATION**:
   - Candidate strategies are validated bar-by-bar using `ReplayDataProvider.stream_bars()` with strict look-ahead protection.
