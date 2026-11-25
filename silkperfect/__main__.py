"""Command line: python -m silkperfect <command>."""
from __future__ import annotations

import argparse
import random
from datetime import date

import numpy as np
import pandas as pd

from . import config, corporate_actions as ca, dataset, nse, parse, scoreboard
from .forecasters import Chronos, TimesFM, default_forecasters


def _renames() -> dict[str, str]:
    if config.SYMBOL_CHANGE_PATH.exists():
        return parse.parse_symbol_changes(config.SYMBOL_CHANGE_PATH)
    return {}


def cmd_fetch(args) -> None:
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    print(f"Downloading NSE daily bundles {start} to {end} ...")
    counts = nse.fetch_range(start, end, workers=args.workers)
    print(f"  downloaded {counts['ok']}, no file (holiday/weekend) {counts['missing']}, "
          f"already had {counts['skipped']}, failed {counts['error']}")
    nse.fetch_symbol_changes()
    print("  symbol-change list updated")
    if counts["error"]:
        raise SystemExit("Some days failed to download; run fetch again.")


def cmd_build(args) -> None:
    bad = nse.verify_manifest()
    if bad:
        raise SystemExit(f"{len(bad)} files do not match data/manifest.csv "
                         f"(first: {bad[0]}). Delete them and run fetch again.")
    prices, events = dataset.build(renames=_renames(), manual=dataset.read_manual(),
                                   cache_dir=config.DAY_CACHE_DIR)
    dataset.save(prices, events)
    stocks = prices[prices["series"] != parse.INDEX_SERIES]
    print(f"Built {len(prices):,} rows: {stocks['symbol'].nunique():,} stocks, "
          f"{prices['date'].nunique():,} trading days, "
          f"{prices['date'].min():%Y-%m-%d} to {prices['date'].max():%Y-%m-%d}")
    print("Corporate actions by outcome:")
    print(events.groupby(["kind", "status"]).size().to_string())


def cmd_crosscheck(args) -> None:
    prices = dataset.load_prices()
    stocks = prices[prices["series"] != parse.INDEX_SERIES]
    days = sorted(stocks["date"].dt.date.unique())
    random.seed(args.seed)
    sample = sorted(random.sample(days, min(args.days, len(days))))
    renames = _renames()
    worst, compared, mismatched, checked_days = 0.0, 0, 0, 0
    for d in sample:
        got = nse.fetch_crosscheck(d)
        if got is None:
            print(f"  {d}: bhavcopy not available, skipped")
            continue
        fmt, path = got
        other = (parse.parse_udiff_bhavcopy if fmt == "udiff" else parse.parse_legacy_bhavcopy)(path)
        other = dataset.combine_days([dataset.apply_renames(other, renames)])
        mine = stocks[stocks["date"] == pd.Timestamp(d)]
        both = mine.merge(other, on=["date", "symbol"], suffixes=("", "_bhav"))
        diff = np.zeros(len(both))
        for col in ("open", "high", "low", "close"):
            diff = np.maximum(diff, (both[col] - both[f"{col}_bhav"]).abs().to_numpy())
        bad = int((diff > 0.011).sum())
        compared += len(both)
        mismatched += bad
        checked_days += 1
        worst = max(worst, float(diff.max()) if len(diff) else 0.0)
        print(f"  {d} ({fmt}): {len(both):,} stocks compared, {bad} differ")
    print(f"Cross-check: {checked_days} days, {compared:,} stock-days, "
          f"{mismatched} mismatches, largest difference Rs {worst:.2f}")
    if mismatched:
        raise SystemExit(1)


