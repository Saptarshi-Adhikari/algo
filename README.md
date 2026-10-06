# AI Quantitative Research & Local Paper-Trading System

A local-first, provider-agnostic AI quantitative research and paper-trading platform designed for **Indian Stock/Index Markets (NSE/BSE)** and **Forex Pairs**.

---

## 🛑 NON-NEGOTIABLE SAFETY GUARANTEE
- **PAPER-TRADING ONLY**: This platform operates strictly with simulated virtual capital, simulated order fills, transaction fees, and slippage.
- **NO REAL BROKER EXECUTION**: The system does NOT contain any real broker order placement APIs (`place_order()`, `modify_order()`, `cancel_order()`, etc.).
- **DETERMINISTIC METRICS**: All backtesting returns, Sharpe ratios, and drawdowns are calculated using pure Python math—never delegated to LLM hallucination.

---

## 🤖 LLM Router Priority (Local-First Architecture)

```
                       LLM ROUTER
                           │
                           ▼
                 ┌───────────────────┐
                 │  Ollama / Qwen    │  <-- PRIMARY (Local-First)
                 └─────────┬─────────┘
                           │ failure / unavailable
                           ▼
                 ┌───────────────────┐
                 │    Gemini API     │  <-- SECONDARY (Optional, if key set in .env)
                 └─────────┬─────────┘
                           │ failure / unavailable
                           ▼
                 ┌───────────────────┐
                 │   OpenRouter API  │  <-- TERTIARY (Optional, if key set in .env)
                 └─────────┬─────────┘
                           │ failure / unavailable
                           ▼
                 ┌───────────────────┐
                 │   Mock Provider   │  <-- FINAL SAFE FALLBACK
                 └───────────────────┘
```

The application is **100% functional locally** using Ollama alone without requiring any cloud API key or paid subscription.

---

## 🔒 Security & Environment Rules

- **API Keys**: Place your private credentials in `.env` (never committed).
- **`.env.example`**: Contains only empty placeholders (`GEMINI_API_KEY=`, `OPENROUTER_API_KEY=`).
- **`.gitignore`**: Strictly ignores `.env` and `.env.*` to prevent credential exposure.
- **Rotation Note**: Any previously exposed key should be immediately rotated/revoked.

---

## ⚡ Quick Start

### 1. Installation
Clone the repository and set up a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Local Environment Configuration
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

To use optional Gemini or OpenRouter fallback, populate `GEMINI_API_KEY` or `OPENROUTER_API_KEY` inside `.env`.

### 3. Running the System

#### Launch Interactive Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`.

#### Execute Test Suite
```bash
pytest -v
```

---

## 📚 Documentation Suite

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Core component design & AI workflow
- [`docs/AI_MODELS.md`](docs/AI_MODELS.md) — LLM provider abstraction, 4-tier fallback router & Pydantic JSON schemas
- [`docs/PAPER_TRADING.md`](docs/PAPER_TRADING.md) — Paper execution engine & safety constraints
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — Market data adapters & split engine
- [`docs/EXPERIMENT_LOOP.md`](docs/EXPERIMENT_LOOP.md) — Bounded experiment loop & memory persistence
- [`docs/LLM_PROVIDER_VERIFICATION.md`](docs/LLM_PROVIDER_VERIFICATION.md) — LLM router verification report

---

## 📜 License
MIT License