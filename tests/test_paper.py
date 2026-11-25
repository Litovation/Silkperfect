import numpy as np
import pandas as pd
import pytest

from silkperfect import paper, ranking
from silkperfect.costs import CostModel
from test_ranking import make_panel


def market():
    panel = make_panel(n_days=900, n_stocks=30)
    idx = panel.close.index
    fund = pd.DataFrame({"date": idx, "symbol": paper.FUND_SYMBOL, "adj_open": 100.0,
                         "adj_high": 101.0, "adj_low": 99.0,
                         "adj_close": np.linspace(100, 150, len(idx)), "adj_volume": 1e6})
    return panel, fund


def plan(**kw):
    return paper.Plan(**{"amount": 10_000.0, "shares_held": 3, "swap_every_days": 63, **kw})


@pytest.fixture(autouse=True)
def small_universe(monkeypatch):
    real = paper.Plan.settings

    def settings(self):
        s = real(self)
        s.universe_size, s.context, s.min_history, s.liquidity_window = 20, 260, 300, 60
        return s
    monkeypatch.setattr(paper.Plan, "settings", settings)


def test_looking_back_adds_up():
    panel, fund = market()
    o = paper.run_plan(panel, fund, plan())
    assert o.equity.iloc[0] == 10_000 and o.bank.iloc[0] == 10_000 and o.everything.iloc[0] == 10_000
    held = float(o.holdings["Worth now (Rs)"].sum())
    assert o.equity.iloc[-1] == pytest.approx(held + o.cash)
    assert o.fees == pytest.approx(o.trades["fees"].sum()) and o.cash >= 0
    assert (o.holdings["How many"] > 0).all() and len(o.holdings) <= 3
    peak, low, pct = o.worst_fall
    assert low <= peak and pct <= 0
    years = (o.bank.index[-1] - o.bank.index[0]).days / 365.25
    assert o.bank.iloc[-1] == pytest.approx(10_000 * (1 + paper.BANK_RATE) ** years)


def test_fund_buys_whole_units_and_pays_fees():
    bars = pd.DataFrame({"Open": [100.0, 100.0, 100.0], "Close": [100.0, 110.0, 120.0]},
                        index=pd.bdate_range("2024-01-01", periods=3))
    costs = CostModel()
    value = paper.buy_and_hold(bars, 1_050.0, bars.index[0], costs)
    units = 10                                    # the eleventh unit would not leave room for fees
    left = 1_050.0 - units * 100 - costs.cost("buy", units, 100.0)
    assert left >= 0 and value.iloc[-1] == pytest.approx(left + units * 120.0)


def test_pretend_account_starts_today_then_trades_next_day(tmp_path):
    panel, fund = market()
    path = tmp_path / "acct.json"
    assert paper.load_account(path) is None
    start = panel.close.index[-1]
    paper.start_account(plan(), start, path)
    saved = paper.load_account(path)
    assert saved["start"] == start and saved["plan"] == plan()

    today = paper.run_plan(panel, fund, saved["plan"], start=saved["start"])
    assert len(today.trades) == 0 and today.equity.iloc[-1] == 10_000
    assert len(today.picks_waiting) == 3 and today.days_to_next_swap == 63

    # Twenty market days later, with new prices in the data.
    earlier = panel.close.index[-21]
    later = paper.run_plan(panel, fund, saved["plan"], start=earlier)
    assert set(later.trades["action"]) == {"Buy"} and later.trades["date"].min() == panel.close.index[-20]
    assert later.days_to_next_swap == 43 and later.picks_waiting == []
    assert later.equity.iloc[-1] == pytest.approx(later.holdings["Worth now (Rs)"].sum() + later.cash)
    paper.close_account(path)
    assert paper.load_account(path) is None


def test_same_data_gives_the_same_account():
    panel, fund = market()
    start = panel.close.index[-200]
    a = paper.run_plan(panel, fund, plan(), start=start)
    b = paper.run_plan(panel, fund, plan(), start=start)
    pd.testing.assert_series_equal(a.equity, b.equity)
    pd.testing.assert_frame_equal(a.trades, b.trades)