def cmd_scoreboard(args) -> None:
    universe = config.load_universe()
    settings = scoreboard.Settings(horizon=args.horizon, min_history=args.min_history,
                                   capital=args.capital)
    prices = dataset.load_prices(symbols=universe + [settings.benchmark])
    events = pd.read_csv(config.ACTIONS_PATH, parse_dates=["ex_date"])
    forecasters = default_forecasters()
    if args.timesfm:
        forecasters.append(TimesFM(max_context=settings.max_context))
        print("Running TimesFM. The first run is slow (about 2 to 3 minutes per symbol "
              "on a laptop); results are saved, so later runs take seconds.")
    result = scoreboard.run(prices, universe, settings, forecasters,
                            cache_dir=config.FORECAST_CACHE_DIR,
                            progress=lambda msg: print(msg, flush=True))
    text = scoreboard.render(result, settings, events, ca.unexplained_gaps(prices))
    scoreboard.save(result, text)
    print(text)
    print(f"Saved to {config.REPORTS_DIR}/scoreboard.md")


def cmd_rank(args) -> None:
    from . import ranking
    settings = ranking.RankSettings(universe_size=args.universe, top_n=args.top,
                                    rebalance_days=args.every)
    print("Loading prices ...", flush=True)
    prices = dataset.load_prices()
    panel = ranking.make_panel(prices, exclude=ranking.etf_symbols())
    signals = [ranking.Momentum(), ranking.IndexMomentum(), ranking.LowVolatility()]
    if args.models:
        signals += [ranking.ForecastSignal(TimesFM(max_context=settings.context)),
                    ranking.ForecastSignal(Chronos(max_context=settings.context))]
        print("Running forecasting models. The first run is slow; results are saved.")
    if args.qlib:
        from .qlib_signal import QlibSignal
        members = {panel.close.index[i]: ranking.eligible(panel, i, settings)
                   for i in range(settings.context - 1, len(panel.close), 21)}
        # Retrain about every three months whatever the swap schedule.
        signals.append(QlibSignal(panel, members, retrain_every=max(1, round(63 / args.every))))
        print("Running Qlib's Alpha158 + LightGBM recipe (a few minutes; saved afterwards).")
    if args.kronos:
        from .kronos_signal import KronosSignal
        signals.append(KronosSignal())
        print("Running Kronos. Without a graphics card the first run takes about 2 hours; "
              "it saves as it goes, so it can be stopped and resumed.")
    result = ranking.run(panel, signals, settings, cache_dir=config.FORECAST_CACHE_DIR,
                         progress=lambda msg: print(f"  {msg}", flush=True) if "scored" in msg else None)
    bench = dataset.ohlcv(prices, config.BENCHMARK)["Close"].loc[result.start:result.end]
    text = ranking.render(result, bench)
    suffix = "" if args.every == 21 else f"_every{args.every}"
    ranking.save(result, text, suffix=suffix)
    print(text)
    print(f"Saved to {config.REPORTS_DIR}/ranking{suffix}.md")


def _paper_status_text(o, account) -> str:
    """A short plain-language status of the pretend account."""
    from . import paper
    plan = account["plan"]
    now = o.equity.iloc[-1]
    lines = [
        "# Pretend account today",
        "",
        f"- Prices up to: {o.end:%d %b %Y}",
        f"- Started: {account['start']:%d %b %Y} with Rs {plan.amount:,.0f}",
        f"- Plan: hold {plan.shares_held} shares, picked as \"{paper.METHODS[plan.method].lower()}\", "
        f"swapped every {plan.swap_every_days} market days",
        f"- Worth now: Rs {now:,.0f} ({now - plan.amount:+,.0f})",
        f"- Fees paid so far: Rs {o.fees:,.0f}",
        f"- Cash not invested: Rs {(o.cash if len(o.trades) else plan.amount):,.0f}",
        f"- Market days until the next swap: {max(o.days_to_next_swap, 0)}",
        "",
    ]
    if o.picks_waiting:
        lines += ["Shares to buy at the next market open: " + ", ".join(o.picks_waiting), ""]
    if len(o.holdings):
        lines += ["| Share | How many | Price now (Rs) | Worth now (Rs) |", "| --- | ---: | ---: | ---: |"]
        for _, r in o.holdings.iterrows():
            lines.append(f"| {r['Share']} | {r['How many']} | {r['Price now (Rs)']:,.2f} | "
                         f"{r['Worth now (Rs)']:,.0f} |")
        lines.append("")
    lines.append("No real orders are placed. This is a pretend account on real prices.")
    return "\n".join(lines) + "\n"


