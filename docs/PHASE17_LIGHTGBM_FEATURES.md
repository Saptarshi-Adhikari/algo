# Phase 17 — LightGBM Feature Schema (`LIGHTGBM_FEATURE_SCHEMA_V1`)

## Feature Definitions (All computed strictly <= t)
1. **Price Returns**: `return_1`, `return_2`, `return_4`, `return_8`, `return_16`
2. **Moving Averages**: `sma_5`, `sma_10`, `sma_20`, `sma_50`
3. **Relative Positions**: `close_vs_sma_10`, `close_vs_sma_20`, `close_vs_sma_50`
4. **Volatility Indicators**: `rolling_std_5`, `rolling_std_10`, `rolling_std_20`, `atr_14`
5. **Momentum & Trend**: `rsi_14`, `momentum_5`, `momentum_10`, `ema_12`, `ema_26`, `macd`, `macd_signal`
6. **Volume Indicators**: `volume_change`, `volume_sma_ratio`

## Look-Ahead Leakage Safeguards
All indicators use backward-looking rolling windows (`rolling()`, `pct_change()`, `ewm()`).
`FutureDataReferenceValidator` verifies no negative shifts or future timestamps exist in feature vectors.
