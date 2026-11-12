"""A battery of common intraday strategies on NSE 5-minute bars.

Every strategy is a function that looks at one share's bars for one day, bar
by bar, and says what it wants to hold after each bar closes: +1 (bought),
-1 (sold short) or 0 (nothing). It only ever sees bars up to the current one.
Trades fill at that bar's close, nothing is opened after 15:00, and everything
is closed at 15:20. Results are a percentage of the money in the trade,
before and after Indian intraday costs.

Settings are the textbook defaults for each method. None was tuned on this data.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import config
from .costs import CostModel
from .daytrade import SESSION_BARS, _slot

O, H, L, C, V = range(5)
OR_BARS = 3                          # first 15 minutes
LAST_ENTRY = _slot("15:00")          # no new trades after this bar
FLAT = _slot("15:20")                # everything closed at this bar


@dataclass
class Day:
    bars: np.ndarray                 # 75 x 5: open, high, low, close, volume
    prev_close: float
    prev_high: float
    prev_low: float


def vwap(bars: np.ndarray) -> np.ndarray:
    """Running volume-weighted average price for the day."""
    typical = (bars[:, H] + bars[:, L] + bars[:, C]) / 3
    vol = np.where(bars[:, V] > 0, bars[:, V], 1.0)
    return np.cumsum(typical * vol) / np.cumsum(vol)


def rsi(close: np.ndarray, n: int = 14) -> np.ndarray:
    diff = np.diff(close, prepend=close[0])
    up, down = np.clip(diff, 0, None), np.clip(-diff, 0, None)
    out = np.full(len(close), np.nan)
    avg_up, avg_down = up[1:n + 1].mean(), down[1:n + 1].mean()
    for i in range(n, len(close)):
        if i > n:
            avg_up = (avg_up * (n - 1) + up[i]) / n
            avg_down = (avg_down * (n - 1) + down[i]) / n
        out[i] = 100.0 if avg_down == 0 else 100 - 100 / (1 + avg_up / avg_down)
    return out


def ema(values: np.ndarray, n: int) -> np.ndarray:
    out, k = np.empty(len(values)), 2 / (n + 1)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = values[i] * k + out[i - 1] * (1 - k)
    return out


def _stateful(n: int, decide) -> np.ndarray:
    """Walk the day bar by bar; decide(i, held) returns the position wanted after bar i."""
    pos, held = np.zeros(n, dtype=int), 0
    for i in range(n):
        if i >= FLAT:
            held = 0
        else:
            want = decide(i, held)
            if want != held and want != 0 and i > LAST_ENTRY:
                want = held if held == 0 else 0     # too late to open or flip: only closing allowed
            held = want
        pos[i] = held
    return pos


# ---- strategies -----------------------------------------------------------------

def opening_range_breakout(day: Day, side: int) -> np.ndarray:
    """First close beyond the first 15 minutes' range; stop at its middle; target 1x the risk."""
    b = day.bars
    high, low = b[:OR_BARS, H].max(), b[:OR_BARS, L].min()
    mid = (high + low) / 2
    state = {"done": False, "target": None}

    def decide(i, held):
        c = b[i, C]
        if held == 0:
            if state["done"] or i < OR_BARS:
                return 0
            if side > 0 and c > high:
                state.update(done=True, target=c + (c - mid))
                return 1
            if side < 0 and c < low:
                state.update(done=True, target=c - (mid - c))
                return -1
            return 0
        if held > 0 and (c <= mid or c >= state["target"]):
            return 0
        if held < 0 and (c >= mid or c <= state["target"]):
            return 0
        return held
    return _stateful(len(b), decide)


