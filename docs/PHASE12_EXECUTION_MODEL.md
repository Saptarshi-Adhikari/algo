# Phase 12: Realistic Transaction-Cost & Execution Simulation Layer

## Overview
Phase 12 implements a realistic, versioned transaction-cost and execution simulation layer for **QuantAI-PaperTrader / ALGO**. This layer prevents strategies from being falsely flagged as profitable under idealized assumptions (e.g. 0 fees, 0 slippage, zero spread, instant fills).

## Core Architecture

1. **`CostModel` (`app/domain/execution_schemas.py`)**:
   - `cost_model_id` (e.g. `COST_V1_BASELINE`)
   - `commission_bps` (e.g. 3.0 bps = 0.0003)
   - `tax_levy_bps` (exchange fees/STT/taxes)
   - `minimum_charge` (minimum order fee)
   - Asset-class and broker profile configuration.

2. **`ExecutionModel` (`app/domain/execution_schemas.py`)**:
   - `execution_model_id` (e.g. `EXEC_V1_BASELINE`)
   - `execution_mode`: `IDEALIZED`, `BASELINE_REALISTIC`, `STRESS`
   - `delay_mode`: `SAME_BAR_SIMULATION`, `NEXT_BAR`, `N_BAR_DELAY`
   - `slippage_bps` (e.g. 1.0 bps) & `spread_proxy_bps` (e.g. 2.0 bps for OHLCV proxies)
   - `liquidity_mode`: `MAX_BAR_VOLUME_PCT` (e.g. max 10.0% of bar volume).

3. **`CanonicalExecutionCalculator` (`app/services/execution_calculator.py`)**:
   - Centralizes net execution price, spread/slippage penalties, commission/tax fees, and fill quantities across Backtester, Replay Engine, and Paper Portfolio.

## Safety & Boundaries
- Simulation only — no live order routing or real money broker APIs exist.
- `PAPER_TRADING_ONLY = True` & `ALLOW_REAL_BROKER = False` strictly enforced.
