from __future__ import annotations

import numpy as np
import pandas as pd


DIRECTION_WEIGHT = {"negative": -1.0, "neutral": 0.0, "positive": 1.0}
EVIDENCE_WEIGHT = {
    "reported_fact": 1.0,
    "derived_value": 0.8,
    "issuer_claim": 0.5,
    "estimate": 0.35,
    "relationship_assertion": 0.0,
}


def _utc(value: object) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def build_weekly_features(
    events: pd.DataFrame,
    start: object | None = None,
    end: object | None = None,
    half_life_days: float = 28.0,
) -> pd.DataFrame:
    """Build Friday point-in-time scores using only already-tradable evidence."""
    required = {
        "security_id", "direction", "claim_label", "tradable_from",
        "alpha_feature_eligible"
    }
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"events missing columns: {sorted(missing)}")

    frame = events.copy()
    frame["tradable_from"] = pd.to_datetime(frame["tradable_from"], utc=True)
    frame = frame[
        frame["alpha_feature_eligible"].astype(str).str.lower().eq("true")
    ].copy()
    if frame.empty:
        return pd.DataFrame(columns=["date", "security_id", "raw_score", "feature"])

    frame["signed_weight"] = (
        frame["direction"].map(DIRECTION_WEIGHT)
        * frame["claim_label"].map(EVIDENCE_WEIGHT)
    )
    if frame["signed_weight"].isna().any():
        raise ValueError("events contain an unsupported direction or claim_label")

    first = _utc(start if start is not None else frame["tradable_from"].min())
    last = _utc(end if end is not None else frame["tradable_from"].max())
    anchors = pd.date_range(
        first.normalize(),
        last.normalize(),
        freq="W-FRI",
        tz="UTC",
    ) + pd.Timedelta(hours=23, minutes=59, seconds=59)

    rows: list[dict[str, object]] = []
    for anchor in anchors:
        eligible = frame[frame["tradable_from"] <= anchor].copy()
        if eligible.empty:
            continue
        age_days = (anchor - eligible["tradable_from"]).dt.total_seconds() / 86400.0
        eligible["contribution"] = (
            eligible["signed_weight"] * np.exp2(-age_days / half_life_days)
        )
        scores = eligible.groupby("security_id", sort=True)["contribution"].sum()
        for security_id, score in scores.items():
            rows.append(
                {"date": anchor.normalize(), "security_id": security_id, "raw_score": score}
            )

    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(columns=["date", "security_id", "raw_score", "feature"])
    result["feature"] = result.groupby("date")["raw_score"].rank(pct=True) - 0.5
    return result.sort_values(["date", "security_id"]).reset_index(drop=True)
