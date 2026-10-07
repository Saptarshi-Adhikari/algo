# Phase 16 — Laya Shadow Validation Architecture

## Overview
Model `ALGO_LAYA_V001` remains frozen and locked to `SHADOW_ONLY`. All inferences are logged and evaluated against delayed actual outcomes without trading execution.

## Delayed Outcome Resolution
- Predictions are generated at bar timestamp $T$.
- Outcomes resolve at horizon $T+k$.
- Ground truth directions, raw returns, and net returns (via Phase 12 cost models) are attached asynchronously.
