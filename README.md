# AI Quantitative Research & Local Paper-Trading System

A local-first, provider-agnostic AI quantitative research and paper-trading platform designed for **Indian Stock/Index Markets (NSE/BSE)** and **Forex Pairs**.

---

## 🛑 NON-NEGOTIABLE SAFETY GUARANTEE
- **PAPER-TRADING ONLY**: This platform operates strictly with simulated virtual capital, simulated order fills, transaction fees, and slippage.
- **NO REAL BROKER EXECUTION**: The system does NOT contain any real broker order placement APIs (`place_order()`, `modify_order()`, `cancel_order()`, etc.).
- **DETERMINISTIC METRICS**: All backtesting returns, Sharpe ratios, and drawdowns are calculated using pure Python math—never delegated to LLM hallucination.

---

## 🏛️ System Architecture

```
[ Market Data Adapters ]  -->  [ Data Split Engine (Dev / Val / Holdout) ]
(Indian NSE, Forex, Replay)             │
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

## ⚡ Quick Start

### 1. Prerequisites
- **Python 3.10+**
- *(Optional)* **Ollama** installed locally for fully offline AI generation (`qwen2.5:7b` recommended).

### 2. Installation
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

### 3. Running the System

#### A. Launch Interactive Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`.

#### B. Run Automated Research Loop via Python CLI
```python
from app.services.experiment_runner import ExperimentRunner
from app.data.indian_provider import IndianMarketDataProvider

runner = ExperimentRunner(data_provider=IndianMarketDataProvider())
results = runner.run_experiments(symbol="RELIANCE.NS", max_experiments=5)
```

#### C. Execute Test Suite
```bash
pytest
```

---

## 🤖 Ollama & LLM Configuration

The system uses a provider-agnostic LLM router:
- **Primary**: Local [Ollama](https://ollama.ai) (`qwen2.5:7b` or `llama3.2`).
- **Fallback**: Automatic fallback to structured mock/rule provider if Ollama is offline.

To start Ollama with Qwen 2.5:
```bash
ollama run qwen2.5:7b
```

To configure environment variables, create a `.env` file:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

---

## 📚 Documentation Suite

Detailed architecture guides are available in the `docs/` folder:
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Core component design & AI workflow
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — Market data adapters & split engine
- [`docs/AI_MODELS.md`](docs/AI_MODELS.md) — LLM provider abstraction & Pydantic JSON schemas
- [`docs/PAPER_TRADING.md`](docs/PAPER_TRADING.md) — Paper execution engine & safety constraints
- [`docs/EXPERIMENT_LOOP.md`](docs/EXPERIMENT_LOOP.md) — Bounded experiment loop & memory persistence
- [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) — Completed task roadmap

---

## 📜 License
MIT License