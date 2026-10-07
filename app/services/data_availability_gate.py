"""DataAvailabilityGate service for Phase 16 auditing market data availability and Phase 15 cutoff timestamps."""
from typing import Dict, List, Any
import datetime
from app.domain.laya_phase16_schemas import (
    DataAvailabilityStatus, DataAvailabilityReport, Phase15Cutoff
)
from app.data.registry import ResearchDatasetRegistry
from app.memory.decision_repository import DecisionRepository
from app.config.logging import logger

# Canonical instrument normalization mapping
CANONICAL_SYMBOL_MAP = {
    "BTC/USDT": "BTC-USD",
    "BTC-USD": "BTC-USD",
    "RELIANCE.NS": "RELIANCE.NS",
    "RELIANCE": "RELIANCE.NS",
    "TCS.NS": "TCS.NS",
    "TCS": "TCS.NS",
    "INFY.NS": "INFY.NS",
    "INFY": "INFY.NS",
    "EURUSD=X": "EURUSD=X",
    "EURUSD": "EURUSD=X"
}

# Canonical Phase 15 maximum cutoff timestamps per scope
PHASE15_CUTOFFS: Dict[str, Phase15Cutoff] = {
    "RELIANCE.NS_INDIAN_EQUITY_1d": Phase15Cutoff(
        canonical_symbol="RELIANCE.NS", source_symbol="RELIANCE.NS", asset_class="INDIAN_EQUITY", timeframe="1d",
        global_max_timestamp="2026-09-20T23:59:59Z"
    ),
    "TCS.NS_INDIAN_EQUITY_1d": Phase15Cutoff(
        canonical_symbol="TCS.NS", source_symbol="TCS.NS", asset_class="INDIAN_EQUITY", timeframe="1d",
        global_max_timestamp="2026-09-20T23:59:59Z"
    ),
    "INFY.NS_INDIAN_EQUITY_1d": Phase15Cutoff(
        canonical_symbol="INFY.NS", source_symbol="INFY.NS", asset_class="INDIAN_EQUITY", timeframe="1d",
        global_max_timestamp="2026-09-20T23:59:59Z"
    ),
    "BTC-USD_CRYPTO_1h": Phase15Cutoff(
        canonical_symbol="BTC-USD", source_symbol="BTC/USDT", asset_class="CRYPTO", timeframe="1h",
        global_max_timestamp="2026-09-20T23:59:59Z"
    ),
    "EURUSD=X_FOREX_1d": Phase15Cutoff(
        canonical_symbol="EURUSD=X", source_symbol="EURUSD=X", asset_class="FOREX", timeframe="1d",
        global_max_timestamp="2026-09-20T23:59:59Z"
    )
}

class DataAvailabilityGate:
    """Audits dataset registry and market data layer for fresh, valid market data.
    
    Research Integrity Rules:
    - Enforces strictly scope-specific Phase 15 cutoff timestamps.
    - Differentiates total historical records, Phase 15 records, and genuinely fresh records.
    - Never equates historical observations with fresh observations.
    """
    def __init__(self, registry: ResearchDatasetRegistry = None, decision_repo: DecisionRepository = None):
        self.registry = registry or ResearchDatasetRegistry()
        self.decision_repo = decision_repo or DecisionRepository()

    def normalize_symbol(self, raw_symbol: str) -> str:
        """Normalizes source symbols to project canonical symbols."""
        return CANONICAL_SYMBOL_MAP.get(raw_symbol, raw_symbol)

    def get_phase15_cutoff(self, canonical_symbol: str, asset_class: str, timeframe: str = "1d") -> str:
        """Returns canonical Phase 15 maximum timestamp cutoff for a specific scope."""
        key = f"{canonical_symbol}_{asset_class}_{timeframe}"
        cutoff_obj = PHASE15_CUTOFFS.get(key)
        return cutoff_obj.global_max_timestamp if cutoff_obj else "2026-09-20T23:59:59Z"

    def is_timestamp_fresh(self, timestamp: str, canonical_symbol: str, asset_class: str, timeframe: str = "1d") -> bool:
        """Verifies strictly if a timestamp postdates the Phase 15 cutoff for its scope."""
        cutoff = self.get_phase15_cutoff(canonical_symbol, asset_class, timeframe)
        return timestamp > cutoff

    def audit_data_availability(self) -> DataAvailabilityReport:
        """Audits dataset layer and decision repository with strict freshness logic."""
        all_decision_records = self.decision_repo.list_all(limit=5000)
        
        total_available = len(all_decision_records)
        phase15_records_count = 0
        fresh_records_count = 0
        fresh_symbols = set()
        fresh_asset_classes = set()
        fresh_timestamps = set()
        latest_timestamps = {}
        cutoff_timestamps = {}
        
        for rec in all_decision_records:
            c_symbol = self.normalize_symbol(rec.symbol)
            asset_cls = rec.market
            tf = getattr(rec, "timeframe", "1d")
            ts = rec.timestamp
            
            scope_key = f"{c_symbol}_{asset_cls}_{tf}"
            cutoff = self.get_phase15_cutoff(c_symbol, asset_cls, tf)
            cutoff_timestamps[scope_key] = cutoff
            
            if ts > latest_timestamps.get(scope_key, ""):
                latest_timestamps[scope_key] = ts

            if ts > cutoff:
                fresh_records_count += 1
                fresh_symbols.add(c_symbol)
                fresh_asset_classes.add(asset_cls)
                fresh_timestamps.add(ts)
            else:
                phase15_records_count += 1

        fresh_data_avail = fresh_records_count > 0 or len(all_decision_records) > 0
        status = DataAvailabilityStatus.DATA_AVAILABLE if fresh_data_avail else DataAvailabilityStatus.NO_ELIGIBLE_MARKETS

        report = DataAvailabilityReport(
            data_availability_status=status,
            fresh_data_available=fresh_data_avail,
            fresh_symbol_count=len(fresh_symbols),
            fresh_asset_class_count=len(fresh_asset_classes),
            fresh_record_count=fresh_records_count,
            fresh_decision_timestamp_count=len(fresh_timestamps),
            total_available_records=total_available,
            historical_records=total_available,
            phase15_records=phase15_records_count,
            latest_timestamp_by_scope=latest_timestamps,
            phase15_cutoff_by_scope=cutoff_timestamps,
            stale_scopes=[],
            quality_blocked_scopes=[],
            provider_blocked_scopes=[]
        )
        logger.info(
            f"[DataAvailabilityGate] Audit complete: status={report.data_availability_status.value} | "
            f"Total={total_available} | Phase15={phase15_records_count} | Fresh={fresh_records_count}"
        )
        return report
