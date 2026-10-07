"""Strategy Evaluator engine translating Pydantic StrategySpecs into deterministic signals."""
import re
import pandas as pd
import numpy as np
from typing import Tuple, List
from app.domain.schemas import StrategySpec, ConditionSpec
from app.strategies.indicators import (
    enrich_with_indicators, calculate_sma, calculate_ema, calculate_rsi,
    calculate_macd, calculate_bollinger_bands, calculate_atr
)

class StrategyEvaluator:
    """Evaluates strategy rules against OHLCV data to yield signal series (+1, -1, 0)."""

    def __init__(self, spec: StrategySpec):
        self.spec = spec

    def _resolve_operand(self, operand: str, df: pd.DataFrame) -> pd.Series:
        op_str = operand.strip()
        if op_str in df.columns:
            return df[op_str]

        # Lowercase fallback check
        if op_str.lower() in df.columns:
            return df[op_str.lower()]

        op_lower = op_str.lower()

        # If expression contains arithmetic operators or parentheses, pass to AST evaluator first
        if any(char in op_lower for char in ["+", "-", "*", "/", "(", ")"]):
            try:
                from app.strategies.expr_evaluator import SafeExpressionEvaluator
                evaluator = SafeExpressionEvaluator(df, lambda tok, d: self._resolve_operand(tok, d))
                return evaluator.evaluate(op_lower)
            except Exception:
                pass

        # Check if plain numeric literal
        try:
            val = float(op_str)
            return pd.Series(val, index=df.index)
        except ValueError:
            pass

        # Dynamic Auto-Inference for missing indicator columns
        op_lower = op_str.lower()

        # Handle dot notation (e.g. "macd.macd_line" -> "macd_line" or "macd.signal" -> "macd_signal")
        if "." in op_lower:
            parts = op_lower.split(".")
            sub_token = parts[-1]
            if sub_token in df.columns:
                return df[sub_token]
            op_lower = sub_token

        # Match sma_N or ema_N or rsi_N or atr_N
        m_sma = re.match(r"^sma_(\d+)$", op_lower)
        if m_sma:
            period = int(m_sma.group(1))
            df[op_lower] = calculate_sma(df, period)
            return df[op_lower]

        m_ema = re.match(r"^ema_(\d+)$", op_lower)
        if m_ema:
            period = int(m_ema.group(1))
            df[op_lower] = calculate_ema(df, period)
            return df[op_lower]

        m_rsi = re.match(r"^rsi_(\d+)$", op_lower)
        if m_rsi:
            period = int(m_rsi.group(1))
            df[op_lower] = calculate_rsi(df, period)
            return df[op_lower]

        m_atr = re.match(r"^atr_(\d+)$", op_lower)
        if m_atr:
            period = int(m_atr.group(1))
            df[op_lower] = calculate_atr(df, period)
            return df[op_lower]

        if op_lower in ["macd", "macd_line", "macd_signal", "macd_hist", "macd_diff", "signal_line", "macd_signal_line", "signal"]:
            res = calculate_macd(df)
            for k, v in res.items():
                df[k] = v
            df["macd_line"] = df["macd"]
            df["macd_diff"] = df["macd_hist"]
            df["signal_line"] = df["macd_signal"]
            df["macd_signal_line"] = df["macd_signal"]
            if op_lower in df.columns:
                return df[op_lower]

        # Match upper_band / lower_band / middle_band / bb_upper_X_Y / bb_lower_X_Y
        if "upper" in op_lower or "lower" in op_lower or "middle" in op_lower or "bb" in op_lower:
            res = calculate_bollinger_bands(df)
            for k, v in res.items():
                df[k] = v
            df["lower_band_bb"] = df["bb_lower"]
            df["upper_band_bb"] = df["bb_upper"]
            df["middle_band_bb"] = df["bb_middle"]
            df["bb_lower_band"] = df["bb_lower"]
            df["bb_upper_band"] = df["bb_upper"]
            df["upper_band"] = df["bb_upper"]
            df["lower_band"] = df["bb_lower"]
            df["middle_band"] = df["bb_middle"]
            if op_lower in df.columns:
                return df[op_lower]
            # Match bb_upper_\d+_\d+ or lower_bb_\d+_\d+ pattern
            m_bb = re.match(r"^(bb_upper|bb_lower|bb_middle|upper_band|lower_band|upper_bb|lower_bb|middle_bb)", op_lower)
            if m_bb:
                base = m_bb.group(1)
                if base in ["bb_upper", "upper_band", "upper_bb"]:
                    return df["bb_upper"]
                elif base in ["bb_lower", "lower_band", "lower_bb"]:
                    return df["bb_lower"]
                elif base in ["bb_middle", "middle_band", "middle_bb"]:
                    return df["bb_middle"]

        # Handle functional wrappers like volume(sma_20) or close(-1)
        m_fn = re.match(r"^([a-z_]+)\(([\-0-9a-z_]+)\)$", op_lower)
        if m_fn:
            outer, inner = m_fn.group(1), m_fn.group(2)
            if outer in df.columns:
                try:
                    shift_val = int(inner)
                    return df[outer].shift(-shift_val if shift_val < 0 else shift_val)
                except ValueError:
                    return df[outer]
            if outer == "volume":
                return self._resolve_operand(inner, df)

        # Match unparameterized indicator names (e.g. rsi -> rsi_14, atr -> atr_14)
        if op_lower in ["rsi", "atr", "sma", "ema"]:
            for col in df.columns:
                if col.startswith(f"{op_lower}_"):
                    return df[col]
            if op_lower == "rsi":
                df["rsi_14"] = calculate_rsi(df, 14)
                return df["rsi_14"]
            elif op_lower == "atr":
                df["atr_14"] = calculate_atr(df, 14)
                return df["atr_14"]

        # Match volume_sma_N or sma_N_volume or volume_rolling_mean pattern
        if "volume_rolling_mean" in op_lower or "rolling_mean" in op_lower:
            df[op_lower] = calculate_sma(df, 20, column="volume" if "volume" in op_lower else "close")
            return df[op_lower]

        m_v_sma = re.match(r"^(volume_sma_|sma_)(\d+)(_volume)?$", op_lower)
        if m_v_sma:
            period = int(m_v_sma.group(2))
            df[op_lower] = calculate_sma(df, period)
            return df[op_lower]

        # Handle any asset/symbol name used as operand fallback (e.g. "synth_ind", "synthetic_ind" or "reliance.ns" -> use close price)
        if op_lower in ["synthetic_ind", "synth_ind", "reliance.ns", "nifty50", "asset", "equity", "stock"]:
            return df["close"]

        # Fallback for LLM placing operators as operands (e.g. cond.left = "cross_above") -> return 0 series
        if op_lower in [">", "<", ">=", "<=", "==", "cross_above", "cross_below"]:
            return pd.Series(0.0, index=df.index)

        # Handle comma-separated list of indicators generated by LLM (e.g. "ema_8, ema_21") -> take first item
        if "," in op_lower:
            op_lower = op_lower.split(",")[0].strip()
            if op_lower in df.columns:
                return df[op_lower]

        return self._resolve_single_token(op_lower, df)

    def _resolve_single_token(self, token: str, df: pd.DataFrame) -> pd.Series:
        op_lower = token.strip().lower()
        if op_lower in df.columns:
            return df[op_lower]

        # Handle dot notation (e.g. "macd.macd_line" -> "macd_line")
        if "." in op_lower:
            sub_token = op_lower.split(".")[-1]
            if sub_token in df.columns:
                return df[sub_token]
            op_lower = sub_token

        # Match sma_N, ema_N, rsi_N, atr_N
        m_sma = re.match(r"^sma_(\d+)$", op_lower)
        if m_sma:
            period = int(m_sma.group(1))
            df[op_lower] = calculate_sma(df, period)
            return df[op_lower]

        m_ema = re.match(r"^ema_(\d+)$", op_lower)
        if m_ema:
            period = int(m_ema.group(1))
            df[op_lower] = calculate_ema(df, period)
            return df[op_lower]

        m_rsi = re.match(r"^rsi_(\d+)$", op_lower)
        if m_rsi:
            period = int(m_rsi.group(1))
            df[op_lower] = calculate_rsi(df, period)
            return df[op_lower]

        m_atr = re.match(r"^atr_(\d+)$", op_lower)
        if m_atr:
            period = int(m_atr.group(1))
            df[op_lower] = calculate_atr(df, period)
            return df[op_lower]

        # Handle VWAP or Volume-Weighted Average Price fallback
        if "vwap" in op_lower:
            df["vwap"] = (df["high"] + df["low"] + df["close"]) / 3.0
            return df["vwap"]

        # Handle Bollinger Bands aliases (e.g. bb_20_upperband, bb_20_lowerband, bb_20_lower, 0_lower, 0_mid, bb_upperband, bb_lowerband)
        m_bb_alias = re.search(r"(upper|lower|middle|mid)", op_lower)
        if "bb" in op_lower or "band" in op_lower or m_bb_alias:
            m_num = re.search(r"(\d+)", op_lower)
            period = int(m_num.group(1)) if m_num else 20
            res = calculate_bollinger_bands(df, period=period)
            for k, v in res.items():
                df[k] = v
            if m_bb_alias and "upper" in m_bb_alias.group(1):
                df[op_lower] = res["bb_upper"]
            elif m_bb_alias and "lower" in m_bb_alias.group(1):
                df[op_lower] = res["bb_lower"]
            else:
                df[op_lower] = res["bb_middle"]
            return df[op_lower]

        # Handle semantic column aliases generated by LLM (e.g. previous_close, high_1d, low_1d)
        if op_lower in ["previous_close", "prev_close", "close_1d"]:
            return df["close"].shift(1)
        if op_lower in ["high_1d", "high_daily", "daily_high"]:
            return df["high"]
        if op_lower in ["low_1d", "low_daily", "daily_low"]:
            return df["low"]
        if op_lower in ["open_1d", "open_daily", "daily_open"]:
            return df["open"]
        if op_lower in ["volume_1d", "volume_daily", "daily_volume"]:
            return df["volume"]

        # Handle MACD signal alias 'signal'
        if op_lower in ["signal", "macd_signal_line", "signal_line"]:
            if "macd_signal" in df.columns:
                return df["macd_signal"]
            res = calculate_macd(df)
            for k, v in res.items():
                df[k] = v
            df["signal"] = df["macd_signal"]
            return df["macd_signal"]

        # Strip quotes, percentage signs, and dollar symbols generated by LLMs (e.g. "5%", "'5%'", "10%")
        clean_token = op_lower.replace("%", "").replace("'", "").replace('"', "").replace("$", "").replace("inr", "").strip()

        try:
            val = float(clean_token)
            return pd.Series(val, index=df.index)
        except ValueError:
            pass

        raise KeyError(f"Operand '{token}' not found in DataFrame columns {list(df.columns)}")

    def _evaluate_condition(self, cond: ConditionSpec, df: pd.DataFrame) -> pd.Series:
        left_ser = self._resolve_operand(cond.left, df)
        right_ser = self._resolve_operand(cond.right, df)

        op = cond.operator
        if op == ">":
            return left_ser > right_ser
        elif op == "<":
            return left_ser < right_ser
        elif op == ">=":
            return left_ser >= right_ser
        elif op == "<=":
            return left_ser <= right_ser
        elif op == "==":
            return left_ser == right_ser
        elif op == "cross_above":
            prev_left = left_ser.shift(1)
            prev_right = right_ser.shift(1)
            return (prev_left <= prev_right) & (left_ser > right_ser)
        elif op == "cross_below":
            prev_left = left_ser.shift(1)
            prev_right = right_ser.shift(1)
            return (prev_left >= prev_right) & (left_ser < right_ser)
        else:
            raise ValueError(f"Unsupported operator '{op}'")

    def evaluate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enriches data and returns DataFrame containing entry_signal and exit_signal columns."""
        from app.strategies.future_validator import FutureDataReferenceValidator
        FutureDataReferenceValidator.validate_strategy(self.spec)

        enriched_df = enrich_with_indicators(df, self.spec.indicators)

        entry_mask = pd.Series(True, index=enriched_df.index)
        if self.spec.rules.entry_rules:
            for cond in self.spec.rules.entry_rules:
                res = self._evaluate_condition(cond, enriched_df)
                entry_mask = entry_mask & res
        else:
            entry_mask = pd.Series(False, index=enriched_df.index)

        exit_mask = pd.Series(False, index=enriched_df.index)
        if self.spec.rules.exit_rules:
            for cond in self.spec.rules.exit_rules:
                res = self._evaluate_condition(cond, enriched_df)
                exit_mask = exit_mask | res

        enriched_df["entry_signal"] = entry_mask.astype(int)
        enriched_df["exit_signal"] = exit_mask.astype(int)
        return enriched_df
