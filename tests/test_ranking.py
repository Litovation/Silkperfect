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
