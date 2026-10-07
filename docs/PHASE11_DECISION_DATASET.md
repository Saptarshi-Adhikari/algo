# Phase 11: Research Benchmark & Decision Dataset Foundation

## Overview
Phase 11 implements the formal, auditable decision dataset foundation for **QuantAI-PaperTrader / ALGO**, transforming historical market states and backtest observations into structured, leakage-free decision records formatted for future model training and calibration (such as Laya).

## Core Architecture
- **Input State**: `MarketState` captures causal OHLCV and indicator features available strictly at or before timestamp $T$.
- **Ground Truth**: `GroundTruthOutcome` computes objective future performance (realized return, MFE, MAE, target/stop hits) strictly over future horizon $[T+1, T+H]$.
- **Typed Questions**: `DecisionQuestion` defines typed choice/score questions (`q_market_regime`, `q_direction`, `q_trade_permission`).
- **Persistence**: `DecisionRepository` persists `DecisionRecord` objects into SQLite with indexed metadata (`dataset_id`, `dataset_hash`, `data_split`).
- **Export Engine**: `LayaDatasetExporter` formats records into Laya-compatible `state`, `questions`, and `gold` cases.

## Protection against Future Data Leakage
- `StateSnapshotBuilder` slices input DataFrames strictly up to index $T$.
- `DatasetLeakageAuditor` validates that no state timestamp overlaps or exceeds future observation windows.
- Train / Validation / Holdout splits are partitioned chronologically per asset (70% Development, 15% Validation, 15% Holdout).
