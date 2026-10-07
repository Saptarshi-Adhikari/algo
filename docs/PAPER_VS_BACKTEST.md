# BACKTEST VS PAPER TRADING EVALUATION METHODOLOGY

## Architectural Alignment
The system enforces strict consistency across backtesting, bar-by-bar replay, and paper execution:

1. **SIGNAL GENERATION**:
   - Backtest engine and paper execution share the exact same `StrategyEvaluator`.
   - Replay engine uses `stream_bars()` to feed historical price series bar-by-bar, preventing look-ahead bias.

2. **EXECUTION ASSUMPTIONS**:
   - **Fees**: Configurable fixed or percentage transaction fees (e.g., $5.0 per order).
   - **Slippage**: Simulated market impact and price movement allowance.
   - **Order Model**: Standardized `PaperOrder` structures (`PAPER BUY`, `PAPER SELL`) tracked in `PaperTradingSession`.

3. **DISCREPANCY METRICS**:
   - `BACKTEST vs PAPER` reports compare:
     * Expected vs. observed fill prices
     * Cumulative fee impact
     * Trade count alignment across splits
     * Max drawdown variance
