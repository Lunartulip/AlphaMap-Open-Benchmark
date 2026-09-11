from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from alphamap_open.backtest import (
    align_forward_returns,
    evaluate_rank_ic,
    moving_block_interval,
)
from alphamap_open.signal import build_weekly_features
from alphamap_open.validate import validate_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SCEM-4W-v2 audit pipeline")
    parser.add_argument("--prices", required=True, type=Path)
    parser.add_argument("--data", type=Path, default=Path("data/sample/v1"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    validate_directory(args.data, check_manifest=True)
    manifest = json.loads(
        (args.data / "release_manifest.json").read_text(encoding="utf-8")
    )
    events = pd.read_csv(args.data / "events.csv")
    relationships = pd.read_csv(args.data / "relationships.csv")
    securities = pd.read_csv(args.data / "security_mappings.csv")
    prices = pd.read_csv(args.prices)
    if prices.empty:
        raise ValueError("price file contains no observations")

    price_dates = pd.to_datetime(prices["date"], utc=True)
    features = build_weekly_features(
        events,
        securities=securities,
        relationships=relationships,
        start=price_dates.min(),
        end=price_dates.max(),
    )
    aligned = align_forward_returns(features, prices, horizon=20)
    by_date, summary = evaluate_rank_ic(aligned)
    ci_low, ci_high = moving_block_interval(
        by_date["rank_ic"] if len(by_date) else pd.Series(dtype=float)
    )
    summary["block_bootstrap_95pct_low"] = ci_low
    summary["block_bootstrap_95pct_high"] = ci_high
    result = {
        "protocol_id": "SCEM-4W-v2",
        "dataset_version": manifest["version"],
        "eligible_for_inference": manifest["eligible_for_inference"],
        "claim_status": "pipeline_diagnostic_only",
        "summary": summary,
    }
    print(json.dumps(result, indent=2))
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        aligned.to_csv(args.output / "aligned_security_weeks.csv", index=False)
        by_date.to_csv(args.output / "rank_ic_by_date.csv", index=False)
        (args.output / "summary.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
