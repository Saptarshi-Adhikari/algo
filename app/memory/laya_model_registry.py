"""Laya Model Registry for versioned candidate model manifest persistence."""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.config.settings import settings
from app.config.logging import logger

REGISTRY_FILE = Path(__file__).parent.parent.parent / "models" / "laya" / "model_registry.json"

class LayaModelRegistry:
    """Manages versioned model manifests and candidate model registries."""

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or REGISTRY_FILE
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_registry()

    def _init_registry(self) -> None:
        if not self.registry_path.exists():
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump({"models": {}, "active_candidate": None}, f, indent=2)

    def register_model(self, manifest: Dict[str, Any]) -> None:
        model_id = manifest["model_id"]
        data = self._load()
        data["models"][model_id] = manifest
        if manifest.get("promotion_status") == "PROMOTE_TO_SHADOW":
            data["active_candidate"] = model_id
        self._save(data)
        logger.info(f"Registered model {model_id} in Laya Model Registry with status {manifest.get('promotion_status')}")

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        data = self._load()
        return data["models"].get(model_id)

    def get_active_candidate(self) -> Optional[Dict[str, Any]]:
        data = self._load()
        active_id = data.get("active_candidate")
        return data["models"].get(active_id) if active_id else None

    def list_models(self) -> List[Dict[str, Any]]:
        data = self._load()
        return list(data["models"].values())

    def _load(self) -> Dict[str, Any]:
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
