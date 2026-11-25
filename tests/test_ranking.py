import numpy as np
import pandas as pd
import pytest

from silkperfect import ranking
from silkperfect.costs import CostModel


def make_panel(n_days=700, n_stocks=30, seed=0, drift=None):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n_days)
    cols = [f"S{i:02d}" for i in range(n_stocks)]
    mu = np.zeros(n_stocks) if drift is None else drift
    close = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(mu, 0.01, (n_days, n_stocks)), axis=0)),
                         index=idx, columns=cols)
    value = pd.DataFrame(np.tile(np.arange(n_stocks, 0, -1) * 1e6, (n_days, 1)), index=idx, columns=cols)
    return ranking.Panel(close, close.shift(1).fillna(close.iloc[0]), value)


SMALL = dict(universe_size=10, top_n=3, rebalance_days=21, min_history=300, context=260,
             liquidity_window=60, holdout_days=100)


def test_universe_is_most_liquid_clean_and_point_in_time():
    panel = make_panel()
    s = ranking.RankSettings(**SMALL)
    assert ranking.eligible(panel, 400, s) == [f"S{i:02d}" for i in range(10)]
    panel.close.iloc[380, 0] *= 2                      # a suspect one-day doubling
    panel.close.iloc[50:120, 1] = np.nan               # gap, but outside the context window
    panel.close.iloc[395, 2] = np.nan                  # gap inside the window
    names = ranking.eligible(panel, 400, s)
    assert "S00" not in names and "S02" not in names and "S01" in names
    future = make_panel()
    future.close.iloc[401:] *= 5                       # the future must not change today's universe
    assert ranking.eligible(future, 400, s) == [f"S{i:02d}" for i in range(10)]


def test_momentum_and_low_volatility_scores():
    idx = pd.bdate_range("2022-01-01", periods=300)
    up = pd.Series(np.linspace(100, 200, 300), index=idx)
    flat = pd.Series(100.0 + np.tile([0, 1], 150), index=idx)
    close = pd.DataFrame({"UP": up, "FLAT": flat})
    mom = ranking.Momentum(252, 21).score(close, 21)
    assert mom["UP"] == pytest.approx(up.iloc[-22] / up.iloc[-253] - 1) and mom["UP"] > mom["FLAT"]
    vol = ranking.LowVolatility(252).score(close, 21)
    assert vol["UP"] > vol["FLAT"]                     # the steadier stock scores higher


def test_scores_only_see_the_past():
    panel = make_panel()
    seen = []

    class Spy(ranking.Signal):
        name = "spy"

        def score(self, close, horizon):
            seen.append(close.index[-1])
            return close.iloc[-1]

    result = ranking.run(panel, [Spy()], ranking.RankSettings(**SMALL))
    dates = list(result.periods["date"])
    assert seen == dates                               # each score ends on its own rebalance day
    assert result.rebalances == len(dates)


def test_simulation_matches_hand_calculation_and_charges_costs():
    idx = pd.bdate_range("2024-01-01", periods=6)
    close = pd.DataFrame({"A": [100, 100, 110, 121, 121, 121.0], "B": [50, 50, 50, 50, 50, 50.0]}, index=idx)
    panel = ranking.Panel(close, close.copy(), close * 0 + 1e6)
    free = CostModel(brokerage_flat=0, stt=0, exchange_txn=0, sebi_fee=0, stamp_duty_buy=0,
                     dp_charge_sell=0, slippage_bps=0)
    s = ranking.RankSettings(capital=1000.0, costs=free)
    sim = ranking.simulate(panel, {0: ["A", "B"], 2: ["B"]}, s)
    # Day 1 open: 5 of A and 10 of B. Day 2 close: A 550 + B 500.
    # Day 3 open: A at 121 -> 605 + 500 = 1105, all into B (22 shares, Rs 5 left over).
    assert sim["equity"].loc[idx[2]] == pytest.approx(1050.0)
    assert sim["equity"].iloc[-1] == pytest.approx(1105.0)
    assert sim["shares"]["B"] == 22 and sim["cash"] == pytest.approx(5.0)
    assert list(sim["trades"]["action"]) == ["Buy", "Buy", "Sell", "Buy"]
    assert sim["costs"] == 0
    paid = ranking.simulate(panel, {0: ["A", "B"], 2: ["B"]}, ranking.RankSettings(capital=1e6))
    assert paid["costs"] > 0 and paid["equity"].iloc[-1] < 1105.0 * 1000
    assert paid["turnover_pct"] > sim["turnover_pct"] * 0.99


