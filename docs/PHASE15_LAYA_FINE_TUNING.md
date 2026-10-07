# Phase 15 — Laya Domain Fine-Tuning Specification

## Overview & Candidate Architecture (`ALGO_LAYA_V001`)
In Phase 15, an ALGO-specific candidate model (`ALGO_LAYA_V001`) was fine-tuned under run ID `ALGO_LAYA_TRAIN_RUN_001` using dataset package `ALGO_LAYA_DATASET_V1` and target policy `ALGO_LAYA_TARGET_POLICY_V1`.

## Key Execution Safeguards
1. **Base Checkpoint Untouched**: Base model `convaiinnovations/laya` (v0.3.5) remains untouched in its original location.
2. **Candidate Isolation**: Candidate weights and metadata are isolated under `models/laya/ALGO_LAYA_V001/`.
3. **No Training on Holdout**: `LAYA_TRAIN` (524 records) was used for training; `LAYA_CALIBRATION` (131 records) for temperature calibration; `VALIDATION` (149 records) and `HOLDOUT` (139 records) were strictly withheld.
4. **Authority**: Decision authority remains `SHADOW_ONLY`.
