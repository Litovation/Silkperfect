"""Build the scoreboard: forecast accuracy and after-cost trading results."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import backtest, config, dataset, walkforward as wf
from .costs import CostModel
from .forecasters import Forecaster, default_forecasters


@dataclass
class Settings:
    horizon: int = config.HORIZON
    min_history: int = config.MIN_HISTORY
    max_context: int = config.MAX_CONTEXT
    capital: float = config.CAPITAL_PER_SYMBOL
    sma_fast: int = config.SMA_FAST
    sma_slow: int = config.SMA_SLOW
    benchmark: str = config.BENCHMARK
    costs: CostModel = field(default_factory=CostModel)


@dataclass
class Result:
    accuracy: pd.DataFrame          # one row per forecaster
    skill_by_year: pd.DataFrame     # forecaster x calendar year
    trading: pd.DataFrame           # one row per strategy, whole portfolio
    by_symbol: pd.DataFrame         # strategy x symbol
    symbols: list[str]
    skipped: list[str]
    start: pd.Timestamp
    end: pd.Timestamp
    entry_threshold: float
    # Raw material for the visualizer (see silkperfect/visualize.py).
    closes: dict[str, pd.Series] = field(default_factory=dict)              # symbol -> close
    forecasts: dict[str, dict[str, pd.DataFrame]] = field(default_factory=dict)  # symbol -> forecaster -> walk-forward frame
    curves: dict[str, list[pd.Series]] = field(default_factory=dict)        # strategy -> per-symbol equity
    trade_logs: dict[str, dict[str, pd.DataFrame]] = field(default_factory=dict)  # strategy -> symbol -> trades
    benchmark: pd.Series | None = None                                      # index close over the judged period


def run(prices: pd.DataFrame, universe: list[str], settings: Settings | None = None,
        forecasters: list[Forecaster] | None = None,
        cache_dir: Path | None = None, progress=None) -> Result:
    s = settings or Settings()
    forecasters = forecasters or default_forecasters()
    entry = s.costs.round_trip_fraction(s.capital)
    need = s.min_history + s.horizon + 20

    forecast_frames: dict[str, list[pd.DataFrame]] = {f.name: [] for f in forecasters}
    curves: dict[str, list[pd.Series]] = {}
    trade_logs: dict[str, dict[str, pd.DataFrame]] = {}
    closes: dict[str, pd.Series] = {}
    forecasts: dict[str, dict[str, pd.DataFrame]] = {}
    rows, used, skipped = [], [], []

    for symbol in universe:
        bars = dataset.ohlcv(prices, symbol)
        if len(bars) < need:
            skipped.append(symbol)
            continue
        used.append(symbol)
        close = bars["Close"]
        closes[symbol] = close
        forecasts[symbol] = {}
        window = bars.iloc[s.min_history - 1:]   # the period every strategy is judged on

        signals = {
            "Buy and hold": pd.Series(1, index=window.index),
            f"Moving-average crossover ({s.sma_fast}/{s.sma_slow})":
                wf.sma_signal(close, s.sma_fast, s.sma_slow).loc[window.index],
        }
        for f in forecasters:
            if progress and f.cache_key:
                progress(f"  {f.name}: {symbol}")
            frame = wf.cached_walk_forward(close, f, s.horizon, s.min_history,
                                           s.max_context, cache_dir, label=symbol)
            forecast_frames[f.name].append(frame)
            forecasts[symbol][f.name] = frame
            signals[f"Forecast rule: {f.name}"] = wf.forecast_signal(frame["pred_ret"], entry)

        for name, signal in signals.items():
            res = backtest.run_signal(window, signal, s.capital, s.costs)
            curves.setdefault(name, []).append(res["equity"])
            trade_logs.setdefault(name, {})[symbol] = res["trade_log"]
            m = backtest.curve_metrics(res["equity"])
            rows.append({"strategy": name, "symbol": symbol, **m, "trades": res["trades"],
                         "costs_rupees": res["costs"], "exposure_pct": res["exposure_pct"]})

    if not used:
        raise ValueError("no symbol in the universe has enough history")

    by_symbol = pd.DataFrame(rows)
    acc_rows, year_rows = [], []
    for name, frames in forecast_frames.items():
        pooled = pd.concat(frames)
        beaten = sum(wf.skill(f) > 0 for f in frames)
        acc_rows.append({"forecaster": name, **wf.accuracy(pooled),
                         "symbols_beaten": f"{beaten} of {len(frames)}"})
        scored = pooled.dropna(subset=["actual_ret"])
        year_rows.append({"forecaster": name,
                          **{str(y): wf.skill(g) for y, g in scored.groupby(scored.index.year)}})
    accuracy = pd.DataFrame(acc_rows)
    skill_by_year = pd.DataFrame(year_rows)

    trading_rows = []
    for name, sleeve_curves in curves.items():
        portfolio = backtest.combine_equity(sleeve_curves, s.capital)
        sub = by_symbol[by_symbol["strategy"] == name]
        trading_rows.append({"strategy": name, **backtest.curve_metrics(portfolio),
                             "trades": int(sub["trades"].sum()),
                             "costs_rupees": float(sub["costs_rupees"].sum()),
                             "exposure_pct": float(sub["exposure_pct"].mean())})
    start = min(c.index[0] for c in curves["Buy and hold"])
    end = max(c.index[-1] for c in curves["Buy and hold"])

    bench = dataset.ohlcv(prices, s.benchmark)["Close"].loc[start:end]
    if len(bench) > 1:
        trading_rows.append({"strategy": f"{s.benchmark.title()} index (no costs, no dividends)",
                             **backtest.curve_metrics(bench), "trades": 0,
                             "costs_rupees": 0.0, "exposure_pct": 100.0})

    return Result(accuracy, skill_by_year, pd.DataFrame(trading_rows), by_symbol, used, skipped,
                  start, end, entry, closes=closes, forecasts=forecasts, curves=curves,
                  trade_logs=trade_logs, benchmark=bench if len(bench) > 1 else None)


def _table(df: pd.DataFrame, columns: dict[str, tuple[str, str]]) -> str:
    """Render a markdown table. columns maps field -> (header, format)."""
    head = "| " + " | ".join(h for h, _ in columns.values()) + " |"
    rule = "|" + "|".join(" --- " if i == 0 else " ---: " for i in range(len(columns))) + "|"
    lines = [head, rule]
    for _, row in df.iterrows():
        cells = []
        for key, (_, fmt) in columns.items():
            v = row[key]
            cells.append("n/a" if isinstance(v, float) and pd.isna(v) else format(v, fmt))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render(result: Result, settings: Settings, events: pd.DataFrame | None = None,
           gaps: pd.DataFrame | None = None) -> str:
    s = settings
    acc = _table(result.accuracy, {
        "forecaster": ("Forecaster", ""),
        "forecasts": ("Forecasts", ",d"),
        "mae_pct": ("Avg error (%)", ".3f"),
        "skill_vs_no_change": ("Skill vs no change", "+.4f"),
        "direction_hit_pct": ("Direction right (%)", ".1f"),
        "symbols_beaten": ("Symbols where it beats no change", ""),
    })
    years = [c for c in result.skill_by_year.columns if c != "forecaster"]
    by_year = _table(result.skill_by_year[result.skill_by_year["forecaster"] != "No change"],
                     {"forecaster": ("Skill vs no change, by year", ""),
                      **{y: (y, "+.4f") for y in years}})
    trade = _table(result.trading, {
        "strategy": ("Strategy", ""),
        "total_return_pct": ("Total return (%)", ".1f"),
        "cagr_pct": ("Per year (%)", ".1f"),
        "max_drawdown_pct": ("Worst drop (%)", ".1f"),
        "sharpe": ("Sharpe", ".2f"),
        "trades": ("Trades", ",d"),
        "costs_rupees": ("Costs (Rs)", ",.0f"),
        "exposure_pct": ("Time invested (%)", ".0f"),
    })
    out = [
        "# Scoreboard",
        "",
        f"- Period judged: {result.start:%d %b %Y} to {result.end:%d %b %Y}",
        f"- Symbols ({len(result.symbols)}): {', '.join(result.symbols)}",
        f"- Capital: Rs {s.capital:,.0f} per symbol, long or cash only, whole shares",
        f"- Forecast horizon: {s.horizon} trading days; first {s.min_history} days are history only",
        f"- Entry rule: buy when the forecast gain exceeds the round-trip cost "
        f"({result.entry_threshold * 100:.2f}%); sell when the forecast turns negative",
        "- Trades fill at the next day's open. Prices are adjusted for splits, bonuses and dividends.",
    ]
    if result.skipped:
        out.append(f"- Skipped for too little history: {', '.join(result.skipped)}")
    out += [
        "",
        "## Forecast accuracy",
        "",
        "Skill above zero means the forecaster beats assuming the price stays where it is.",
        "TimesFM has to clear that bar to be worth trading.",
        "",
        acc,
        "",
        "A real edge should show up in most years and most symbols, not just one.",
        "",
        by_year,
        "",
        "## Trading results after costs",
        "",
        trade,
        "",
        "The index row is a reference only: it pays no costs and leaves out dividends,",
        "while the strategies pay full costs and include dividends.",
        "",
    ]
    if events is not None:
        mine = events[events["symbol"].isin(result.symbols)]
        applied = mine[mine["status"].isin(("applied", "estimated", "manual"))
                       & (mine["kind"] != "dividend")]
        review = mine[mine["status"].isin(("unconfirmed", "unparsed"))]
        out += ["## Data checks", "",
                f"- Dividends applied: {int(((mine['kind'] == 'dividend') & (mine['status'] == 'applied')).sum())}",
                f"- Splits, bonuses and demergers applied: {len(applied)}"]
        for _, e in applied.iterrows():
            out.append(f"  - {e['symbol']} {e['ex_date']:%Y-%m-%d}: {e['purpose']} "
                       f"(factor {e['factor']:.4f}, {e['status']})")
        out.append(f"- Events needing a manual look: {len(review)}")
        for _, e in review.iterrows():
            out.append(f"  - {e['symbol']} {e['ex_date']:%Y-%m-%d}: {e['purpose']} ({e['status']})")
        if gaps is not None:
            g = gaps[gaps["symbol"].isin(result.symbols)]
            out.append(f"- Unexplained overnight jumps over 30%: {len(g)}")
            for _, r in g.iterrows():
                out.append(f"  - {r['symbol']} {r['date']:%Y-%m-%d}: {r['overnight_move_pct']:+.1f}%")
        out.append("")
    return "\n".join(out)


def save(result: Result, text: str, out_dir: Path = config.REPORTS_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scoreboard.md").write_text(text)
    result.accuracy.round(6).to_csv(out_dir / "forecast_accuracy.csv", index=False)
    result.skill_by_year.round(6).to_csv(out_dir / "skill_by_year.csv", index=False)
    result.trading.round(4).to_csv(out_dir / "trading.csv", index=False)
    result.by_symbol.round(4).to_csv(out_dir / "trading_by_symbol.csv", index=False)
