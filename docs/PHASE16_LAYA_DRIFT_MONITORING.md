# Phase 16 — Laya Drift Monitoring & Decoupled Calibration

## Baseline vs Fresh Calibration
- **Phase 15 Baseline Calibration**: Evaluated on 131 held-out calibration cases ($T = 1.85$, ECE $0.08$, Brier $0.19$).
- **Phase 16 Fresh Calibration**: Evaluated only on resolved fresh-shadow predictions. Samples $< 30$ report `INSUFFICIENT_EVIDENCE` and `NOT_AVAILABLE`.

## Drift Status Sufficiency Rules
Drift statuses (`Feature Drift`, `Prediction Drift`, `Calibration Drift`, `Regime Drift`) require a minimum of 30 resolved fresh-shadow predictions. Samples $< 30$ report `INSUFFICIENT_EVIDENCE` rather than `STABLE`.
