# Phase 13 — Laya Integration

## Overview
Laya is integrated into **QuantAI-PaperTrader / ALGO** as a candidate structured decision model. Laya provides structured predictions on market regime, trade direction, strategy family, trade permission, risk level, and signal strength.

## Key Principles & Boundaries
1. **Decision Candidate Only**: Laya operates strictly as a decision candidate (`SHADOW_ONLY`).
2. **No Execution Authority**: Laya cannot place broker orders, execute trades, or override risk controls.
3. **No Self-Modification / Fine-Tuning**: Autonomous retraining or self-modification is strictly disabled in Phase 13.
4. **Authoritative Hierarchy**:
   - Ground Truth / Backtester (Authoritative)
   - Rule Strategies (Candidate Evidence)
   - Laya (Candidate Structured Decision)
   - Qwen2.5 7B (Research Reasoning / Explanation)
   - Dashboard (Observation & Control)

## Architecture
- `app/domain/laya_schemas.py`: Versioned decision schema contract (`LAYA_DECISION_SCHEMA_V1`).
- `app/decision/laya_adapter.py`: Adapter translating ALGO `MarketState` into Laya `predict()` input and normalizing prediction outputs.
- `app/memory/laya_repository.py`: SQLite persistence for decision logs.
