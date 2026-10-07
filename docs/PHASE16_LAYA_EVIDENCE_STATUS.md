# Phase 16 — Laya Evidence Status Policy

## Evidence Status Architecture
Evidence Status answers:
> "Is there enough resolved fresh evidence to support a performance conclusion?"

## Allowed Status Values
- `NO_EVIDENCE`: Zero resolved fresh-shadow predictions.
- `INSUFFICIENT_EVIDENCE`: Below preliminary threshold (< 100 resolved).
- `LIMITED_EVIDENCE`: Minimum preliminary threshold reached (>= 100 resolved), but limited asset coverage.
- `ADEQUATE_EVIDENCE`: Adequate sample size and multi-asset coverage achieved.
- `STRONG_EVIDENCE`: >= 300 resolved predictions with >= 75 across >= 3 asset classes.
- `EVIDENCE_DEGRADED`: Calibration failure or severe drift detected on previously adequate evidence.

## Independence Rule
Evidence Status is decoupled from Collection Status. Pausing or stopping collection preserves accumulated evidence.
