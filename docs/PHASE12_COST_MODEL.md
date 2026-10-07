# Phase 12: Friction & Cost Model Specification

## Provenance & Configuration
Costs in QuantAI-PaperTrader are fully versioned and configurable per asset class to ensure historical experiment reproducibility:

| Asset Class | Default Commission (bps) | Spread Proxy (bps) | Default Slippage (bps) | Cost Model ID |
|---|---|---|---|---|
| **INDIAN_EQUITY** | 3.0 bps | 2.0 bps | 1.0 bps | `COST_V1_INDIAN_EQUITY` |
| **INDIAN_INDEX** | 2.0 bps | 1.0 bps | 0.5 bps | `COST_V1_INDIAN_INDEX` |
| **FOREX** | 0.5 bps | 1.5 bps | 0.5 bps | `COST_V1_FOREX` |
| **CRYPTO** | 10.0 bps | 5.0 bps | 2.0 bps | `COST_V1_CRYPTO` |
| **GOLD** | 3.0 bps | 3.0 bps | 1.0 bps | `COST_V1_GOLD` |

## Calculation Formula
$$\text{Fill Price}_{\text{Buy}} = \text{Raw Price} \times \left(1 + \frac{\text{Spread}_{\text{half}} + \text{Slippage}}{10000}\right)$$
$$\text{Fill Price}_{\text{Sell}} = \text{Raw Price} \times \left(1 - \frac{\text{Spread}_{\text{half}} + \text{Slippage}}{10000}\right)$$
$$\text{Total Fee} = \max\left(\text{Gross Value} \times \frac{\text{Commission}_{\text{bps}} + \text{Tax}_{\text{bps}}}{10000}, \text{Minimum Charge}\right)$$
