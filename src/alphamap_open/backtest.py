from __future__ import annotations

import numpy as np
import pandas as pd


def align_forward_returns(
    features: pd.DataFrame,
    prices: pd.DataFrame,
    horizon: int = 20,
) -> pd.DataFrame:
    """Execute at the first observed close strictly after each formation timestamp."""
    required = {"date", "security_id", "adjusted_close"}
    missing = required - set(prices.columns)
    if missing:
        raise ValueError(f"prices missing columns: {sorted(missing)}")

    market = prices.copy()
    market["price_at"] = pd.to_datetime(market["date"], utc=True).dt.normalize()
    market = market.sort_values(["security_id", "price_at"])
    market["forward_return"] = (
        market.groupby("security_id")["adjusted_close"].shift(-horizon)
        / market["adjusted_close"]
        - 1.0
    )

    aligned: list[pd.DataFrame] = []
    for security_id, left in features.groupby("security_id"):
        right = market[market["security_id"] == security_id][
            ["price_at", "adjusted_close", "forward_return"]
        ].sort_values("price_at")
        joined = pd.merge_asof(
            left.sort_values("formation_at"),
            right,
            left_on="formation_at",
            right_on="price_at",
            direction="forward",
            allow_exact_matches=False,
        )
        joined["execution_price_field"] = "next_session_adjusted_close"
        aligned.append(joined)

    result = pd.concat(aligned, ignore_index=True)
    group = result.groupby("formation_at")["forward_return"]
    total = group.transform("sum")
    count = group.transform("count")
    result["benchmark_return"] = (total - result["forward_return"]) / (count - 1)
    result.loc[count < 2, "benchmark_return"] = np.nan
    result["forward_relative_return"] = (
        result["forward_return"] - result["benchmark_return"]
    )
    return result.sort_values(["formation_at", "security_id"]).reset_index(drop=True)


def evaluate_rank_ic(
    aligned: pd.DataFrame,
    minimum_cross_section: int = 5,
) -> tuple[pd.DataFrame, dict[str, float | int]]:
    usable = aligned.dropna(subset=["feature", "forward_relative_return"])

    records: list[dict[str, object]] = []
    for formation_at, group in usable.groupby("formation_at"):
        if len(group) < minimum_cross_section:
            continue
        rank_ic = group["feature"].rank().corr(
            group["forward_relative_return"].rank()
        )
        records.append(
            {"formation_at": formation_at, "rank_ic": float(rank_ic), "n": len(group)}
        )
    by_date = pd.DataFrame(records)
    summary: dict[str, float | int] = {
        "dates": int(len(by_date)),
        "mean_rank_ic": (
            float(by_date["rank_ic"].mean()) if len(by_date) else float("nan")
        ),
        "median_rank_ic": (
            float(by_date["rank_ic"].median()) if len(by_date) else float("nan")
        ),
    }
    return by_date, summary


def moving_block_interval(
    values: pd.Series,
    block_length: int = 5,
    draws: int = 10_000,
    seed: int = 0,
) -> tuple[float, float]:
    clean = values.dropna().to_numpy()
    if len(clean) < block_length:
        return float("nan"), float("nan")
    starts = np.arange(len(clean) - block_length + 1)
    blocks_per_draw = int(np.ceil(len(clean) / block_length))
    rng = np.random.default_rng(seed)
    means = np.empty(draws)
    for draw in range(draws):
        chosen = rng.choice(starts, size=blocks_per_draw, replace=True)
        sample = np.concatenate([clean[start : start + block_length] for start in chosen])
        means[draw] = sample[: len(clean)].mean()
    low, high = np.quantile(means, [0.025, 0.975])
    return float(low), float(high)
