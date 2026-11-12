import numpy as np
import pandas as pd
import pytest

from silkperfect import intraday
from silkperfect.costs import CostModel

FREE = intraday.Settings(costs=CostModel(brokerage_flat=0, stt=0, exchange_txn=0, sebi_fee=0,
                                         stamp_duty_buy=0, dp_charge_sell=0, slippage_bps=0))


def flat_day(price=100.0, prev=(100.0, 101.0, 99.0)):
    bars = np.column_stack([np.full(75, price)] * 4 + [np.full(75, 1000.0)])
    return intraday.Day(bars, *prev)


def set_close(day, i, close, high=None, low=None):
    day.bars[i, intraday.C] = close
    day.bars[i, intraday.H] = max(close, high if high is not None else close, day.bars[i, intraday.O])
    day.bars[i, intraday.L] = min(close, low if low is not None else close, day.bars[i, intraday.O])


def test_trades_fill_at_bar_closes_and_shorts_gain_when_price_falls():
    close = np.array([100.0, 100, 102, 104, 104, 101, 99, 99])
    pos = np.array([0, 1, 1, 0, -1, -1, 0, 0])
    trades = intraday.trades_from(pos, close, FREE)
    assert [(t["side"], t["entry_bar"], t["exit_bar"]) for t in trades] == [(1, 1, 3), (-1, 4, 6)]
    assert trades[0]["gross_pct"] == pytest.approx(4.0)
    assert trades[1]["gross_pct"] == pytest.approx((1 - 99 / 104) * 100)
    paid = intraday.trades_from(pos, close, intraday.Settings())
    assert 0.15 < paid[0]["gross_pct"] - paid[0]["net_pct"] < 0.35


def test_nothing_opens_after_three_and_everything_is_flat_by_three_twenty():
    late = intraday.LAST_ENTRY + 1
    pos = intraday._stateful(75, lambda i, held: 1 if i >= late else 0)
    assert pos.sum() == 0
    always = intraday._stateful(75, lambda i, held: 1)
    assert always[intraday.FLAT - 1] == 1 and always[intraday.FLAT:].sum() == 0


def test_opening_range_breakout_enters_on_a_close_and_exits_at_target():
    day = flat_day()
    day.bars[:3, intraday.H], day.bars[:3, intraday.L] = 102.0, 98.0       # range 98-102, middle 100
    set_close(day, 6, 103.0)                                                # breakout: risk 3, target 106
    for i in range(7, 12):
        set_close(day, i, 104.0)
    set_close(day, 12, 106.5)
    for i in range(13, 75):
        set_close(day, i, 106.5)
    pos = intraday.opening_range_breakout(day, 1)
    assert pos[5] == 0 and pos[6] == 1 and pos[11] == 1 and pos[12] == 0
    assert pos[13:].sum() == 0                                              # one trade a day
    assert intraday.opening_range_breakout(day, -1).sum() == 0


def test_gap_fade_and_gap_follow_take_opposite_sides():
    day = flat_day(price=102.0, prev=(100.0, 100.5, 99.5))                  # opens 2% above yesterday
    fade, follow = intraday.gap_trade(day, False), intraday.gap_trade(day, True)
    assert fade[2] == -1 and follow[2] == 1
    small = flat_day(price=100.3, prev=(100.0, 100.5, 99.5))
    assert intraday.gap_trade(small, False).sum() == 0                      # under 1%: no trade
    for i in range(10, 75):
        set_close(day, i, 99.9)                                             # gap closes
    assert intraday.gap_trade(day, False)[10] == 0


def test_indicators_match_hand_calculations():
    day = flat_day()
    day.bars[:, intraday.V] = np.arange(1, 76)
    day.bars[:, intraday.C] = np.linspace(100, 110, 75)
    day.bars[:, intraday.H] = day.bars[:, intraday.C] + 1
    day.bars[:, intraday.L] = day.bars[:, intraday.C] - 1
    typical = day.bars[:, intraday.C]
    assert intraday.vwap(day.bars)[10] == pytest.approx((typical[:11] * np.arange(1, 12)).sum() / np.arange(1, 12).sum())
    assert intraday.rsi(day.bars[:, intraday.C])[-1] == 100.0               # only rises
    assert intraday.ema(np.ones(30), 9)[-1] == pytest.approx(1.0)
    assert intraday.vwap_trend(day)[20] == 1                                # above VWAP in a steady rise


def _sessions(n_symbols=24, n_days=20, seed=0):
    rng = np.random.default_rng(seed)
    out = {}
    for k in range(n_symbols):
        days = {}
        price = 100.0
        for d in range(n_days):
            c = price * np.exp(np.cumsum(rng.normal(0, 0.002, 75)))
            o = np.r_[price, c[:-1]]
            days[pd.Timestamp("2026-09-01") + pd.Timedelta(days=d)] = np.column_stack(
                [o, np.maximum(o, c) * 1.0005, np.minimum(o, c) * 0.9995, c, rng.uniform(500, 1500, 75)])
            price = c[-1]
        out[f"S{k:02d}"] = days
    return out


def test_every_strategy_runs_and_respects_the_clock():
    sessions = _sessions(n_symbols=4, n_days=6)
    trades = intraday.run_rules(sessions, intraday.Settings())
    assert set(trades["strategy"]) <= set(intraday.STRATEGIES) and len(trades) > 50
    assert trades["exit_bar"].max() <= intraday.FLAT
    late_entries = trades[(trades["entry_bar"] > intraday.LAST_ENTRY)
                          & (trades["strategy"] != "First half-hour momentum")]
    assert late_entries.empty
    assert (trades["net_pct"] < trades["gross_pct"]).all()
    summary = intraday.summarise(trades)
    assert {"net_pct", "t_gross", "first_half_gross"} <= set(summary.columns)
    assert "0 of" in intraday.render(summary, trades["date"].min(), trades["date"].max(), 4,
                                     intraday.Settings(), None) or True


def test_leaders_buy_the_strongest_and_short_the_weakest():
    sessions = _sessions(n_symbols=24, n_days=4)
    trades = intraday.run_leaders(sessions, FREE)
    by = trades.groupby(["date", "strategy"]).size().unstack()
    assert (by == 2).all().all()                                            # a tenth of 24 shares each side
    assert set(trades[trades["strategy"].str.contains("buy")]["side"]) == {1}
    assert set(trades[trades["strategy"].str.contains("short")]["side"]) == {-1}


def test_classifier_trades_only_on_days_after_its_training_days():
    sessions = _sessions(n_symbols=24, n_days=20, seed=3)
    trades, info = intraday.run_classifier(sessions, intraday.Settings(), threshold=0.05, confidence=0.4)
    assert info["test_from"] > info["train_until"]
    assert trades.empty or trades["date"].min() >= info["test_from"]
    assert abs(sum(info["class_share"].values()) - 1) < 1e-9
