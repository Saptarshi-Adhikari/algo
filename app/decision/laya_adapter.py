"""Isolated Laya Adapter and Shadow Inference Layer for ALGO (Phase 13)."""
import time
import json
from typing import Dict, Any, Optional, List
from app.domain.decision_schemas import MarketState
from app.domain.laya_schemas import LayaPredictionResult
from app.config.logging import logger

class LayaAdapter:
    """Isolated integration adapter exposing a stable ALGO prediction interface for Laya v0.3.5."""

    def __init__(self, model_id: str = "convaiinnovations/laya", device: Optional[str] = None):
        self.model_id = model_id
        self.device = device
        self._agent = None
        self._is_loaded = False
        self._load_error = None

    def _ensure_loaded(self) -> bool:
        if self._is_loaded:
            return True
        if self._load_error:
            return False

        try:
            import laya
            logger.info(f"Initializing Laya Agent (model={self.model_id})...")
            # Lazy load Laya agent
            self._agent = laya.Agent(model_id_or_path=self.model_id, device=self.device)
            self._is_loaded = True
            return True
        except Exception as e:
            self._load_error = str(e)
            logger.warning(f"Laya Agent initialization unavailable/failed: {e}")
            return False

    @staticmethod
    def build_laya_questions() -> Dict[str, Dict[str, Any]]:
        """Constructs Laya v0.3.5 typed question dictionary matching LAYA_DECISION_SCHEMA_V1."""
        return {
            "q_market_regime": {
                "type": "choice",
                "instructions": "Determine the current market regime.",
                "criteria": {
                    "TRENDING": "Strong directional trend in progress",
                    "RANGING": "Price bound within historical range",
                    "HIGH_VOLATILITY": "Large high-low price swings",
                    "LOW_VOLATILITY": "Low price movement range",
                    "UNKNOWN": "Unclear or regime undetermined"
                }
            },
            "q_direction": {
                "type": "choice",
                "instructions": "Determine the optimal directional position stance for the next 4 bars.",
                "criteria": {
                    "BUY": "Expected positive return over horizon",
                    "SELL": "Expected negative return over horizon",
                    "HOLD": "No strong directional bias or expected sideways return"
                }
            },
            "q_strategy_family": {
                "type": "choice",
                "instructions": "Select the strategy family most appropriate for the current market state.",
                "criteria": {
                    "TREND": "Trend following strategies",
                    "MOMENTUM": "Momentum strategies",
                    "MEAN_REVERSION": "Mean reversion strategies",
                    "BREAKOUT": "Breakout strategies",
                    "PRICE_ACTION": "Price action strategies",
                    "CANDLESTICK": "Candlestick pattern strategies",
                    "VOLATILITY": "Volatility expansion strategies",
                    "NONE": "No applicable strategy family"
                }
            },
            "q_trade_permission": {
                "type": "choice",
                "instructions": "Should a trade be permitted based on risk profile?",
                "criteria": {
                    "ALLOW": "Risk is within acceptable parameters",
                    "REJECT": "Risk is excessive or adverse excursion is high"
                }
            },
            "q_risk": {
                "type": "choice",
                "instructions": "Assess the risk level of taking a trade position.",
                "criteria": {
                    "LOW": "Low risk of adverse drawdown",
                    "MEDIUM": "Moderate risk of drawdown",
                    "HIGH": "High risk of adverse drawdown"
                }
            }
        }

    def predict(self, state: MarketState, decision_id: Optional[str] = None) -> LayaPredictionResult:
        """Executes shadow inference over a MarketState snapshot."""
        start_time = time.time()
        dec_id = decision_id or f"SHADOW_LAYA_{state.symbol}_{int(time.time()*1000)}"

        # Prepare Laya State representation (strictly causal fields)
        laya_state = state.model_dump(exclude_none=True)
        laya_questions = self.build_laya_questions()

        if not self._ensure_loaded():
            # Return graceful structured error result if model fails to load
            elapsed = (time.time() - start_time) * 1000.0
            return LayaPredictionResult(
                decision_id=dec_id,
                timestamp=state.timestamp,
                symbol=state.symbol,
                market=state.market,
                timeframe=state.timeframe,
                dataset_id=state.dataset_id,
                dataset_hash=state.dataset_hash,
                state_hash=state.dataset_hash,
                confidence_status="UNCALIBRATED",
                decision_authority="SHADOW_ONLY",
                latency_ms=round(elapsed, 2),
                status="MODEL_UNAVAILABLE",
                error_message=self._load_error or "Laya model unavailable"
            )

        try:
            # Execute Laya predict call
            raw_out = self._agent.predict(state=laya_state, questions=laya_questions)
            elapsed = (time.time() - start_time) * 1000.0

            # Extract typed outputs cleanly from Laya v0.3.5 'answers' dict
            answers_dict = raw_out.get("answers", raw_out)
            regime_pred = answers_dict.get("q_market_regime", {}).get("choice") or answers_dict.get("q_market_regime", {}).get("answer") or "UNKNOWN"
            dir_pred = answers_dict.get("q_direction", {}).get("choice") or answers_dict.get("q_direction", {}).get("answer") or "HOLD"
            fam_pred = answers_dict.get("q_strategy_family", {}).get("choice") or answers_dict.get("q_strategy_family", {}).get("answer") or "NONE"
            perm_pred = answers_dict.get("q_trade_permission", {}).get("choice") or answers_dict.get("q_trade_permission", {}).get("answer") or "REJECT"
            risk_pred = answers_dict.get("q_risk", {}).get("choice") or answers_dict.get("q_risk", {}).get("answer") or "HIGH"

            # Observe raw confidence scores if available (marked UNCALIBRATED)
            conf_val = answers_dict.get("q_direction", {}).get("confidence")

            return LayaPredictionResult(
                decision_id=dec_id,
                timestamp=state.timestamp,
                symbol=state.symbol,
                market=state.market,
                timeframe=state.timeframe,
                dataset_id=state.dataset_id,
                dataset_hash=state.dataset_hash,
                state_hash=state.dataset_hash,
                predicted_regime=regime_pred,
                predicted_direction=dir_pred,
                predicted_strategy_family=fam_pred,
                predicted_trade_permission=perm_pred,
                predicted_risk=risk_pred,
                raw_predictions=raw_out,
                confidence=conf_val,
                confidence_status="UNCALIBRATED",
                decision_authority="SHADOW_ONLY",
                model_name=self.model_id,
                model_version="0.3.5",
                latency_ms=round(elapsed, 2),
                status="SUCCESS"
            )

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000.0
            logger.error(f"Laya shadow inference error: {e}")
            return LayaPredictionResult(
                decision_id=dec_id,
                timestamp=state.timestamp,
                symbol=state.symbol,
                market=state.market,
                timeframe=state.timeframe,
                dataset_id=state.dataset_id,
                dataset_hash=state.dataset_hash,
                state_hash=state.dataset_hash,
                confidence_status="UNCALIBRATED",
                decision_authority="SHADOW_ONLY",
                latency_ms=round(elapsed, 2),
                status="MODEL_ERROR",
                error_message=str(e)
            )
