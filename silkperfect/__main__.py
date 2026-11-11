"""Command line: python -m silkperfect <command>."""
from __future__ import annotations

import argparse
import random
from datetime import date

import numpy as np
import pandas as pd

from . import config, corporate_actions as ca, dataset, nse, parse, scoreboard
from .forecasters import TimesFM, default_forecasters


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
    prices, events = dataset.build(renames=_renames(), manual=dataset.read_manual())
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
