import json

import numpy as np
import pandas as pd
import pytest

from silkperfect import daytrade
from silkperfect.costs import CostModel

FREE = CostModel(brokerage_flat=0, stt=0, exchange_txn=0, sebi_fee=0, stamp_duty_buy=0,
                 dp_charge_sell=0, slippage_bps=0)


def day(path):
    """75 bars. Opening range 100-102 (middle 101), then prices from `path` by bar index.

    Bars after the first one given (the entry bar) sit quietly at its close,
    clear of both the stop and the target, unless `path` says otherwise.
    """
    bars = np.full((75, 4), 101.0)
    bars[:3] = [[101, 102, 100, 101]] * 3
    first = min(path)
    rest = path[first][3]
    bars[first + 1:] = [rest, rest + 0.2, rest - 0.2, rest]
    for i, (o, h, l, c) in path.items():
        bars[i] = [o, h, l, c]
    return bars


def test_no_close_above_the_range_means_no_trade():
    s = daytrade.DayTradeSettings(costs=FREE)
    assert daytrade.trade_session(day({5: (101, 103, 101, 102)}), s) is None     # a wick above, close at the high
    late = daytrade._slot("15:00") + 1
    assert daytrade.trade_session(day({late: (101, 104, 101, 103)}), s) is None  # too late in the day


def test_target_stop_and_tie_follow_the_original_rule():
    s = daytrade.DayTradeSettings(costs=FREE)
    entry = {5: (101, 103.2, 101, 103)}                    # closes at 103: risk 2, target 105
    win = daytrade.trade_session(day({**entry, 9: (103, 105, 102.5, 104.5)}), s)
    assert (win["entry"], win["stop"], win["target"]) == (103.0, 101.0, 105.0)
    assert win["outcome"] == "target" and win["gross_r"] == pytest.approx(1.0)
    loss = daytrade.trade_session(day({**entry, 9: (103, 103, 101, 101.5)}), s)
    assert loss["outcome"] == "stop" and loss["gross_r"] == pytest.approx(-1.0)
    both = daytrade.trade_session(day({**entry, 9: (103, 105.5, 100.5, 104)}), s)
    assert both["outcome"] == "stop"                       # a bar touching both counts as a loss
    same_bar = daytrade.trade_session(day({5: (101, 106, 100.5, 103)}), s)
    assert same_bar["outcome"] == "time"                   # the entry bar itself is not checked


def test_open_trade_is_closed_at_the_flat_time():
    s = daytrade.DayTradeSettings(costs=FREE)
    flat = daytrade._slot("15:20")
    path = {5: (101, 103.2, 101, 103), flat: (104, 104, 104, 104), flat + 1: (120, 120, 90, 90)}
    t = daytrade.trade_session(day(path), s)
    assert t["outcome"] == "time" and t["exit"] == 104 and t["gross_r"] == pytest.approx(0.5)


def test_costs_reduce_the_result_and_scale_with_a_tight_stop():
    entry = {5: (101, 103.2, 101, 103), 9: (103, 105, 102.5, 104.5)}
    free = daytrade.trade_session(day(entry), daytrade.DayTradeSettings(costs=FREE))
    paid = daytrade.trade_session(day(entry), daytrade.DayTradeSettings())
    assert paid["gross_r"] == free["gross_r"] and paid["net_r"] < free["net_r"]
    cost_pct = paid["gross_pct"] - paid["net_pct"]
    assert 0.15 < cost_pct < 0.35                          # about a quarter of a percent a round trip
    assert free["gross_r"] - paid["net_r"] == pytest.approx(cost_pct / paid["risk_pct"])
    c = CostModel.intraday()
    assert c.cost("buy", 100, 100.0) < c.cost("sell", 100, 100.0)     # sales tax is on the sell side only
    assert c.cost("sell", 100, 100.0) < CostModel().cost("sell", 100, 100.0)


def test_loader_fills_short_gaps_and_drops_broken_days(tmp_path):
    offset = 19800
    def stamps(date):
        base = int(pd.Timestamp(f"{date} 09:15").timestamp()) - 0
        return [base - offset + 300 * i for i in range(75)]
    good, gappy, broken = stamps("2026-11-02"), stamps("2026-11-03"), stamps("2026-11-04")
    close = [100.0 + i for i in range(75)]
    def quote(blank):
        vals = [None if i in blank else v for i, v in enumerate(close)]
        return vals
    blanks = [set(), {72, 73, 74}, {1, 40, 41, 42, 43}]
    series = [quote(b) for b in blanks]
    flat = [v for s in series for v in s]
    doc = {"chart": {"result": [{"meta": {"gmtoffset": offset}, "timestamp": good + gappy + broken,
           "indicators": {"quote": [{"open": flat, "high": flat, "low": flat, "close": flat}]}}]}}
    path = tmp_path / "X.json"
    path.write_text(json.dumps(doc))
    sessions = daytrade.read_sessions(path)
    assert sorted(d.strftime("%Y-%m-%d") for d in sessions) == ["2026-11-02", "2026-11-03"]
    filled = sessions[pd.Timestamp("2026-11-03")]
    assert filled.shape == (75, 4) and list(filled[72:, 3]) == [171.0, 171.0, 171.0]


def test_summary_counts_days_not_trades_for_strength():
    rows = []
    for d in range(10):
        for k in range(20):                                # 20 trades a day that move together
            r = 0.5 if d % 2 == 0 else -0.5
            rows.append({"symbol": f"S{k}", "date": pd.Timestamp("2026-10-01") + pd.Timedelta(days=d),
                         "outcome": "target" if r > 0 else "stop", "gross_r": r, "net_r": r - 0.3,
                         "gross_pct": r, "net_pct": r - 0.3, "risk_pct": 1.0})
    trades = pd.DataFrame(rows)
    m = daytrade.summarise(trades, share_days=400)
    assert m["trades"] == 200 and m["days"] == 10 and m["fired_pct"] == 50
    assert abs(m["t_gross"]) < 0.01 and m["t_net"] < -1.5 and m["avg_net_r"] == pytest.approx(-0.3)
    text = daytrade.render(trades, m, daytrade.DayTradeSettings())
    assert "no reliable edge even before costs" in text
