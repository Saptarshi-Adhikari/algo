# Phase 16 — Laya Drift Monitoring & Calibration Stability

## Drift Monitoring Dimensions
- **Feature Drift**: Structural changes in input state vectors.
- **Prediction Drift**: Shifts in output decision distributions over time.
- **Calibration Drift**: Deviations between model confidence and actual direction accuracy.
- **Regime Drift**: Unseen market regime transitions.

## Calibration Status
- `CALIBRATION_STABLE`: ECE <= 0.15.
- `CALIBRATION_DRIFT`: ECE 0.15–0.25.
- `CALIBRATION_FAILED`: ECE > 0.25.
