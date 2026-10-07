"""QuantAI-PaperTrader: Professional Quantitative Research & Paper Trading Dashboard.

Phase 9 redesign: multi-page information architecture with 8 dedicated pages.
Local-first, paper-trading only, no broker execution.

Architecture:
    - This file is the Streamlit entry point.
    - All pages are implemented as functions imported from dashboard/pages/.
    - Business logic is NOT duplicated here — it delegates to existing services.
"""
import streamlit as st
from pathlib import Path
import json
import sys

# Ensure root package is on path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import settings
from app.config.safety import assert_paper_trading_only

# Safety assertion — fail fast if configuration is broken
assert_paper_trading_only()

st.set_page_config(
    page_title="QuantAI PaperTrader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "QuantAI-PaperTrader: Local-first AI quantitative research. Paper trading only."}
)

# --- Global CSS for professional look ---
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0f1117; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    /* Top metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1d2e 0%, #23263a 100%);
        border: 1px solid #2d3154;
        border-radius: 10px;
        padding: 12px 16px;
    }
    [data-testid="metric-container"] label { color: #8892a4 !important; font-size: 0.78rem; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e6eaf4 !important; }

    /* Status badges */
    .badge-paper { background: #1b4332; color: #52b788; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; }
    .badge-no-trades { background: #3d1f00; color: #f4a261; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; }
    .badge-reject { background: #3b0000; color: #e63946; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; }
    .badge-keep { background: #0a3628; color: #2dc653; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; }
    .badge-retest { background: #1a2a4a; color: #74b0ff; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; }
    .badge-limited { background: #2a2000; color: #e9c46a; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; }
    .badge-adequate { background: #003049; color: #48cae4; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; }

    /* Page title */
    h1 { color: #e6eaf4 !important; }
    h2 { color: #c8cfe0 !important; }
    h3 { color: #a8b2c8 !important; border-bottom: 1px solid #2d3154; padding-bottom: 4px; }

    /* Tables */
    [data-testid="stDataFrame"] { border: 1px solid #2d3154; border-radius: 8px; }

    /* Main background */
    .main .block-container { padding-top: 1.5rem; }

    /* Safety banner */
    .safety-banner {
        background: linear-gradient(90deg, #0d2137 0%, #0f2f1a 100%);
        border: 1px solid #1e4d2b;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 12px;
        display: flex;
        gap: 16px;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# SIDEBAR NAVIGATION
# =============================================
st.sidebar.markdown("## 📈 QuantAI PaperTrader")
st.sidebar.markdown("*Local-First AI Research Platform*")
st.sidebar.divider()

# Safety status always visible in sidebar
st.sidebar.markdown("""
<div style='background:#0a1f12;border:1px solid #1e4d2b;border-radius:8px;padding:10px;margin-bottom:12px;'>
  <span style='color:#52b788;font-weight:700;font-size:0.85rem;'>🛡️ PAPER TRADING ONLY</span><br>
  <span style='color:#6b7280;font-size:0.75rem;'>No real orders · No broker · No live keys</span>
</div>
""", unsafe_allow_html=True)

PAGE_LABELS = {
    "📊 Overview": "overview",
    "🌏 Markets": "markets",
    "🧪 Experiments": "experiments",
    "🎯 Strategies": "strategies",
    "💼 Paper Trading": "paper_trading",
    "🧠 AI Brain": "ai_brain",
    "📋 Decision Dataset": "decision_dataset",
    "🤖 Laya Shadow": "laya_shadow",
    "🌲 LightGBM Predictor": "lightgbm_predictor",
    "📂 Data & Datasets": "data",
    "⚙️ System / Safety": "system",
}

selected_label = st.sidebar.radio("Navigation", list(PAGE_LABELS.keys()), index=0)
page = PAGE_LABELS[selected_label]

st.sidebar.divider()
st.sidebar.caption(f"LLM: {settings.OLLAMA_MODEL} (Ollama Primary)")
st.sidebar.caption(f"DB: {settings.DB_PATH.name}")
st.sidebar.caption("v1.3.0 · Phase 13 Laya Shadow")

# =============================================
# SHARED SERVICES (cached)
# =============================================
@st.cache_resource
def get_repo():
    from app.memory.repository import ExperimentRepository
    return ExperimentRepository()

@st.cache_resource
def get_portfolio():
    from app.paper_trading.portfolio import PaperPortfolio
    return PaperPortfolio(initial_cash=settings.DEFAULT_INITIAL_CASH)

repo = get_repo()
portfolio = get_portfolio()

# =============================================
# PAGE: OVERVIEW
# =============================================
def render_overview():
    st.title("📊 Research Overview")
    st.markdown("Real-time summary of the AI research engine and paper portfolio status.")

    # Safety banner
    st.markdown("""
    <div class='safety-banner'>
      <span style='color:#52b788;font-size:1.1rem;'>🛡️</span>
      <div>
        <span style='color:#52b788;font-weight:700;'>PAPER TRADING ONLY</span> &nbsp;|&nbsp;
        <span style='color:#6b7280;'>ALLOW_REAL_BROKER = FALSE</span> &nbsp;|&nbsp;
        <span style='color:#6b7280;'>LOCAL-FIRST · No cloud required</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Portfolio state
    state = portfolio.update_market_prices({})
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Virtual Cash", f"₹{state.virtual_cash:,.2f}")
    c2.metric("📈 Total Equity", f"₹{state.total_equity:,.2f}")
    c3.metric("✅ Realized P&L", f"₹{state.realized_pnl:,.2f}", delta=f"{state.realized_pnl:.2f}")
    c4.metric("📉 Max Drawdown", f"{state.drawdown_pct:.2f}%")
    c5.metric("📋 Open Positions", len(state.open_positions))

    st.divider()

    # Experiment summary
    all_exps = repo.get_all_experiments()
    col_stats, col_recent = st.columns([2, 3])

    with col_stats:
        st.subheader("📊 Experiment Statistics")
        if not all_exps:
            st.info("No experiments recorded yet. Use the Markets page to start research.")
        else:
            total = len(all_exps)
            passed = sum(1 for e in all_exps if e.critic_verdict == "KEEP_FOR_PAPER_TESTING")
            rejected = sum(1 for e in all_exps if e.critic_verdict == "REJECT")
            no_trades = sum(1 for e in all_exps if e.metrics.sample_size_warning == "NO_TRADES")
            limited = sum(1 for e in all_exps if e.metrics.sample_size_warning == "LIMITED_SAMPLE")
            adequate = sum(1 for e in all_exps if e.metrics.sample_size_warning == "ADEQUATE_SAMPLE")

            mc1, mc2 = st.columns(2)
            mc1.metric("Total Experiments", total)
            mc2.metric("Passed to Paper Testing", passed)
            mc1.metric("Rejected", rejected)
            mc2.metric("Zero-Trade (NO_TRADES)", no_trades)

            st.markdown("**Sample Size Distribution:**")
            for label, count, badge_class in [
                ("NO_TRADES", no_trades, "badge-no-trades"),
                ("LIMITED_SAMPLE", limited, "badge-limited"),
                ("ADEQUATE_SAMPLE", adequate, "badge-adequate"),
            ]:
                pct = round(count / total * 100) if total > 0 else 0
                st.markdown(f"<span class='{badge_class}'>{label}</span> → {count} ({pct}%)", unsafe_allow_html=True)

    with col_recent:
        st.subheader("🕐 Recent Experiments")
        if not all_exps:
            st.info("No experiments available.")
        else:
            recent = sorted(all_exps, key=lambda e: e.timestamp, reverse=True)[:5]
            for e in recent:
                sample_w = e.metrics.sample_size_warning or "UNKNOWN"
                verdict = e.critic_verdict

                if sample_w == "NO_TRADES":
                    badge = "badge-no-trades"
                elif verdict == "KEEP_FOR_PAPER_TESTING":
                    badge = "badge-keep"
                elif verdict == "REJECT":
                    badge = "badge-reject"
                else:
                    badge = "badge-retest"

                st.markdown(f"""
                <div style='background:#1a1d2e;border:1px solid #2d3154;border-radius:8px;padding:10px;margin-bottom:8px;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <span style='color:#e6eaf4;font-weight:600;font-size:0.9rem;'>{e.experiment_id}</span>
                    <span class='{badge}'>{verdict}</span>
                  </div>
                  <div style='color:#8892a4;font-size:0.8rem;margin-top:4px;'>
                    {e.symbol} · {e.market} · Sharpe: {e.metrics.sharpe_ratio:.2f} · Trades: {e.metrics.trade_count}
                    <span style='margin-left:8px;' class='badge-{"no-trades" if sample_w=="NO_TRADES" else "limited" if "LIMITED" in sample_w else "adequate"}'>{sample_w}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

# =============================================
# PAGE: MARKETS
# =============================================
def render_markets():
    import plotly.graph_objects as go
    from app.data.universe import UNIVERSE_BY_CLASS, ALL_INSTRUMENTS
    from app.data.provider_factory import get_provider
    from app.data.registry import ResearchDatasetRegistry
    from app.data.quality import DataQualityChecker

    st.title("🌏 Market Universe")
    st.markdown("Browse and select instruments across all supported asset classes. Only instruments with valid provider data are shown as fully available.")

    tabs = st.tabs(["🇮🇳 India (Equity)", "🇮🇳 India (Indices)", "💱 Forex", "₿ Crypto", "🥇 Gold"])
    asset_classes = ["INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"]

    for tab, ac in zip(tabs, asset_classes):
        with tab:
            instruments = UNIVERSE_BY_CLASS.get(ac, [])
            if not instruments:
                st.info("No instruments registered for this asset class.")
                continue

            rows = []
            for inst in instruments:
                notes = inst.notes or "-"
                rows.append({
                    "Symbol": inst.symbol,
                    "Name": inst.display_name,
                    "Currency": inst.currency,
                    "Provider": inst.provider.replace("DataProvider", ""),
                    "Notes": notes,
                })

            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Data inspection for selected symbol
            st.markdown("---")
            st.subheader("🔍 Inspect Instrument Data")
            sym_options = [i.symbol for i in instruments]
            sel_sym = st.selectbox(f"Select symbol to inspect [{ac}]", sym_options, key=f"market_{ac}")

            if st.button(f"Fetch & Validate {sel_sym}", key=f"btn_{ac}"):
                with st.spinner(f"Fetching {sel_sym}..."):
                    try:
                        provider = get_provider(ac, sel_sym)
                        data = provider.fetch_ohlcv(sel_sym)
                        entry = ResearchDatasetRegistry.register(data, provider_name=provider.__class__.__name__)
                        report = DataQualityChecker.inspect(data.df, symbol=sel_sym)

                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Total Bars", report.total_rows)
                        c2.metric("Start Date", str(data.start_date)[:10])
                        c3.metric("End Date", str(data.end_date)[:10])
                        c4.metric("Quality", report.status)

                        calendar_days = (data.end_date - data.start_date).days
                        years = round(calendar_days / 365.25, 2)
                        st.info(f"**Dataset ID:** `{entry.dataset_id}` | **Hash:** `{entry.dataset_hash}` | **Span:** {years} years ({calendar_days} days) | **Provider:** `{entry.provider}`")

                        if report.warnings:
                            for w in report.warnings:
                                st.warning(f"⚠️ {w}")
                        else:
                            st.success("✅ Dataset passed all quality checks.")

                        # Price chart
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=data.df["timestamp"],
                            y=data.df["close"],
                            mode="lines",
                            name="Close Price",
                            line=dict(color="#48cae4", width=1.5)
                        ))
                        fig.update_layout(
                            title=f"{sel_sym} — Close Price",
                            xaxis_title="Date",
                            yaxis_title="Price",
                            paper_bgcolor="#0f1117",
                            plot_bgcolor="#1a1d2e",
                            font=dict(color="#e6eaf4"),
                            height=350,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    except ValueError as ve:
                        st.error(f"⛔ Provider reports data UNAVAILABLE for {sel_sym}: {ve}")
                    except Exception as e:
                        st.error(f"Error fetching {sel_sym}: {e}")

# =============================================
# PAGE: EXPERIMENTS
# =============================================
def render_experiments():
    import pandas as pd

    st.title("🧪 Experiment History")
    st.markdown("Browse all AI research experiments. Filters apply to the experiment browser below.")

    all_exps = repo.get_all_experiments()
    if not all_exps:
        st.info("📭 No experiment records found. Run an AI experiment loop from the Markets or Overview page.")
        return

    # Build dataframe
    rows = []
    for e in all_exps:
        sw = e.metrics.sample_size_warning or "UNKNOWN"
        rows.append({
            "ID": e.experiment_id,
            "Symbol": e.symbol,
            "Asset Class": e.market,
            "Version": e.strategy_version,
            "Regime": e.market_regime,
            "Verdict": e.critic_verdict,
            "Sample": sw,
            "Trades": e.metrics.trade_count,
            "Return %": round(e.metrics.total_return_pct, 2),
            "Sharpe": round(e.metrics.sharpe_ratio, 2),
            "Sortino": round(e.metrics.sortino_ratio or 0, 2),
            "Calmar": round(e.metrics.calmar_ratio or 0, 2),
            "Max DD %": round(e.metrics.max_drawdown_pct, 2),
            "Win Rate": round(e.metrics.win_rate, 3),
            "Profit Factor": round(e.metrics.profit_factor, 2),
            "Timestamp": e.timestamp[:19],
        })
    df = pd.DataFrame(rows)

    # Filters
    with st.expander("🔍 Filters", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        classes = ["All"] + sorted(df["Asset Class"].unique().tolist())
        verdicts = ["All"] + sorted(df["Verdict"].unique().tolist())
        samples = ["All"] + sorted(df["Sample"].unique().tolist())
        symbols = ["All"] + sorted(df["Symbol"].unique().tolist())

        sel_class = fc1.selectbox("Asset Class", classes)
        sel_verdict = fc2.selectbox("Verdict", verdicts)
        sel_sample = fc3.selectbox("Sample Status", samples)
        sel_sym = fc4.selectbox("Symbol", symbols)

    filtered = df.copy()
    if sel_class != "All": filtered = filtered[filtered["Asset Class"] == sel_class]
    if sel_verdict != "All": filtered = filtered[filtered["Verdict"] == sel_verdict]
    if sel_sample != "All": filtered = filtered[filtered["Sample"] == sel_sample]
    if sel_sym != "All": filtered = filtered[filtered["Symbol"] == sel_sym]

    st.markdown(f"**Showing {len(filtered)} of {len(df)} experiments**")

    # Color-coded display
    def color_row(row):
        if row["Sample"] == "NO_TRADES":
            return ["background-color: #1a0e00; color: #f4a261"] * len(row)
        elif row["Verdict"] == "REJECT":
            return ["background-color: #1a0000"] * len(row)
        elif row["Verdict"] == "KEEP_FOR_PAPER_TESTING":
            return ["background-color: #001a0e; color: #52b788"] * len(row)
        return [""] * len(row)

    styled = filtered.style.apply(color_row, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Detail inspector
    st.subheader("🔎 Experiment Detail Inspector")
    sel_exp_id = st.selectbox("Select Experiment ID", ["(none)"] + filtered["ID"].tolist())
    if sel_exp_id != "(none)":
        exp = next((e for e in all_exps if e.experiment_id == sel_exp_id), None)
        if exp:
            sw = exp.metrics.sample_size_warning or "UNKNOWN"
            badge_map = {"NO_TRADES": "badge-no-trades", "INSUFFICIENT_SAMPLE": "badge-no-trades",
                         "LIMITED_SAMPLE": "badge-limited", "ADEQUATE_SAMPLE": "badge-adequate"}
            badge = badge_map.get(sw, "badge-limited")

            st.markdown(f"""
            <div style='background:#1a1d2e;border:1px solid #2d3154;border-radius:10px;padding:16px;'>
              <h4 style='color:#e6eaf4;margin:0 0 12px 0;'>{exp.experiment_id}</h4>
              <div><b style='color:#8892a4;'>Symbol:</b> <span style='color:#e6eaf4;'>{exp.symbol}</span> &nbsp;|&nbsp;
                   <b style='color:#8892a4;'>Market:</b> <span style='color:#e6eaf4;'>{exp.market}</span> &nbsp;|&nbsp;
                   <b style='color:#8892a4;'>Version:</b> <span style='color:#e6eaf4;'>{exp.strategy_version}</span></div>
              <div style='margin-top:8px;'><b style='color:#8892a4;'>Hypothesis:</b> <span style='color:#c8cfe0;'>{exp.hypothesis}</span></div>
              <div style='margin-top:8px;'><b style='color:#8892a4;'>Critic:</b> <span style='color:#c8cfe0;'>{exp.critic_reasoning}</span></div>
              <div style='margin-top:8px;'>
                <span class='badge-{"keep" if exp.critic_verdict=="KEEP_FOR_PAPER_TESTING" else "reject" if exp.critic_verdict=="REJECT" else "retest"}'>{exp.critic_verdict}</span>
                &nbsp;<span class='{badge}'>{sw}</span>
                &nbsp;<span style='color:#6b7280;font-size:0.8rem;'>{exp.timestamp[:19]}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
            mc1.metric("Return %", f"{exp.metrics.total_return_pct:.2f}%")
            mc2.metric("Sharpe", f"{exp.metrics.sharpe_ratio:.2f}")
            mc3.metric("Max DD %", f"{exp.metrics.max_drawdown_pct:.2f}%")
            mc4.metric("Trades", exp.metrics.trade_count)
            mc5.metric("Win Rate", f"{exp.metrics.win_rate:.1%}")

    # Export
    st.markdown("---")
    col_csv, col_json = st.columns(2)
    csv_bytes = filtered.to_csv(index=False).encode()
    json_bytes = filtered.to_json(orient="records", indent=2).encode()
    col_csv.download_button("⬇ Export CSV", csv_bytes, "experiments.csv", "text/csv")
    col_json.download_button("⬇ Export JSON", json_bytes, "experiments.json", "application/json")

# =============================================
# PAGE: STRATEGIES
# =============================================
def render_strategies():
    import pandas as pd

    st.title("🎯 Strategy Browser")
    st.markdown("View all strategy versions, their scope, and research outcomes.")

    all_exps = repo.get_all_experiments()
    if not all_exps:
        st.info("No strategy records yet.")
        return

    # Aggregate strategies by strategy_version
    strat_map = {}
    for e in all_exps:
        key = e.strategy_version
        if key not in strat_map:
            strat_map[key] = {
                "version": key,
                "symbol": e.symbol,
                "asset_class": e.market,
                "hypothesis": e.hypothesis[:80] + "..." if len(e.hypothesis) > 80 else e.hypothesis,
                "experiments": [],
                "verdicts": [],
                "type": "BASELINE" if "BASELINE" in e.strategy_version.upper() else "AI_GENERATED",
            }
        strat_map[key]["experiments"].append(e.experiment_id)
        strat_map[key]["verdicts"].append(e.critic_verdict)

    rows = []
    for k, v in strat_map.items():
        best_verdict = "KEEP_FOR_PAPER_TESTING" if "KEEP_FOR_PAPER_TESTING" in v["verdicts"] else (
            "RETEST" if "RETEST" in v["verdicts"] else "REJECT"
        )
        rows.append({
            "Version": v["version"],
            "Type": v["type"],
            "Symbol": v["symbol"],
            "Asset Class": v["asset_class"],
            "Experiments": len(v["experiments"]),
            "Best Verdict": best_verdict,
            "Hypothesis (preview)": v["hypothesis"],
        })

    df = pd.DataFrame(rows)

    # Tabs by type
    t1, t2 = st.tabs(["All Strategies", "Filter by Type"])
    with t1:
        st.dataframe(df, use_container_width=True, hide_index=True)
    with t2:
        sel_type = st.radio("Strategy Type", ["ALL", "BASELINE", "AI_GENERATED"], horizontal=True)
        filtered = df if sel_type == "ALL" else df[df["Type"] == sel_type]
        st.dataframe(filtered, use_container_width=True, hide_index=True)

    # Legend
    st.markdown("---")
    st.markdown("**Legend:**")
    cols = st.columns(5)
    for col, (label, css) in zip(cols, [
        ("BASELINE", "badge-adequate"), ("AI_GENERATED", "badge-limited"),
        ("KEEP_FOR_PAPER_TESTING", "badge-keep"), ("REJECT", "badge-reject"), ("RETEST", "badge-retest")
    ]):
        col.markdown(f"<span class='{css}'>{label}</span>", unsafe_allow_html=True)

# =============================================
# PAGE: PAPER TRADING
# =============================================
def render_paper_trading():
    st.title("💼 Paper Trading")

    # Safety state — always prominent
    st.markdown("""
    <div style='background:linear-gradient(90deg,#0a1f0f 0%,#0d1f3a 100%);
                border:2px solid #1e4d2b;border-radius:10px;padding:16px;margin-bottom:16px;'>
      <h3 style='color:#52b788;margin:0;'>🛡️ PAPER TRADING ONLY — VIRTUAL EXECUTION</h3>
      <div style='margin-top:6px;color:#6b7280;font-size:0.85rem;'>
        <b>ALLOW_REAL_BROKER = FALSE</b> &nbsp;|&nbsp;
        <b>PAPER_TRADING_ONLY = TRUE</b> &nbsp;|&nbsp;
        All trades simulated with virtual capital only. No real orders sent.
      </div>
    </div>
    """, unsafe_allow_html=True)

    state = portfolio.update_market_prices({})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Virtual Cash", f"₹{state.virtual_cash:,.2f}")
    c2.metric("📊 Total Equity", f"₹{state.total_equity:,.2f}")
    c3.metric("✅ Realized P&L", f"₹{state.realized_pnl:,.2f}", delta=f"{state.realized_pnl:.2f}")
    c4.metric("📉 Drawdown", f"{state.drawdown_pct:.2f}%")

    st.divider()

    col_pos, col_trades = st.columns(2)
    with col_pos:
        st.subheader("🔓 Open Positions")
        if not state.open_positions:
            st.info("No open paper positions.")
        else:
            import pandas as pd
            pos_df = pd.DataFrame([p.model_dump() for p in state.open_positions])
            st.dataframe(pos_df, use_container_width=True, hide_index=True)

    with col_trades:
        st.subheader("📋 Completed Paper Trades")
        if not state.closed_trades:
            st.info("No completed paper trades yet.")
        else:
            import pandas as pd
            trades_df = pd.DataFrame([t.model_dump() for t in state.closed_trades])
            st.dataframe(trades_df, use_container_width=True, hide_index=True)

    # Equity curve
    if state.closed_trades:
        import pandas as pd
        import plotly.graph_objects as go
        trades_data = [t.model_dump() for t in state.closed_trades]
        trades_df = pd.DataFrame(trades_data)
        if "exit_time" in trades_df.columns and "pnl" in trades_df.columns:
            trades_df["exit_time"] = pd.to_datetime(trades_df["exit_time"])
            trades_df = trades_df.sort_values("exit_time")
            trades_df["cumulative_pnl"] = trades_df["pnl"].cumsum()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trades_df["exit_time"],
                y=trades_df["cumulative_pnl"],
                mode="lines+markers",
                name="Cumulative P&L",
                line=dict(color="#52b788", width=2),
                fill="tozeroy",
                fillcolor="rgba(82,183,136,0.15)"
            ))
            fig.update_layout(
                title="Paper Portfolio — Cumulative P&L",
                xaxis_title="Time",
                yaxis_title="Cumulative P&L (₹)",
                paper_bgcolor="#0f1117",
                plot_bgcolor="#1a1d2e",
                font=dict(color="#e6eaf4"),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Run experiment button
    st.divider()
    st.subheader("▶ Run AI Experiment Loop")
    from app.data.universe import UNIVERSE_BY_CLASS
    all_symbols = []
    for cls in ["INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"]:
        all_symbols += [i.symbol for i in UNIVERSE_BY_CLASS.get(cls, [])]

    ec1, ec2, ec3 = st.columns(3)
    run_sym = ec1.selectbox("Symbol", all_symbols)
    run_n = ec2.slider("Max Experiments", 1, 5, 2)
    run_btn = ec3.button("▶ Start Research Loop", type="primary")

    if run_btn:
        from app.data.provider_factory import get_provider_for_symbol
        from app.data.universe import ALL_INSTRUMENTS
        from app.services.experiment_runner import ExperimentRunner

        inst = ALL_INSTRUMENTS.get(run_sym)
        market = inst.asset_class if inst else "INDIAN_EQUITY"

        with st.spinner(f"Running {run_n} experiments for {run_sym}..."):
            try:
                provider = get_provider_for_symbol(run_sym)
                runner = ExperimentRunner(repository=repo, data_provider=provider)
                results = runner.run_experiments(symbol=run_sym, market=market, max_experiments=run_n)
                st.success(f"Completed {len(results)} experiments for {run_sym}.")
                for r in results:
                    sw = r.metrics.sample_size_warning or "UNKNOWN"
                    badge = "badge-no-trades" if sw == "NO_TRADES" else ("badge-keep" if r.critic_verdict == "KEEP_FOR_PAPER_TESTING" else "badge-reject")
                    sw_badge = "no-trades" if sw == "NO_TRADES" else ("limited" if "LIMITED" in sw else "adequate")
                    st.markdown(f"<span class='{badge}'>{r.critic_verdict}</span> {r.experiment_id} · Sharpe: {r.metrics.sharpe_ratio:.2f} · Trades: {r.metrics.trade_count} · <span class='badge-{sw_badge}'>{sw}</span>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Experiment failed: {e}")

# =============================================
# PAGE: AI BRAIN
# =============================================
def render_ai_brain():
    from app.services.ai_brain import AIBrainService

    st.title("🧠 AI Brain")
    st.markdown("Evidence-grounded research conclusions. All observations cite specific experiment IDs and symbols.")

    st.info("⚠️ AI Brain observations reflect past experiment outcomes only. They are not financial advice or investment signals. Evidence scope is always limited to the specific symbol and asset class cited.")

    brain_service = AIBrainService(repository=repo)
    brain_summary = brain_service.generate_learned_summary()

    st.subheader("📌 Evidence-Grounded Observations")
    observations = brain_summary.get("evidence_supported_observations", [])
    if not observations or observations == ["No experiment memory recorded yet."]:
        st.info("No experiment evidence available yet. Run experiments first.")
    else:
        for obs in observations:
            st.success(f"📊 {obs}")

    if brain_summary.get("repeated_failures"):
        st.subheader("⚠️ Repeated Failure Patterns")
        for fail in brain_summary["repeated_failures"]:
            st.warning(f"❌ {fail}")

    # Regime insights
    regime_data = brain_summary.get("regime_insights", {})
    if regime_data:
        st.subheader("📈 Regime-Based Insights")
        import pandas as pd
        regime_rows = []
        for regime, info in regime_data.items():
            regime_rows.append({
                "Regime": regime,
                "Total Tested": info.get("total_tested", 0),
                "Passed": info.get("passed_count", 0),
                "Experiment IDs": ", ".join(info.get("experiment_ids", [])[:3]) + ("..." if len(info.get("experiment_ids", [])) > 3 else ""),
            })
        st.dataframe(pd.DataFrame(regime_rows), use_container_width=True, hide_index=True)

    # Cited experiments
    cited = brain_summary.get("all_cited_experiment_ids", [])
    if cited:
        st.subheader("🔗 Cited Experiment IDs")
        st.markdown(", ".join([f"`{eid}`" for eid in cited]))

    st.divider()
    st.caption("🔒 AI Brain evidence is scoped by symbol and asset class. Cross-asset generalizations are not made.")

# =============================================
# PAGE: DATA & DATASETS
# =============================================
def render_data():
    import pandas as pd
    from app.data.registry import ResearchDatasetRegistry
    from app.data.universe import UNIVERSE_BY_CLASS, ALL_INSTRUMENTS

    st.title("📂 Data & Dataset Registry")
    st.markdown("Research dataset provenance, quality status, and provider limitations.")

    # Dataset registry
    all_ds = ResearchDatasetRegistry.list_all()
    if not all_ds:
        st.info("No datasets registered yet. Visit the Markets page and inspect instruments to populate the registry.")
    else:
        rows = []
        for ds in all_ds:
            rows.append({
                "Dataset ID": ds.dataset_id,
                "Symbol": ds.symbol,
                "Asset Class": ds.market,
                "Provider": ds.provider,
                "Timeframe": ds.timeframe,
                "Start Date": ds.start_date[:10],
                "End Date": ds.end_date[:10],
                "Span (days)": ds.calendar_span_days,
                "Bars": ds.total_bars,
                "Hash": ds.dataset_hash,
                "Quality": ds.quality_status,
                "Mode": ds.data_mode,
                "Notes": ds.notes[:60] + "..." if ds.notes and len(ds.notes) > 60 else ds.notes,
            })
        df_ds = pd.DataFrame(rows)
        st.subheader("🗄️ Registered Datasets")
        st.dataframe(df_ds, use_container_width=True, hide_index=True)
        st.download_button("⬇ Export Dataset Registry (CSV)", df_ds.to_csv(index=False).encode(), "dataset_registry.csv")

    st.divider()

    # Market universe coverage
    st.subheader("📋 Market Universe Coverage")
    for ac, instruments in UNIVERSE_BY_CLASS.items():
        with st.expander(f"**{ac}** ({len(instruments)} instruments)"):
            rows = [{"Symbol": i.symbol, "Description": i.description, "Currency": i.currency,
                     "Provider": i.provider.replace("DataProvider", ""), "Notes": i.notes or "-"}
                    for i in instruments]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()

    # CSV import info
    st.subheader("📁 Local CSV Data Import")
    st.markdown(f"""
    Import your own historical OHLCV data using `CSVDataProvider`.

    **Required CSV schema:**
    ```
    timestamp,open,high,low,close,volume
    2020-01-01 09:15:00,1200.5,1210.0,1195.0,1205.2,150000
    ```

    **Data folder:** `{settings.DATA_DIR}`

    Place CSV files as `<SYMBOL>.csv` in the data folder. All imported files are hashed and registered automatically.
    """)

    csv_files = list(settings.DATA_DIR.glob("*.csv"))
    if csv_files:
        st.markdown("**Available CSV files:**")
        for f in csv_files:
            st.markdown(f"- `{f.name}` ({f.stat().st_size // 1024} KB)")
    else:
        st.info("No local CSV files found in data folder.")

    # Provider limitation notice
    st.divider()
    st.subheader("⚠️ Provider Limitations")
    st.markdown("""
    | Provider | Asset Class | Coverage | Limitation |
    |---|---|---|---|
    | yfinance | INDIAN_EQUITY | ~5 years (1d) | Free endpoint, rate limited |
    | yfinance | INDIAN_INDEX | ~5 years (1d) | Free endpoint |
    | yfinance | FOREX | ~250 daily bars | Free endpoint depth limit |
    | yfinance | CRYPTO | ~5 years (1d) | BTC-USD, ETH-USD, etc. |
    | yfinance | GOLD (GC=F) | ~5 years (1d) | Futures front month, not spot |
    | CSV | Any | User-defined | Local file only |
    | Synthetic | Any | N/A | Fallback only — not real data |
    """)

# =============================================
# PAGE: SYSTEM / SAFETY
# =============================================
def render_system():
    import subprocess
    st.title("⚙️ System & Safety Status")
    st.markdown("Complete system health, LLM provider chain, and safety verification.")

    # Safety status — always rendered first
    pt_status = "✅ TRUE" if settings.PAPER_TRADING_ONLY else "❌ FALSE"
    rb_status = "✅ DISABLED" if not settings.ALLOW_REAL_BROKER else "❌ ENABLED"

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"""
        <div style='background:#0a2a12;border:2px solid #1e4d2b;border-radius:10px;padding:20px;text-align:center;'>
          <div style='font-size:1.5rem;font-weight:700;color:#52b788;'>PAPER_TRADING_ONLY</div>
          <div style='font-size:2rem;font-weight:900;color:{"#52b788" if settings.PAPER_TRADING_ONLY else "#e63946"};'>{pt_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_s2:
        st.markdown(f"""
        <div style='background:#0a2a12;border:2px solid #1e4d2b;border-radius:10px;padding:20px;text-align:center;'>
          <div style='font-size:1.5rem;font-weight:700;color:#52b788;'>ALLOW_REAL_BROKER</div>
          <div style='font-size:2rem;font-weight:900;color:{"#52b788" if not settings.ALLOW_REAL_BROKER else "#e63946"};'>{rb_status}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # LLM status
    st.subheader("🤖 LLM Provider Chain")
    try:
        import httpx
        r = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        ollama_ok = r.status_code == 200
    except Exception:
        ollama_ok = False

    lc1, lc2, lc3, lc4 = st.columns(4)
    lc1.metric("Primary", settings.OLLAMA_MODEL, delta="Ollama" if ollama_ok else "Offline")
    lc2.metric("Fallback 1", settings.GEMINI_MODEL, delta="Gemini (if key set)")
    lc3.metric("Fallback 2", settings.OPENROUTER_MODEL, delta="OpenRouter (if key set)")
    lc4.metric("Final Fallback", "Mock", delta="Always available")

    st.info("ℹ️ API keys are read from `.env` file and are never displayed here or logged to console.")

    # DB status
    st.divider()
    st.subheader("🗄️ Database Status")
    db_path = settings.DB_PATH
    if db_path.exists():
        size_kb = db_path.stat().st_size // 1024
        all_exps = repo.get_all_experiments()
        st.success(f"✅ SQLite DB: `{db_path}` ({size_kb} KB, {len(all_exps)} experiments)")
    else:
        st.warning(f"⚠️ SQLite DB not found at `{db_path}`")

    # Test status shortcut
    st.divider()
    st.subheader("🧪 Run Safety Verification")
    if st.button("▶ Run pytest (safety tests only)"):
        with st.spinner("Running safety tests..."):
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", "tests/test_broker_safety_audit.py", "tests/test_safety.py", "-v", "--tb=short"],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(ROOT_DIR)
                )
                if result.returncode == 0:
                    st.success("✅ Safety tests passed.")
                else:
                    st.error("❌ Safety tests FAILED.")
                st.code(result.stdout + result.stderr, language="text")
            except Exception as e:
                st.error(f"Could not run tests: {e}")

    st.divider()
    st.subheader("⚙️ Configuration")
    st.json({
        "APP_NAME": settings.APP_NAME,
        "PAPER_TRADING_ONLY": settings.PAPER_TRADING_ONLY,
        "ALLOW_REAL_BROKER": settings.ALLOW_REAL_BROKER,
        "DEFAULT_INITIAL_CASH": settings.DEFAULT_INITIAL_CASH,
        "DEFAULT_MAX_EXPERIMENTS": settings.DEFAULT_MAX_EXPERIMENTS,
        "OLLAMA_BASE_URL": settings.OLLAMA_BASE_URL,
        "OLLAMA_MODEL": settings.OLLAMA_MODEL,
        "DEFAULT_MARKET": settings.DEFAULT_MARKET,
        "DEFAULT_TIMEFRAME": settings.DEFAULT_TIMEFRAME,
        "DB_PATH": str(settings.DB_PATH),
        "DATA_DIR": str(settings.DATA_DIR),
        # API keys intentionally NOT shown
        "GEMINI_API_KEY": "*** (not shown)",
        "OPENROUTER_API_KEY": "*** (not shown)",
    })

def render_decision_dataset():
    st.title("📋 Phase 11 Decision Dataset & Ground Truth")
    st.markdown("Auditable dataset records prepared for future decision model calibration and Laya export.")

    from app.memory.decision_repository import DecisionRepository
    from app.evaluation.leakage_auditor import DatasetLeakageAuditor
    from app.evaluation.benchmark_engine import BenchmarkEvaluator

    dec_repo = DecisionRepository()
    records = dec_repo.list_all(limit=2000)

    # Dataset KPIs
    col1, col2, col3, col4 = st.columns(4)
    total_cnt = len(records)
    dev_cnt = sum(1 for r in records if r.data_split == "DEVELOPMENT")
    val_cnt = sum(1 for r in records if r.data_split == "VALIDATION")
    hold_cnt = sum(1 for r in records if r.data_split == "HOLDOUT")

    col1.metric("Total Decision Records", total_cnt)
    col2.metric("Development (Train)", dev_cnt)
    col3.metric("Validation", val_cnt)
    col4.metric("Holdout (Protected)", hold_cnt)

    if total_cnt == 0:
        st.info("ℹ️ No DecisionRecords persisted in SQLite database yet. Run `python scripts/verify_phase11.py` or HistoricalDatasetBuilder to populate.")
    else:
        st.divider()
        st.subheader("🛡️ Data Leakage & Quality Audit")
        audit_res = DatasetLeakageAuditor.audit_records(records)
        ac1, ac2, ac3, ac4 = st.columns(4)
        ac1.metric("Future Leakage", audit_res["future_leakage_count"], delta="0 Expected" if audit_res["future_leakage_count"] == 0 else "FAIL", delta_color="normal")
        ac2.metric("Duplicates", audit_res["duplicate_record_count"], delta="0 Expected" if audit_res["duplicate_record_count"] == 0 else "FAIL", delta_color="normal")
        ac3.metric("Invalid Labels", audit_res["invalid_label_count"])
        ac4.metric("Missing Fields", audit_res["missing_field_count"])

        if audit_res["audit_passed"]:
            st.success("✅ Dataset Leakage Audit PASSED: 0 future leakage, 0 duplicates, 0 invalid labels.")
        else:
            st.error("❌ Dataset Leakage Audit FAILED. Review errors above.")

        # Class Distribution
        st.divider()
        st.subheader("🎯 Ground Truth Label Distribution")
        bench_res = BenchmarkEvaluator.evaluate_decisions(records)
        st.json(bench_res["class_counts"])

        # Table
        st.divider()
        st.subheader("📄 Persistent Decision Records")
        table_data = []
        for r in records[:100]:
            table_data.append({
                "Decision ID": r.decision_id,
                "Timestamp": r.timestamp,
                "Symbol": r.symbol,
                "Market": r.market,
                "Split": r.data_split,
                "Direction": r.ground_truth.direction_outcome,
                "Return (%)": r.ground_truth.realized_return_pct,
                "MFE (%)": r.ground_truth.max_favorable_excursion_pct,
                "MAE (%)": r.ground_truth.max_adverse_excursion_pct,
                "Dataset Hash": r.dataset_hash[:8]
            })
        st.dataframe(table_data, use_container_width=True)

def render_laya_shadow():
    st.title("🤖 Laya Shadow Inference, Continuous Validation & Phase 16 Status Engine")
    st.markdown("Observation, decision logging, continuous validation, and Phase 16 independent status engine (`ALGO_LAYA_V001`).")

    # Safety & Authority Banners
    st.warning("⚠️ LAYA DECISION AUTHORITY: SHADOW ONLY. Candidate model predictions do NOT execute trades or override risk controls. Status: PROMOTE_TO_SHADOW.")

    from app.memory.laya_repository import LayaPredictionRepository
    from app.memory.laya_model_registry import LayaModelRegistry
    from app.services.laya_shadow_collector import LayaShadowCollectorService

    laya_repo = LayaPredictionRepository()
    registry = LayaModelRegistry()
    collector = LayaShadowCollectorService()
    assessment = collector.generate_assessment()
    predictions = laya_repo.list_all(limit=1000)
    total_preds = len(predictions)
    active_candidate = registry.get_active_candidate()

    st.divider()
    st.subheader("📊 Phase 16 Independent Status Engine (Research-Integrity Corrected)")
    st.info("ℹ️ Collection Status and Evidence Status are decoupled. Data Availability requires timestamp audit post-Phase 15 cutoff. Economic metrics enforce minimum sample sufficiency rules.")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("1. Data Availability", assessment.data_availability_status.value)
    s2.metric("2. Collection Status", assessment.collection_status.value)
    s3.metric("3. Evidence Status", assessment.evidence_status.value)
    s4.metric("4. Fresh Calibration", assessment.fresh_calibration_status.value)

    st.markdown(f"**Model Health:** `{assessment.model_health_status.value}` · **Economic Shadow Status:** `<span class='badge-no-trades'>{assessment.economic_shadow_status}</span>`", unsafe_allow_html=True)

    # Data Availability Cutoff Audit Panel
    st.divider()
    st.subheader("🛡️ Fresh Data Audit & Phase 15 Cutoff Verification")
    da1, da2, da3, da4 = st.columns(4)
    da1.metric("Total Historical Records", assessment.total_available_records)
    da2.metric("Phase 15 Baseline Records", assessment.phase15_records)
    da3.metric("Fresh Shadow Records", assessment.fresh_records, delta="Post Phase 15 Cutoff")
    da4.metric("Fresh Symbols", assessment.fresh_records if assessment.fresh_records > 0 else 0)

    # Baseline vs Fresh Calibration Panel
    st.divider()
    st.subheader("🎯 Calibration Audit: Phase 15 Baseline vs Phase 16 Fresh Shadow")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**PHASE 15 BASELINE CALIBRATION (131 Calibration Cases)**")
        st.json(assessment.phase15_baseline_calibration)
    with c2:
        st.markdown("**PHASE 16 FRESH SHADOW CALIBRATION (Resolved Fresh Predictions)**")
        st.json({
            "fresh_calibration_status": assessment.fresh_calibration_status.value,
            "fresh_calibrated_ece": str(assessment.fresh_calibrated_ece),
            "fresh_brier_score": str(assessment.fresh_brier_score),
            "sample_note": "Requires >= 30 resolved fresh predictions for calibration stability claim"
        })

    # Economic Shadow Analysis & Sufficiency Rules Panel
    st.divider()
    st.subheader("💹 Economic Shadow Results (Hypothetical Only)")
    st.info("⚠️ Economic metrics strictly enforce sample sufficiency rules. Single-trade results do NOT calculate Sharpe ratio or Sharpe-based conclusions.")
    ec1, ec2, ec3, ec4 = st.columns(4)
    ec1.metric("Shadow Trades", assessment.trade_count)
    ec2.metric("Raw Return", f"{assessment.hypothetical_raw_return * 100:+.2f}%")
    ec3.metric("Net Return", f"{assessment.hypothetical_net_return * 100:+.2f}%")
    ec4.metric("Sharpe Ratio", str(assessment.sharpe_ratio))

    # Drift Status Panel
    st.divider()
    st.subheader("🌊 Drift Monitoring (Sufficiency Gate Active)")
    dr1, dr2, dr3, dr4 = st.columns(4)
    dr1.metric("Feature Drift", assessment.data_drift_status.value)
    dr2.metric("Prediction Drift", assessment.prediction_drift_status.value)
    dr3.metric("Calibration Drift", assessment.calibration_drift_status.value)
    dr4.metric("Regime Drift", assessment.regime_drift_status.value)

    # Latency Stats Panel
    st.divider()
    st.subheader("⏱️ Latency Measurement Audit")
    l1, l2 = st.columns(2)
    with l1:
        st.markdown("**Model Forward Inference Latency (ms)**")
        st.json(assessment.model_inference_latency.model_dump())
    with l2:
        st.markdown("**End-to-End Prediction Pipeline Latency (ms)**")
        st.json(assessment.end_to_end_latency.model_dump())

    st.divider()
    st.subheader("⚙️ Active Candidate Model (`ALGO_LAYA_V001`)")
    if active_candidate:
        st.success(f"✅ Candidate Model Registered: `{active_candidate['model_id']}` (Run: `{active_candidate['run_id']}`)")
        st.json({
            "model_id": active_candidate.get("model_id"),
            "run_id": active_candidate.get("run_id"),
            "base_model": active_candidate.get("base_model"),
            "promotion_status": active_candidate.get("promotion_status"),
            "calibration": active_candidate.get("calibration"),
            "validation_metrics": active_candidate.get("validation_metrics"),
            "holdout_metrics": active_candidate.get("holdout_metrics"),
            "decision_authority": "SHADOW_ONLY"
        })
    else:
        st.info("ℹ️ No candidate model currently registered. Run `python scripts/verify_phase15.py` to execute Phase 15 pipeline.")

    # Phase 14 Dataset Package Panel
    manifest_path = ROOT_DIR / "data" / "laya" / "dataset_manifest.json"
    if manifest_path.exists():
        st.divider()
        st.subheader("📦 Laya Fine-Tuning Dataset Package (`ALGO_LAYA_DATASET_V1`)")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        mc1, mc2, mc3, mc4 = st.columns(4)
        counts = manifest_data.get("record_counts", {})
        mc1.metric("Train Cases", counts.get("train", 0))
        mc2.metric("Calibration Cases", counts.get("calibration", 0))
        mc3.metric("Validation Cases", counts.get("validation", 0))
        mc4.metric("Holdout (Protected)", counts.get("holdout", 0))

        st.json(manifest_data)

    if total_preds > 0:
        st.divider()
        st.subheader("📄 Persistent Shadow Prediction Audit Log")
        table_data = []
        for p in predictions[:100]:
            table_data.append({
                "Decision ID": p.decision_id,
                "Timestamp": p.timestamp,
                "Symbol": p.symbol,
                "Market": p.market,
                "Direction": p.predicted_direction,
                "Regime": p.predicted_regime,
                "Risk": p.predicted_risk,
                "Confidence": f"{p.confidence:.2f}" if p.confidence is not None else "N/A",
                "Latency (ms)": p.latency_ms,
                "Status": p.status
            })
        st.dataframe(table_data, use_container_width=True)

def render_lightgbm_predictor():
    st.title("🌲 LightGBM Numerical Prediction Foundation (`ALGO_LGBM_V001`)")
    st.markdown("Dedicated numerical machine-learning layer predicting 4-bar forward returns (`LIGHTGBM_TARGET_POLICY_V1`).")

    st.warning("⚠️ LIGHTGBM AUTHORITY: OFFLINE RESEARCH ONLY. Numerical predictions do NOT execute trades, alter paper portfolios, or override risk controls.")

    from app.memory.lightgbm_model_registry import LightGBMModelRegistry
    registry = LightGBMModelRegistry()
    manifest = registry.get_manifest("ALGO_LGBM_V001")

    if manifest:
        st.success(f"✅ Active Registered Candidate: `{manifest.model_id}` (Status: `{manifest.status.value}`)")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Model ID", manifest.model_id)
        m2.metric("Target Horizon", "4 Bars Forward")
        m3.metric("Status", manifest.status.value)
        m4.metric("Trading Authority", manifest.decision_authority)

        st.divider()
        st.subheader("🎯 Evaluation Metrics (Validation vs Protected Holdout)")
        val_m = manifest.validation_metrics
        hold_m = manifest.holdout_metrics

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**VALIDATION SPLIT METRICS (15% Chronological)**")
            st.json(val_m)
        with c2:
            st.markdown("**PROTECTED HOLDOUT METRICS (15% Chronological)**")
            st.json(hold_m)

        st.divider()
        st.subheader("📊 Deterministic Baseline Model Comparison")
        st.json(manifest.baseline_metrics)

        st.divider()
        st.subheader("⚙️ Model Architecture & Provenance Manifest")
        st.json(manifest.model_dump())
    else:
        st.info("ℹ️ No LightGBM manifest registered yet. Run `python scripts/verify_phase17.py` to fit and register ALGO_LGBM_V001.")

# =============================================
# MAIN ROUTER
# =============================================
if page == "overview":
    render_overview()
elif page == "markets":
    render_markets()
elif page == "experiments":
    render_experiments()
elif page == "strategies":
    render_strategies()
elif page == "paper_trading":
    render_paper_trading()
elif page == "ai_brain":
    render_ai_brain()
elif page == "decision_dataset":
    render_decision_dataset()
elif page == "laya_shadow":
    render_laya_shadow()
elif page == "lightgbm_predictor":
    render_lightgbm_predictor()
elif page == "data":
    render_data()
elif page == "system":
    render_system()