def previous_day_breakout(day: Day) -> np.ndarray:
    """Buy a close above yesterday's high, short a close below yesterday's low; out if it comes back."""
    b = day.bars
    state = {"done": False}

    def decide(i, held):
        c = b[i, C]
        if held == 0:
            if state["done"] or i < OR_BARS:
                return 0
            if c > day.prev_high:
                state["done"] = True
                return 1
            if c < day.prev_low:
                state["done"] = True
                return -1
            return 0
        if held > 0 and c < day.prev_high:
            return 0
        if held < 0 and c > day.prev_low:
            return 0
        return held
    return _stateful(len(b), decide)


def gap_trade(day: Day, follow: bool, size: float = 0.01) -> np.ndarray:
    """A gap of 1% or more at the open: follow it, or bet on it closing back to yesterday's close."""
    b = day.bars
    gap = b[0, O] / day.prev_close - 1
    if abs(gap) < size:
        return np.zeros(len(b), dtype=int)
    direction = int(np.sign(gap)) if follow else -int(np.sign(gap))
    high, low = b[:OR_BARS, H].max(), b[:OR_BARS, L].min()
    state = {"done": False}

    def decide(i, held):
        c = b[i, C]
        if held == 0:
            if state["done"] or i != OR_BARS - 1:
                return 0
            state["done"] = True
            return direction
        if held > 0 and c < low:                      # stop: through the first 15 minutes' range
            return 0
        if held < 0 and c > high:
            return 0
        if not follow and (c - day.prev_close) * direction >= 0:
            return 0                                  # the gap has closed
        return held
    return _stateful(len(b), decide)


def vwap_trend(day: Day) -> np.ndarray:
    """Bought while price is above the day's VWAP, short while below (from 9:45)."""
    b, line = day.bars, vwap(day.bars)
    return _stateful(len(b), lambda i, held: 0 if i < 6 else (1 if b[i, C] > line[i] else -1))


def vwap_reversion(day: Day, width: float = 2.0) -> np.ndarray:
    """Fade a stretch of 2 standard deviations from VWAP; out when price is back at VWAP."""
    b, line = day.bars, vwap(day.bars)
    gap = b[:, C] - line

    def decide(i, held):
        if i < 12:
            return 0
        sd = gap[:i + 1].std()
        if held == 0:
            if sd > 0 and gap[i] > width * sd:
                return -1
            if sd > 0 and gap[i] < -width * sd:
                return 1
            return 0
        return 0 if gap[i] * held >= 0 else held
    return _stateful(len(b), decide)


def rsi_reversion(day: Day) -> np.ndarray:
    """RSI(14) on 5-minute closes: buy below 30, short above 70, out at 50."""
    b = day.bars
    r = rsi(b[:, C])

    def decide(i, held):
        if np.isnan(r[i]):
            return 0
        if held == 0:
            return 1 if r[i] < 30 else (-1 if r[i] > 70 else 0)
        return 0 if (held > 0 and r[i] >= 50) or (held < 0 and r[i] <= 50) else held
    return _stateful(len(b), decide)


def bollinger_reversion(day: Day, n: int = 20, width: float = 2.0) -> np.ndarray:
    """Buy below the lower Bollinger band, short above the upper; out at the middle."""
    c = day.bars[:, C]

    def decide(i, held):
        if i < n - 1:
            return 0
        window = c[i - n + 1:i + 1]
        mid, sd = window.mean(), window.std()
        if held == 0:
            return 1 if c[i] < mid - width * sd else (-1 if c[i] > mid + width * sd else 0)
        return 0 if (held > 0 and c[i] >= mid) or (held < 0 and c[i] <= mid) else held
    return _stateful(len(c), decide)