def _load_market():
    from . import ranking
    prices = dataset.load_prices()
    return prices, ranking.make_panel(prices, exclude=ranking.etf_symbols())


def cmd_paper(args) -> None:
    """Start, show or close the pretend account from the terminal."""
    from . import paper
    if args.action == "close":
        paper.close_account()
        print("Pretend account closed.")
        return
    prices, panel = _load_market()
    if args.action == "start":
        if paper.load_account() is not None:
            raise SystemExit("A pretend account already exists. Close it first: "
                             "python -m silkperfect paper close")
        plan = paper.Plan(amount=args.amount, method=args.method, shares_held=args.hold,
                          swap_every_days=args.swap)
        paper.start_account(plan, panel.close.index[-1])
        print(f"Started a pretend account with Rs {args.amount:,.0f}.")
    account = paper.load_account()
    if account is None:
        raise SystemExit("No pretend account yet. Start one: python -m silkperfect paper start")
    outcome = paper.run_plan(panel, prices, account["plan"], start=account["start"],
                             cache_dir=config.FORECAST_CACHE_DIR)
    text = _paper_status_text(outcome, account)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (config.REPORTS_DIR / "live.md").write_text(text)
    print(text)


def cmd_daily(args) -> None:
    """The once-a-day job: get new prices, rebuild, update the pretend account."""
    print(f"Daily update, {date.today():%d %b %Y}")
    counts = nse.fetch_range(date.fromisoformat(config.DEFAULT_START), date.today())
    print(f"  {counts['ok']} new day(s) of prices")
    if counts["ok"] or not config.PRICES_PATH.exists():
        nse.fetch_symbol_changes()
        cmd_build(args)
    from . import paper
    if paper.load_account() is None:
        print("No pretend account yet. Start one: python -m silkperfect paper start")
        return
    args.action = "status"
    cmd_paper(args)


def cmd_chinese(args) -> None:
    from . import chinese, ranking
    print("Loading prices ...", flush=True)
    prices, panel = _load_market()
    settings = ranking.RankSettings()
    start_i = settings.min_history - 1
    symbols = ranking.eligible(panel, start_i, settings)
    print(f"Running Chan theory (czsc), RSRS and turtle rules on {len(symbols)} shares ...", flush=True)
    result = chinese.run_timing(panel, symbols, panel.close.index[start_i],
                                progress=lambda msg: print(f"  {msg}", flush=True))
    picks = ranking.run(panel, [ranking.Momentum(), chinese.ShortTermReversal()], settings)
    text = chinese.render(result, picks.summary)
    chinese.save(result, text)
    print(text)
    print(f"Saved to {config.REPORTS_DIR}/chinese_methods.md")


def cmd_intraday(args) -> None:
    from . import daytrade, intraday, ranking
    print("Loading prices ...", flush=True)
    prices, panel = _load_market()
    start = max(len(panel.close) - 61, 0)
    universe = ranking.eligible(panel, start, ranking.RankSettings(universe_size=args.universe))
    print(f"Getting 5-minute prices for {len(universe)} shares ...", flush=True)
    daytrade.fetch(universe, refresh=args.refresh, progress=lambda m: print(f"  {m}", flush=True))
    sessions = {}
    for symbol in universe:
        path = config.INTRADAY_DIR / f"{symbol}.json"
        if path.exists():
            found = daytrade.read_sessions(path)
            if found:
                sessions[symbol] = found
    settings = intraday.Settings()
    print("Running the rule-based strategies ...", flush=True)
    parts = [intraday.run_rules(sessions, settings, progress=lambda m: print(f"  {m}", flush=True)),
             intraday.run_leaders(sessions, settings)]
    print("Training and testing the ML classifier ...", flush=True)
    ml_trades, ml_info = intraday.run_classifier(sessions, settings)
    trades = pd.concat(parts + [ml_trades], ignore_index=True)
    summary = intraday.summarise(trades)
    text = intraday.render(summary, trades["date"].min(), trades["date"].max(), len(sessions),
                           settings, ml_info)
    intraday.save(trades, summary, text)
    print(text)
    print(f"Saved to {config.REPORTS_DIR}/intraday.md")


