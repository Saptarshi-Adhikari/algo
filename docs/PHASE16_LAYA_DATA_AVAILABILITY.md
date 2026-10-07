# Phase 16 — Laya Data Availability Policy & Cutoff Methodology

## Data Availability Status Architecture
Data Availability Status concerns the market-data layer only. It answers:
> "Can the system currently obtain sufficiently fresh, valid market data?"

## Phase 15 Cutoff Methodology
- **Scope-Specific Cutoffs**: Cutoff timestamps (`2026-09-20T23:59:59Z`) are evaluated per symbol, asset class, and timeframe.
- **Fresh Record Audit**: A record is classified as `FRESH` if and only if its timestamp is strictly greater than the Phase 15 cutoff for its scope (`timestamp > scope_cutoff`).
- **Separation of Quantities**: Total historical records (e.g. 943) are never conflated with fresh post-Phase 15 observations.

## Instrument Normalization
Source symbols (e.g. `BTC/USDT`, `RELIANCE`) are normalized to canonical project symbols (`BTC-USD`, `RELIANCE.NS`) while preserving full source provenance (`source_symbol`, `provider`).