def test_informative_signal_wins_and_noise_does_not_look_significant():
    drift = np.linspace(-0.001, 0.001, 30)
    panel = make_panel(drift=drift)

    class Oracle(ranking.Signal):
        name = "oracle"

        def score(self, close, horizon):
            return pd.Series(drift, index=panel.close.columns)[close.columns]

    class Noise(ranking.Signal):
        name = "noise"

        def score(self, close, horizon):
            rng = np.random.default_rng(len(close) + int(close.iloc[-1].sum()))
            return pd.Series(rng.normal(size=close.shape[1]), index=close.columns)

    s = ranking.RankSettings(**{**SMALL, "universe_size": 30})
    result = ranking.run(panel, [Oracle(), Noise()], s)
    summary = result.summary.set_index("method")
    assert summary.loc["oracle", "cagr_pct"] > summary.loc[ranking.HOLD_ALL, "cagr_pct"]
    assert summary.loc["oracle", "rank_t_stat"] > 2
    assert abs(summary.loc["noise", "rank_t_stat"]) < 2.5
    text = ranking.render(result)
    assert "Hold all equally" in text and "oracle" in text


def test_slow_scores_are_cached(tmp_path):
    panel = make_panel()
    calls = []

    class Slow(ranking.Signal):
        name, cache_key = "slow", "slow-v1"

        def score(self, close, horizon):
            calls.append(1)
            return close.iloc[-1]

    s = ranking.RankSettings(**SMALL)
    a = ranking.run(panel, [Slow()], s, cache_dir=tmp_path)
    first = len(calls)
    b = ranking.run(panel, [Slow()], s, cache_dir=tmp_path)
    assert len(calls) == first
    pd.testing.assert_frame_equal(a.summary, b.summary)


def test_small_money_skips_shares_it_cannot_afford():
    price = pd.Series({"DEAR": 900.0, "MID": 300.0, "CHEAP": 50.0, "ALSO": 40.0})
    ranked = ["DEAR", "MID", "CHEAP", "ALSO"]
    assert ranking.affordable(ranked, price, worth=1000.0, count=2) == ["MID", "CHEAP"]
    assert ranking.affordable(ranked, price, worth=1_000_000.0, count=2) == ["DEAR", "MID"]
    assert ranking.affordable(ranked, price, worth=10.0, count=2) == []
    assert ranking.affordable(ranked, price, worth=10.0, count=None) == ranked


def test_fees_never_push_the_account_below_zero_cash():
    panel = make_panel()
    s = ranking.RankSettings(**{**SMALL, "capital": 10_000.0})
    result = ranking.run(panel, [ranking.Momentum(126, 21)], s)
    sim = result.sims["Momentum (6-1 month)"]
    assert sim["cash"] >= 0 and (sim["trades"]["shares"] % 1 == 0).all()
    assert sim["costs"] == pytest.approx(sim["trades"]["fees"].sum())


def test_weekly_bars_group_past_days_counting_back():
    from silkperfect.kronos_signal import weekly_bars
    idx = pd.bdate_range("2024-01-01", periods=12)
    c = pd.DataFrame({"A": np.arange(1.0, 13.0)}, index=idx)
    past = ranking.Panel(c, c - 0.5, c * 0, high=c + 1, low=c - 1, volume=c * 0 + 10)
    bars = weekly_bars(past, "A")
    assert len(bars) == 2                                   # the two oldest days are dropped
    assert list(bars["close"]) == [7.0, 12.0] and list(bars["open"]) == [2.5, 7.5]
    assert list(bars["high"]) == [8.0, 13.0] and list(bars["low"]) == [2.0, 7.0]
    assert list(bars["volume"]) == [50.0, 50.0]


def test_bar_methods_receive_only_past_bars():
    panel = make_panel()
    panel.high, panel.low, panel.volume = panel.close * 1.01, panel.close * 0.99, panel.value
    seen = []

    class Bars(ranking.Signal):
        name = "bars"

        def score_bars(self, past, horizon):
            seen.append((past.close.index[-1], past.high.index[-1], len(past.volume)))
            return past.close.iloc[-1]

    s = ranking.RankSettings(**SMALL)
    result = ranking.run(panel, [Bars()], s)
    assert [d for d, _, _ in seen] == list(result.holdings["bars"])
    assert all(d == h and n == s.context for d, h, n in seen)


