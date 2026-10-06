# Implementation Plan: Local AI Quantitative Research & Paper-Trading System

This document outlines the systematic task breakdown for building a local-first, provider-agnostic, paper-trading-only AI quantitative research platform for Indian equity markets and Forex pairs.

---

## Architecture Overview

```
[ Market Data Adapters ]  -->  [ Data Split Engine (Dev / Val / Holdout) ]
(Indian, Forex, Replay)                 │
                                        ▼
[ Local LLM Layer ]       -->  [ Core AI Agents ]
(Ollama / Gemini / Fallback)   (Researcher, Builder, Reviewer, Critic, Next-Exp)
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

## Core Safety Constraints
- **PAPER-TRADING ONLY**: Pure simulation with virtual cash, simulated execution, fees, and slippage.
- **NO BROKER EXECUTION PATH**: No real order placement APIs (`place_order`, `cancel_order`, etc.) exist anywhere in the codebase.
- **LOCAL FIRST**: Operates locally with SQLite storage, Streamlit UI, and local LLM (Ollama) support with zero paid cloud requirement.
- **DETERMINISTIC COMPUTE**: Backtesting and metrics calculations are pure Python math, never delegated to LLM hallucination.

---

## Tasks Breakdown

### Task 01: Repository Audit, Project Structure & Baseline Environment Setup
- **Objective**: Establish project file hierarchy, virtual environment instructions, `requirements.txt`, `pyproject.toml`, and basic directory structure.
- **Files**: `requirements.txt`, `pyproject.toml`, `app/__init__.py`, `tests/conftest.py`
- **Acceptance Criteria**: All initial dependencies installed cleanly; pytest discovers test suite.

### Task 02: System Configuration, Logging & Absolute Execution Safety Guards
- **Objective**: Implement central settings using Pydantic Settings, environment variable loaders, structured logging, and safety assertion module preventing broker connections.
- **Files**: `app/config/settings.py`, `app/config/logging.py`, `app/config/safety.py`, `tests/test_safety.py`
- **Acceptance Criteria**: Safety module strictly blocks any broker execution attempts; settings validate configuration.

### Task 03: Core Domain Models & Schemas
- **Objective**: Define Pydantic models for Market Data, Strategy Specs, Trades, Backtest Metrics, Critic Verdicts, Experiments, and Portfolio State.
- **Files**: `app/domain/schemas.py`, `tests/test_schemas.py`
- **Acceptance Criteria**: Strict validation of strategy JSON, experiment records, and metrics; serialization/deserialization tests pass.

### Task 04: SQLite Experiment Memory & Storage Repository
- **Objective**: Build SQLite storage manager with schema creation and queries for filtering by regime, success, failures, lineage, and similarity.
- **Files**: `app/memory/sqlite_db.py`, `app/memory/repository.py`, `tests/test_memory.py`
- **Acceptance Criteria**: Experiment records safely inserted, retrieved, updated, and queried; zero missing loss history.

### Task 05: Market Data Abstraction & Data Split Engine
- **Objective**: Implement `BaseDataProvider` interface, `MarketData` container, and `DataSplitter` enforcing strict DEV (60%), VALIDATION (20%), and HOLDOUT (20%) boundaries.
- **Files**: `app/data/base_provider.py`, `app/data/splitter.py`, `tests/test_splitter.py`
- **Acceptance Criteria**: Holdout set is strictly protected from strategy optimization; splits are verified non-overlapping.

### Task 06: Data Adapters (Indian Markets, Forex, CSV, & Replay Engine)
- **Objective**: Create data adapters for Indian stock/index data, Forex currency pairs, local CSV/Parquet import, and a synthetic Replay/Demo provider.
- **Files**: `app/data/indian_provider.py`, `app/data/forex_provider.py`, `app/data/csv_provider.py`, `app/data/replay_provider.py`, `tests/test_data_providers.py`
- **Acceptance Criteria**: Data fetched or generated cleanly for NSE/BSE symbols (e.g., `RELIANCE.NS`, `NIFTY50`) and Forex (e.g., `EURUSD=X`), formatted into standardized OHLCV DataFrames.

### Task 07: Deterministic Strategy Representation & Rule Evaluator Engine
- **Objective**: Create pure Python strategy definition interpreter evaluating indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR) and generating entry/exit signals.
- **Files**: `app/strategies/indicators.py`, `app/strategies/evaluator.py`, `tests/test_strategy_evaluator.py`
- **Acceptance Criteria**: Deterministic signal generation from structured JSON strategy definitions without look-ahead bias.

### Task 08: Pure Deterministic Backtesting Engine & Metrics Calculator
- **Objective**: Implement event-driven/vectorized Python backtester accounting for position sizing, transaction fees, slippage, stop loss, and take profit. Calculate return, Sharpe ratio, drawdown, win rate, profit factor, etc.
- **Files**: `app/backtesting/engine.py`, `app/backtesting/metrics.py`, `tests/test_backtesting.py`
- **Acceptance Criteria**: Backtest engine calculates realistic metrics; verified against edge cases (no trades, 100% loss, fee impacts).

### Task 09: Market Regime Classifier
- **Objective**: Build regime classification engine detecting `TRENDING`, `RANGING`, `HIGH_VOLATILITY`, and `LOW_VOLATILITY` regimes using ADX, ATR, and moving average slope.
- **Files**: `app/evaluation/regime.py`, `tests/test_regime.py`
- **Acceptance Criteria**: Market regimes accurately identified per bar/period and attached to backtest evaluation data.

### Task 10: Simulated Paper-Trading Portfolio Engine
- **Objective**: Build a simulated portfolio manager tracking virtual cash, open/closed positions, unrealized/realized P&L, equity curve, drawdown, and transaction history.
- **Files**: `app/paper_trading/portfolio.py`, `app/paper_trading/engine.py`, `tests/test_paper_trading.py`
- **Acceptance Criteria**: Complete separation from live brokers; virtual order execution with realistic simulated fill prices, fees, and slippage.

### Task 11: LLM Provider Abstraction Layer
- **Objective**: Build provider-agnostic LLM interface supporting Ollama (primary local), Gemini API, OpenRouter, and custom OpenAI-compatible endpoints with fallback, retries, JSON mode, and schema parsing.
- **Files**: `app/llm/base.py`, `app/llm/ollama_provider.py`, `app/llm/gemini_provider.py`, `app/llm/router.py`, `tests/test_llm.py`
- **Acceptance Criteria**: Seamless switching between local Ollama and cloud fallbacks; resilient output formatting and JSON parsing error handling.

### Task 12: AI Agents — Researcher & Strategy Builder
- **Objective**: Implement Researcher Agent (queries memory, proposes single structured hypothesis citing experiment IDs) and Strategy Builder Agent (translates hypothesis into executable strategy JSON schema).
- **Files**: `app/agents/researcher.py`, `app/agents/builder.py`, `tests/test_researcher_builder.py`
- **Acceptance Criteria**: Researcher uses past failures to formulate distinct hypotheses; Builder produces strictly valid Pydantic strategy specs.

### Task 13: AI Agents — Backtest Reviewer, Critic, Memory Agent, & Next-Experiment Agent
- **Objective**: Implement Reviewer (summarizes results), Critic (audits for overfitting, look-ahead bias, low trade count, issue REJECT/RETEST/KEEP verdict), Memory Agent (formats lessons), and Next-Experiment Agent (determines lineage direction).
- **Files**: `app/agents/reviewer.py`, `app/agents/critic.py`, `app/agents/memory_agent.py`, `app/agents/next_experiment.py`, `tests/test_eval_agents.py`
- **Acceptance Criteria**: Critic correctly flags overfitted or low-trade strategies; Memory Agent records losing strategies without bias.

### Task 14: Automated Bounded Experiment Loop Engine
- **Objective**: Build loop orchestrator executing bounded research iterations (max N, default 10): Memory -> Hypothesis -> Build -> Backtest -> Validation -> Critique -> Persist -> Next Exp.
- **Files**: `app/services/experiment_runner.py`, `tests/test_experiment_runner.py`
- **Acceptance Criteria**: Loop runs autonomously up to max iterations, halts cleanly, records all outputs, and permits manual step-by-step or batch runs.

### Task 15: Strategy Lineage & Version Control Manager
- **Objective**: Track parent-child strategy relationships (V1 -> V2 -> V3), maintain version tree, support version rollback, and record rejected variants.
- **Files**: `app/strategies/versioning.py`, `tests/test_versioning.py`
- **Acceptance Criteria**: Complete tree history preserved; rollback function resets active candidate to prior parent version.

### Task 16: Local Streamlit Dashboard Implementation
- **Objective**: Build interactive local dashboard displaying System Status, Data Mode, Paper Portfolio, Cash/Equity/P&L, Active Positions, Trade History, Experiments, Strategy Tree, Critic Verdicts, Metrics, and AI Activity Logs.
- **Files**: `dashboard/app.py`, `dashboard/components/portfolio_view.py`, `dashboard/components/experiment_view.py`, `dashboard/components/agent_logs.py`, `tests/test_dashboard.py`
- **Acceptance Criteria**: Dashboard runs cleanly with `streamlit run dashboard/app.py`, updates dynamically, renders responsive charts, and allows starting experiment loops.

### Task 17: Safety Audit & E2E System Integration Verification
- **Objective**: Run comprehensive integration test suite validating end-to-end flow: data ingestion -> AI generation -> backtesting -> validation -> critique -> paper execution simulation -> database persistence. Assert no real broker code exists.
- **Files**: `tests/test_e2e_integration.py`, `tests/test_broker_safety_audit.py`
- **Acceptance Criteria**: All unit, integration, and safety tests pass cleanly (100% pass rate).

### Task 18: Project Documentation Suite & Final Hardening
- **Objective**: Compile final documentation set: `README.md`, `docs/ARCHITECTURE.md`, `docs/DATA_SOURCES.md`, `docs/AI_MODELS.md`, `docs/PAPER_TRADING.md`, `docs/EXPERIMENT_LOOP.md`.
- **Files**: `README.md`, `docs/*.md`
- **Acceptance Criteria**: Complete user guides, step-by-step setup for Ollama, data providers, paper trading, and CLI execution.
