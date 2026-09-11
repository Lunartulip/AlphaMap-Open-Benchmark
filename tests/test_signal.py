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
                "event_type": "production_start",
                "product": "HBM3E",
                "direction": "positive",
                "claim_label": "issuer_reported_actual",
                "tradable_from": "2026-01-02T14:30:00Z",
                "alpha_feature_eligible": "true",
            },
            {
                "event_id": "E2",
                "subject_entity_id": "SUPPLIER",
                "security_id": "SEC-S",
                "event_type": "order_growth",
                "product": "consumer_DRAM",
                "direction": "positive",
                "claim_label": "issuer_reported_actual",
                "tradable_from": "2026-01-02T14:30:00Z",
                "alpha_feature_eligible": "true",
            },
        ]
    )


def _relationships() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "relationship_id": "R1",
                "from_entity_id": "SUPPLIER",
                "from_security_id": "SEC-S",
                "to_security_id": "SEC-C",
                "valid_from": "2026-01-01",
                "valid_to": "",
                "tradable_from": "2026-01-20T14:30:00Z",
                "applicable_event_type": "production_start",
                "applicable_product_prefix": "HBM3E",
                "propagation_weight": 0.25,
                "alpha_feature_eligible": "true",
            }
        ]
    )


def _securities() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"security_id": "SEC-S", "valid_from": "2026-01-01", "valid_to": ""},
            {"security_id": "SEC-C", "valid_from": "2026-01-01", "valid_to": ""},
            {"security_id": "SEC-Z", "valid_from": "2026-01-01", "valid_to": ""},
            {"security_id": "SEC-LATE", "valid_from": "2026-02-01", "valid_to": ""},
        ]
    )


def test_relation_knowledge_and_product_gate_propagation() -> None:
    result = build_weekly_features(
        _events(),
        securities=_securities(),
        relationships=_relationships(),
        start="2026-01-02",
        end="2026-02-06",
    )
    before = result[result["formation_at"] == pd.Timestamp("2026-01-16T23:59:59Z")]
    after = result[result["formation_at"] == pd.Timestamp("2026-01-23T23:59:59Z")]
    assert before.loc[before["security_id"] == "SEC-C", "propagated_stock"].item() == 0
    assert after.loc[after["security_id"] == "SEC-C", "propagated_stock"].item() > 0
    assert "SEC-LATE" not in set(before["security_id"])
    assert "SEC-LATE" in set(result["security_id"])


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
