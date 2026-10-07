"""Unit tests for Phase 15 Laya Domain Fine-Tuning, Calibration, and Evaluation."""
import pytest
import json
from pathlib import Path
from app.config.settings import settings
from app.memory.laya_model_registry import LayaModelRegistry
from app.decision.laya_trainer import LayaDomainTrainer, CANDIDATE_MODEL_ID, RUN_ID

def test_laya_model_registry(tmp_path):
    reg_file = tmp_path / "model_registry.json"
    registry = LayaModelRegistry(registry_path=reg_file)

    manifest = {
        "model_id": "TEST_MODEL_V1",
        "run_id": "RUN_TEST",
        "promotion_status": "PROMOTE_TO_SHADOW"
    }
    registry.register_model(manifest)

    fetched = registry.get_model("TEST_MODEL_V1")
    assert fetched is not None
    assert fetched["model_id"] == "TEST_MODEL_V1"

    active = registry.get_active_candidate()
    assert active is not None
    assert active["model_id"] == "TEST_MODEL_V1"

def test_laya_trainer_pipeline(tmp_path):
    data_dir = Path(__file__).parent.parent / "data" / "laya"
    models_dir = tmp_path / "models"

    trainer = LayaDomainTrainer(data_dir=data_dir, models_dir=models_dir)
    manifest = trainer.run_full_pipeline()

    assert manifest["model_id"] == CANDIDATE_MODEL_ID
    assert manifest["run_id"] == RUN_ID
    assert manifest["promotion_status"] == "PROMOTE_TO_SHADOW"
    assert manifest["calibration"]["calibration_status"] == "CALIBRATED"
    assert manifest["calibration"]["calibrated_ece"] <= manifest["calibration"]["raw_ece"]
    assert manifest["decision_authority"] == "SHADOW_ONLY"
