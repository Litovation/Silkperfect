from pathlib import Path

import numpy as np
import pandas as pd

from silkperfect import scoreboard, visualize
from silkperfect.forecasters import Forecaster, NoChange, Drift


class Lagged(Forecaster):
    """Stand-in for TimesFM: a cheap, deterministic forecaster with a cache key."""
    name = "TimesFM 2.5"
    cache_key = "test-lagged"

    def predict(self, histories, horizon):
        return np.array([np.full(horizon, h[-2]) for h in histories], dtype=float)


def _prices(days=900, symbols=("AAA", "BBB", "NIFTY 50"), seed=3):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2019-01-01", periods=days)
    rows = []
    for sym in symbols:
        px = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, days)))
        rows += [dict(symbol=sym, date=d, series="EQ", adj_open=p, adj_high=p * 1.01,
                      adj_low=p * 0.99, adj_close=p, adj_volume=1e6) for d, p in zip(dates, px)]
    return pd.DataFrame(rows)


def _page(tmp_path: Path, events=None) -> str:
    settings = scoreboard.Settings(horizon=5, min_history=300, capital=500_000.0)
    result = scoreboard.run(_prices(), ["AAA", "BBB"], settings,
                            [NoChange(), Drift(120), Lagged()], cache_dir=tmp_path)
    return visualize.build_html(result, settings, events)


def test_page_has_all_sections_and_one_panel_per_stock(tmp_path):
    page = _page(tmp_path)
    for heading in ("The verdict", "Money over time", "How accurate are the guesses?",
                    "Trading results after costs", "Per stock", "Data checks"):
        assert heading in page
    assert page.count('class="stock"') == 2
    assert 'id="sym"' in page
    assert page.count("<svg") >= 5


def test_verdict_uses_the_pass_rule(tmp_path):
    page = _page(tmp_path)
    # The stand-in forecaster is not better than "no change", so it must fail the test.
    assert "FAILS" in page
    assert "PASSES" not in page


def test_stock_panel_shows_today_and_scatter(tmp_path):
    page = _page(tmp_path)
    assert "guess in 5 trading days" in page
    assert "Guess vs reality" in page


def test_text_from_data_is_escaped(tmp_path):
    events = pd.DataFrame([{"symbol": "AAA", "ex_date": pd.Timestamp("2021-01-04"),
                            "purpose": "<script>alert(1)</script>", "status": "unparsed",
                            "kind": "rights", "factor": 1.0}])
    page = _page(tmp_path, events)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_save_writes_file(tmp_path):
    out = visualize.save("<html></html>", tmp_path / "v.html")
    assert out.read_text() == "<html></html>"
