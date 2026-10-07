"""Script to execute 10 controlled experiments, paper replay session, research audit, and safety check."""
import os
import sys
import json
from pathlib import Path
import pandas as pd

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.memory.repository import ExperimentRepository
from app.data.replay_provider import ReplayDataProvider
from app.data.indian_provider import IndianMarketDataProvider
from app.services.experiment_runner import ExperimentRunner
from app.services.ai_brain import AIBrainService
from app.paper_trading.portfolio import PaperPortfolio
from app.config.safety import assert_paper_trading_only
from app.config.logging import logger

def run_phase5_experiments_and_audit():
    print("==================================================")
    print("   QUANT AI PHASE 5 RESEARCH & AUDIT SUITE")
    print("==================================================")

    # 1. Safety Audit
    print("\n--> STEP 1: Broker Safety Boundary Audit")
    assert_paper_trading_only()
    print("  [OK] PAPER_TRADING_ONLY=true & ALLOW_REAL_BROKER=false strictly verified.")

    # 2. Setup SQLite DB for phase 5
    db_path = Path("data/experiments.db")
    repo = ExperimentRepository()

    # 3. Execute 10 Controlled Experiments Loop
    print("\n--> STEP 2: Running 10 Controlled Bounded Research Experiments...")
    provider = ReplayDataProvider(regime="TRENDING", num_bars=300)
    runner = ExperimentRunner(repository=repo, data_provider=provider)

    exp_records = runner.run_experiments(
        symbol="SYNTHETIC_IND",
        market="INDIAN_EQUITY",
        timeframe="1d",
        max_experiments=10
    )

    print(f"  [OK] Completed {len(exp_records)} experiments.")
    for i, exp in enumerate(exp_records, 1):
        print(f"  #{i:02d} | ID: {exp.experiment_id} | Version: {exp.strategy_version} | Verdict: {exp.critic_verdict:22s} | Sharpe: {exp.metrics.sharpe_ratio:5.2f}")

    # 4. Paper Replay Session Campaign
    print("\n--> STEP 3: Executing Sequential Bar-by-Bar Paper Replay Campaign...")
    paper_portfolio = PaperPortfolio(initial_cash=100000.0)
    replay_provider = ReplayDataProvider(regime="TRENDING", num_bars=100)

    # Simulate sequential bar-by-bar paper trading
    for bar_data in replay_provider.stream_bars(symbol="SYNTHETIC_IND"):
        latest_row = bar_data.df.iloc[-1]
        cur_price = float(latest_row["close"])
        cur_symbol = bar_data.symbol

        # Simple paper rule for verification stream
        state = paper_portfolio.update_market_prices({cur_symbol: cur_price})
        if cur_symbol not in paper_portfolio.positions and len(bar_data.df) > 10:
            paper_portfolio.open_position(symbol=cur_symbol, side="LONG", fill_price=cur_price, quantity=10.0, fee=5.0)
        elif cur_symbol in paper_portfolio.positions and len(bar_data.df) > 30:
            paper_portfolio.close_position(symbol=cur_symbol, exit_price=cur_price, fee=5.0, exit_reason="REPLAY_EXIT")

    final_state = paper_portfolio.update_market_prices({})
    print(f"  [OK] Paper Replay completed. Closed trades: {len(final_state.closed_trades)}, Final Equity: INR/${final_state.total_equity:.2f}")

    # 5. AI Brain Summary Generation
    print("\n--> STEP 4: AI Brain Evidence Summary Generation...")
    brain_service = AIBrainService(repository=repo)
    summary = brain_service.generate_learned_summary()
    print(f"  Title: {summary['title']}")
    for obs in summary['evidence_supported_observations']:
        print(f"  [Evidence] {obs}")

    print("\n==================================================")
    print("   PHASE 5 CAMPAIGN & AUDIT COMPLETED CLEANLY")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_phase5_experiments_and_audit()
