"""Strategy Evaluator engine translating Pydantic StrategySpecs into deterministic signals."""
import pandas as pd
import numpy as np
from typing import Tuple, List
from app.domain.schemas import StrategySpec, ConditionSpec
from app.strategies.indicators import enrich_with_indicators

class StrategyEvaluator:
    """Evaluates strategy rules against OHLCV data to yield signal series (+1, -1, 0)."""

    def __init__(self, spec: StrategySpec):
        self.spec = spec

    def _resolve_operand(self, operand: str, df: pd.DataFrame) -> pd.Series:
        op_str = operand.strip()
        if op_str in df.columns:
            return df[op_str]

        # Check if numeric literal
        try:
            val = float(op_str)
            return pd.Series(val, index=df.index)
        except ValueError:
            pass

        # Lowercase fallback check
        if op_str.lower() in df.columns:
            return df[op_str.lower()]

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
        n = len(enriched_df)

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
