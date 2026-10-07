# Phase 17 — LightGBM Numerical Prediction Foundation

## Overview
Phase 17 introduces the first dedicated **numerical machine-learning prediction layer** into ALGO (`ALGO_LGBM_V001`).

## Runtime Manifest
- **Python**: `3.11.0`
- **LightGBM**: `4.7.0`
- **NumPy**: `1.26.4`
- **Pandas**: `2.2.3`
- **Training Device**: `CPU`

## Architecture Separation
```
MarketState
    ↓
Feature Builder (LIGHTGBM_FEATURE_SCHEMA_V1)
    ↓
LightGBM (ALGO_LGBM_V001)
    ↓
Numerical 4-Bar Return Prediction
    ↓
Offline Research Evaluation
```

Laya V001 and LightGBM V001 remain completely independent models. Neither model uses the other's outputs as input features.
