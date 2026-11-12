"""Tests of rule-based methods from the Chinese retail quant community.

Timing rules (each share is either held or in cash):

- **Chan theory (缠论) buy and sell points**, computed by czsc
  (github.com/waditu/czsc, Apache-2.0, by zengbin93). Hold from a buy point
  until the next sell point.
- **RSRS** (阻力支撑相对强度, from a 2017 光大证券 research report): the slope
  of daily highs against daily lows over 18 days, standardised over 600 days.
  Buy above +0.7, sell below -0.7.
- **Turtle breakout** (海龟): buy a new 20-day high, sell a new 10-day low.

Each rule runs on the same fixed list of shares, every share with the same
money, and is judged against simply holding those same shares.

All settings are the published defaults. None was tuned on NSE data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import backtest, config
from .costs import CostModel
from .ranking import Panel, Signal

CZSC_SIGNALS = {
    "first_buy": "cxt_first_buy_V221126", "first_sell": "cxt_first_sell_V221126",
    "second": "cxt_second_bs_V230320", "third": "cxt_third_bs_V230318",
}
BUY_WORDS = {"一买": 1, "二买": 2, "三买": 3}
SELL_WORDS = {"一卖": 1, "二卖": 2, "三卖": 3}


def bars_for(panel: Panel, symbol: str) -> pd.DataFrame:
    """One share's adjusted daily bars, days with a price only."""
    df = pd.DataFrame({"Open": panel.open[symbol], "High": panel.high[symbol],
                       "Low": panel.low[symbol], "Close": panel.close[symbol],
                       "Volume": panel.volume[symbol], "Value": panel.value[symbol]})
    return df.dropna(subset=["Open", "High", "Low", "Close"])


def hold_between(buy: pd.Series, sell: pd.Series) -> pd.Series:
    """1 from a day `buy` is true until a day `sell` is true, else 0."""
    out, held = np.zeros(len(buy), dtype=int), False
    for i, (b, s) in enumerate(zip(buy.to_numpy(), sell.to_numpy())):
        if s:
            held = False
        elif b:
            held = True
        out[i] = int(held)
    return pd.Series(out, index=buy.index)


def chan_points(bars: pd.DataFrame, symbol: str = "X") -> pd.DataFrame:
    """Chan theory buy and sell points for each day, from czsc.

    Returns columns buy and sell holding 0, or 1/2/3 for the class of point.
    Each day's value uses bars up to that day only.
    """
    from czsc import Freq, format_standard_kline, generate_czsc_signals
    df = pd.DataFrame({"symbol": symbol, "dt": bars.index, "open": bars["Open"].to_numpy(),
                       "close": bars["Close"].to_numpy(), "high": bars["High"].to_numpy(),
                       "low": bars["Low"].to_numpy(), "vol": bars["Volume"].fillna(0).to_numpy(),
                       "amount": bars["Value"].fillna(0).to_numpy()})
    raw = format_standard_kline(df, freq=Freq.D)
    cfg = [{"name": name, "freq": "日线", "di": 1} for name in CZSC_SIGNALS.values()]
    out = generate_czsc_signals(raw, cfg, sdt=f"{bars.index[0]:%Y%m%d}", init_n=100, df=True)
    when = pd.to_datetime(out["dt"]).dt.tz_localize(None)
    cols = [c for c in out.columns if "V2" in c]
    kind = pd.DataFrame({c: out[c].str.split("_").str[0].to_numpy() for c in cols}, index=when)
    buy = kind.apply(lambda col: col.map(BUY_WORDS)).max(axis=1).fillna(0).astype(int)
    sell = kind.apply(lambda col: col.map(SELL_WORDS)).max(axis=1).fillna(0).astype(int)
    return pd.DataFrame({"buy": buy, "sell": sell}).reindex(bars.index).fillna(0).astype(int)


def chan_positions(points: pd.DataFrame, classes: tuple[int, ...] = (1, 2, 3)) -> pd.Series:
    return hold_between(points["buy"].isin(classes), points["sell"].isin(classes))