def supertrend(day: Day, n: int = 10, mult: float = 3.0) -> np.ndarray:
    """Supertrend(10, 3): bought while the trend line is below price, short while above."""
    b = day.bars
    prev_c = np.r_[b[0, C], b[:-1, C]]
    tr = np.maximum(b[:, H] - b[:, L], np.maximum(abs(b[:, H] - prev_c), abs(b[:, L] - prev_c)))
    atr = pd.Series(tr).rolling(n).mean().to_numpy()
    mid = (b[:, H] + b[:, L]) / 2
    trend = np.zeros(len(b), dtype=int)
    upper = lower = math.nan
    for i in range(n - 1, len(b)):
        up, lo = mid[i] + mult * atr[i], mid[i] - mult * atr[i]
        if i == n - 1:
            upper, lower, trend[i] = up, lo, 1 if b[i, C] > mid[i] else -1
            continue
        upper = up if up < upper or b[i - 1, C] > upper else upper
        lower = lo if lo > lower or b[i - 1, C] < lower else lower
        trend[i] = 1 if b[i, C] > upper else (-1 if b[i, C] < lower else trend[i - 1])
    return _stateful(len(b), lambda i, held: int(trend[i]))


def ema_crossover(day: Day, fast: int = 9, slow: int = 21) -> np.ndarray:
    """Bought while the 9-bar average is above the 21-bar average, short while below."""
    c = day.bars[:, C]
    f, s = ema(c, fast), ema(c, slow)
    return _stateful(len(c), lambda i, held: 0 if i < slow else (1 if f[i] > s[i] else -1))


def first_half_hour(day: Day) -> np.ndarray:
    """The move from yesterday's close to 9:45 is traded again from 14:50 to 15:20."""
    b = day.bars
    direction = int(np.sign(b[5, C] / day.prev_close - 1))
    pos = np.zeros(len(b), dtype=int)
    pos[_slot("14:50"):FLAT] = direction
    return pos


STRATEGIES = {
    "Opening-range breakout, buy": lambda d: opening_range_breakout(d, 1),
    "Opening-range breakout, short": lambda d: opening_range_breakout(d, -1),
    "Previous-day high/low breakout": previous_day_breakout,
    "Gap and go (follow a 1% gap)": lambda d: gap_trade(d, True),
    "Gap fade (bet a 1% gap closes)": lambda d: gap_trade(d, False),
    "VWAP trend (with price vs VWAP)": vwap_trend,
    "VWAP reversion (fade 2 sd)": vwap_reversion,
    "RSI reversion (30/70)": rsi_reversion,
    "Bollinger reversion (20, 2)": bollinger_reversion,
    "Supertrend (10, 3)": supertrend,
    "Moving-average crossover (9/21)": ema_crossover,
    "First half-hour momentum": first_half_hour,
}


# ---- engine ---------------------------------------------------------------------

@dataclass
class Settings:
    position: float = 10_000.0
    costs: CostModel = field(default_factory=CostModel.intraday)


def trades_from(pos: np.ndarray, close: np.ndarray, s: Settings) -> list[dict]:
    """Turn a day's positions into trades filled at bar closes."""
    out, held, entry, entry_bar = [], 0, 0.0, 0
    for i, want in enumerate(pos):
        if want == held:
            continue
        if held != 0:
            move = (close[i] / entry - 1) * held
            shares = s.position / entry
            first, second = ("buy", "sell") if held > 0 else ("sell", "buy")
            fees = s.costs.cost(first, shares, entry) + s.costs.cost(second, shares, close[i])
            out.append({"side": held, "entry_bar": entry_bar, "exit_bar": i,
                        "gross_pct": move * 100, "net_pct": move * 100 - fees / s.position * 100})
        held, entry, entry_bar = int(want), float(close[i]), i
    return out


def make_days(sessions: dict[pd.Timestamp, np.ndarray]) -> dict[pd.Timestamp, Day]:
    """Attach yesterday's close, high and low to each day (the first day is dropped)."""
    out, prev = {}, None
    for day in sorted(sessions):
        bars = sessions[day]
        if prev is not None:
            out[day] = Day(bars, float(prev[-1, C]), float(prev[:, H].max()), float(prev[:, L].min()))
        prev = bars
    return out


