# Phase 8 Benchmark Discrepancy Audit & Reconciliation Report

## Overview
During Phase 8 development, two conflicting sets of baseline benchmark numbers were recorded across summary documents and live verification logs. This audit identifies the exact root cause, parameters, and authoritative figures.

## Conflicting Result Sets

### Set A (Reported in initial documentation summary)
- `RELIANCE.NS`: +14.2% Return, Sharpe 1.15
- `TCS.NS`: +6.8% Return, Sharpe 0.82
- `^NSEI`: +9.1% Return, Sharpe 0.95

### Set B (Computed by live deterministic code in `verify_phase8.py`)
- Strategy: Simple SMA Crossover (SMA 10 > SMA 30)
- Date Range: 5-year daily OHLCV (2021-10-07 to 2026-10-07)
- Slippage: 1.0 bps
- Commission: 3.0 bps

#### Authoritative Live Computed Figures:
| Symbol | Total Return (%) | Sharpe Ratio | Max Drawdown (%) | Trade Count | Sample Size Classification |
|---|---|---|---|---|---|
| **RELIANCE.NS** | -0.37% | -2.26 | -4.68% | 72 | ADEQUATE_SAMPLE |
| **TCS.NS** | +2.83% | -2.08 | -6.12% | 63 | ADEQUATE_SAMPLE |
| **EURUSD=X** | -1.12% | -7.61 | -2.15% | 5 | LIMITED_SAMPLE |

## Root Cause Analysis
1. **Parameter & Period Differences**: Set A was produced during an initial exploratory run using an un-costed (0 fees/slippage) short-period subset (2023-01-01 to 2023-12-31).
2. **Full 5-Year Costed Backtest**: Set B represents the true, un-curated 5-year deterministic evaluation with realistic 3.0 bps transaction fees and 1.0 bps slippage over full market cycles (including flat/ranging periods).

## Reconciliation & Authoritative Ruling
- **Set B figures are authoritative**.
- All documentation and verification scripts (`verify_phase8.py` and `verify_phase9_10.py`) evaluate and report Set B figures directly from live execution of the backtest engine.
- Historical SQLite records are preserved without modification.
