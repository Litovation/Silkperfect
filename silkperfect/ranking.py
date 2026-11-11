"""Ranking test: pick the best few stocks out of the most liquid ones.

Every `rebalance_days` the most liquid stocks are scored, the top few are
bought in equal amounts at the next day's open and held until the next
rebalance. Each scoring method is judged against holding all of them equally.

The liquid universe is rebuilt at every rebalance from data available on
that day, so stocks that later fell out of favour are still in the test.
"""
from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import backtest, config, parse
from .costs import CostModel
from .forecasters import Forecaster

HOLD_ALL = "Hold all equally"


@dataclass
class RankSettings:
    universe_size: int = 200       # most liquid stocks considered at each rebalance
    top_n: int = 20                # stocks held
    rebalance_days: int = 21       # trading days between rebalances (about a month)
    min_history: int = 525         # trading days before the first rebalance (must cover context)
    liquidity_window: int = 126    # days of traded value used to rank liquidity
    context: int = 512             # closes handed to forecasting models
    capital: float = 10_000_000.0  # Rs 1 crore
    max_daily_move: float = 0.35   # a bigger one-day log move in the past year marks suspect data
    holdout_days: int = 252        # most recent trading days reported separately
    costs: CostModel = field(default_factory=CostModel)


@dataclass
class Panel:
    """Wide tables, dates down and symbols across."""
    close: pd.DataFrame
    open: pd.DataFrame
    value: pd.DataFrame


def make_panel(prices: pd.DataFrame, exclude: set[str] = frozenset()) -> Panel:
    stocks = prices[(prices["series"] == "EQ") & ~prices["symbol"].isin(exclude)]
    wide = stocks.pivot(index="date", columns="symbol",
                        values=["adj_close", "adj_open", "value"]).sort_index()
    return Panel(wide["adj_close"], wide["adj_open"], wide["value"])


def etf_symbols(pr_dir: Path = config.PR_DIR) -> set[str]:
    """Symbols NSE lists as exchange-traded funds (read from one bundle per year)."""
    found: set[str] = set()
    for year_dir in sorted(pr_dir.glob("*")):
        files = sorted(year_dir.glob("PR*.zip"), key=parse.pr_date)
        if not files:
            continue
        with zipfile.ZipFile(files[-1]) as z:
            name = next((n for n in z.namelist() if n.lower().startswith("etf")), None)
            if name:
                df = pd.read_csv(z.open(name), encoding="latin1", dtype=str,
                                 skipinitialspace=True, on_bad_lines="skip")
                df.columns = [c.strip() for c in df.columns]
                found |= set(df["SYMBOL"].dropna().str.strip())
    return found


def eligible(panel: Panel, i: int, s: RankSettings) -> list[str]:
    """The liquid universe on day i, using only data up to day i."""
    close = panel.close.iloc[max(0, i + 1 - s.context):i + 1]
    full = close.notna().all(axis=0) & (len(close) >= s.context)
    year = np.log(close.iloc[-253:]).diff().abs().max(axis=0)
    clean = year < s.max_daily_move
    liquidity = panel.value.iloc[i + 1 - s.liquidity_window:i + 1].median(axis=0)
    ranked = liquidity[full & clean].dropna().sort_values(ascending=False)
    return list(ranked.index[:s.universe_size])


class Signal:
    """Scores stocks; higher means more attractive."""
    name = "signal"
    cache_key: str | None = None

    def score(self, close: pd.DataFrame, horizon: int) -> pd.Series:
        """`close` holds past closes only, oldest first, one column per stock."""
        raise NotImplementedError


class Momentum(Signal):
    """Return over the past `lookback` days, leaving out the latest `skip` days."""

    def __init__(self, lookback: int = 252, skip: int = 21):
        self.lookback, self.skip = lookback, skip
        self.name = f"Momentum ({lookback // 21}-{skip // 21} month)"

    def score(self, close, horizon):
        return close.iloc[-1 - self.skip] / close.iloc[-1 - self.lookback] - 1


class LowVolatility(Signal):
    """Prefer the steadiest stocks over the past `lookback` days."""

    def __init__(self, lookback: int = 252):
        self.lookback = lookback
        self.name = "Low volatility (12 month)"

    def score(self, close, horizon):
        return -np.log(close.iloc[-self.lookback - 1:]).diff().std()


class ForecastSignal(Signal):
    """Rank by a forecasting model's expected return over the holding period."""

    def __init__(self, forecaster: Forecaster):
        self.forecaster = forecaster
        self.name = forecaster.name
        self.cache_key = forecaster.cache_key

    def score(self, close, horizon):
        histories = [close[c].to_numpy(dtype=float) for c in close.columns]
        paths = np.asarray(self.forecaster.predict(histories, horizon), dtype=float)
        return pd.Series(paths[:, -1] / close.iloc[-1].to_numpy() - 1, index=close.columns)


