# Phase 14 — Laya Dataset Specification & Manifest

## Overview (`ALGO_LAYA_DATASET_V1`)
The Phase 14 Laya training dataset is constructed from the Phase 11 decision dataset (943 DecisionRecords across Indian Equities, Crypto, and Forex).

## Split Distribution
1. **LAYA_TRAIN**: 524 records (80% chronological slice of DEVELOPMENT set)
2. **LAYA_CALIBRATION**: 131 records (20% chronological slice of DEVELOPMENT set)
3. **VALIDATION**: 149 records (100% Phase 11 validation set)
4. **HOLDOUT**: 139 records (**100% Protected Phase 11 holdout set — Strictly untouched**)

## File Artifacts (`data/laya/`)
- `train.jsonl`: 524 formatted Laya training cases
- `calibration.jsonl`: 131 formatted Laya calibration cases
- `validation.jsonl`: 149 validation benchmark cases
- `holdout.jsonl`: 139 protected holdout cases
- `dataset_manifest.json`: Versioned provenance and split statistics manifest

## Safety & Causal Integrity
- State representations contain **zero** future lookahead fields.
- `fine_tuning_executed = false`
- `model_weights_mutated = false`
- `decision_authority = SHADOW_ONLY`
