import numpy as np
import pandas as pd
import pytest

from silkperfect import backtest, scoreboard, walkforward as wf
from silkperfect.costs import CostModel
from silkperfect.forecasters import Drift, Forecaster, MovingAverage, NoChange


def series(n=400, seed=1):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    return pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0004, 0.012, n))), index=idx)


def bars(close):
    return pd.DataFrame({"Open": close.shift(1).fillna(close.iloc[0]), "High": close * 1.01,
                         "Low": close * 0.99, "Close": close, "Volume": 1e6})


def test_costs_match_a_hand_calculation():
    c = CostModel()
    t = 100 * 1000.0                                        # Rs 1,00,000 turnover
    taxable = 20 + t * 0.0000297 + t * 0.000001
    buy = taxable * 1.18 + t * 0.001 + t * 0.00015 + t * 0.0005
    sell = (taxable + 20) * 1.18 + t * 0.001 + t * 0.0005
    assert c.cost("buy", 100, 1000) == pytest.approx(buy)
    assert c.cost("sell", 100, 1000) == pytest.approx(sell)
    assert c.per_leg(100, 1000) * 2 == pytest.approx(buy + sell)
    assert 0.003 < c.round_trip_fraction(500_000) < 0.004
    assert CostModel(brokerage_pct=0.0001).cost("buy", 1, 100) < c.cost("buy", 1, 100)


def test_forecasters_see_only_the_past():
    close = series()
    seen = []

    class Spy(Forecaster):
        name = "spy"

        def predict(self, histories, horizon):
            seen.extend(histories)
            return np.array([np.full(horizon, h[-1]) for h in histories])

    out = wf.walk_forward(close, Spy(), horizon=5, min_history=100, max_context=150)
    assert len(seen) == len(out) == len(close) - 99
    for i, h in enumerate(seen):
        end = 100 + i
        assert len(h) == min(end, 150)
        np.testing.assert_array_equal(h, close.to_numpy()[end - len(h):end])


@pytest.mark.parametrize("forecaster", [NoChange(), Drift(60), MovingAverage(20)])
def test_changing_the_future_does_not_change_earlier_forecasts(forecaster):
    close = series()
    changed = close.copy()
    changed.iloc[300:] *= 3
    a = wf.walk_forward(close, forecaster, 5, 100)
    b = wf.walk_forward(changed, forecaster, 5, 100)
    pd.testing.assert_series_equal(a["pred_price"].iloc[:200], b["pred_price"].iloc[:200])


def test_accuracy_targets_and_no_change_skill():
    close = series()
    out = wf.walk_forward(close, NoChange(), 5, 100)
    assert out["actual_ret"].iloc[0] == pytest.approx(np.log(close.iloc[104] / close.iloc[99]))
    assert out["actual_ret"].isna().sum() == 5
    score = wf.accuracy(out)
    assert score["skill_vs_no_change"] == pytest.approx(0.0)
    assert score["forecasts"] == len(out) - 5

    perfect = out.assign(pred_ret=out["actual_ret"])
    assert wf.accuracy(perfect)["skill_vs_no_change"] == pytest.approx(1.0)
    assert wf.accuracy(perfect)["direction_hit_pct"] == pytest.approx(100.0)


def test_signals():
    r = pd.Series([0.0, 0.01, 0.002, -0.001, 0.001, 0.02])
    assert list(wf.forecast_signal(r, entry=0.005)) == [0, 1, 1, 0, 0, 1]
    up = pd.Series(np.arange(1.0, 101.0))
    assert wf.sma_signal(up, 5, 20).iloc[-1] == 1 and wf.sma_signal(up[::-1].reset_index(drop=True), 5, 20).iloc[-1] == 0


