"""Data Splitter engine for non-overlapping Development, Validation, and Holdout sets."""
from typing import Dict, Tuple
from app.data.base_provider import MarketData
from app.domain.schemas import DataSplitName

class HoldoutProtectionError(PermissionError):
    """Raised when an automated agent attempts unauthorized optimization on holdout data."""
    pass

class DataSplitter:
    """Splits MarketData into non-overlapping chronologically ordered sets."""

    def __init__(
        self,
        dev_pct: float = 0.60,
        val_pct: float = 0.20,
        holdout_pct: float = 0.20
    ):
        if not abs((dev_pct + val_pct + holdout_pct) - 1.0) < 1e-5:
            raise ValueError("Split percentages must sum to 1.0")
        self.dev_pct = dev_pct
        self.val_pct = val_pct
        self.holdout_pct = holdout_pct

    def split(self, data: MarketData) -> Dict[DataSplitName, MarketData]:
        df = data.df.copy()
        n = len(df)

        if n < 30:
            raise ValueError(f"Dataset for {data.symbol} is too small ({n} bars) to split safely.")

        dev_end_idx = int(n * self.dev_pct)
        val_end_idx = int(n * (self.dev_pct + self.val_pct))

        dev_df = df.iloc[:dev_end_idx].reset_index(drop=True)
        val_df = df.iloc[dev_end_idx:val_end_idx].reset_index(drop=True)
        holdout_df = df.iloc[val_end_idx:].reset_index(drop=True)

        return {
            "DEVELOPMENT": MarketData(data.symbol, data.market, data.timeframe, dev_df, {**data.metadata, "split": "DEVELOPMENT"}),
            "VALIDATION": MarketData(data.symbol, data.market, data.timeframe, val_df, {**data.metadata, "split": "VALIDATION"}),
            "HOLDOUT": MarketData(data.symbol, data.market, data.timeframe, holdout_df, {**data.metadata, "split": "HOLDOUT"})
        }

    @staticmethod
    def get_split_data(
        splits: Dict[DataSplitName, MarketData],
        split_name: DataSplitName,
        allow_holdout: bool = False
    ) -> MarketData:
        """Retrieve split data with holdout safety enforcement."""
        if split_name == "HOLDOUT" and not allow_holdout:
            raise HoldoutProtectionError(
                "HOLDOUT ACCESS BLOCKED: Automated strategy optimization/loop is not permitted to query "
                "the holdout dataset to prevent overfitting. Holdout access requires explicit manual approval."
            )
        return splits[split_name]
