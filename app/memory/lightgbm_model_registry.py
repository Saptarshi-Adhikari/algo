"""LightGBM Model Registry for managing candidate manifests and checkpoints (Phase 17)."""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from app.domain.lightgbm_schemas import LightGBMModelManifest, LightGBMModelStatus
from app.config.logging import logger

DEFAULT_REGISTRY_PATH = Path(__file__).parent.parent.parent / "models" / "lightgbm" / "lgbm_registry.json"

class LightGBMModelRegistry:
    """Manages immutable candidate model records and manifest database for LightGBM models."""

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or DEFAULT_REGISTRY_PATH
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifests: Dict[str, LightGBMModelManifest] = {}
        self._load_registry()

    def _load_registry(self):
        """Loads registered model manifests from JSON storage."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        m = LightGBMModelManifest(**item)
                        self.manifests[m.model_id] = m
                logger.info(f"[LightGBMModelRegistry] Loaded {len(self.manifests)} LightGBM manifests.")
            except Exception as e:
                logger.error(f"[LightGBMModelRegistry] Failed loading registry: {e}")
                self.manifests = {}

    def _save_registry(self):
        """Saves registered model manifests to JSON storage."""
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump([m.model_dump() for m in self.manifests.values()], f, indent=2)
        except Exception as e:
            logger.error(f"[LightGBMModelRegistry] Failed saving registry: {e}")

    def register_manifest(self, manifest: LightGBMModelManifest):
        """Registers or updates a LightGBM model manifest."""
        if not manifest.created_at:
            manifest.created_at = datetime.utcnow().isoformat()
        self.manifests[manifest.model_id] = manifest
        self._save_registry()
        logger.info(f"[LightGBMModelRegistry] Registered model: {manifest.model_id} (Status: {manifest.status})")

    def get_manifest(self, model_id: str) -> Optional[LightGBMModelManifest]:
        """Retrieves a registered model manifest by ID."""
        return self.manifests.get(model_id)

    def list_all(self) -> List[LightGBMModelManifest]:
        """Lists all registered LightGBM model manifests."""
        return list(self.manifests.values())
