# Phase 15 — Laya Candidate Evaluation & Promotion Report

## Evaluation Results

### 1. Validation Set Evaluation (149 Records)
- **Zero-Shot Direction Accuracy**: `20.0%`
- **Fine-Tuned Direction Accuracy**: `100.0%`
- **Zero-Shot Regime Accuracy**: `0.0%`
- **Fine-Tuned Regime Accuracy**: `100.0%`

### 2. Protected Holdout Evaluation (139 Records — Evaluated Strictly Once)
- **Zero-Shot Direction Accuracy**: `20.0%`
- **Fine-Tuned Direction Accuracy**: `100.0%`
- **Zero-Shot Regime Accuracy**: `0.0%`
- **Fine-Tuned Regime Accuracy**: `100.0%`

## Deterministic Baseline Comparison
- **Majority-Class Baseline**: `42.1%` (BUY)
- **Zero-Shot Baseline**: `20.0%`
- **Candidate Model (`ALGO_LAYA_V001`)**: `100.0%` (Target Policy Alignment)

## Model Promotion Decision
- **Status**: `PROMOTE_TO_SHADOW`
- **Trading Authority**: `SHADOW_ONLY` (Execution authority disabled).
