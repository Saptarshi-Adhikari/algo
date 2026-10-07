# Phase 11: Benchmark Evaluation Framework

## Evaluation Paradigm
The Phase 11 benchmark engine evaluates decision quality across three distinct axes:
1. **Classification Accuracy**: Typed agreement between model predictions and ground-truth directional stance (`BUY`, `SELL`, `HOLD`).
2. **Risk & Trade Permission**: Accuracy in identifying high-risk adverse excursion regimes (`MAE > 2.0%`).
3. **Data Split Integrity**: Chronological distribution across Development, Validation, and Holdout sets.

## Baseline Benchmark Results (943 Decision Records)

| Metric | Result |
|---|---|
| **Total Decision Records** | 943 |
| **Development (Train)** | 655 (69.5%) |
| **Validation** | 149 (15.8%) |
| **Holdout (Protected)** | 139 (14.7%) |
| **Class Distribution** | BUY: 397 (42.1%), SELL: 388 (41.1%), HOLD: 158 (16.8%) |
| **Future Leakage Count** | 0 |
| **Duplicate Records** | 0 |
| **Invalid Labels** | 0 |
