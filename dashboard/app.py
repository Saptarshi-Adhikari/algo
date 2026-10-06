"""Local Interactive Streamlit Dashboard for AI Quantitative Research and Paper Trading."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys

# Ensure root package is on path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import settings
from app.config.safety import assert_paper_trading_only
from app.memory.repository import ExperimentRepository
from app.paper_trading.portfolio import PaperPortfolio
from app.data.indian_provider import IndianMarketDataProvider
from app.data.forex_provider import ForexDataProvider
from app.data.replay_provider import ReplayDataProvider
from app.services.experiment_runner import ExperimentRunner

st.set_page_config(
    page_title="AI Quant Research & Paper Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "portfolio" not in st.session_state:
    st.session_state.portfolio = PaperPortfolio(initial_cash=settings.DEFAULT_INITIAL_CASH)

if "repo" not in st.session_state:
    st.session_state.repo = ExperimentRepository()

repo = st.session_state.repo
portfolio = st.session_state.portfolio

# Sidebar Settings
st.sidebar.title("🤖 Quant AI Dashboard")
st.sidebar.markdown("**Local-First Paper Trading Engine**")

data_mode = st.sidebar.selectbox(
    "Data Mode",
    ["HISTORICAL", "LIVE_PAPER", "REPLAY", "DEMO"],
    index=0
)

market_type = st.sidebar.selectbox(
    "Market",
    ["INDIAN_EQUITY", "FOREX"],
    index=0
)

symbols_list = (
    ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "TATAMOTORS.NS", "^NSEI"]
    if market_type == "INDIAN_EQUITY"
    else ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDINR=X"]
)

selected_symbol = st.sidebar.selectbox("Symbol / Instrument", symbols_list, index=0)
timeframe = st.sidebar.selectbox("Timeframe", ["1d", "1h", "15m"], index=0)

st.sidebar.markdown("---")
st.sidebar.success("🛡️ **PAPER TRADING ONLY**\nNo real money execution path.")

# Main Interface Tabs
tab_overview, tab_runner, tab_experiments, tab_lineage = st.tabs([
    "📊 Portfolio & Status",
    "🚀 Run AI Experiment Loop",
    "📚 Experiment Memory",
    "🧬 Strategy Version Lineage"
])

# --- TAB 1: PORTFOLIO & STATUS ---
with tab_overview:
    st.header("Simulated Paper Portfolio Overview")

    col1, col2, col3, col4 = st.columns(4)
    state = portfolio.update_market_prices({})

    col1.metric("Virtual Cash", f"₹/${state.virtual_cash:,.2f}")
    col2.metric("Total Equity", f"₹/${state.total_equity:,.2f}")
    col3.metric("Realized P&L", f"₹/${state.realized_pnl:,.2f}", delta=f"{state.realized_pnl:.2f}")
    col4.metric("Max Drawdown", f"{state.drawdown_pct:.2f}%")

    st.subheader("Open Paper Positions")
    if not state.open_positions:
        st.info("No open paper positions currently.")
    else:
        pos_df = pd.DataFrame([p.model_dump() for p in state.open_positions])
        st.dataframe(pos_df, use_container_width=True)

    st.subheader("Completed Trade History")
    if not state.closed_trades:
        st.info("No completed trades recorded in paper trading session yet.")
    else:
        trades_df = pd.DataFrame([t.model_dump() for t in state.closed_trades])
        st.dataframe(trades_df, use_container_width=True)

# --- TAB 2: RUN AI EXPERIMENT LOOP ---
with tab_runner:
    st.header("Autonomous AI Strategy Research Loop")
    st.markdown("Launch bounded iterative AI quantitative research cycles.")

    max_exps = st.slider("Max Experiments per Run", min_value=1, max_value=10, value=3)

    if st.button("▶ Start Bounded Research Loop", type="primary"):
        with st.spinner(f"Running {max_exps} AI research iterations for {selected_symbol}..."):
            provider = (
                ReplayDataProvider(regime="TRENDING") if data_mode in ["REPLAY", "DEMO"]
                else (IndianMarketDataProvider() if market_type == "INDIAN_EQUITY" else ForexDataProvider())
            )
            runner = ExperimentRunner(repository=repo, data_provider=provider)

            try:
                results = runner.run_experiments(
                    symbol=selected_symbol,
                    market=market_type,
                    timeframe=timeframe,
                    max_experiments=max_exps
                )
                st.success(f"Successfully completed {len(results)} experiments!")

                for res in results:
                    with st.expander(f"Iter {res.experiment_id} — Verdict: {res.critic_verdict} (Sharpe: {res.metrics.sharpe_ratio:.2f})"):
                        st.write(f"**Hypothesis:** {res.hypothesis}")
                        st.write(f"**Critic Reasoning:** {res.critic_reasoning}")
                        st.write(f"**Lesson Learned:** {res.lesson_learned}")
            except Exception as e:
                st.error(f"Experiment Loop Error: {e}")

# --- TAB 3: EXPERIMENT MEMORY ---
with tab_experiments:
    st.header("Persistent Experiment Records")
    all_exps = repo.get_all_experiments()

    if not all_exps:
        st.info("No experiments persisted in database memory yet. Run an experiment loop to populate memory!")
    else:
        exp_data = []
        for e in all_exps:
            exp_data.append({
                "ID": e.experiment_id,
                "Version": e.strategy_version,
                "Symbol": e.symbol,
                "Regime": e.market_regime,
                "Verdict": e.critic_verdict,
                "Sharpe Ratio": e.metrics.sharpe_ratio,
                "Total Return %": e.metrics.total_return_pct,
                "Max DD %": e.metrics.max_drawdown_pct,
                "Trades": e.metrics.trade_count,
                "Split": e.data_split,
                "Timestamp": e.timestamp
            })
        st.dataframe(pd.DataFrame(exp_data), use_container_width=True)

# --- TAB 4: STRATEGY LINEAGE ---
with tab_lineage:
    st.header("Strategy Version Lineage Tree")
    all_exps = repo.get_all_experiments()
    if not all_exps:
        st.info("No strategy version lineage data available yet.")
    else:
        for e in all_exps:
            st.markdown(f"**{e.strategy_version}** (Parent: `{e.parent_experiment_id or 'Root'}`) -> `{e.critic_verdict}` | {e.hypothesis}")
