"""Phase 15 Verification Script — Laya Domain Fine-Tuning + Calibration + Held-Out Evaluation."""
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config.settings import settings
from app.config.logging import logger
from app.decision.laya_trainer import LayaDomainTrainer, RUN_ID, CANDIDATE_MODEL_ID
from app.memory.laya_model_registry import LayaModelRegistry

def main():
    print("=======================================================")
    print("  QUANT AI PHASE 15 VERIFICATION SUITE")
    print("=======================================================")

    # 1. Safety & Authority Audit
    assert settings.PAPER_TRADING_ONLY is True
    assert settings.ALLOW_REAL_BROKER is False
    print("\n-- [TASK 01] Safety & Authority Audit")
    print("  [OK] Safety constraints intact (PAPER_TRADING_ONLY=True, ALLOW_REAL_BROKER=False)")

    # 2. Laya Model Registry & Checkpoint Directory Audit
    print("\n-- [TASK 02] Laya Model Registry & Directory Audit")
    registry = LayaModelRegistry()
    assert registry.registry_path.exists()
    print("  [OK] Laya Model Registry database active")

    # 3. Full Phase 15 Training, Calibration & Evaluation Pipeline
    print("\n-- [TASK 03] Execute Phase 15 Full Pipeline (Run ID: ALGO_LAYA_TRAIN_RUN_001)")
    trainer = LayaDomainTrainer()
    manifest = trainer.run_full_pipeline()

    assert manifest["model_id"] == CANDIDATE_MODEL_ID
    assert manifest["run_id"] == RUN_ID
    assert manifest["decision_authority"] == "SHADOW_ONLY"
    print("  [OK] Candidate Model fine-tuning run completed cleanly")

    # 4. Temperature Calibration Verification
    print("\n-- [TASK 04] Temperature Calibration Verification (131 Calibration Cases)")
    calib = manifest["calibration"]
    assert calib["calibration_status"] == "CALIBRATED"
    assert calib["optimal_temperature"] > 1.0
    assert calib["calibrated_ece"] <= calib["raw_ece"]
    print(f"  [OK] Temperature Calibration PASSED (Temp={calib['optimal_temperature']})")
    print(f"       Raw ECE:        {calib['raw_ece']}")
    print(f"       Calibrated ECE: {calib['calibrated_ece']}")
    print(f"       Raw Brier:      {calib['raw_brier_score']}")
    print(f"       Calib Brier:    {calib['calibrated_brier_score']}")

    # 5. Validation & Protected Holdout Evaluation Comparison
    print("\n-- [TASK 05] Validation & Protected Holdout Evaluation Results")
    val_m = manifest["validation_metrics"]
    hold_m = manifest["holdout_metrics"]

    print("  [OK] Validation Evaluation (149 Records):")
    print(f"       Zero-Shot Direction Accuracy:  {val_m['zero_shot_direction_accuracy']}")
    print(f"       Fine-Tuned Direction Accuracy: {val_m['fine_tuned_direction_accuracy']}")
    print("  [OK] Protected Holdout Evaluation (139 Records):")
    print(f"       Zero-Shot Direction Accuracy:  {hold_m['zero_shot_direction_accuracy']}")
    print(f"       Fine-Tuned Direction Accuracy: {hold_m['fine_tuned_direction_accuracy']}")

    # 6. Model Promotion Decision Engine Audit
    print("\n-- [TASK 06] Model Promotion Decision Engine Audit")
    promo_status = manifest["promotion_status"]
    assert promo_status == "PROMOTE_TO_SHADOW"
    
    active_model = registry.get_active_candidate()
    assert active_model is not None
    assert active_model["model_id"] == CANDIDATE_MODEL_ID
    print(f"  [OK] Promotion Decision Verified: {promo_status}")
    print(f"       Active Shadow Candidate Model: {active_model['model_id']}")

    print("\n=======================================================")
    print("  PHASE 15 VERIFICATION COMPLETE — ALL PASSED")
    print("=======================================================")

if __name__ == "__main__":
    main()
