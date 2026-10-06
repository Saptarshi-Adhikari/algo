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

        # Check if numeric literal
        try:
            val = float(op_str)
            return pd.Series(val, index=df.index)
        except ValueError:
            pass

        # Dynamic Auto-Inference for missing indicator columns
        op_lower = op_str.lower()

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

        if op_lower in ["macd", "macd_line", "macd_signal", "macd_hist", "macd_diff"]:
            res = calculate_macd(df)
            for k, v in res.items():
                df[k] = v
            df["macd_line"] = df["macd"]
            df["macd_diff"] = df["macd_hist"]
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
            # Match bb_upper_\d+_\d+ pattern
            m_bb = re.match(r"^(bb_upper|bb_lower|bb_middle|upper_band|lower_band)", op_lower)
            if m_bb:
                base = m_bb.group(1)
                if base in ["bb_upper", "upper_band"]:
                    return df["bb_upper"]
                elif base in ["bb_lower", "lower_band"]:
                    return df["bb_lower"]
                elif base in ["bb_middle", "middle_band"]:
                    return df["bb_middle"]

        # Handle functional wrappers like volume(sma_20) or volume_sma_20 -> volume sma
        m_fn = re.match(r"^([a-z_]+)\(([a-z0-9_]+)\)$", op_lower)
        if m_fn:
            outer, inner = m_fn.group(1), m_fn.group(2)
            if outer == "volume":
                return self._resolve_operand(inner, df)

        # Fallback for LLM placing operators as operands (e.g. cond.left = "cross_above") -> return 0 series
        if op_lower in [">", "<", ">=", "<=", "==", "cross_above", "cross_below"]:
            return pd.Series(0.0, index=df.index)

        # Handle arithmetic expression strings (e.g. "sma_20 - 1.5 * atr_14" or "close + 2 * std_dev")
        # Split by + or - while respecting operator precedence
        if "+" in op_lower or "-" in op_lower or "*" in op_lower or "/" in op_lower:
            try:
                # Tokenize simple linear expressions safely using simple regex math
                tokens = re.split(r'(\+|\-|\*|\/)', op_lower)
                if len(tokens) > 1:
                    result_ser = None
                    curr_op = "+"
                    i = 0
                    while i < len(tokens):
                        token = tokens[i].strip()
                        if not token:
                            i += 1
                            continue
                        if token in ["+", "-", "*", "/"]:
                            curr_op = token
                            i += 1
                            continue
                        sub_ser = self._resolve_operand(token, df)
                        if result_ser is None:
                            result_ser = sub_ser
                        else:
                            if curr_op == "+":
                                result_ser = result_ser + sub_ser
                            elif curr_op == "-":
                                result_ser = result_ser - sub_ser
                            elif curr_op == "*":
                                result_ser = result_ser * sub_ser
                            elif curr_op == "/":
                                result_ser = result_ser / sub_ser
                        i += 1
                    if result_ser is not None:
                        return result_ser
            except Exception:
                pass

        raise KeyError(f"Operand '{operand}' not found in DataFrame columns {list(df.columns)}")

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
