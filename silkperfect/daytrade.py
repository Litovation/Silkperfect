"""Test of an opening-range-breakout day trade on NSE shares.

The rule is the one in the "day-trader-skill" pack (MIT licence,
github.com/jakeschincariol/day-trader-skill, trader-entry / trader-exit /
trader-timemachine), moved from New York hours to NSE hours:

- Opening range: high and low of the first 15 minutes (three 5-minute bars).
- Entry: the first later bar that CLOSES above the range high, at that close.
  Buying only. One trade per share per day.
- Stop: the middle of the opening range. Target: the same distance above the
  entry (1R). Bar by bar the stop is checked first, so a bar that touches
  both counts as a loss.
- Otherwise the trade is closed at a fixed time before the market shuts.

Results are in R: +1 is a win of the amount risked, -1 a loss of it.
Prices are Yahoo Finance 5-minute bars, which only go back 60 trading days.
"""
from __future__ import annotations

import json
import math
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from . import config
from .costs import CostModel

CHART_URL = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range=60d&interval=5m"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; silkperfect-research)"}
PAUSE = 0.5                      # seconds between requests, to be polite to a free service
SESSION_BARS = 75                # 9:15 to 15:30 in 5-minute bars
OPEN_MINUTE = 9 * 60 + 15


@dataclass
class DayTradeSettings:
    or_minutes: int = 15             # opening range length
    target_r: float = 1.0
    last_entry: str = "15:00"        # no new trades after this bar close (30 minutes before the close)
    flat_by: str = "15:20"           # close whatever is open at this time
    position: float = 10_000.0       # rupees per trade, used to work out fees
    costs: CostModel = field(default_factory=CostModel.intraday)


def _slot(clock: str) -> int:
    """Index of the bar that CLOSES at this time."""
    h, m = map(int, clock.split(":"))
    return (h * 60 + m - OPEN_MINUTE) // 5 - 1


def yahoo_symbol(symbol: str) -> str:
    return urllib.parse.quote(f"{symbol}.NS", safe=".-")


def fetch(symbols: list[str], out_dir: Path = config.INTRADAY_DIR, refresh: bool = False,
          progress=None) -> dict[str, str]:
    """Download 60 days of 5-minute bars per symbol. Returns {symbol: problem} for failures."""
    out_dir.mkdir(parents=True, exist_ok=True)
    problems = {}
    for k, symbol in enumerate(symbols, 1):
        path = out_dir / f"{symbol}.json"
        if path.exists() and not refresh:
            continue
        url = CHART_URL.format(symbol=yahoo_symbol(symbol))
        try:
            for attempt in range(3):
                r = requests.get(url, headers=HEADERS, timeout=30)
                if r.status_code != 429:
                    break
                time.sleep(5 * (attempt + 1))
            if r.status_code == 200 and (r.json().get("chart") or {}).get("result"):
                path.write_text(r.text)
            else:
                problems[symbol] = f"HTTP {r.status_code}"
        except (requests.RequestException, ValueError) as exc:
            problems[symbol] = str(exc)[:80]
        if progress and k % 25 == 0:
            progress(f"{k} of {len(symbols)} downloaded")
        time.sleep(PAUSE)
    return problems


MAX_GAPS = 3                     # blank bars tolerated in a day


def read_sessions(path: Path) -> dict[pd.Timestamp, np.ndarray]:
    """Usable sessions: {date: array of 75 rows (open, high, low, close)}.

    Yahoo often leaves a few bars blank, mostly the last ones of the day. Up
    to MAX_GAPS blank bars are filled flat at the last traded price; a day
    with more, or with a blank in its first half hour, is dropped.
    """
    result = json.loads(Path(path).read_text())["chart"]["result"][0]
    stamps = result.get("timestamp") or []
    quote = result["indicators"]["quote"][0]
    offset = result["meta"]["gmtoffset"]
    when = pd.to_datetime(np.array(stamps) + offset, unit="s")
    df = pd.DataFrame({"o": quote["open"], "h": quote["high"], "l": quote["low"],
                       "c": quote["close"]}, index=when).astype(float)
    df["slot"] = (df.index.hour * 60 + df.index.minute - OPEN_MINUTE) // 5
    sessions = {}
    for day, bars in df.groupby(df.index.normalize()):
        bars = bars[(bars["slot"] >= 0) & (bars["slot"] < SESSION_BARS)]
        bars = bars.drop_duplicates("slot").set_index("slot").reindex(range(SESSION_BARS))
        blank = bars["c"].isna()
        if blank.sum() > MAX_GAPS or blank.iloc[:6].any():
            continue
        last = bars["c"].ffill()
        for col in ("o", "h", "l", "c"):
            bars[col] = bars[col].where(~blank, last)
        sessions[day] = bars[["o", "h", "l", "c"]].to_numpy()
    return sessions


