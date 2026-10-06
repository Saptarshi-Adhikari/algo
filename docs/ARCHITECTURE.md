# System Architecture

## Overview

This AI Quantitative Research Platform provides an end-to-end, local-first research environment designed specifically for Indian Equity markets (NSE/BSE) and Forex currency pairs.

```
[ Market Data Adapters ]  -->  [ Data Split Engine (Dev / Val / Holdout) ]
(Indian, Forex, Replay)                 │
                                        ▼
[ 4-Tier Local LLM Router ] --> [ Core AI Agents ]
(Ollama -> Gemini -> OR -> Mock) (Researcher, Builder, Reviewer, Critic, Next-Exp)
                                        │
                                        ▼
                               [ Deterministic Backtester ]
                                        │
                                        ▼
                               [ Regime Classifier & Metrics Engine ]
                                        │
                                        ▼
                               [ Paper Portfolio Engine ]
                                        │
                                        ▼
                               [ SQLite Memory & Version Lineage ]
                                        │
                                        ▼
                               [ Local Streamlit Dashboard ]
```

---

## LLM Layer Integration

The LLM abstraction uses a local-first priority chain:
1. **Ollama (Primary Local)**: Communicates with local Ollama (`qwen2.5:7b`). Zero paid cloud dependency.
2. **Gemini API (Secondary Optional)**: Used only if configured in local `.env` and Ollama is unreachable.
3. **OpenRouter API (Tertiary Optional)**: Used only if configured in local `.env` and prior providers fail.
4. **Mock Provider (Final Safe Fallback)**: Offline deterministic fallback guaranteeing zero system crashes.

---

## Core Logical Agents

1. **Researcher Agent (`app/agents/researcher.py`)**
   - Queries historical SQLite memory for past wins and failures.
   - Proposes exactly ONE new hypothesis (`HypothesisSpec`), citing past experiment IDs.

2. **Strategy Builder Agent (`app/agents/builder.py`)**
   - Converts qualitative research hypotheses into deterministic trading rules (`StrategySpec`).

3. **Deterministic Backtester (`app/backtesting/engine.py`)**
   - Non-LLM pure Python math engine executing bar-by-bar backtests with stop loss, take profit, fees, and slippage.

4. **Backtest Reviewer Agent (`app/agents/reviewer.py`)**
   - Summarizes calculated quantitative metrics without inventing figures.

5. **Critic Agent (`app/agents/critic.py`)**
   - Adversarial audit agent evaluating backtest evidence for overfitting, look-ahead bias, low trade count (< 10 trades), and severe drawdowns. Issues `REJECT`, `RETEST`, or `KEEP_FOR_PAPER_TESTING`.

6. **Memory Agent (`app/agents/memory_agent.py`)**
   - Persists full unedited experiment records and lessons into SQLite database.

7. **Next-Experiment Agent (`app/agents/next_experiment.py`)**
   - Determines lineage direction (`NEW_HYPOTHESIS`, `RETEST_VARIATION`, `ROLLBACK_PARENT`).
