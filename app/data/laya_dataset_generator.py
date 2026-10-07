"""Laya Dataset Generator for ALGO Phase 14 fine-tuning readiness."""
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from app.domain.decision_schemas import DecisionRecord
from app.domain.laya_questions_v2 import LAYA_QUESTION_SET_V2, LAYA_QUESTION_SET_V2_VERSION
from app.decision.laya_target_policy import LayaTargetPolicy, TARGET_POLICY_VERSION, DISTRIBUTION_POLICY_VERSION
from app.memory.decision_repository import DecisionRepository
from app.config.settings import settings
from app.config.logging import logger

DATASET_VERSION = "ALGO_LAYA_DATASET_V1"

class LayaDatasetGenerator:
    """Generates Laya-compatible JSONL dataset files and metadata manifest."""

    def __init__(self, output_dir: Path = None, repo: DecisionRepository = None):
        if output_dir is None:
            output_dir = getattr(settings, "DATA_DIR", Path(__file__).parent.parent.parent / "data") / "laya"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.repo = repo or DecisionRepository()

    def generate_all_splits(self) -> Dict[str, Any]:
        """Generates train, calibration, validation, and holdout JSONL files."""
        dev_records = self.repo.list_by_split("DEVELOPMENT")
        val_records = self.repo.list_by_split("VALIDATION")
        holdout_records = self.repo.list_by_split("HOLDOUT")

        # Split DEVELOPMENT into LAYA_TRAIN (80%) and LAYA_CALIBRATION (20%)
        split_idx = int(len(dev_records) * 0.8)
        train_records = dev_records[:split_idx]
        calib_records = dev_records[split_idx:]

        train_file = self.output_dir / "train.jsonl"
        calib_file = self.output_dir / "calibration.jsonl"
        val_file = self.output_dir / "validation.jsonl"
        holdout_file = self.output_dir / "holdout.jsonl"

        train_count = self._write_jsonl(train_records, train_file)
        calib_count = self._write_jsonl(calib_records, calib_file)
        val_count = self._write_jsonl(val_records, val_file)
        holdout_count = self._write_jsonl(holdout_records, holdout_file)

        manifest = {
            "dataset_version": DATASET_VERSION,
            "question_schema_version": LAYA_QUESTION_SET_V2_VERSION,
            "target_policy_version": TARGET_POLICY_VERSION,
            "distribution_policy_version": DISTRIBUTION_POLICY_VERSION,
            "record_counts": {
                "train": train_count,
                "calibration": calib_count,
                "validation": val_count,
                "holdout": holdout_count,
                "total": train_count + calib_count + val_count + holdout_count
            },
            "split_definition": {
                "train_source": "DEVELOPMENT (80% chronological slice)",
                "calibration_source": "DEVELOPMENT (20% chronological slice)",
                "validation_source": "VALIDATION (100% Phase 11 validation set)",
                "holdout_source": "HOLDOUT (100% protected Phase 11 holdout set)"
            },
            "files": {
                "train": str(train_file),
                "calibration": str(calib_file),
                "validation": str(val_file),
                "holdout": str(holdout_file)
            },
            "fine_tuning_executed": False,
            "model_weights_mutated": False,
            "decision_authority": "SHADOW_ONLY"
        }

        manifest_file = self.output_dir / "dataset_manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Laya dataset generation complete at {self.output_dir}")
        return manifest

    def _write_jsonl(self, records: List[DecisionRecord], output_path: Path) -> int:
        count = 0
        with open(output_path, "w", encoding="utf-8") as f:
            for rec in records:
                gold_targets = LayaTargetPolicy.compute_gold_targets(rec)
                soft_dists = LayaTargetPolicy.compute_soft_distribution(rec)

                # Format answers compatible with Laya v0.3.5
                answers = {
                    "market_regime_v2": {"choice": gold_targets["market_regime_v2"]},
                    "direction_v2": {"choice": gold_targets["direction_v2"]},
                    "trade_permission_v2": {"choice": gold_targets["trade_permission_v2"]},
                    "risk_level_v2": {"choice": gold_targets["risk_level_v2"]}
                }

                features_dict = getattr(rec.state, "custom_features", {}) or getattr(rec.state, "features", {}) or {}

                # Causal State formatting
                state_dict = {
                    "symbol": rec.symbol,
                    "market": str(rec.market),
                    "timeframe": rec.timeframe,
                    "timestamp": rec.timestamp,
                    "regime": rec.state.regime,
                    "features": features_dict
                }

                item = {
                    "state": state_dict,
                    "questions": LAYA_QUESTION_SET_V2,
                    "gold": {
                        "answers": answers,
                        "soft_distributions": soft_dists
                    }
                }

                f.write(json.dumps(item) + "\n")
                count += 1
        return count
