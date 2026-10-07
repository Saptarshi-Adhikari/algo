# Phase 17 — LightGBM Target Policy (`LIGHTGBM_TARGET_POLICY_V1`)

## Target Specification
- **Target Name**: `target_return_4bar`
- **Horizon**: 4 bars forward ($t+4$)
- **Formula**: $\text{target}[t] = \frac{\text{close}[t+4]}{\text{close}[t]} - 1$
- **Tail Unresolvable Rows**: Unresolvable tail rows where $t+4 > N$ are cleanly excluded from training.
- **Immutability**: Target definition is versioned and immutable for this experiment.