def cmd_daytrade(args) -> None:
    from . import daytrade, ranking
    print("Loading prices ...", flush=True)
    prices = dataset.load_prices()
    panel = ranking.make_panel(prices, exclude=ranking.etf_symbols())
    # The liquid list as it stood 60 trading days ago, so it is not chosen with hindsight.
    start = max(len(panel.close) - 61, 0)
    universe = ranking.eligible(panel, start, ranking.RankSettings(universe_size=args.universe))
    print(f"Downloading 5-minute prices for {len(universe)} shares from Yahoo Finance ...", flush=True)
    problems = daytrade.fetch(universe, refresh=args.refresh,
                              progress=lambda msg: print(f"  {msg}", flush=True))
    sessions = {}
    for symbol in universe:
        path = config.INTRADAY_DIR / f"{symbol}.json"
        if path.exists():
            found = daytrade.read_sessions(path)
            if found:
                sessions[symbol] = found
    print(f"  {len(sessions)} shares with data, {len(problems)} not available")
    if args.variants:
        table, split = daytrade.explore(sessions)
        text = daytrade.render_variants(table, split)
        (config.REPORTS_DIR / "daytrade_variants.md").write_text(text)
        table.round(4).to_csv(config.REPORTS_DIR / "daytrade_variants.csv", index=False)
        print(text)
        return
    settings = daytrade.DayTradeSettings()
    trades = daytrade.run(sessions, settings)
    share_days = sum(len(v) for v in sessions.values())
    text = daytrade.render(trades, daytrade.summarise(trades, share_days), settings)
    daytrade.save(trades, text)
    print(text)
    print(f"Saved to {config.REPORTS_DIR}/daytrade.md")


def cmd_device(args) -> None:
    """Say whether the forecasting models will use a graphics card."""
    try:
        import torch
    except ImportError:
        raise SystemExit("PyTorch is not installed. Run: pip install -r requirements-timesfm.txt")
    if torch.cuda.is_available():
        print(f"Graphics card found: {torch.cuda.get_device_name(0)}. The models will use it.")
    else:
        print(f"No graphics card visible to PyTorch (version {torch.__version__}). "
              "The models will use the processor, which is much slower.")
        if "+cpu" in torch.__version__:
            print("This PyTorch build is processor-only. If the computer has an NVIDIA card, "
                  "install the graphics build: see README, 'Using a graphics card'.")


