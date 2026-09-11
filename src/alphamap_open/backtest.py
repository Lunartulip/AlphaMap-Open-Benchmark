from __future__ import annotations

import numpy as np
import pandas as pd


def prepare_forward_returns(
    prices: pd.DataFrame,
    horizon: int = 20,
) -> pd.DataFrame:
    """Create forward adjusted and relative returns without calendar look-ahead."""
    required = {"date", "security_id", "adjusted_close"}
    missing = required - set(prices.columns)
    if missing:
        raise ValueError(f"prices missing columns: {sorted(missing)}")

    frame = prices.copy()
    frame["date"] = pd.to_datetime(frame["date"], utc=True).dt.normalize()
    frame = frame.sort_values(["security_id", "date"])
    forward_price = frame.groupby("security_id")["adjusted_close"].shift(-horizon)
    frame["forward_return"] = forward_price / frame["adjusted_close"] - 1.0

    universe_benchmark = frame.groupby("date")["forward_return"].transform("mean")
    if "sector" in frame.columns:
        group = frame.groupby(["date", "sector"])["forward_return"]
        sector_benchmark = group.transform("mean")
        sector_size = group.transform("count")
        frame["benchmark_source"] = np.where(
            sector_size >= 3, "sector", "universe_fallback"
        )
        benchmark = sector_benchmark.where(sector_size >= 3, universe_benchmark)
    else:
        frame["benchmark_source"] = "universe"
        benchmark = universe_benchmark
    frame["forward_relative_return"] = frame["forward_return"] - benchmark
    return frame


def evaluate_rank_ic(
    features: pd.DataFrame,
    returns: pd.DataFrame,
    minimum_cross_section: int = 5,
) -> tuple[pd.DataFrame, dict[str, float | int]]:
    merged = features.merge(
        returns[["date", "security_id", "forward_relative_return"]],
        on=["date", "security_id"],
        how="inner",
        validate="one_to_one",
    ).dropna(subset=["feature", "forward_relative_return"])

    def calculate(group: pd.DataFrame) -> float:
        if len(group) < minimum_cross_section:
            return float("nan")
        return float(
            group["feature"].rank().corr(group["forward_relative_return"].rank())
        )

    series = merged.groupby("date").apply(calculate, include_groups=False).dropna()
    by_date = series.rename("rank_ic").reset_index()
    summary: dict[str, float | int] = {
        "dates": int(len(by_date)),
        "mean_rank_ic": float(by_date["rank_ic"].mean()) if len(by_date) else float("nan"),
        "median_rank_ic": (
            float(by_date["rank_ic"].median()) if len(by_date) else float("nan")
        ),
    }
    return by_date, summary
