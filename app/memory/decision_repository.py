"""Decision Record SQLite Repository extension."""
import json
import sqlite3
from typing import List, Optional, Dict, Any
from pathlib import Path
from app.domain.decision_schemas import DecisionRecord
from app.config.settings import settings
from app.config.logging import logger

class DecisionRepository:
    """Persistence repository for Phase 11 DecisionRecords in SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_records (
                    decision_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    market TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    dataset_id TEXT NOT NULL,
                    dataset_hash TEXT NOT NULL,
                    data_split TEXT NOT NULL,
                    direction_outcome TEXT NOT NULL,
                    realized_return_pct REAL NOT NULL,
                    raw_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dec_symbol ON decision_records(symbol);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dec_market ON decision_records(market);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dec_split ON decision_records(data_split);")
            conn.commit()

    def save(self, record: DecisionRecord) -> None:
        raw_json = json.dumps(record.model_dump())
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO decision_records (
                    decision_id, timestamp, symbol, market, timeframe,
                    dataset_id, dataset_hash, data_split, direction_outcome,
                    realized_return_pct, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                record.decision_id,
                record.timestamp,
                record.symbol,
                record.market,
                record.timeframe,
                record.dataset_id,
                record.dataset_hash,
                record.data_split,
                record.ground_truth.direction_outcome,
                record.ground_truth.realized_return_pct,
                raw_json
            ))
            conn.commit()

    def get_by_id(self, decision_id: str) -> Optional[DecisionRecord]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT raw_json FROM decision_records WHERE decision_id = ?",
                (decision_id,)
            ).fetchone()
            if row:
                return DecisionRecord.model_validate(json.loads(row["raw_json"]))
            return None

    def list_all(self, limit: int = 1000) -> List[DecisionRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM decision_records ORDER BY timestamp ASC LIMIT ?",
                (limit,)
            ).fetchall()
            return [DecisionRecord.model_validate(json.loads(r["raw_json"])) for r in rows]

    def list_by_split(self, data_split: str) -> List[DecisionRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM decision_records WHERE data_split = ? ORDER BY timestamp ASC",
                (data_split,)
            ).fetchall()
            return [DecisionRecord.model_validate(json.loads(r["raw_json"])) for r in rows]

    def count(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute("SELECT COUNT(*) FROM decision_records;").fetchone()
            return res[0] if res else 0

    def clear(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM decision_records;")
            conn.commit()
