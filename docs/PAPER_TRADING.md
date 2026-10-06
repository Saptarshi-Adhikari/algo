# Paper Trading Engine & Safety Constraints

## Architecture Boundary

```
MARKET DATA  -->  SIGNAL  -->  PAPER EXECUTION ENGINE  -->  SIMULATED PORTFOLIO
```

There is **NO DIRECT PATH** from signal generation to any broker or real trading API.

---

## Portfolio Simulation Features
- **Virtual Cash**: Configurable initial capital (default ₹/$100,000.0).
- **Position Tracking**: Real-time open positions, entry prices, quantity, unrealized P&L.
- **Transaction Costs**: Configurable transaction fees (default 3 bps = 0.0003) and slippage (default 1 bps = 0.0001).
- **Drawdown & Peak Equity**: Tracks max equity peak and current equity drawdown percentage.

---

## Absolute Safety Module (`app/config/safety.py`)
- Raises `RealMoneyExecutionForbiddenError` if `PAPER_TRADING_ONLY` is set to False or if any unauthorized broker call is detected.
- Verified via AST / Regex scan in automated test suite (`tests/test_broker_safety_audit.py`).