def test_buy_and_hold_matches_hand_calculation():
    close = series(300)
    b = bars(close)
    costs = CostModel()
    res = backtest.run_signal(b, pd.Series(1, index=b.index), 500_000, costs)
    # backtesting.py starts acting on the second bar, fills at the next open,
    # and closes whatever is still held at the final bar's open.
    entry, exit_ = b["Open"].iloc[2], b["Open"].iloc[-1]
    shares = int(500_000 * 0.99 // (entry + costs.per_leg(0.99, entry) / 0.99))
    paid = costs.per_leg(shares, entry) + costs.per_leg(shares, exit_)
    expected = 500_000 + shares * (exit_ - entry) - paid
    assert res["trades"] == 1
    assert res["equity"].iloc[-1] == pytest.approx(expected, rel=1e-9)
    assert res["costs"] == pytest.approx(paid, rel=1e-9)
    assert res["equity"].iloc[0] == 500_000


def test_flat_signal_never_trades_and_costs_reduce_returns():
    close = series(300)
    b = bars(close)
    flat = backtest.run_signal(b, pd.Series(0, index=b.index), 500_000, CostModel())
    assert flat["trades"] == 0 and flat["equity"].iloc[-1] == 500_000
    flip = pd.Series((np.arange(len(b)) // 5) % 2, index=b.index)
    free = CostModel(brokerage_flat=0, stt=0, exchange_txn=0, sebi_fee=0, stamp_duty_buy=0,
                     dp_charge_sell=0, slippage_bps=0)
    assert (backtest.run_signal(b, flip, 500_000, CostModel())["equity"].iloc[-1]
            < backtest.run_signal(b, flip, 500_000, free)["equity"].iloc[-1])


def test_curve_metrics_and_combining():
    idx = pd.to_datetime(["2020-01-01", "2020-07-01", "2021-01-01"])
    m = backtest.curve_metrics(pd.Series([100.0, 80.0, 121.0], index=idx))
    assert m["total_return_pct"] == pytest.approx(21.0)
    assert m["max_drawdown_pct"] == pytest.approx(-20.0)
    assert m["cagr_pct"] == pytest.approx(21.0, abs=0.2)
    late = pd.Series([50.0, 60.0], index=idx[1:])
    total = backtest.combine_equity([pd.Series([100.0, 80.0, 121.0], index=idx), late], capital=50.0)
    assert list(total) == [150.0, 130.0, 181.0]


def test_scoreboard_end_to_end():
    frames = []
    for i, sym in enumerate(["AAA", "BBB", "NIFTY 50", "SHORT"]):
        c = series(120 if sym == "SHORT" else 420, seed=i)
        b = bars(c)
        frames.append(pd.DataFrame({"date": b.index, "symbol": sym, "adj_open": b["Open"],
                                    "adj_high": b["High"], "adj_low": b["Low"],
                                    "adj_close": b["Close"], "adj_volume": b["Volume"]}))
    prices = pd.concat(frames, ignore_index=True)
    settings = scoreboard.Settings(min_history=200)
    result = scoreboard.run(prices, ["AAA", "BBB", "SHORT"], settings)
    assert result.symbols == ["AAA", "BBB"] and result.skipped == ["SHORT"]
    acc = result.accuracy.set_index("forecaster")
    assert acc.loc["No change", "skill_vs_no_change"] == pytest.approx(0.0)
    trading = result.trading.set_index("strategy")
    assert trading.loc["Forecast rule: No change", "trades"] == 0
    assert trading.loc["Buy and hold", "trades"] == 2
    text = scoreboard.render(result, settings)
    assert "## Forecast accuracy" in text and "Buy and hold" in text


def test_slow_forecasts_are_cached_and_cache_tracks_the_data(tmp_path):
    close = series()
    calls = []

    class Slow(NoChange):
        cache_key = "slow-v1"

        def predict(self, histories, horizon):
            calls.append(len(histories))
            return super().predict(histories, horizon)

    a = wf.cached_walk_forward(close, Slow(), 5, 100, None, tmp_path, "AAA")
    first = len(calls)
    b = wf.cached_walk_forward(close, Slow(), 5, 100, None, tmp_path, "AAA")
    assert len(calls) == first                      # second run read from disk
    pd.testing.assert_frame_equal(a, b)
    wf.cached_walk_forward(close * 1.01, Slow(), 5, 100, None, tmp_path, "AAA")
    assert len(calls) > first                       # new prices are not served stale results
    wf.cached_walk_forward(close, NoChange(), 5, 100, None, tmp_path, "AAA")
    assert len(list(tmp_path.iterdir())) == 2       # fast forecasters are never cached


def test_timesfm_wrapper_passes_only_recent_history(monkeypatch):
    from silkperfect.forecasters import TimesFM

    class FakeModel:
        def forecast(self, horizon, inputs):
            self.inputs = inputs
            return np.array([np.full(64, x[-1] + 1) for x in inputs]), None

    fake = FakeModel()
    tf = TimesFM(max_context=50)
    monkeypatch.setattr(tf, "_load", lambda: fake)
    out = tf.predict([np.arange(200.0), np.arange(30.0)], horizon=5)
    assert out.shape == (2, 5) and out[0, -1] == 200.0
    assert [len(x) for x in fake.inputs] == [50, 30]
    assert "ctx50" in tf.cache_key


def test_skill_by_year_and_symbol_counts_reported():
    frames = []
    for i, sym in enumerate(["AAA", "NIFTY 50"]):
        b = bars(series(420, seed=i))
        frames.append(pd.DataFrame({"date": b.index, "symbol": sym, "adj_open": b["Open"],
                                    "adj_high": b["High"], "adj_low": b["Low"],
                                    "adj_close": b["Close"], "adj_volume": b["Volume"]}))
    settings = scoreboard.Settings(min_history=200)
    result = scoreboard.run(pd.concat(frames, ignore_index=True), ["AAA"], settings)
    assert {"2020", "2021"} <= set(result.skill_by_year.columns)
    assert result.accuracy.set_index("forecaster").loc["No change", "symbols_beaten"] == "0 of 1"
    assert "by year" in scoreboard.render(result, settings)
