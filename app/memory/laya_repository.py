"""Persistence repository for Phase 13 Laya Shadow Predictions in SQLite."""
import json
import sqlite3
from typing import List, Optional
from pathlib import Path
from app.domain.laya_schemas import LayaPredictionResult
from app.config.settings import settings
from app.config.logging import logger

class LayaPredictionRepository:
    """Stores Laya shadow predictions in SQLite for audit and agreement comparison."""

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
                CREATE TABLE IF NOT EXISTS laya_shadow_predictions (
                    decision_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    market TEXT NOT NULL,
                    dataset_id TEXT NOT NULL,
                    predicted_direction TEXT NOT NULL,
                    confidence REAL,
                    decision_authority TEXT NOT NULL DEFAULT 'SHADOW_ONLY',
                    status TEXT NOT NULL,
                    raw_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_laya_symbol ON laya_shadow_predictions(symbol);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_laya_status ON laya_shadow_predictions(status);")
            conn.commit()

    def save(self, record: LayaPredictionResult) -> None:
        raw_json = json.dumps(record.model_dump())
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO laya_shadow_predictions (
                    decision_id, timestamp, symbol, market, dataset_id,
                    predicted_direction, confidence, decision_authority, status, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                record.decision_id,
                record.timestamp,
                record.symbol,
                record.market,
                record.dataset_id,
                record.predicted_direction or "HOLD",
                record.confidence,
                record.decision_authority,
                record.status,
                raw_json
            ))
            conn.commit()

    def list_all(self, limit: int = 1000) -> List[LayaPredictionResult]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM laya_shadow_predictions ORDER BY timestamp ASC LIMIT ?",
                (limit,)
            ).fetchall()
            return [LayaPredictionResult.model_validate(json.loads(r["raw_json"])) for r in rows]

    def count(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute("SELECT COUNT(*) FROM laya_shadow_predictions;").fetchone()
            return res[0] if res else 0

    def clear(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM laya_shadow_predictions;")
            conn.commit()