def run_rules(sessions_by_symbol: dict[str, dict], settings: Settings | None = None,
              progress=None) -> pd.DataFrame:
    """Every trade of every rule-based strategy."""
    s = settings or Settings()
    rows = []
    for k, (symbol, sessions) in enumerate(sessions_by_symbol.items(), 1):
        for date, day in make_days(sessions).items():
            close = day.bars[:, C]
            for name, rule in STRATEGIES.items():
                for trade in trades_from(rule(day), close, s):
                    rows.append({"strategy": name, "symbol": symbol, "date": date, **trade})
        if progress and k % 25 == 0:
            progress(f"{k} of {len(sessions_by_symbol)} shares done")
    return pd.DataFrame(rows, columns=["strategy", "symbol", "date", "side", "entry_bar",
                                       "exit_bar", "gross_pct", "net_pct"])


def run_leaders(sessions_by_symbol: dict[str, dict], settings: Settings | None = None,
                at: str = "10:15", share: float = 0.1) -> pd.DataFrame:
    """At 10:15 buy the morning's strongest tenth of shares and short the weakest tenth, to 15:20."""
    s = settings or Settings()
    slot = _slot(at)
    by_day: dict[pd.Timestamp, list] = {}
    for symbol, sessions in sessions_by_symbol.items():
        for date, day in make_days(sessions).items():
            by_day.setdefault(date, []).append((symbol, day))
    rows = []
    for date, items in by_day.items():
        if len(items) < 20:
            continue
        ranked = sorted(items, key=lambda it: it[1].bars[slot, C] / it[1].prev_close)
        n = max(1, int(len(ranked) * share))
        for group, side, name in ((ranked[-n:], 1, "Morning leaders, buy"),
                                  (ranked[:n], -1, "Morning laggards, short")):
            for symbol, day in group:
                pos = np.zeros(SESSION_BARS, dtype=int)
                pos[slot:FLAT] = side
                for trade in trades_from(pos, day.bars[:, C], s):
                    rows.append({"strategy": name, "symbol": symbol, "date": date, **trade})
    return pd.DataFrame(rows)


# ---- machine-learning classifier --------------------------------------------------

HOLD_BARS = 6                    # the classifier predicts the next 30 minutes
FEATURES = ["ret1", "ret3", "ret6", "ret12", "vs_vwap", "range_pos", "rsi", "rel_volume",
            "time", "gap", "since_open", "range_width", "market3", "market12"]


def _features(day: Day, market: np.ndarray) -> np.ndarray:
    """One row per bar, built from bars up to that bar only. `market` is the average
    share's return since yesterday's close at each bar."""
    b = day.bars
    c = b[:, C]
    def back(k):
        return c / np.r_[np.full(k, c[0]), c[:-k]] - 1
    line = vwap(b)
    hi, lo = np.maximum.accumulate(b[:, H]), np.minimum.accumulate(b[:, L])
    vol = np.where(b[:, V] > 0, b[:, V], np.nan)
    rel = vol / (np.nancumsum(vol) / np.arange(1, len(c) + 1))
    def mback(k):
        return market - np.r_[np.full(k, market[0]), market[:-k]]
    return np.column_stack([
        back(1), back(3), back(6), back(12), c / line - 1, (c - lo) / (hi - lo + 1e-12),
        np.nan_to_num(rsi(c), nan=50.0), np.nan_to_num(rel, nan=1.0),
        np.arange(len(c)) / SESSION_BARS, np.full(len(c), b[0, O] / day.prev_close - 1),
        c / b[0, O] - 1, (hi - lo) / c, mback(3), mback(12)])


