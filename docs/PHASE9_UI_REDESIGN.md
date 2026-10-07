# Phase 9: UI Redesign & Serious Research Platform Architecture

## Overview
Phase 9 redesigns the local web dashboard for **QuantAI-PaperTrader**, elevating it from a developer debug interface into an institutional-grade quantitative research and paper-trading workspace.

## Dashboard Architecture & Page Structure
The dashboard is modularized into discrete page handlers within `dashboard/app.py`:

1. **📊 Executive Overview**:
   - High-level KPIs: Active Market, Symbol, Strategy Version, Sharpe Ratio, Max Drawdown, Sample Warning Badge, Paper Portfolio Equity.
   - Interactive Plotly equity curves and asset performance comparison charts.

2. **📈 Markets & Universe**:
   - Multi-asset class explorer supporting Indian Equities, Indian Indices, Forex, Crypto, and Gold.
   - Live historical price charts with timeframe selector and provider limitation notes.

3. **🧪 Experiments & Iteration Memory**:
   - Tabular and detailed view of all SQLite-persisted experiments.
   - Parameter diffs, hypothesis lineage, dataset hashes, and Critic verdicts.

4. **⚡ Strategies & Versioning**:
   - Active strategy specification inspector, indicator parameter displays, entry/exit rules, and version lineage tree.

5. **💼 Paper Trading Portfolio**:
   - Real-time simulated portfolio balance, unrealized P&L, position tables, trade logs, and safety indicator (`PAPER_TRADING_ONLY=True`).

6. **🧠 AI Brain**:
   - Evidence-grounded synthesis of system learnings citing specific experiment IDs and asset classes.

7. **📁 Data & Datasets**:
   - Full registry view (`ResearchDatasetRegistry.list_all()`) displaying dataset ID, SHA-256 hash, symbol, asset class, timeframe, span days, total bars, and quality status.

8. **🛡️ System / Safety**:
   - Infrastructure status, active LLM provider chain status (`LLMRouter.get_status()`), safety constraint audit (`ALLOW_REAL_BROKER=False`), and secret protection verification.

## Safety & Presentation Rules
- No secrets or raw API key strings are ever rendered.
- Zero-trade strategies are styled with dedicated `NO_TRADES` badges.
- Provider fallback status (e.g. synthetic fallback or limited Forex depth) is explicitly communicated.
