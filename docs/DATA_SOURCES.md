# Market Data Sources & Split Engine

## Supported Providers

1. **Indian Equity & Index Data Provider (`IndianMarketDataProvider`)**
   - Fetches NSE/BSE stocks (e.g. `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`) and index data (`^NSEI` for NIFTY 50) using legitimate free APIs (`yfinance`).
   - Includes graceful synthetic fallback generation if network or rate limits fail.

2. **Forex Data Provider (`ForexDataProvider`)**
   - Supports major and minor currency pairs (e.g. `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`, `USDINR=X`).

3. **CSV & Local File Provider (`CSVDataProvider`)**
   - Import offline CSV market data directly from `data/` directory.

4. **Replay & Synthetic Generator (`ReplayDataProvider`)**
   - Tailored market regime data generator (`TRENDING`, `RANGING`, `HIGH_VOLATILITY`, `LOW_VOLATILITY`).

---

## Chronological Data Split Engine

The dataset is partitioned chronologically to protect research integrity:
- **DEVELOPMENT (60%)**: Strategy rule discovery and initial backtesting.
- **VALIDATION (20%)**: Strategy critique and out-of-sample evaluation.
- **HOLDOUT (20%)**: Final validation set protected from repeated strategy optimization.