def run_classifier(sessions_by_symbol: dict[str, dict], settings: Settings | None = None,
                   train_share: float = 0.6, threshold: float = 0.25, confidence: float = 0.5):
    """Train a LightGBM classifier (up / down / sideways over the next 30 minutes) on the
    earlier days and trade it on the later days only. Returns (trades, info)."""
    import lightgbm as lgb
    s = settings or Settings()
    days_by_symbol = {sym: make_days(sess) for sym, sess in sessions_by_symbol.items()}
    all_days = sorted({d for days in days_by_symbol.values() for d in days})
    cut = all_days[int(len(all_days) * train_share)]
    test_from = all_days[int(len(all_days) * train_share) + 1]     # one day's gap
    market = {}
    for d in all_days:
        rets = [days[d].bars[:, C] / days[d].prev_close - 1 for days in days_by_symbol.values() if d in days]
        market[d] = np.mean(rets, axis=0)

    usable = np.arange(12, FLAT - HOLD_BARS)
    X_train, y_train = [], []
    for days in days_by_symbol.values():
        for d, day in days.items():
            if d >= cut:
                continue
            c = day.bars[:, C]
            fwd = (c[usable + HOLD_BARS] / c[usable] - 1) * 100
            X_train.append(_features(day, market[d])[usable])
            y_train.append(np.where(fwd > threshold, 2, np.where(fwd < -threshold, 0, 1)))
    X_train, y_train = np.vstack(X_train), np.concatenate(y_train)
    params = dict(objective="multiclass", num_class=3, learning_rate=0.05, num_leaves=31,
                  min_data_in_leaf=200, bagging_fraction=0.8, bagging_freq=1, feature_fraction=0.8,
                  seed=0, num_threads=4, verbosity=-1, deterministic=True)
    model = lgb.train(params, lgb.Dataset(X_train, y_train), num_boost_round=300)

    rows = []
    for symbol, days in days_by_symbol.items():
        for d, day in days.items():
            if d < test_from:
                continue
            prob = model.predict(_features(day, market[d]))
            pos, until = np.zeros(SESSION_BARS, dtype=int), -1
            for i in usable:
                if i <= until or i > LAST_ENTRY:
                    continue
                side = 1 if prob[i, 2] >= confidence else (-1 if prob[i, 0] >= confidence else 0)
                if side:
                    until = min(i + HOLD_BARS, FLAT)
                    pos[i:until] = side
            for trade in trades_from(pos, day.bars[:, C], s):
                rows.append({"strategy": "ML classifier (LightGBM)", "symbol": symbol, "date": d, **trade})
    info = {"train_rows": len(y_train), "train_until": cut, "test_from": test_from,
            "test_days": sum(1 for d in all_days if d >= test_from),
            "class_share": {k: float((y_train == v).mean()) for k, v in (("down", 0), ("flat", 1), ("up", 2))}}
    return pd.DataFrame(rows, columns=["strategy", "symbol", "date", "side", "entry_bar",
                                       "exit_bar", "gross_pct", "net_pct"]), info


# ---- scoring --------------------------------------------------------------------

def _t(daily: pd.Series) -> float:
    return float(daily.mean() / daily.std() * math.sqrt(len(daily))) if len(daily) > 2 and daily.std() > 0 else np.nan


