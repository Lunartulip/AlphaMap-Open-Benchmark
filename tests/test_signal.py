import pandas as pd

from alphamap_open.backtest import prepare_forward_returns
from alphamap_open.signal import build_weekly_features


def test_feature_excludes_future_and_ineligible_evidence() -> None:
    events = pd.DataFrame(
        [
            {
                "security_id": "SEC-A",
                "direction": "positive",
                "claim_label": "reported_fact",
                "tradable_from": "2026-01-02T14:30:00Z",
                "alpha_feature_eligible": "true",
            },
            {
                "security_id": "SEC-B",
                "direction": "positive",
                "claim_label": "reported_fact",
                "tradable_from": "2026-01-10T14:30:00Z",
                "alpha_feature_eligible": "true",
            },
            {
                "security_id": "SEC-C",
                "direction": "positive",
                "claim_label": "relationship_assertion",
                "tradable_from": "2026-01-02T14:30:00Z",
                "alpha_feature_eligible": "false",
            },
        ]
    )
    result = build_weekly_features(events, start="2026-01-02", end="2026-01-09")
    final_ids = set(result.loc[result["date"] == pd.Timestamp("2026-01-09", tz="UTC"), "security_id"])
    assert final_ids == {"SEC-A"}


def test_forward_return_uses_future_observation() -> None:
    prices = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=22, freq="B"),
            "security_id": ["SEC-A"] * 22,
            "adjusted_close": [100.0] * 20 + [110.0, 110.0],
        }
    )
    result = prepare_forward_returns(prices, horizon=20)
    assert result.iloc[0]["forward_return"] == 0.1
