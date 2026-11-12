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
    stop_rule: str = "or_mid"        # "or_mid": middle of the range; "or_far": its far edge
    side: str = "buy"                # "buy" above the range, or "sell" (short) below it
    min_volume_x: float = 0.0        # entry bar volume needed, as a multiple of the range bars' average
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
    """Usable sessions: {date: array of 75 rows (open, high, low, close, volume)}.

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
                       "c": quote["close"], "v": quote.get("volume") or [0] * len(stamps)},
                      index=when).astype(float)
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
        bars["v"] = bars["v"].fillna(0.0)
        sessions[day] = bars[["o", "h", "l", "c", "v"]].to_numpy()
    return sessions


def trade_session(bars: np.ndarray, s: DayTradeSettings) -> dict | None:
    """Apply the rule to one day's bars. Returns the trade, or None if it never triggered."""
    n = s.or_minutes // 5
    long = s.side == "buy"
    last_entry, flat = _slot(s.last_entry), _slot(s.flat_by)
    high, low = bars[:n, 1].max(), bars[:n, 2].min()
    need_volume = s.min_volume_x * bars[:n, 4].mean() if s.min_volume_x and bars.shape[1] > 4 else 0.0

    def triggers(i: int) -> bool:
        beyond = bars[i, 3] > high if long else bars[i, 3] < low
        return bool(beyond and (not need_volume or bars[i, 4] >= need_volume))

    entry_bar = next((i for i in range(n, last_entry + 1) if triggers(i)), None)
    if entry_bar is None:
        return None
    entry = round(float(bars[entry_bar, 3]), 2)
    level = (high + low) / 2 if s.stop_rule == "or_mid" else (low if long else high)
    cents = round(level * 100, 4)                                  # rounded away from the entry
    stop = (math.floor(cents) if long else math.ceil(cents)) / 100
    risk = entry - stop if long else stop - entry
    if risk <= 0:
        return None
    target = round(entry + s.target_r * risk, 2) if long else round(entry - s.target_r * risk, 2)
    outcome, exit_price = "time", float(bars[flat, 3])
    for i in range(entry_bar + 1, flat + 1):
        if (bars[i, 2] <= stop) if long else (bars[i, 1] >= stop):  # stop first, as the skill does
            outcome, exit_price = "stop", stop
            break
        if (bars[i, 1] >= target) if long else (bars[i, 2] <= target):
            outcome, exit_price = "target", target
            break
    move = exit_price - entry if long else entry - exit_price
    shares = s.position / entry
    first, second = ("buy", "sell") if long else ("sell", "buy")
    fees = s.costs.cost(first, shares, entry) + s.costs.cost(second, shares, exit_price)
    return {"entry_bar": entry_bar, "entry": entry, "stop": stop, "target": target,
            "outcome": outcome, "exit": exit_price, "risk_pct": risk / entry * 100,
            "gross_r": move / risk, "net_r": move / risk - fees / (shares * risk),
            "gross_pct": move / entry * 100,
            "net_pct": move / entry * 100 - fees / s.position * 100}


def run(sessions_by_symbol: dict[str, dict], settings: DayTradeSettings | None = None) -> pd.DataFrame:
    """Every trade the rule would have taken. One row per symbol and day it fired."""
    s = settings or DayTradeSettings()
    rows = []
    for symbol, sessions in sessions_by_symbol.items():
        for day, bars in sessions.items():
            trade = trade_session(bars, s)
            if trade:
                rows.append({"symbol": symbol, "date": day, **trade})
    columns = ["symbol", "date", "entry_bar", "entry", "stop", "target", "outcome", "exit",
               "risk_pct", "gross_r", "net_r", "gross_pct", "net_pct"]
    return pd.DataFrame(rows, columns=columns)


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


