"""SQLite database connection and schema initialization."""
import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from app.config.settings import settings
from app.config.logging import logger

CREATE_EXPERIMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    strategy_version TEXT NOT NULL,
    parent_experiment_id TEXT,
    market TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    parameters JSON NOT NULL,
    data_period TEXT NOT NULL,
    data_split TEXT NOT NULL,
    metrics JSON NOT NULL,
    fees_assumed REAL NOT NULL,
    slippage_assumed REAL NOT NULL,
    critic_verdict TEXT NOT NULL,
    critic_reasoning TEXT NOT NULL,
    failure_reason TEXT,
    market_regime TEXT NOT NULL,
    lesson_learned TEXT NOT NULL,
    status TEXT NOT NULL,
    code_version TEXT NOT NULL
);
"""

CREATE_STRATEGY_VERSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS strategy_versions (
    version_id TEXT PRIMARY KEY,
    parent_version_id TEXT,
    strategy_spec JSON NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

CREATE_PORTFOLIO_SNAPSHOTS_TABLE = """
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    virtual_cash REAL NOT NULL,
    unrealized_pnl REAL NOT NULL,
    realized_pnl REAL NOT NULL,
    total_equity REAL NOT NULL,
    drawdown_pct REAL NOT NULL,
    snapshot_json JSON NOT NULL
);
"""

class Database:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_EXPERIMENTS_TABLE)
            cursor.execute(CREATE_STRATEGY_VERSIONS_TABLE)
            cursor.execute(CREATE_PORTFOLIO_SNAPSHOTS_TABLE)
            conn.commit()
        logger.info(f"SQLite DB initialized at {self.db_path}")

db = Database()
