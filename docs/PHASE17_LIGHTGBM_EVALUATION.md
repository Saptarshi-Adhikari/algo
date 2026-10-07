# Phase 17 — LightGBM Evaluation & Baseline Benchmarks

## Evaluation Metrics
1. **RMSE**: Root Mean Squared Error against 4-bar forward returns.
2. **MAE**: Mean Absolute Error.
3. **$R^2$ Score**: Coefficient of determination.
4. **Directional Accuracy**: Proportion of correct return sign predictions ($\text{sign}(\hat{y}) == \text{sign}(y)$).
5. **Correlation**: Pearson correlation coefficient.

## Benchmark Models
- **`ZERO_RETURN`**: Predicts $\hat{y} = 0$.
- **`HISTORICAL_MEAN`**: Predicts $\hat{y} = \text{mean}(y_{\text{train}})$.
- **`ALGO_LGBM_V001`**: LightGBM Regressor ($n=300, \text{lr}=0.03$).