def variants() -> list[tuple[str, DayTradeSettings]]:
    """Every setting the original skill offers, on both sides of the market."""
    out = []
    for side in ("buy", "sell"):
        for minutes in (15, 30):
            for stop in ("or_mid", "or_far"):
                for target in (1.0, 2.0, 3.0):
                    for volume in (0.0, 1.5):
                        label = (f"{'Buy' if side == 'buy' else 'Short'}, {minutes}-min range, stop at "
                                 f"{'middle' if stop == 'or_mid' else 'far edge'}, target {target:g}R"
                                 + (", volume 1.5x" if volume else ""))
                        out.append((label, DayTradeSettings(or_minutes=minutes, stop_rule=stop,
                                                            side=side, target_r=target,
                                                            min_volume_x=volume)))
    return out


def explore(sessions_by_symbol: dict[str, dict]) -> pd.DataFrame:
    """Run every variant, scored separately on the first and second half of the days.

    The first half is for finding what looks good; the second half is the
    check. With this many variants a few will look good on any one stretch
    by luck alone, so only one that holds up in both halves means anything.
    """
    days = sorted({d for sessions in sessions_by_symbol.values() for d in sessions})
    split = days[len(days) // 2]
    rows = []
    for label, settings in variants():
        trades = run(sessions_by_symbol, settings)
        row = {"variant": label, "trades": len(trades)}
        for name, part in (("first", trades[trades["date"] < split]),
                           ("second", trades[trades["date"] >= split])):
            row[f"{name}_gross_r"] = part["gross_r"].mean()
            row[f"{name}_net_r"] = part["net_r"].mean()
            row[f"{name}_t_gross"] = _t_stat(part.groupby("date")["gross_r"].mean())
            row[f"{name}_t_net"] = _t_stat(part.groupby("date")["net_r"].mean())
        row["all_gross_r"], row["all_net_r"] = trades["gross_r"].mean(), trades["net_r"].mean()
        row["all_t_net"] = _t_stat(trades.groupby("date")["net_r"].mean())
        rows.append(row)
    return pd.DataFrame(rows), split


def render_variants(table: pd.DataFrame, split: pd.Timestamp) -> str:
    n = len(table)
    held_gross = table[(table["first_t_gross"] >= 2) & (table["second_t_gross"] >= 2)]
    held_net = table[(table["first_net_r"] > 0) & (table["second_net_r"] > 0)]
    best_first = table.sort_values("first_net_r", ascending=False).head(5)
    lines = [
        "# Day-trade rule: every variant",
        "",
        f"{n} variants of the opening-range breakout: buying or shorting, a 15- or 30-minute range,",
        "the stop at the middle or far edge of the range, targets of 1, 2 or 3 times the risk, with",
        "and without a volume filter. Same 200 shares, same costs.",
        "",
        f"The days are split at {split:%d %b %Y}. The first half is where a pattern is looked for;",
        "the second half is the check. Trying this many variants guarantees a few look good by luck,",
        "so only a variant that works in both halves counts.",
        "",
        f"- Variants that made money after costs in both halves: **{len(held_net)} of {n}**",
        f"- Variants with a reliable edge before costs in both halves: **{len(held_gross)} of {n}**",
        f"- Variants that made money after costs over all days: **{int((table['all_net_r'] > 0).sum())} of {n}**",
        f"- Best result after costs over all days: {table['all_net_r'].max():+.3f} R a trade",
        "",
        "## The five that looked best in the first half, and what they did next",
        "",
        "| Variant | Trades | First half, after costs (R) | Second half, after costs (R) | Before costs, all days (R) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for _, r in best_first.iterrows():
        lines.append(f"| {r['variant']} | {r['trades']:,} | {r['first_net_r']:+.3f} | "
                     f"{r['second_net_r']:+.3f} | {r['all_gross_r']:+.3f} |")
    lines += ["", "## All variants", "",
              "| Variant | Trades | Before costs (R) | After costs (R) | Strength after costs (t) |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for _, r in table.sort_values("all_net_r", ascending=False).iterrows():
        lines.append(f"| {r['variant']} | {r['trades']:,} | {r['all_gross_r']:+.3f} | "
                     f"{r['all_net_r']:+.3f} | {r['all_t_net']:+.2f} |")
    lines.append("")
    return "\n".join(lines)


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
