"""Repository for querying and persisting experiment memory and strategy lineage."""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.domain.schemas import (
    ExperimentRecord, BacktestMetrics, CriticVerdictType, MarketRegimeType, StrategySpec
)
from app.memory.sqlite_db import Database, db as default_db

class ExperimentRepository:
    def __init__(self, database: Database = None):
        self.db = database or default_db

    def _row_to_experiment(self, row) -> ExperimentRecord:
        data = dict(row)
        data["parameters"] = json.loads(data["parameters"]) if isinstance(data["parameters"], str) else data["parameters"]
        data["metrics"] = json.loads(data["metrics"]) if isinstance(data["metrics"], str) else data["metrics"]
        return ExperimentRecord.model_validate(data)

    def insert_experiment(self, record: ExperimentRecord) -> None:
        sql = """
        INSERT OR REPLACE INTO experiments (
            experiment_id, timestamp, hypothesis, strategy_version, parent_experiment_id,
            market, symbol, timeframe, parameters, data_period, data_split, metrics,
            fees_assumed, slippage_assumed, critic_verdict, critic_reasoning, failure_reason,
            market_regime, lesson_learned, status, code_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_connection() as conn:
            conn.execute(sql, (
                record.experiment_id,
                record.timestamp,
                record.hypothesis,
                record.strategy_version,
                record.parent_experiment_id,
                record.market,
                record.symbol,
                record.timeframe,
                json.dumps(record.parameters),
                record.data_period,
                record.data_split,
                json.dumps(record.metrics.model_dump()),
                record.fees_assumed,
                record.slippage_assumed,
                record.critic_verdict,
                record.critic_reasoning,
                record.failure_reason,
                record.market_regime,
                record.lesson_learned,
                record.status,
                record.code_version
            ))
            conn.commit()

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentRecord]:
        sql = "SELECT * FROM experiments WHERE experiment_id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql, (experiment_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_experiment(row)
        return None

    def get_recent_experiments(self, limit: int = 10) -> List[ExperimentRecord]:
        sql = "SELECT * FROM experiments ORDER BY timestamp DESC LIMIT ?"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql, (limit,))
            return [self._row_to_experiment(r) for r in cursor.fetchall()]

    def get_all_experiments(self) -> List[ExperimentRecord]:
        sql = "SELECT * FROM experiments ORDER BY timestamp ASC"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql)
            return [self._row_to_experiment(r) for r in cursor.fetchall()]

    def get_experiments_by_verdict(self, verdict: CriticVerdictType) -> List[ExperimentRecord]:
        sql = "SELECT * FROM experiments WHERE critic_verdict = ? ORDER BY timestamp DESC"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql, (verdict,))
            return [self._row_to_experiment(r) for r in cursor.fetchall()]

    def get_failed_experiments(self) -> List[ExperimentRecord]:
        sql = "SELECT * FROM experiments WHERE critic_verdict = 'REJECT' OR status = 'FAILED' ORDER BY timestamp DESC"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql)
            return [self._row_to_experiment(r) for r in cursor.fetchall()]

    def get_successful_experiments(self) -> List[ExperimentRecord]:
        sql = "SELECT * FROM experiments WHERE critic_verdict = 'KEEP_FOR_PAPER_TESTING' ORDER BY timestamp DESC"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql)
            return [self._row_to_experiment(r) for r in cursor.fetchall()]

    def get_experiments_by_regime(self, regime: MarketRegimeType) -> List[ExperimentRecord]:
        sql = "SELECT * FROM experiments WHERE market_regime = ? ORDER BY timestamp DESC"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql, (regime,))
            return [self._row_to_experiment(r) for r in cursor.fetchall()]

    def get_strategy_lineage(self, strategy_version: str) -> List[ExperimentRecord]:
        sql = "SELECT * FROM experiments WHERE strategy_version = ? ORDER BY timestamp ASC"
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql, (strategy_version,))
            return [self._row_to_experiment(r) for r in cursor.fetchall()]

    def get_summary_statistics(self) -> Dict[str, Any]:
        all_exps = self.get_all_experiments()
        if not all_exps:
            return {
                "total_experiments": 0,
                "passed_count": 0,
                "retest_count": 0,
                "rejected_count": 0,
                "avg_sharpe": 0.0,
                "best_sharpe": 0.0,
                "regimes_tested": []
            }

        passed = [e for e in all_exps if e.critic_verdict == "KEEP_FOR_PAPER_TESTING"]
        retest = [e for e in all_exps if e.critic_verdict == "RETEST"]
        rejected = [e for e in all_exps if e.critic_verdict == "REJECT"]
        sharpes = [e.metrics.sharpe_ratio for e in all_exps]

        return {
            "total_experiments": len(all_exps),
            "passed_count": len(passed),
            "retest_count": len(retest),
            "rejected_count": len(rejected),
            "avg_sharpe": sum(sharpes) / len(sharpes) if sharpes else 0.0,
            "best_sharpe": max(sharpes) if sharpes else 0.0,
            "regimes_tested": list(set(e.market_regime for e in all_exps))
        }

    def save_strategy_spec(self, spec: StrategySpec, status: str = "CANDIDATE") -> None:
        sql = "INSERT OR REPLACE INTO strategy_versions (version_id, parent_version_id, strategy_spec, status, created_at) VALUES (?, ?, ?, ?, ?)"
        with self.db.get_connection() as conn:
            spec_dict = spec.model_dump()
            conn.execute(sql, (
                spec.version,
                spec.parent_version_id,
                json.dumps(spec_dict),
                status,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
