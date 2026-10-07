"""Research Dataset Registry module for dataset reproducibility.

Each dataset ingested by any provider is registered with:
- A stable dataset_id (based on symbol + hash)
- SHA-256 content hash for reproducibility verification
- Full provenance metadata (provider, asset class, timeframe, date range, quality)

Registry state is in-memory per session. Raw experiment records in SQLite are the
authoritative long-term record.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.data.base_provider import MarketData
from app.domain.schemas import DataMode, MarketType


class ResearchDatasetEntry(BaseModel):
    dataset_id: str
    provider: str
    symbol: str
    market: MarketType
    timeframe: str
    start_date: str
    end_date: str
    dataset_hash: str
    data_mode: DataMode
    total_bars: int
    calendar_span_days: int = 0
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    quality_status: str = "UNKNOWN"  # "PASS", "WARN", "FAIL", "UNKNOWN"
    notes: str = ""


class ResearchDatasetRegistry:
    """Tracks and registers reproducible dataset metadata per experiment.

    Design note: Registry is class-level in-process cache.
    Historical records are preserved in SQLite via ExperimentRepository.
    Do NOT silently overwrite existing entries with the same ID.
    """

    _registry: Dict[str, ResearchDatasetEntry] = {}

    @classmethod
    def register(
        cls,
        data: MarketData,
        provider_name: str = "yfinance",
        quality_status: str = "UNKNOWN",
        notes: str = ""
    ) -> ResearchDatasetEntry:
        ds_id = f"DS_{data.symbol}_{data.dataset_hash[:8]}"
        is_synthetic = data.metadata.get("is_synthetic", False)
        is_replay = data.metadata.get("is_replay", False)

        data_mode: DataMode = "SYNTHETIC" if is_synthetic else ("REPLAY" if is_replay else "HISTORICAL")

        # Compute calendar span
        try:
            span_days = (data.end_date - data.start_date).days
        except Exception:
            span_days = 0

        entry = ResearchDatasetEntry(
            dataset_id=ds_id,
            provider=provider_name if not is_synthetic else "synthetic_generator",
            symbol=data.symbol,
            market=data.market,
            timeframe=data.timeframe,
            start_date=str(data.start_date),
            end_date=str(data.end_date),
            dataset_hash=data.dataset_hash,
            data_mode=data_mode,
            total_bars=len(data),
            calendar_span_days=span_days,
            quality_status=quality_status,
            notes=notes or (data.metadata.get("note", "") or "")
        )
        cls._registry[ds_id] = entry
        return entry

    @classmethod
    def get(cls, dataset_id: str) -> Optional[ResearchDatasetEntry]:
        return cls._registry.get(dataset_id)

    @classmethod
    def list_all(cls) -> List[ResearchDatasetEntry]:
        """Return all registered dataset entries."""
        return list(cls._registry.values())

    @classmethod
    def list_by_asset_class(cls, asset_class: str) -> List[ResearchDatasetEntry]:
        """Return entries filtered by asset class / market type."""
        return [e for e in cls._registry.values() if e.market == asset_class]

    @classmethod
    def clear(cls) -> None:
        """Clear registry (used in testing only)."""
        cls._registry.clear()
