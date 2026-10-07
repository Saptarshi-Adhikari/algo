# Phase 16 — Laya Evidence Status Policy

## Evidence Status Architecture
Evidence Status answers:
> "Is there enough resolved fresh evidence to support a performance conclusion?"

## Allowed Status Values & Thresholds
- `NO_EVIDENCE`: Zero resolved fresh-shadow predictions.
- `INSUFFICIENT_EVIDENCE`: Below preliminary threshold (< 100 resolved).
- `LIMITED_EVIDENCE`: Preliminary threshold reached (>= 100 resolved), but limited asset coverage.
- `ADEQUATE_EVIDENCE`: Adequate sample size and multi-asset coverage achieved (>= 100 resolved across >= 2 assets).
- `STRONG_EVIDENCE`: >= 300 resolved predictions with >= 75 across >= 3 asset classes.
- `EVIDENCE_DEGRADED`: Calibration failure or severe drift detected on previously adequate evidence.

## Independence Rule
Evidence Status is decoupled from Collection Status. A single resolved prediction or small sample MUST yield `INSUFFICIENT_EVIDENCE`.
