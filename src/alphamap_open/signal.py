from __future__ import annotations

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


def _active_security_ids(
    securities: pd.DataFrame,
    formation_at: pd.Timestamp,
) -> list[str]:
    day = formation_at.tz_convert("UTC").date().isoformat()
    valid_from = securities["valid_from"].astype(str)
    valid_to = securities["valid_to"].fillna("").astype(str)
    active = valid_from.le(day) & (valid_to.eq("") | valid_to.ge(day))
    return securities.loc[active, "security_id"].drop_duplicates().tolist()


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
    direct = direct.rename(columns={"tradable_from": "impulse_at", "base_weight": "weight"})
    direct["component"] = "direct"
    direct["relationship_id"] = ""

    relations = relationships[
        relationships["alpha_feature_eligible"].astype(str).str.lower().eq("true")
        & relationships["confidence_tier"].eq("confirmed")
    ].copy()
    relations["tradable_from"] = pd.to_datetime(relations["tradable_from"], utc=True)
    propagated_rows: list[dict[str, object]] = []
    for event in eligible.to_dict("records"):
        event_product = str(event["product"])
        candidates = relations[
            relations["from_entity_id"].eq(event["subject_entity_id"])
            & relations["applicable_event_type"].eq(event["event_type"])
            & relations["applicable_product_prefix"].map(event_product.startswith)
        ].copy()
        event_day = event["tradable_from"].date()
        candidates = candidates[
            pd.to_datetime(candidates["valid_from"]).dt.date.le(event_day)
        ]
        valid_to = candidates["valid_to"].fillna("").astype(str)
        candidates = candidates[
            valid_to.eq("") | valid_to.ge(event_day.isoformat())
        ]
        if candidates.empty:
            continue

        candidates["impulse_at"] = candidates["tradable_from"].where(
            candidates["tradable_from"] >= event["tradable_from"],
            event["tradable_from"],
        )
        candidates = candidates.sort_values(
            ["impulse_at", "tradable_from", "relationship_id"]
        ).drop_duplicates(
            ["from_security_id", "to_security_id"],
            keep="first",
        )
        for relation in candidates.to_dict("records"):
            propagated_rows.append(
                {
                    "event_id": event["event_id"],
                    "subject_entity_id": event["subject_entity_id"],
                    "security_id": relation["to_security_id"],
                    "impulse_at": relation["impulse_at"],
                    "weight": event["base_weight"]
                    * float(relation["propagation_weight"]),
                    "component": "propagated",
                    "relationship_id": relation["relationship_id"],
                }
            )
    propagated = pd.DataFrame(propagated_rows, columns=direct.columns)
    return pd.concat([direct, propagated], ignore_index=True)


def build_weekly_features(
    events: pd.DataFrame,
    securities: pd.DataFrame,
    relationships: pd.DataFrame,
    start: object | None = None,
    end: object | None = None,
    half_life_days: float = 28.0,
    momentum_lag_weeks: int = 4,
) -> pd.DataFrame:
    """Build PIT-membership Friday features from already-tradable evidence."""
    impulses = _expanded_impulses(events, relationships)
    if impulses.empty:
        return pd.DataFrame()

    first = _utc(start if start is not None else impulses["impulse_at"].min())
    last = _utc(end if end is not None else impulses["impulse_at"].max())
    anchors = pd.date_range(
        first.normalize(),
        last.normalize(),
        freq="W-FRI",
        tz="UTC",
    ) + pd.Timedelta(hours=23, minutes=59, seconds=59)

    rows: list[dict[str, object]] = []
    for formation_at in anchors:
        visible = impulses[impulses["impulse_at"] <= formation_at].copy()
        if visible.empty:
            visible["decayed"] = pd.Series(dtype=float)
        else:
            age_days = (
                formation_at - visible["impulse_at"]
            ).dt.total_seconds() / 86400.0
            visible["decayed"] = visible["weight"] * np.exp2(
                -age_days / half_life_days
            )
        for security_id in _active_security_ids(securities, formation_at):
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