def summarise(trades: pd.DataFrame) -> pd.DataFrame:
    """One row per strategy. Strength counts each day once, since a day's trades move together."""
    rows = []
    days = sorted(trades["date"].unique())
    half = days[len(days) // 2] if days else None
    for name, t in trades.groupby("strategy", sort=False):
        gross_day, net_day = t.groupby("date")["gross_pct"].mean(), t.groupby("date")["net_pct"].mean()
        first, second = t[t["date"] < half], t[t["date"] >= half]
        rows.append({
            "strategy": name, "trades": len(t), "days": t["date"].nunique(),
            "win_pct": (t["gross_pct"] > 0).mean() * 100,
            "gross_pct": t["gross_pct"].mean(), "net_pct": t["net_pct"].mean(),
            "cost_pct": (t["gross_pct"] - t["net_pct"]).mean(),
            "t_gross": _t(gross_day), "t_net": _t(net_day),
            "first_half_gross": first["gross_pct"].mean() if len(first) else np.nan,
            "second_half_gross": second["gross_pct"].mean() if len(second) else np.nan,
            "winning_days_pct": (net_day > 0).mean() * 100,
            "minutes_held": (t["exit_bar"] - t["entry_bar"]).mean() * 5})
    return pd.DataFrame(rows).sort_values("net_pct", ascending=False).reset_index(drop=True)


def render(summary: pd.DataFrame, start, end, shares: int, s: Settings, ml_info: dict | None) -> str:
    made_money = summary[summary["net_pct"] > 0]
    real_gross = summary[(summary["t_gross"] >= 2) & (summary["first_half_gross"] > 0)
                         & (summary["second_half_gross"] > 0)]
    cost = summary["cost_pct"].mean()
    lines = [
        "# Day-trading strategies on NSE 5-minute bars",
        "",
        f"- Period: {start:%d %b %Y} to {end:%d %b %Y} (Yahoo's 5-minute history goes back about 60 trading days)",
        f"- Shares: the {shares} most traded NSE shares",
        "- Trades fill at the close of a 5-minute bar; nothing new after 15:00; everything closed at 15:20",
        f"- Costs: intraday brokerage, taxes and {s.costs.slippage_bps:g} basis points of slippage per side, "
        f"about {cost:.2f}% for a round trip on Rs {s.position:,.0f}",
        "- Settings are each method's textbook defaults; none was tuned on this data",
        "",
        f"**Strategies that made money after costs: {len(made_money)} of {len(summary)}.**",
        f"**Strategies with a reliable edge before costs (strength 2 or more, positive in both halves): "
        f"{len(real_gross)} of {len(summary)}.**",
        "",
        "| Strategy | Trades | Wins (%) | Avg before costs (%) | Avg after costs (%) | Strength before costs (t) "
        "| First half, before costs (%) | Second half, before costs (%) | Days in profit after costs (%) | Held (min) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    def cell(v, fmt):
        return "n/a" if pd.isna(v) else format(v, fmt)
    for _, r in summary.iterrows():
        lines.append(f"| {r['strategy']} | {int(r['trades']):,} | {r['win_pct']:.0f} | {r['gross_pct']:+.3f} | "
                     f"{r['net_pct']:+.3f} | {cell(r['t_gross'], '+.2f')} | {cell(r['first_half_gross'], '+.3f')} | "
                     f"{cell(r['second_half_gross'], '+.3f')} | {r['winning_days_pct']:.0f} | {r['minutes_held']:.0f} |")
    lines += ["",
              "Percentages are of the money in one trade. Strength counts each day once; 2 or more means",
              "the result is unlikely to be luck. With this many strategies, one or two will clear that bar",
              "by chance, which is why both halves of the period must agree.", ""]
    if ml_info:
        lines += [f"The ML classifier was trained on days before {ml_info['train_until']:%d %b %Y} "
                  f"({ml_info['train_rows']:,} examples) and traded only on the {ml_info['test_days']} days from "
                  f"{ml_info['test_from']:%d %b %Y}, so its row covers a shorter period than the others.", ""]
    lines += ["## Not tested, and why", "",
              "- **Options strategies** (straddles, strangles, spreads, premium decay): there is no free history "
              "of option prices, and they cannot be judged without it.",
              "- **Reinforcement learning:** sixty days of data is far too little; an agent would memorise it.",
              "- **Index arbitrage and pairs trading:** need futures prices and speed that a home setup lacks.",
              ""]
    return "\n".join(lines)


def save(trades: pd.DataFrame, summary: pd.DataFrame, text: str, out_dir: Path = config.REPORTS_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "intraday.md").write_text(text)
    summary.round(4).to_csv(out_dir / "intraday_summary.csv", index=False)
    daily = trades.groupby(["strategy", "date"]).agg(trades=("net_pct", "size"), gross_pct=("gross_pct", "mean"),
                                                     net_pct=("net_pct", "mean")).round(4).reset_index()
    daily["date"] = pd.to_datetime(daily["date"]).dt.strftime("%Y-%m-%d")
    daily.to_csv(out_dir / "intraday_daily.csv", index=False)
