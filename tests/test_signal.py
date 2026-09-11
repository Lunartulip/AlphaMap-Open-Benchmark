import pandas as pd
import pytest

from alphamap_open.backtest import align_forward_returns
from alphamap_open.signal import build_weekly_features


def _events() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_id": "E1",
                "subject_entity_id": "SUPPLIER",
                "security_id": "SEC-S",
                "direction": "positive",
                "claim_label": "issuer_reported_actual",
                "tradable_from": "2026-01-02T14:30:00Z",
                "alpha_feature_eligible": "true",
            }
        ]
    )


def _relationships() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "relationship_id": "R1",
                "from_entity_id": "SUPPLIER",
                "to_security_id": "SEC-C",
                "valid_from": "2026-01-01",
                "valid_to": "",
                "propagation_weight": 0.25,
                "alpha_feature_eligible": "true",
            }
        ]
    )


def test_feature_has_complete_universe_and_propagation() -> None:
    result = build_weekly_features(
        _events(),
        universe=["SEC-S", "SEC-C", "SEC-Z"],
        relationships=_relationships(),
        start="2026-01-02",
        end="2026-02-06",
    )
    final = result[result["formation_at"] == result["formation_at"].max()]
    assert set(final["security_id"]) == {"SEC-S", "SEC-C", "SEC-Z"}
    assert final.loc[final["security_id"] == "SEC-Z", "direct_stock"].item() == 0
    assert final.loc[final["security_id"] == "SEC-C", "propagated_stock"].item() > 0


def test_return_executes_after_formation() -> None:
    features = pd.DataFrame(
        {
            "formation_at": [pd.Timestamp("2026-01-02T23:59:59Z")],
            "security_id": ["SEC-A"],
            "feature": [0.5],
        }
    )
    prices = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-02", periods=22, freq="B"),
            "security_id": ["SEC-A"] * 22,
            "adjusted_close": [90.0, 100.0] + [100.0] * 19 + [110.0],
        }
    )
    result = align_forward_returns(features, prices, horizon=20)
    assert result.iloc[0]["price_at"] == pd.Timestamp("2026-01-05", tz="UTC")
    assert result.iloc[0]["adjusted_close"] == 100.0
    assert result.iloc[0]["forward_return"] == pytest.approx(0.1)