def trade_session(bars: np.ndarray, s: DayTradeSettings) -> dict | None:
    """Apply the rule to one day's bars. Returns the trade, or None if it never triggered."""
    n = s.or_minutes // 5
    last_entry, flat = _slot(s.last_entry), _slot(s.flat_by)
    high, low = bars[:n, 1].max(), bars[:n, 2].min()
    entry_bar = next((i for i in range(n, last_entry + 1) if bars[i, 3] > high), None)
    if entry_bar is None:
        return None
    entry = round(float(bars[entry_bar, 3]), 2)
    stop = math.floor(round((high + low) / 2 * 100, 4)) / 100      # rounded away from the entry
    risk = entry - stop
    if risk <= 0:
        return None
    target = round(entry + s.target_r * risk, 2)
    outcome, exit_price = "time", float(bars[flat, 3])
    for i in range(entry_bar + 1, flat + 1):
        if bars[i, 2] <= stop:                                     # stop first, as the skill does
            outcome, exit_price = "stop", stop
            break
        if bars[i, 1] >= target:
            outcome, exit_price = "target", target
            break
    gross = (exit_price - entry) / risk
    shares = s.position / entry
    fees = s.costs.cost("buy", shares, entry) + s.costs.cost("sell", shares, exit_price)
    return {"entry_bar": entry_bar, "entry": entry, "stop": stop, "target": target,
            "outcome": outcome, "exit": exit_price, "risk_pct": risk / entry * 100,
            "gross_r": gross, "net_r": gross - fees / (shares * risk),
            "gross_pct": (exit_price / entry - 1) * 100,
            "net_pct": (exit_price / entry - 1) * 100 - fees / s.position * 100}


def run(sessions_by_symbol: dict[str, dict], settings: DayTradeSettings | None = None) -> pd.DataFrame:
    """Every trade the rule would have taken. One row per symbol and day it fired."""
    s = settings or DayTradeSettings()
    rows = []
    for symbol, sessions in sessions_by_symbol.items():
        for day, bars in sessions.items():
            trade = trade_session(bars, s)
            if trade:
                rows.append({"symbol": symbol, "date": day, **trade})
    return pd.DataFrame(rows)


def _t_stat(daily: pd.Series) -> float:
    return float(daily.mean() / daily.std() * math.sqrt(len(daily))) if len(daily) > 2 and daily.std() > 0 else np.nan


def summarise(trades: pd.DataFrame, share_days: int) -> dict:
    """Headline numbers. The t-statistics treat each DAY as one observation,
    because trades taken on the same day rise and fall together."""
    by_day_gross = trades.groupby("date")["gross_r"].mean()
    by_day_net = trades.groupby("date")["net_r"].mean()
    counts = trades["outcome"].value_counts()
    return {
        "share_days": share_days, "trades": len(trades), "days": trades["date"].nunique(),
        "symbols": trades["symbol"].nunique(),
        "fired_pct": len(trades) / share_days * 100 if share_days else np.nan,
        "target_pct": counts.get("target", 0) / len(trades) * 100,
        "stop_pct": counts.get("stop", 0) / len(trades) * 100,
        "time_pct": counts.get("time", 0) / len(trades) * 100,
        "avg_gross_r": trades["gross_r"].mean(), "avg_net_r": trades["net_r"].mean(),
        "avg_gross_pct": trades["gross_pct"].mean(), "avg_net_pct": trades["net_pct"].mean(),
        "avg_risk_pct": trades["risk_pct"].mean(),
        "cost_in_r": (trades["gross_r"] - trades["net_r"]).mean(),
        "t_gross": _t_stat(by_day_gross), "t_net": _t_stat(by_day_net),
        "winning_days_pct": (by_day_net > 0).mean() * 100,
        "start": trades["date"].min(), "end": trades["date"].max(),
    }


