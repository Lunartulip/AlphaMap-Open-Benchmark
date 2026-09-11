from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


DIRECTION_WEIGHT = {"negative": -1.0, "neutral": 0.0, "positive": 1.0}
EVIDENCE_WEIGHT = {
    "issuer_reported_actual": 1.0,
    "derived_value": 0.8,
    "issuer_forward_statement": 0.5,
    "estimate": 0.35,
    "relationship_assertion": 0.0,
}


def _utc(value: object) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _expanded_impulses(
    events: pd.DataFrame,
    relationships: pd.DataFrame,
) -> pd.DataFrame:
    eligible = events[
        events["alpha_feature_eligible"].astype(str).str.lower().eq("true")
    ].copy()
    eligible["tradable_from"] = pd.to_datetime(eligible["tradable_from"], utc=True)
    eligible["base_weight"] = (
        eligible["direction"].map(DIRECTION_WEIGHT)
        * eligible["claim_label"].map(EVIDENCE_WEIGHT)
    )
    if eligible["base_weight"].isna().any():
        raise ValueError("events contain an unsupported direction or claim label")

    direct = eligible[
        ["event_id", "subject_entity_id", "security_id", "tradable_from", "base_weight"]
    ].copy()
    direct["component"] = "direct"
    direct["weight"] = direct.pop("base_weight")
    direct["relationship_id"] = ""

    propagated_rows: list[dict[str, object]] = []
    active = relationships[
        relationships["alpha_feature_eligible"].astype(str).str.lower().eq("true")
    ].copy()
    for event in eligible.to_dict("records"):
        event_day = event["tradable_from"].date()
        for relation in active.to_dict("records"):
            valid_to = relation.get("valid_to")
            if event["subject_entity_id"] != relation["from_entity_id"]:
                continue
            if event_day < pd.Timestamp(relation["valid_from"]).date():
                continue
            if pd.notna(valid_to) and str(valid_to) and event_day > pd.Timestamp(valid_to).date():
                continue
            propagated_rows.append(
                {
                    "event_id": event["event_id"],
                    "subject_entity_id": event["subject_entity_id"],
                    "security_id": relation["to_security_id"],
                    "tradable_from": event["tradable_from"],
                    "component": "propagated",
                    "weight": event["base_weight"]
                    * float(relation["propagation_weight"]),
                    "relationship_id": relation["relationship_id"],
                }
            )
    propagated = pd.DataFrame(propagated_rows, columns=direct.columns)
    return pd.concat([direct, propagated], ignore_index=True)


def build_weekly_features(
    events: pd.DataFrame,
    universe: Sequence[str],
    relationships: pd.DataFrame,
    start: object | None = None,
    end: object | None = None,
    half_life_days: float = 28.0,
    momentum_lag_weeks: int = 4,
) -> pd.DataFrame:
    """Build complete-universe Friday features from already-tradable evidence."""
    impulses = _expanded_impulses(events, relationships)
    if impulses.empty:
        return pd.DataFrame()

    first = _utc(start if start is not None else impulses["tradable_from"].min())
    last = _utc(end if end is not None else impulses["tradable_from"].max())
    anchors = pd.date_range(
        first.normalize(), last.normalize(), freq="W-FRI", tz="UTC"
    ) + pd.Timedelta(hours=23, minutes=59, seconds=59)

    rows: list[dict[str, object]] = []
    for formation_at in anchors:
        visible = impulses[impulses["tradable_from"] <= formation_at].copy()
        if visible.empty:
            visible["decayed"] = pd.Series(dtype=float)
        else:
            age_days = (
                formation_at - visible["tradable_from"]
            ).dt.total_seconds() / 86400.0
            visible["decayed"] = (
                visible["weight"] * np.exp2(-age_days / half_life_days)
            )
        for security_id in universe:
            own = visible[visible["security_id"] == security_id]
            rows.append(
                {
                    "formation_at": formation_at,
                    "security_id": security_id,
                    "direct_stock": own.loc[
                        own["component"] == "direct", "decayed"
                    ].sum(),
                    "propagated_stock": own.loc[
                        own["component"] == "propagated", "decayed"
                    ].sum(),
                    "visible_event_count": int(own["event_id"].nunique()),
                }
            )

    result = pd.DataFrame(rows).sort_values(["security_id", "formation_at"])
    result["propagated_momentum"] = result.groupby("security_id")[
        "propagated_stock"
    ].diff(momentum_lag_weeks)
    result["feature"] = result.groupby("formation_at")[
        "propagated_momentum"
    ].rank(pct=True) - 0.5
    return result.sort_values(["formation_at", "security_id"]).reset_index(drop=True)
