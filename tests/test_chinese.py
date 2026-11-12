import numpy as np
import pandas as pd
import pytest

from silkperfect import chinese


def make_bars(n=700, seed=0, drift=0.0003):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-01", periods=n)
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.015, n)))
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"Open": o, "High": np.maximum(o, c) * 1.005, "Low": np.minimum(o, c) * 0.995,
                         "Close": c, "Volume": 1e5, "Value": 1e7}, index=idx)


def test_hold_between_buys_and_sells():
    buy = pd.Series([0, 1, 0, 0, 1, 0, 1], dtype=bool)
    sell = pd.Series([0, 0, 0, 1, 0, 0, 1], dtype=bool)
    assert list(chinese.hold_between(buy, sell)) == [0, 1, 1, 0, 1, 1, 0]   # a sell wins a tie


def test_turtle_buys_new_highs_and_sells_new_lows():
    idx = pd.bdate_range("2024-01-01", periods=60)
    close = pd.Series(np.r_[np.full(25, 100.0), np.linspace(101, 120, 20), np.linspace(119, 90, 15)], index=idx)
    bars = pd.DataFrame({"Open": close, "High": close, "Low": close, "Close": close})
    pos = chinese.turtle_positions(bars)
    assert pos.iloc[24] == 0 and pos.iloc[25] == 1                 # first close above the 20-day high
    assert pos.iloc[44] == 1 and pos.iloc[-1] == 0                 # out once it breaks the 10-day low
    assert pos.iloc[:25].sum() == 0


def test_rsrs_uses_only_the_past_and_trades_both_ways():
    bars = make_bars(1200, seed=2)
    pos = chinese.rsrs_positions(bars)
    assert set(pos.unique()) <= {0, 1} and 0 < pos.mean() < 1
    changed = bars.copy()
    changed.iloc[900:] *= 1.5
    pd.testing.assert_series_equal(pos.iloc[:900], chinese.rsrs_positions(changed).iloc[:900])


def test_chan_points_from_czsc_are_causal_and_classified():
    pytest.importorskip("czsc")
    bars = make_bars(900, seed=1)
    full = chinese.chan_points(bars)
    assert set(full["buy"].unique()) <= {0, 1, 2, 3} and set(full["sell"].unique()) <= {0, 1, 2, 3}
    assert full["buy"].gt(0).sum() > 5 and full["sell"].gt(0).sum() > 5
    short = chinese.chan_points(bars.iloc[:700])
    pd.testing.assert_frame_equal(full.iloc[:700], short)        # later bars do not change earlier points
    pos = chinese.chan_positions(full, (3,))
    assert set(pos.unique()) <= {0, 1}


def test_reversal_scores_the_biggest_faller_highest():
    idx = pd.bdate_range("2024-01-01", periods=40)
    close = pd.DataFrame({"UP": np.linspace(100, 130, 40), "DOWN": np.linspace(100, 70, 40)}, index=idx)
    score = chinese.ShortTermReversal(21).score(close, 21)
    assert score["DOWN"] > 0 > score["UP"]
