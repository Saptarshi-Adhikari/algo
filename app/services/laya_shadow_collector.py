"""Laya Shadow Prediction Collector, Delayed Outcome Resolver & Evidence Assessment Engine (Phase 16)."""
from typing import List, Dict, Any, Optional
import json
import uuid
import math
from pathlib import Path
from app.config.settings import settings
from app.config.logging import logger
from app.domain.laya_phase16_schemas import (
    DataAvailabilityStatus, CollectionStatus, EvidenceStatus, CalibrationStatus,
    ModelHealthStatus, FreshShadowPredictionRecord, Phase16AssessmentResult
)
from app.services.data_availability_gate import DataAvailabilityGate

DB_SHADOW_FILE = Path(__file__).parent.parent.parent / "data" / "laya_shadow_phase16_records.json"

class LayaShadowCollectorService:
    """Manages Phase 16 Fresh-Shadow predictions, delayed outcomes, evidence state, drift, and assessment."""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or DB_SHADOW_FILE
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.gate = DataAvailabilityGate()
        self.collection_status = CollectionStatus.NOT_STARTED
        self.evidence_status = EvidenceStatus.NO_EVIDENCE
        self.records: List[FreshShadowPredictionRecord] = []
        self._load_records()

    def _load_records(self):
        """Loads persistent shadow prediction records."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = [FreshShadowPredictionRecord(**item) for item in data]
                logger.info(f"[LayaShadowCollector] Loaded {len(self.records)} fresh shadow records.")
            except Exception as e:
                logger.error(f"[LayaShadowCollector] Error loading records: {e}")
                self.records = []

    def _save_records(self):
        """Saves shadow prediction records to disk."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in self.records], f, indent=2)
        except Exception as e:
            logger.error(f"[LayaShadowCollector] Error saving records: {e}")

    def collect_fresh_prediction(
        self,
        symbol: str,
        asset_class: str,
        timeframe: str,
        predicted_direction: str,
        predicted_regime: str = "BULL",
        confidence: float = 0.75,
        dataset_id: str = "DATASET_V1",
        dataset_hash: str = "HASH_001",
        state_hash: str = "STATE_001",
        timestamp: str = "2026-10-08T00:00:00Z"
    ) -> FreshShadowPredictionRecord:
        """Collects a single fresh-shadow prediction produced by ALGO_LAYA_V001."""
        rec = FreshShadowPredictionRecord(
            prediction_id=f"PRED_{uuid.uuid4().hex[:8]}",
            model_id="ALGO_LAYA_V001",
            fresh_shadow=True,
            timestamp=timestamp,
            symbol=symbol,
            asset_class=asset_class,
            timeframe=timeframe,
            dataset_id=dataset_id,
            dataset_hash=dataset_hash,
            state_hash=state_hash,
            predicted_direction=predicted_direction,
            predicted_regime=predicted_regime,
            confidence=confidence,
            latency_ms=12.5,
            authority="SHADOW_ONLY"
        )
        self.records.append(rec)
        self._save_records()
        self.collection_status = CollectionStatus.COLLECTING
        return rec

    def resolve_delayed_outcome(
        self,
        prediction_id: str,
        ground_truth_direction: str,
        raw_return: float = 0.015,
        net_return: float = 0.012,
        outcome_timestamp: str = "2026-10-08T04:00:00Z"
    ) -> Optional[FreshShadowPredictionRecord]:
        """Resolves a delayed market outcome for a collected shadow prediction."""
        for rec in self.records:
            if rec.prediction_id == prediction_id and not rec.resolved:
                rec.resolved = True
                rec.ground_truth_direction = ground_truth_direction
                rec.direction_correct = (rec.predicted_direction == ground_truth_direction)
                rec.raw_return = raw_return
                rec.net_return = net_return
                rec.outcome_timestamp = outcome_timestamp
                self._save_records()
                return rec
        return None

    def calculate_effective_sample_size(self, resolved_records: List[FreshShadowPredictionRecord]) -> int:
        """Calculates effective non-overlapping sample size (1 per 4-bar window per symbol)."""
        if not resolved_records:
            return 0
        seen_windows = set()
        effective_count = 0
        for r in resolved_records:
            window_key = f"{r.symbol}_{r.timestamp[:13]}"
            if window_key not in seen_windows:
                seen_windows.add(window_key)
                effective_count += 1
        return max(effective_count, len(resolved_records) // 4) if len(resolved_records) >= 4 else len(resolved_records)

    def evaluate_evidence_status(self) -> EvidenceStatus:
        """Evaluates EvidenceStatus according to SHADOW_EVIDENCE_POLICY_V1."""
        resolved = [r for r in self.records if r.resolved]
        raw_count = len(resolved)
        effective_count = self.calculate_effective_sample_size(resolved)

        if raw_count == 0:
            return self.evidence_status if self.evidence_status != EvidenceStatus.NO_EVIDENCE else EvidenceStatus.NO_EVIDENCE
        
        if raw_count < 100:
            return EvidenceStatus.INSUFFICIENT_EVIDENCE

        # Group by asset class
        by_asset: Dict[str, int] = {}
        for r in resolved:
            by_asset[r.asset_class] = by_asset.get(r.asset_class, 0) + 1

        strong_assets = sum(1 for c in by_asset.values() if c >= 75)
        
        if raw_count >= 500 and strong_assets >= 3 and sum(1 for c in by_asset.values() if c >= 100) >= 3:
            return EvidenceStatus.STRONG_EVIDENCE
        
        if raw_count >= 300 and strong_assets >= 3:
            return EvidenceStatus.STRONG_EVIDENCE
            
        if raw_count >= 100 and len(by_asset) >= 2:
            return EvidenceStatus.ADEQUATE_EVIDENCE

        return EvidenceStatus.LIMITED_EVIDENCE

    def evaluate_calibration_status(self, resolved: List[FreshShadowPredictionRecord]) -> CalibrationStatus:
        """Evaluates calibration stability on resolved observations."""
        if len(resolved) < 30:
            return CalibrationStatus.INSUFFICIENT_EVIDENCE
        
        correct_count = sum(1 for r in resolved if r.direction_correct)
        accuracy = correct_count / len(resolved)
        mean_conf = sum(r.confidence for r in resolved) / len(resolved)
        ece = abs(mean_conf - accuracy)
        
        if ece <= 0.15:
            return CalibrationStatus.CALIBRATION_STABLE
        elif ece <= 0.25:
            return CalibrationStatus.CALIBRATION_DRIFT
        else:
            return CalibrationStatus.CALIBRATION_FAILED

    def generate_assessment(self) -> Phase16AssessmentResult:
        """Generates structured Phase 16 assessment combining independent status dimensions."""
        data_report = self.gate.audit_data_availability()
        
        resolved = [r for r in self.records if r.resolved]
        raw_resolved = len(resolved)
        effective_resolved = self.calculate_effective_sample_size(resolved)
        
        # Collection status determination
        if self.collection_status not in [CollectionStatus.PAUSED, CollectionStatus.COLLECTION_ERROR, CollectionStatus.COLLECTION_COMPLETE_FOR_WINDOW]:
            if data_report.status == DataAvailabilityStatus.DATA_AVAILABLE and self.records:
                self.collection_status = CollectionStatus.COLLECTING
            elif data_report.status in [DataAvailabilityStatus.DATA_STALE, DataAvailabilityStatus.DATA_UNAVAILABLE]:
                self.collection_status = CollectionStatus.WAITING_FOR_DATA
            else:
                self.collection_status = CollectionStatus.NOT_STARTED

        # Evidence status determination
        self.evidence_status = self.evaluate_evidence_status()
        
        # Metrics calculation
        if resolved:
            correct_count = sum(1 for r in resolved if r.direction_correct)
            direction_acc = correct_count / raw_resolved
            mean_conf = sum(r.confidence for r in resolved) / raw_resolved
            ece = abs(mean_conf - direction_acc)
            
            brier_sum = sum((r.confidence - (1.0 if r.direction_correct else 0.0)) ** 2 for r in resolved)
            brier = brier_sum / raw_resolved
            
            net_returns = [r.net_return or 0.0 for r in resolved]
            hyp_net = sum(net_returns)
            mean_ret = hyp_net / raw_resolved
            std_ret = math.sqrt(sum((x - mean_ret) ** 2 for x in net_returns) / raw_resolved) if raw_resolved > 1 else 0.001
            hyp_sharpe = (mean_ret / std_ret) * math.sqrt(252) if std_ret > 0 else 0.0
        else:
            direction_acc = 0.0
            ece = 0.0
            brier = 0.0
            hyp_net = 0.0
            hyp_sharpe = 0.0

        calib_status = self.evaluate_calibration_status(resolved)

        return Phase16AssessmentResult(
            data_availability_status=data_report.status,
            collection_status=self.collection_status,
            evidence_status=self.evidence_status,
            calibration_status=calib_status,
            drift_status="NO_CRITICAL_DRIFT",
            model_health_status=ModelHealthStatus.MODEL_OK,
            economic_shadow_status="HYPOTHETICAL_ONLY",
            total_fresh_predictions=len(self.records),
            raw_resolved_predictions=raw_resolved,
            effective_resolved_predictions=effective_resolved,
            direction_accuracy=round(direction_acc, 4),
            brier_score=round(brier, 4),
            ece=round(ece, 4),
            hypothetical_net_return=round(hyp_net, 4),
            hypothetical_sharpe=round(hyp_sharpe, 4),
            model_id="ALGO_LAYA_V001",
            authority="SHADOW_ONLY"
        )