def _cached_score(signal: Signal, close: pd.DataFrame, horizon: int,
                  cache_dir: Path | None) -> pd.Series:
    if cache_dir is None or signal.cache_key is None:
        return signal.score(close, horizon)
    digest = hashlib.sha256(close.to_numpy(dtype=float).tobytes())
    digest.update("|".join(close.columns).encode())
    digest.update(f"{signal.cache_key}|{horizon}|{close.index[-1]}".encode())
    path = Path(cache_dir) / f"rank-{signal.cache_key}-{digest.hexdigest()[:16]}.parquet"
    if path.exists():
        return pd.read_parquet(path)["score"]
    scores = signal.score(close, horizon)
    path.parent.mkdir(parents=True, exist_ok=True)
    scores.rename("score").to_frame().to_parquet(path)
    return scores


def _trade_cost(costs: CostModel, old: pd.Series, new: pd.Series) -> float:
    """Cost of moving from one set of rupee holdings to another."""
    names = old.index.union(new.index)
    change = new.reindex(names, fill_value=0.0) - old.reindex(names, fill_value=0.0)
    total = 0.0
    for delta in change[change.abs() > 1.0]:
        total += costs.cost("buy" if delta > 0 else "sell", abs(delta), 1.0)
    return total


def simulate(panel: Panel, picks: dict[int, list[str]], s: RankSettings) -> dict:
    """Hold each rebalance's picks in equal amounts from the next day's open."""
    close = panel.close.ffill()
    open_ = panel.open.fillna(close.shift(1)).fillna(close)   # no trade that day: last price
    days = sorted(picks)
    shares = pd.Series(dtype=float)
    cash, total_cost, turnover = s.capital, 0.0, []
    values = {}
    for k, signal_day in enumerate(days):
        trade_day = signal_day + 1
        if trade_day >= len(close):
            break
        last_day = days[k + 1] if k + 1 < len(days) else len(close) - 1
        px = open_.iloc[trade_day]
        old = shares * px.reindex(shares.index)
        worth = cash + old.sum()
        names = picks[signal_day]
        new = pd.Series(worth / len(names), index=names)
        cost = _trade_cost(s.costs, old, new)
        new *= (worth - cost) / worth                 # costs come out of the amount invested
        total_cost += cost
        traded = new.reindex(old.index.union(new.index), fill_value=0.0).sub(
            old.reindex(old.index.union(new.index), fill_value=0.0)).abs().sum()
        turnover.append(traded / (2 * worth))
        shares, cash = new / px.reindex(names), 0.0
        block = close.iloc[trade_day:last_day + 1][names]
        for day, row in block.iterrows():
            values[day] = float((shares * row).sum())
    equity = pd.Series(values).sort_index()
    equity = pd.concat([pd.Series({close.index[days[0]]: s.capital}), equity])
    return {"equity": equity, "costs": total_cost,
            "turnover_pct": float(np.mean(turnover)) * 100 if turnover else 0.0}


@dataclass
class RankResult:
    summary: pd.DataFrame            # one row per method
    periods: pd.DataFrame            # method x rebalance: rank correlation and returns
    equity: dict                     # method -> portfolio value by date
    holdings: dict                   # method -> {date: [symbols]}
    settings: RankSettings
    start: pd.Timestamp
    end: pd.Timestamp
    holdout_start: pd.Timestamp
    rebalances: int


def _metrics(equity: pd.Series) -> dict:
    m = backtest.curve_metrics(equity)
    return {"cagr_pct": m["cagr_pct"], "max_drawdown_pct": m["max_drawdown_pct"],
            "sharpe": m["sharpe"]}


def run(panel: Panel, signals: list[Signal], settings: RankSettings | None = None,
        cache_dir: Path | None = None, progress=None) -> RankResult:
    s = settings or RankSettings()
    n = len(panel.close)
    days = list(range(s.min_history - 1, n - 1, s.rebalance_days))
    if len(days) < 3:
        raise ValueError("not enough history for a ranking test")
    close = panel.close.ffill()

    universes, scores = {}, {sig.name: {} for sig in signals}
    for k, i in enumerate(days, 1):
        names = eligible(panel, i, s)
        universes[i] = names
        window = panel.close.iloc[max(0, i + 1 - s.context):i + 1][names]
        for sig in signals:
            if progress and sig.cache_key:
                progress(f"{sig.name}: rebalance {k} of {len(days)}")
            scores[sig.name][i] = _cached_score(sig, window, s.rebalance_days, cache_dir)
        if progress:
            progress(f"rebalance {k} of {len(days)} scored")

    picks = {HOLD_ALL: universes}
    for sig in signals:
        picks[sig.name] = {i: list(scores[sig.name][i].dropna()
                                   .sort_values(ascending=False).index[:s.top_n]) for i in days}

    holdout_i = n - 1 - s.holdout_days
    period_rows = []
    for k, i in enumerate(days):
        j = days[k + 1] if k + 1 < len(days) else n - 1
        fwd = close.iloc[j][universes[i]] / close.iloc[i][universes[i]] - 1
        for sig in signals:
            sc = scores[sig.name][i]
            both = pd.concat([sc, fwd], axis=1, keys=["s", "f"]).dropna()
            period_rows.append({
                "method": sig.name, "date": close.index[i], "holdout": i >= holdout_i,
                "rank_correlation": both["s"].rank().corr(both["f"].rank()),
                "top_return_pct": fwd[picks[sig.name][i]].mean() * 100,
                "universe_return_pct": fwd.mean() * 100})
    periods = pd.DataFrame(period_rows)

    equity, rows = {}, []
    for name, chosen in picks.items():
        sim = simulate(panel, chosen, s)
        equity[name] = sim["equity"]
        row = {"method": name, **_metrics(sim["equity"]),
               "turnover_pct": sim["turnover_pct"], "costs_rupees": sim["costs"]}
        early = sim["equity"][sim["equity"].index < close.index[holdout_i]]
        late = sim["equity"][sim["equity"].index >= close.index[holdout_i]]
        row["cagr_before_pct"] = backtest.curve_metrics(early)["cagr_pct"] if len(early) > 2 else np.nan
        row["return_holdout_pct"] = (late.iloc[-1] / late.iloc[0] - 1) * 100 if len(late) > 2 else np.nan
        if name != HOLD_ALL:
            p = periods[periods["method"] == name]
            ic = p["rank_correlation"]
            row["rank_correlation"] = ic.mean()
            row["rank_t_stat"] = ic.mean() / ic.std() * np.sqrt(len(ic)) if ic.std() > 0 else np.nan
            row["periods_won_pct"] = (p["top_return_pct"] > p["universe_return_pct"]).mean() * 100
        rows.append(row)
    holdings = {name: {close.index[i]: v for i, v in chosen.items()}
                for name, chosen in picks.items() if name != HOLD_ALL}
    return RankResult(pd.DataFrame(rows), periods, equity, holdings, s,
                      close.index[days[0]], close.index[-1], close.index[holdout_i], len(days))


