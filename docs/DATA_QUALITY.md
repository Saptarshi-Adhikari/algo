# DATA PROVIDER AUDIT & DATA QUALITY SPECIFICATION

## Data Provider Audit Matrix

| Provider | Actual Source | Library / Endpoint | Authentication | Data Status Label | Timezone | Symbol Convention | Rate Limits / Terms | Synthetic Fallback | Production Usability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IndianMarketDataProvider** | Yahoo Finance (`yf.Ticker`) | `yfinance` Python library | None (Public API) | **HISTORICAL** / **DELAYED** (15-min delayed during market hours) | `Asia/Kolkata` (Normalized to UTC) | `{SYMBOL}.NS` (e.g. `RELIANCE.NS`, `^NSEI`) | Rate limited by Yahoo IP throttling; non-commercial | Automatically switches to `SYNTHETIC` if network/ticker fails | **Usable** for daily research & backtests |
| **ForexDataProvider** | Yahoo Finance (`yf.Ticker`) | `yfinance` Python library | None (Public API) | **HISTORICAL** / **DELAYED** | `UTC` | `{PAIR}=X` (e.g. `EURUSD=X`, `USDINR=X`) | Rate limited by Yahoo IP throttling; non-commercial | Automatically switches to `SYNTHETIC` if network/pair fails | **Usable** for daily forex research |
| **CSVDataProvider** | Local filesystem | Pandas `read_csv` | File permissions | **HISTORICAL** / **REPLAY** | Preserved from CSV (Normalized to UTC) | File stem name (e.g. `NIFTY50_5MIN`) | Disk I/O limited | None (Fails cleanly if missing) | **Usable** for offline benchmark datasets |
| **ReplayDataProvider** | In-memory synthetic generator | NumPy Geometric Brownian / Ornstein-Uhlenbeck | None | **SYNTHETIC** / **REPLAY** | `UTC` | `SYNTHETIC_IND`, `SYNTHETIC_FX` | None | Fully synthetic | **Usable** for deterministic regime stress testing |

---

## Explicit Data Labels
The system strictly enforces explicit classification labels across log files, database metadata, and UI widgets:
* `REAL`: Verified live exchange feed (requires commercial feed key).
* `HISTORICAL`: Genuine past exchange OHLCV data.
* `DELAYED`: Real-time feed delayed by 15+ minutes.
* `SYNTHETIC`: Generated algorithmic price series (Brownian Motion/OU process).
* `REPLAY`: Sequential bar-by-bar step replay for strategy validation.
* `DEMO`: Mock placeholder data.

---

## Market Data Quality Verification Protocol
All market data converted into internal `MarketData` containers undergoes strictly mandated validation:
1. **Timestamp Normalization**: Datetime format standardization with UTC conversion and duplicate bar detection.
2. **OHLC Relationship Validation**: Enforces `high >= max(open, close)` and `low <= min(open, close)`.
3. **Numeric Type Validation**: Price values must be strictly positive floats (`price > 0`). Volume must be non-negative (`volume >= 0`).
4. **Chronological Ordering**: Enforces strict ascending timestamp sequence.
5. **Data Gap Detection**: Identifies excessive missing bars without silent synthetic interpolation.
