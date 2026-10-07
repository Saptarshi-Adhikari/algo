# Phase 14 — Laya Target Policy Specification

## Target Policy Overview (`ALGO_LAYA_TARGET_POLICY_V1`)
Laya fine-tuning targets are derived strictly from objective, deterministic execution and outcome rules. Qwen, Laya, human intuition, or un-audited manual annotations are **never** used to label targets.

### 1. Raw Direction Target (`raw_direction`)
- `BUY`: Realized forward return $\ge +0.5\%$
- `SELL`: Realized forward return $\le -0.5\%$
- `HOLD`: Realized forward return between $-0.5\%$ and $+0.5\%$

### 2. Net Executable Direction Target (`direction_v2`)
Considers Phase 12 realistic execution costs, commission, and spread friction (estimated 0.10% total friction baseline):
- `BUY`: Net forward return $\ge +0.40\%$
- `SELL`: Net forward return $\le -0.60\%$
- `HOLD`: Sub-cost expected return

### 3. Objective Risk Target (`risk_level_v2`)
Derived from 20-day trailing volatility and RSI extremes:
- `HIGH`: Volatility $\ge 3.5\%$ or RSI $> 80$ / RSI $< 20$
- `MEDIUM`: Volatility $\ge 2.0\%$
- `LOW`: Volatility $< 2.0\%$

### 4. Trade Permission Target (`trade_permission_v2`)
- `ALLOW`: Net Direction $\neq \text{HOLD}$ and Risk Level $\neq \text{HIGH}$
- `REJECT`: High risk or sub-cost return expectation

---

## Soft Target Distribution Policy (`ALGO_LAYA_TARGET_DISTRIBUTION_V1`)
Converts continuous returns and volatility metrics into continuous softmax probability distributions $[p_{\text{buy}}, p_{\text{sell}}, p_{\text{hold}}]$ summing strictly to $1.000000$. Soft targets allow training Laya via RLCD (Reinforcement Learning from Categorical Distributions).