def cmd_dashboard(args) -> None:
    """Get any new NSE prices, then open the dashboard."""
    import subprocess
    import sys
    try:
        print("Checking for new NSE prices ...")
        counts = nse.fetch_range(date.fromisoformat(config.DEFAULT_START), date.today())
        print(f"  {counts['ok']} new day(s) downloaded")
        if counts["ok"] or not config.PRICES_PATH.exists():
            if not config.SYMBOL_CHANGE_PATH.exists() or counts["ok"]:
                nse.fetch_symbol_changes()
            print("Updating the price table ...")
            cmd_build(args)
    except Exception as exc:   # no internet should not stop the dashboard from opening
        print(f"  Could not update prices ({exc}). Opening with the prices already here.")
    if not config.PRICES_PATH.exists():
        raise SystemExit("No price data and no internet. Connect and run this again.")
    print("Opening the dashboard. Press Ctrl+C here to stop it.")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(config.ROOT / "dashboard.py")],
                   cwd=config.ROOT, check=False)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="silkperfect", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    f = sub.add_parser("fetch", help="download NSE daily files")
    f.add_argument("--start", default=config.DEFAULT_START)
    f.add_argument("--end", default=date.today().isoformat())
    f.add_argument("--workers", type=int, default=4)
    f.set_defaults(func=cmd_fetch)

    b = sub.add_parser("build", help="parse downloads into adjusted prices")
    b.set_defaults(func=cmd_build)

    c = sub.add_parser("crosscheck", help="compare prices against NSE bhavcopy files")
    c.add_argument("--days", type=int, default=12)
    c.add_argument("--seed", type=int, default=7)
    c.set_defaults(func=cmd_crosscheck)

    s = sub.add_parser("scoreboard", help="run baselines and write reports/scoreboard.md")
    s.add_argument("--horizon", type=int, default=config.HORIZON)
    s.add_argument("--min-history", type=int, default=config.MIN_HISTORY)
    s.add_argument("--capital", type=float, default=config.CAPITAL_PER_SYMBOL)
    s.add_argument("--timesfm", action="store_true", help="also score TimesFM 2.5")
    s.set_defaults(func=cmd_scoreboard)

    k = sub.add_parser("rank", help="ranking test on the most liquid stocks")
    k.add_argument("--universe", type=int, default=200)
    k.add_argument("--top", type=int, default=20)
    k.add_argument("--models", action="store_true", help="also rank with TimesFM and Chronos")
    k.add_argument("--kronos", action="store_true", help="also rank with Kronos (slow)")
    k.add_argument("--qlib", action="store_true", help="also rank with Qlib's Alpha158 + LightGBM")
    k.add_argument("--every", type=int, default=21, help="trading days between swaps (21 is monthly)")
    k.set_defaults(func=cmd_rank)

    pa = sub.add_parser("paper", help="start, show or close the pretend account")
    pa.add_argument("action", choices=["start", "status", "close"])
    pa.add_argument("--amount", type=float, default=10_000.0)
    pa.add_argument("--method", default="index_momentum",
                    choices=["momentum", "index_momentum", "low_volatility", "timesfm", "chronos", "kronos"])
    pa.add_argument("--hold", type=int, default=5, help="how many shares to hold")
    pa.add_argument("--swap", type=int, default=63, help="market days between swaps")
    pa.set_defaults(func=cmd_paper)

    dy = sub.add_parser("daily", help="once-a-day job: new prices and the pretend account")
    dy.set_defaults(func=cmd_daily)

    cn = sub.add_parser("chinese", help="test Chan theory (czsc), RSRS, turtle and reversal rules")
    cn.set_defaults(func=cmd_chinese)

    it = sub.add_parser("intraday", help="test a battery of day-trading strategies on 5-minute bars")
    it.add_argument("--universe", type=int, default=200)
    it.add_argument("--refresh", action="store_true", help="download the 5-minute prices again")
    it.set_defaults(func=cmd_intraday)

    t = sub.add_parser("daytrade", help="test the opening-range-breakout day trade on NSE shares")
    t.add_argument("--universe", type=int, default=200)
    t.add_argument("--refresh", action="store_true", help="download the 5-minute prices again")
    t.add_argument("--variants", action="store_true", help="test every variant of the rule")
    t.set_defaults(func=cmd_daytrade)

    g = sub.add_parser("device", help="check whether a graphics card will be used")
    g.set_defaults(func=cmd_device)

    d = sub.add_parser("dashboard", help="update prices and open the dashboard")
    d.set_defaults(func=cmd_dashboard)

    r = sub.add_parser("run", help="fetch, build and scoreboard in one go")
    r.add_argument("--start", default=config.DEFAULT_START)
    r.add_argument("--end", default=date.today().isoformat())
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--horizon", type=int, default=config.HORIZON)
    r.add_argument("--min-history", type=int, default=config.MIN_HISTORY)
    r.add_argument("--capital", type=float, default=config.CAPITAL_PER_SYMBOL)
    r.add_argument("--timesfm", action="store_true", help="also score TimesFM 2.5")
    r.set_defaults(func=lambda a: (cmd_fetch(a), cmd_build(a), cmd_scoreboard(a)))

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