def render(result: RankResult, benchmark: pd.Series | None = None) -> str:
    s, df = result.settings, result.summary.copy()
    base = df.set_index("method").loc[HOLD_ALL]

    def cell(v, fmt):
        return "n/a" if pd.isna(v) else format(v, fmt)

    lines = [
        "# Ranking test",
        "",
        f"- Period: {result.start:%d %b %Y} to {result.end:%d %b %Y}, {result.rebalances} rebalances",
        f"- Every {s.rebalance_days} trading days: take the {s.universe_size} most liquid NSE stocks "
        f"(no ETFs), buy the top {s.top_n} by score in equal amounts at the next open",
        f"- Starting money Rs {s.capital:,.0f}; full Indian delivery costs on every trade",
        f"- The bar: holding all {s.universe_size} equally, which returned {base['cagr_pct']:.1f}% a year",
        f"- Last {s.holdout_days} trading days (from {result.holdout_start:%d %b %Y}) are shown "
        "separately as a check on recent behaviour",
        "",
        "## Returns after costs",
        "",
        "| Method | Per year (%) | vs hold-all (pts) | Worst drop (%) | Sharpe | Before holdout, per year (%) "
        "| Holdout return (%) | Turnover per rebalance (%) | Costs (Rs) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['method']} | {r['cagr_pct']:.1f} | {r['cagr_pct'] - base['cagr_pct']:+.1f} | "
            f"{r['max_drawdown_pct']:.1f} | {r['sharpe']:.2f} | {cell(r['cagr_before_pct'], '.1f')} | "
            f"{cell(r['return_holdout_pct'], '.1f')} | {r['turnover_pct']:.0f} | {r['costs_rupees']:,.0f} |")
    if benchmark is not None and len(benchmark) > 2:
        m = backtest.curve_metrics(benchmark)
        lines.append(f"| Nifty 50 index (no costs, no dividends) | {m['cagr_pct']:.1f} | "
                     f"{m['cagr_pct'] - base['cagr_pct']:+.1f} | {m['max_drawdown_pct']:.1f} | "
                     f"{m['sharpe']:.2f} | n/a | n/a | 0 | 0 |")
    lines += [
        "",
        "## Does the ranking carry information?",
        "",
        "Rank correlation compares each method's ordering of the stocks with how they then",
        "performed. Zero means no information. A t-statistic above about 2 means the result",
        "is unlikely to be luck.",
        "",
        "| Method | Avg rank correlation | t-statistic | Rebalances where its picks beat hold-all (%) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for _, r in df[df["method"] != HOLD_ALL].iterrows():
        lines.append(f"| {r['method']} | {r['rank_correlation']:+.3f} | {r['rank_t_stat']:+.2f} | "
                     f"{r['periods_won_pct']:.0f} |")
    lines.append("")
    return "\n".join(lines)


def save(result: RankResult, text: str, out_dir: Path = config.REPORTS_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ranking.md").write_text(text)
    result.summary.round(4).to_csv(out_dir / "ranking_summary.csv", index=False)
    result.periods.round(4).to_csv(out_dir / "ranking_periods.csv", index=False)
    pd.DataFrame(result.equity).round(0).to_csv(out_dir / "ranking_equity.csv", index_label="date")
    rows = [{"method": m, "date": d, "symbols": " ".join(names)}
            for m, by_date in result.holdings.items() for d, names in by_date.items()]
    pd.DataFrame(rows).to_csv(out_dir / "ranking_holdings.csv", index=False)