def test_index_style_momentum_prefers_strong_steady_risers():
    idx = pd.bdate_range("2022-01-01", periods=300)
    rng = np.random.default_rng(0)
    steady = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.002, 0.005, 300))), index=idx)
    wild = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.002, 0.04, 300))), index=idx)
    faller = pd.Series(100 * np.exp(np.cumsum(rng.normal(-0.002, 0.005, 300))), index=idx)
    score = ranking.IndexMomentum().score(pd.DataFrame({"STEADY": steady, "WILD": wild, "FALL": faller}), 21)
    assert score["STEADY"] > score["WILD"] and score["STEADY"] > score["FALL"]
    assert abs(score.mean()) < 1e-9                        # z-scores centre on zero


def _bars_panel(n_days=420, n_stocks=25, seed=0):
    panel = make_panel(n_days=n_days, n_stocks=n_stocks, seed=seed)
    rng = np.random.default_rng(seed + 1)
    panel.open = panel.close.shift(1).fillna(panel.close.iloc[0])
    panel.high = np.maximum(panel.open, panel.close) * (1 + rng.uniform(0, 0.01, panel.close.shape))
    panel.low = np.minimum(panel.open, panel.close) * (1 - rng.uniform(0, 0.01, panel.close.shape))
    panel.volume = pd.DataFrame(rng.uniform(1e4, 2e4, panel.close.shape), index=panel.close.index,
                                columns=panel.close.columns)
    panel.value = panel.volume * panel.close
    return panel


def test_alpha158_has_all_features_and_matches_qlib_formulas():
    from silkperfect.qlib_signal import alpha158
    panel = _bars_panel()
    f = alpha158(panel)
    assert len(f) == 158
    c, o, h, l, v = (getattr(panel, k)["S03"] for k in ("close", "open", "high", "low", "volume"))
    t = 300
    assert f["KMID"]["S03"].iloc[t] == pytest.approx((c.iloc[t] - o.iloc[t]) / o.iloc[t])
    assert f["ROC20"]["S03"].iloc[t] == pytest.approx(c.iloc[t - 20] / c.iloc[t])
    assert f["MA10"]["S03"].iloc[t] == pytest.approx(c.iloc[t - 9:t + 1].mean() / c.iloc[t])
    assert f["MAX5"]["S03"].iloc[t] == pytest.approx(h.iloc[t - 4:t + 1].max() / c.iloc[t])
    window = c.iloc[t - 29:t + 1].to_numpy()
    slope, intercept = np.polyfit(np.arange(30), window, 1)
    assert f["BETA30"]["S03"].iloc[t] == pytest.approx(slope / c.iloc[t])
    assert f["RESI30"]["S03"].iloc[t] == pytest.approx((window[-1] - (intercept + slope * 29)) / c.iloc[t])
    assert f["RSQR30"]["S03"].iloc[t] == pytest.approx(np.corrcoef(np.arange(30), window)[0, 1] ** 2)
    assert f["IMAX10"]["S03"].iloc[t] == pytest.approx((h.iloc[t - 9:t + 1].to_numpy().argmax() + 1) / 10)
    assert f["VMA5"]["S03"].iloc[t] == pytest.approx(v.iloc[t - 4:t + 1].mean() / v.iloc[t])
    ups = (c.diff() > 0).iloc[t - 19:t + 1].mean()
    assert f["CNTP20"]["S03"].iloc[t] == pytest.approx(ups)
    assert f["VWAP0"]["S03"].iloc[t] == pytest.approx(1.0)       # value/volume equals close here


def test_alpha158_and_the_model_use_only_the_past():
    from silkperfect.qlib_signal import QlibSignal, alpha158
    panel = _bars_panel()
    changed = _bars_panel()
    for df in (changed.close, changed.open, changed.high, changed.low, changed.volume, changed.value):
        df.iloc[351:] *= 3.0
    a, b = alpha158(panel), alpha158(changed)
    for name in a:
        pd.testing.assert_frame_equal(a[name].iloc[:351], b[name].iloc[:351])

    names = list(panel.close.columns)
    members = {panel.close.index[i]: names for i in range(60, 420, 21)}
    day = 350
    scores = []
    for p in (panel, changed):
        sig = QlibSignal(p, members, sample_step=2)
        scores.append(sig.score_bars(p.window(day - 259, day + 1, names), 21))
    assert scores[0].abs().sum() > 0                               # a model was trained
    pd.testing.assert_series_equal(scores[0], scores[1])          # and the future did not reach it
