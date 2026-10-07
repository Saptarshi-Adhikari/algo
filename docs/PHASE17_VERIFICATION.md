# Phase 17 — Verification Report

## Verification Highlights
1. **LightGBM Dependency & Runtime**: Installed `lightgbm==4.7.0` on Python 3.11.0 CPU runtime.
2. **Feature Schema & Leakage Protection**: Verified 0 look-ahead features in `LIGHTGBM_FEATURE_SCHEMA_V1` via `scripts/audit_lightgbm_features.py`.
3. **Target Alignment**: Verified target $\text{close}[t+4]/\text{close}[t] - 1$.
4. **Chronological Splitting**: Verified 70% Train, 15% Validation, 15% Holdout split with zero timestamp overlap.
5. **Deterministic Baselines**: Evaluated `ZERO_RETURN` and `HISTORICAL_MEAN` baselines against LightGBM.
6. **Laya Independence**: Verified `ALGO_LAYA_V001` remains frozen and locked to `SHADOW_ONLY`.
7. **Safety & Authority**: `decision_authority = OFFLINE_RESEARCH_ONLY`, `PAPER_TRADING_ONLY = true`, `ALLOW_REAL_BROKER = false`.

## Verification Scripts Run
- `pytest -v` (147 PASSED)
- `verify_phase2.py` (PASSED)
- `verify_phase6.py` (PASSED)
- `verify_phase7.py` (PASSED)
- `verify_phase8.py` (PASSED)
- `verify_phase9_10.py` (PASSED)
- `verify_phase11.py` (PASSED)
- `verify_phase12.py` (PASSED)
- `verify_phase13.py` (PASSED)
- `verify_phase14.py` (PASSED)
- `verify_phase15.py` (PASSED)
- `verify_phase16.py` (PASSED)
- `verify_phase17.py` (PASSED)
- `python -m py_compile dashboard/app.py` (PASSED)
