# Phase 16 — Laya Data Availability Policy

## Data Availability Status Architecture
Data Availability Status concerns the market-data layer only. It answers:
> "Can the system currently obtain sufficiently fresh, valid market data?"

## Allowed Status Values
- `DATA_AVAILABLE`: Fresh eligible market data exists and data pipeline is healthy.
- `DATA_STALE`: Market data feeds or historical datasets have exceeded freshness limits.
- `DATA_UNAVAILABLE`: Market data cannot be accessed or loaded.
- `DATA_QUALITY_BLOCKED`: Data quality audits detected severe corruption or look-ahead leakage.
- `DATA_PROVIDER_BLOCKED`: Underlying provider API is unreachable or rate-limited.
- `NO_ELIGIBLE_MARKETS`: No universe instruments met minimum bar length or quality criteria.

## Important Rule
This status does NOT inspect model performance or evidence counts.
