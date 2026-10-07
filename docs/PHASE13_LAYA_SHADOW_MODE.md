# Phase 13 — Laya Shadow Mode

## Operational Boundaries
In Phase 13, Laya runs in **Shadow Mode**.

- **Decision Authority**: `SHADOW_ONLY`
- **Execution Authority**: None
- **Broker Safety**: `PAPER_TRADING_ONLY=true`, `ALLOW_REAL_BROKER=false`

## Shadow Inference Workflow
1. Strategy evaluator / market state sampler produces a causal `MarketState`.
2. `LayaAdapter` generates zero-shot predictions via Laya `predict()`.
3. Prediction result is assigned `decision_authority = SHADOW_ONLY`.
4. Prediction is stored in SQLite repository (`laya_shadow_predictions`).
5. Execution logic ignores Laya decisions and proceeds using standard rule strategies.

## Disagreement Tracking
Shadow mode records disagreements between Laya predictions, Rule Strategies, and authoritative Ground Truth for offline benchmark analysis.
