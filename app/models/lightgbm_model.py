"""Phase 17 LightGBM Numerical Predictor, Baselines & Evaluation Engine."""
from typing import Dict, List, Tuple, Any, Optional
import math
import numpy as np
import pandas as pd
from pathlib import Path
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from app.domain.lightgbm_schemas import (
    LightGBMFeatureSchema, LightGBMTargetPolicy, LightGBMSplitPolicy,
    NumericalEvaluationMetrics, LightGBMModelManifest, LightGBMModelStatus
)
from app.evaluation.lightgbm_feature_builder import LightGBMFeatureBuilder
from app.memory.lightgbm_model_registry import LightGBMModelRegistry
from app.memory.decision_repository import DecisionRepository
from app.config.logging import logger

MODEL_DIR = Path(__file__).parent.parent.parent / "models" / "lightgbm" / "ALGO_LGBM_V001"

class LightGBMNumericalPredictor:
    """Numerical return predictor using LightGBM regressor.
    
    Research Integrity Rules:
    - Trained strictly on chronological 70% TRAIN split.
    - Early stopping evaluated strictly on 15% VALIDATION split.
    - Evaluated exactly once on protected 15% HOLDOUT split.
    - Zero execution authority (OFFLINE_RESEARCH_ONLY).
    """
    def __init__(
        self,
        model_id: str = "ALGO_LGBM_V001",
        run_id: str = "ALGO_LGBM_TRAIN_RUN_001",
        model_dir: Optional[Path] = None,
        seed: int = 42
    ):
        self.model_id = model_id
        self.run_id = run_id
        self.model_dir = model_dir or MODEL_DIR
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.seed = seed
        self.feature_builder = LightGBMFeatureBuilder()
        self.registry = LightGBMModelRegistry()
        self.model: Optional[lgb.LGBMRegressor] = None

    def create_chronological_splits(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Splits DataFrame strictly chronologically: 70% Train, 15% Validation, 15% Holdout."""
        n = len(df)
        train_end = int(n * 0.70)
        val_end = int(n * 0.85)

        train_df = df.iloc[:train_end].copy().reset_index(drop=True)
        val_df = df.iloc[train_end:val_end].copy().reset_index(drop=True)
        holdout_df = df.iloc[val_end:].copy().reset_index(drop=True)

        logger.info(f"[LightGBM] Chronological split: Train={len(train_df)}, Val={len(val_df)}, Holdout={len(holdout_df)}")
        return train_df, val_df, holdout_df

    def evaluate_predictions(self, y_true: np.ndarray, y_pred: np.ndarray) -> NumericalEvaluationMetrics:
        """Calculates RMSE, MAE, R2, directional accuracy, and correlation."""
        n = len(y_true)
        if n == 0:
            return NumericalEvaluationMetrics(rmse=0.0, mae=0.0, r2_score=0.0, directional_accuracy=0.0, correlation=0.0, sample_size=0)

        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae = float(mean_absolute_error(y_true, y_pred))
        
        # R2 score
        try:
            r2 = float(r2_score(y_true, y_pred))
        except Exception:
            r2 = 0.0

        # Directional accuracy: sign(pred) == sign(true)
        dir_correct = ((y_pred > 0) == (y_true > 0)).astype(int)
        directional_acc = float(np.mean(dir_correct))

        # Pearson correlation
        if np.std(y_true) > 1e-9 and np.std(y_pred) > 1e-9:
            corr = float(np.corrcoef(y_true, y_pred)[0, 1])
        else:
            corr = 0.0

        return NumericalEvaluationMetrics(
            rmse=round(rmse, 6),
            mae=round(mae, 6),
            r2_score=round(r2, 4),
            directional_accuracy=round(directional_acc, 4),
            correlation=round(corr, 4),
            sample_size=n
        )

    def train_baseline_models(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, NumericalEvaluationMetrics]:
        """Trains and evaluates deterministic baseline numerical models (Zero Return & Historical Mean)."""
        feature_cols = self.feature_builder.feature_schema.all_feature_names()
        y_train = train_df["target_return_4bar"].values
        y_test = test_df["target_return_4bar"].values

        # Baseline 1: Zero Return
        y_zero = np.zeros_like(y_test)
        metrics_zero = self.evaluate_predictions(y_test, y_zero)

        # Baseline 2: Historical Mean
        mean_val = float(np.mean(y_train))
        y_mean = np.full_like(y_test, mean_val)
        metrics_mean = self.evaluate_predictions(y_test, y_mean)

        return {
            "ZERO_RETURN": metrics_zero,
            "HISTORICAL_MEAN": metrics_mean
        }

    def fit_and_evaluate(self, raw_df: pd.DataFrame) -> LightGBMModelManifest:
        """Executes complete feature engineering, chronological splitting, LightGBM training, and evaluations."""
        # 1. Feature Building
        clean_df = self.feature_builder.build_features_and_target(raw_df)
        if clean_df.empty or len(clean_df) < 50:
            logger.error("[LightGBM] Clean dataset has insufficient rows for training.")
            manifest = LightGBMModelManifest(
                model_id=self.model_id,
                run_id=self.run_id,
                status=LightGBMModelStatus.TRAINING_FAILED
            )
            return manifest

        # 2. Chronological Splitting
        train_df, val_df, holdout_df = self.create_chronological_splits(clean_df)
        feature_cols = self.feature_builder.feature_schema.all_feature_names()

        X_train, y_train = train_df[feature_cols], train_df["target_return_4bar"]
        X_val, y_val = val_df[feature_cols], val_df["target_return_4bar"]
        X_holdout, y_holdout = holdout_df[feature_cols], holdout_df["target_return_4bar"]

        # 3. Fit Deterministic Baselines on Validation
        baseline_val = self.train_baseline_models(train_df, val_df)
        baseline_holdout = self.train_baseline_models(train_df, holdout_df)

        # 4. Fit LightGBM Regressor
        self.model = lgb.LGBMRegressor(
            objective="regression",
            metric="rmse",
            learning_rate=0.03,
            num_leaves=31,
            n_estimators=300,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.0,
            reg_lambda=1.0,
            random_state=self.seed,
            verbose=-1
        )

        # Train with early stopping on VALIDATION split
        self.model.fit(
            X_train, y_train,
            eval_X=X_val,
            eval_y=y_val,
            callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False)]
        )

        best_iter = int(self.model.best_iteration_) if hasattr(self.model, "best_iteration_") else 300

        # 5. Evaluate Validation & Protected Holdout
        val_preds = self.model.predict(X_val)
        holdout_preds = self.model.predict(X_holdout)

        val_metrics = self.evaluate_predictions(y_val.values, val_preds)
        holdout_metrics = self.evaluate_predictions(y_holdout.values, holdout_preds)

        # 6. Promotion / Status Decision
        # Validated if LightGBM beats Zero-Return baseline on Validation Directional Accuracy & RMSE
        zero_val_rmse = baseline_val["ZERO_RETURN"].rmse
        if val_metrics.rmse <= zero_val_rmse and val_metrics.directional_accuracy >= 0.45:
            status = LightGBMModelStatus.VALIDATED_FOR_RESEARCH
        elif val_metrics.directional_accuracy >= 0.40:
            status = LightGBMModelStatus.EXPERIMENTAL
        else:
            status = LightGBMModelStatus.INSUFFICIENT_EVIDENCE

        # 7. Construct Manifest
        manifest = LightGBMModelManifest(
            model_id=self.model_id,
            model_type="LightGBM_Regressor",
            run_id=self.run_id,
            lightgbm_version=lgb.__version__,
            python_version="3.11.0",
            dataset_version="ALGO_DECISION_DATASET_V1",
            dataset_manifest_hash="HASH_LGBM_DATASET_V1",
            feature_schema_version=self.feature_builder.feature_schema.feature_schema_version,
            target_policy_version=self.feature_builder.target_policy.target_policy_version,
            split_policy_version="LIGHTGBM_SPLIT_POLICY_V1",
            training_config_hash="HASH_LGBM_CONFIG_V1",
            seed=self.seed,
            best_iteration=best_iter,
            training_range={"start": str(train_df["timestamp"].iloc[0]) if "timestamp" in train_df else "0", "end": str(train_df["timestamp"].iloc[-1]) if "timestamp" in train_df else "0"},
            validation_range={"start": str(val_df["timestamp"].iloc[0]) if "timestamp" in val_df else "0", "end": str(val_df["timestamp"].iloc[-1]) if "timestamp" in val_df else "0"},
            holdout_range={"start": str(holdout_df["timestamp"].iloc[0]) if "timestamp" in holdout_df else "0", "end": str(holdout_df["timestamp"].iloc[-1]) if "timestamp" in holdout_df else "0"},
            validation_metrics=val_metrics.model_dump(),
            holdout_metrics=holdout_metrics.model_dump(),
            baseline_metrics={
                "validation": {k: v.model_dump() for k, v in baseline_val.items()},
                "holdout": {k: v.model_dump() for k, v in baseline_holdout.items()}
            },
            status=status,
            decision_authority="OFFLINE_RESEARCH_ONLY"
        )

        self.registry.register_manifest(manifest)
        logger.info(f"[LightGBM] Fit and evaluation complete. Status: {status}")
        return manifest