def rsrs_positions(bars: pd.DataFrame, n: int = 18, m: int = 600, enter: float = 0.7,
                   leave: float = -0.7) -> pd.Series:
    """RSRS timing: standardised slope of high on low."""
    high, low = bars["High"], bars["Low"]
    slope = high.rolling(n).cov(low) / low.rolling(n).var()
    z = (slope - slope.rolling(m, min_periods=m // 3).mean()) / slope.rolling(m, min_periods=m // 3).std()
    return hold_between(z > enter, z < leave)


def turtle_positions(bars: pd.DataFrame, entry: int = 20, exit_: int = 10) -> pd.Series:
    """Turtle breakout: in on a close above the prior 20-day high, out below the prior 10-day low."""
    top = bars["High"].rolling(entry).max().shift(1)
    floor = bars["Low"].rolling(exit_).min().shift(1)
    return hold_between(bars["Close"] > top, bars["Close"] < floor)


RULES = {
    "Chan theory: all buy and sell points": lambda bars, pts: chan_positions(pts, (1, 2, 3)),
    "Chan theory: first-class points only": lambda bars, pts: chan_positions(pts, (1,)),
    "Chan theory: third-class points only": lambda bars, pts: chan_positions(pts, (3,)),
    "RSRS timing (18, 600, 0.7)": lambda bars, pts: rsrs_positions(bars),
    "Turtle breakout (20, 10)": lambda bars, pts: turtle_positions(bars),
}
HOLD = "Hold the same shares"


@dataclass
class TimingResult:
    summary: pd.DataFrame
    equity: dict
    symbols: list[str]
    start: pd.Timestamp
    end: pd.Timestamp
    capital: float


def run_timing(panel: Panel, symbols: list[str], start: pd.Timestamp, capital: float = 500_000.0,
               costs: CostModel | None = None, progress=None) -> TimingResult:
    """Run every timing rule on every share from `start`, against holding the share."""
    costs = costs or CostModel()
    curves: dict[str, list[pd.Series]] = {name: [] for name in [HOLD, *RULES]}
    stats: dict[str, list[dict]] = {name: [] for name in curves}
    used = []
    for k, symbol in enumerate(symbols, 1):
        bars = bars_for(panel, symbol)
        window = bars[bars.index >= start]
        if len(window) < 60 or len(bars) - len(window) < 250:
            continue
        used.append(symbol)
        points = chan_points(bars, symbol)
        signals = {HOLD: pd.Series(1, index=bars.index)}
        signals.update({name: rule(bars, points) for name, rule in RULES.items()})
        ohlcv = window[["Open", "High", "Low", "Close", "Volume"]]
        for name, signal in signals.items():
            res = backtest.run_signal(ohlcv, signal.loc[window.index], capital, costs)
            curves[name].append(res["equity"])
            stats[name].append({"symbol": symbol, "final": float(res["equity"].iloc[-1]),
                                "trades": res["trades"], "costs": res["costs"],
                                "exposure": res["exposure_pct"]})
        if progress and k % 25 == 0:
            progress(f"{k} of {len(symbols)} shares done")
    rows, equity = [], {}
    held_final = pd.DataFrame(stats[HOLD]).set_index("symbol")["final"]
    for name in curves:
        total = backtest.combine_equity(curves[name], capital)
        equity[name] = total
        per = pd.DataFrame(stats[name]).set_index("symbol")
        rows.append({"rule": name, **backtest.curve_metrics(total),
                     "trades": int(per["trades"].sum()), "costs_rupees": float(per["costs"].sum()),
                     "time_invested_pct": float(per["exposure"].mean()),
                     "shares_beating_hold_pct": np.nan if name == HOLD else
                     float((per["final"] > held_final).mean() * 100)})
    first = min(c.index[0] for c in curves[HOLD])
    last = max(c.index[-1] for c in curves[HOLD])
    return TimingResult(pd.DataFrame(rows), equity, used, first, last, capital)


class ShortTermReversal(Signal):
    """Buy last month's biggest fallers: the pattern reported for Chinese A-shares,
    where one-month reversal, not twelve-month momentum, is the documented effect."""

    def __init__(self, lookback: int = 21):
        self.lookback = lookback
        self.name = "One-month reversal"

    def score(self, close, horizon):
        return -(close.iloc[-1] / close.iloc[-1 - self.lookback] - 1)


def render(result: TimingResult, reversal: pd.DataFrame | None = None) -> str:
    s = result.summary.set_index("rule")
    hold = s.loc[HOLD]
    lines = [
        "# Chinese rule-based methods on NSE shares",
        "",
        f"- Period: {result.start:%d %b %Y} to {result.end:%d %b %Y}",
        f"- Shares: the {len(result.symbols)} most traded NSE shares as they stood at the start, "
        f"Rs {result.capital:,.0f} each, bought or held in cash, full delivery costs",
        f"- The bar: holding those same shares throughout, {hold['cagr_pct']:.1f}% a year "
        f"with a worst drop of {hold['max_drawdown_pct']:.1f}%",
        "- Chan theory points come from czsc (Apache-2.0). RSRS and turtle use their published settings.",
        "",
        "## Timing rules",
        "",
        "| Rule | Per year (%) | vs holding (pts) | Worst drop (%) | Sharpe | Trades | Costs (Rs) "
        "| Time invested (%) | Shares where it beat holding (%) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, r in s.iterrows():
        beat = "n/a" if pd.isna(r["shares_beating_hold_pct"]) else f"{r['shares_beating_hold_pct']:.0f}"
        lines.append(f"| {name} | {r['cagr_pct']:.1f} | {r['cagr_pct'] - hold['cagr_pct']:+.1f} | "
                     f"{r['max_drawdown_pct']:.1f} | {r['sharpe']:.2f} | {int(r['trades']):,} | "
                     f"{r['costs_rupees']:,.0f} | {r['time_invested_pct']:.0f} | {beat} |")
    lines += ["",
              "A timing rule sits in cash part of the time, so a lower return with a much smaller",
              "worst drop can still be a fair trade. Cash earns nothing in this test.", ""]
    if reversal is not None:
        lines += ["## One-month reversal (picking, not timing)", "",
                  "Each month, from the 200 most traded shares, buy the 20 that fell most over the past month.",
                  "",
                  "| Method | Per year (%) | Worst drop (%) | Strength (t, needs 2) |", "| --- | ---: | ---: | ---: |"]
        for _, r in reversal.iterrows():
            t = "n/a" if pd.isna(r.get("rank_t_stat", np.nan)) else f"{r['rank_t_stat']:+.2f}"
            lines.append(f"| {r['method']} | {r['cagr_pct']:.1f} | {r['max_drawdown_pct']:.1f} | {t} |")
        lines.append("")
    return "\n".join(lines)


def save(result: TimingResult, text: str, out_dir: Path = config.REPORTS_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "chinese_methods.md").write_text(text)
    result.summary.round(4).to_csv(out_dir / "chinese_methods.csv", index=False)