def render(trades: pd.DataFrame, m: dict, s: DayTradeSettings) -> str:
    daily = trades.groupby("date").agg(trades=("net_r", "size"), gross=("gross_r", "mean"),
                                       net=("net_r", "mean"))
    worst, best = daily["net"].idxmin(), daily["net"].idxmax()
    verdict = ("a real edge before and after costs" if m["t_net"] >= 2 else
               "an edge before costs that fees remove" if m["t_gross"] >= 2 else
               "no reliable edge even before costs")
    lines = [
        "# Day-trade rule test (opening-range breakout)",
        "",
        "The rule comes from the day-trader-skill pack (github.com/jakeschincariol/day-trader-skill),",
        "applied unchanged to NSE shares with NSE hours and Indian intraday costs.",
        "",
        f"- Period: {m['start']:%d %b %Y} to {m['end']:%d %b %Y} ({m['days']} trading days; Yahoo's "
        "5-minute history goes back no further)",
        f"- Shares: the {m['symbols']} most traded NSE shares that had data",
        f"- Rule: buy the first 5-minute close above the first {s.or_minutes} minutes' high; stop at the "
        f"middle of that range; target {s.target_r:g} times the risk; no entries after {s.last_entry}; "
        f"out by {s.flat_by}",
        f"- Costs: intraday brokerage, taxes and charges plus {s.costs.slippage_bps:g} basis points of "
        f"slippage per side, on Rs {s.position:,.0f} per trade",
        "",
        "## Result",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Trades taken | {m['trades']:,} |",
        f"| Share-days where the rule fired | {m['fired_pct']:.0f}% |",
        f"| Hit the target | {m['target_pct']:.1f}% |",
        f"| Hit the stop | {m['stop_pct']:.1f}% |",
        f"| Closed at {s.flat_by} | {m['time_pct']:.1f}% |",
        f"| Average distance to the stop | {m['avg_risk_pct']:.2f}% of the price |",
        f"| Average result before costs | {m['avg_gross_r']:+.3f} R ({m['avg_gross_pct']:+.3f}% of the money in the trade) |",
        f"| Costs per trade | {m['cost_in_r']:.3f} R |",
        f"| Average result after costs | {m['avg_net_r']:+.3f} R ({m['avg_net_pct']:+.3f}%) |",
        f"| Strength before costs (t, needs 2) | {m['t_gross']:+.2f} |",
        f"| Strength after costs (t, needs 2) | {m['t_net']:+.2f} |",
        f"| Days that made money after costs | {m['winning_days_pct']:.0f}% |",
        "",
        f"Verdict: **{verdict}**.",
        "",
        "R is the amount risked on a trade: +1 R is a win of that amount, -1 R a loss of it.",
        "Strength treats each day as one observation, since trades on the same day move together.",
        "",
        f"Best day: {best:%d %b %Y} ({daily.loc[best, 'net']:+.2f} R a trade over "
        f"{int(daily.loc[best, 'trades'])} trades). Worst day: {worst:%d %b %Y} "
        f"({daily.loc[worst, 'net']:+.2f} R over {int(daily.loc[worst, 'trades'])} trades).",
        "",
        "## Limits of this test",
        "",
        "- Sixty trading days is one stretch of market weather, not a full cycle.",
        "- Yahoo's bars are free and unofficial; a stop is assumed to fill exactly at its price,",
        "  which is kinder than real trading when the price gaps through it.",
        "- Buying only, as in the original rule.",
        "",
    ]
    return "\n".join(lines)


def save(trades: pd.DataFrame, text: str, out_dir: Path = config.REPORTS_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "daytrade.md").write_text(text)
    trades.assign(date=trades["date"].dt.strftime("%Y-%m-%d")).round(4).to_csv(
        out_dir / "daytrade_trades.csv", index=False)
    daily = trades.groupby("date").agg(trades=("net_r", "size"), gross_r=("gross_r", "mean"),
                                       net_r=("net_r", "mean")).round(4)
    daily.to_csv(out_dir / "daytrade_daily.csv")
