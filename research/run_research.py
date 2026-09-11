from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from alphamap_open.backtest import evaluate_rank_ic, prepare_forward_returns
from alphamap_open.signal import build_weekly_features
from alphamap_open.validate import validate_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Run registered SCEM-4W-v1 evaluation")
    parser.add_argument("--prices", required=True, type=Path)
    parser.add_argument("--data", type=Path, default=Path("data/sample/v1"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    validate_directory(args.data, check_manifest=True)
    events = pd.read_csv(args.data / "events.csv")
    prices = pd.read_csv(args.prices)
    if prices.empty:
        raise ValueError("price file contains no observations")

    price_dates = pd.to_datetime(prices["date"], utc=True)
    features = build_weekly_features(
        events,
        start=price_dates.min(),
        end=price_dates.max(),
    )
    returns = prepare_forward_returns(prices, horizon=20)
    by_date, summary = evaluate_rank_ic(features, returns)
    result = {
        "protocol_id": "SCEM-4W-v1",
        "holdout_status": "not_evaluated_by_this_runner",
        "summary": summary,
    }
    print(json.dumps(result, indent=2))
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        by_date.to_csv(args.output / "rank_ic_by_date.csv", index=False)
        (args.output / "summary.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
