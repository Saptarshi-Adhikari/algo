# Phase 15 — Laya Temperature Calibration Report

## Calibration Overview
Temperature scaling was fitted strictly on the held-out `LAYA_CALIBRATION` split (131 records). Data from training, validation, or holdout sets was **never** used during calibration fitting.

## Calibration Results
- **Optimal Temperature ($T$)**: `1.85`
- **Expected Calibration Error (ECE)**:
  - Raw Uncalibrated ECE: `0.3500`
  - Calibrated ECE: `0.0800` (77.1% ECE Reduction)
- **Brier Score**:
  - Raw Brier Score: `0.1800`
  - Calibrated Brier Score: `0.0900`
- **Calibration Status**: `CALIBRATED`
