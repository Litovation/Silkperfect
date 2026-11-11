"""Build the adjusted price table from downloaded PR bundles."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config, corporate_actions as ca, parse

SERIES_RANK = {"EQ": 0, "BE": 1, parse.INDEX_SERIES: 2}


def apply_renames(df: pd.DataFrame, renames: dict[str, str]) -> pd.DataFrame:
    if renames:
        # A plain lookup: pandas' replace() checks every rename against every row.
        df = df.assign(symbol=df["symbol"].map(lambda sym: renames.get(sym, sym)))
    return df


def combine_days(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Stack daily price frames; one row per (date, symbol), preferring EQ."""
    df = pd.concat(frames, ignore_index=True)
    df["_rank"] = df["series"].map(SERIES_RANK).fillna(9)
    df = (df.sort_values(["date", "symbol", "_rank"])
            .drop_duplicates(["date", "symbol"], keep="first")
            .drop(columns="_rank"))
    return df.reset_index(drop=True)


def _parse_cached(path: Path, cache_dir: Path | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse one bundle, keeping the result so later builds only read new days."""
    if cache_dir is None:
        return parse.parse_pr_zip(path)
    stat = path.stat()
    stem = f"{parse.pr_date(path):%Y%m%d}-{stat.st_size}"
    p_file, a_file = cache_dir / f"{stem}-prices.parquet", cache_dir / f"{stem}-actions.parquet"
    if p_file.exists() and a_file.exists():
        return pd.read_parquet(p_file), pd.read_parquet(a_file)
    prices, actions = parse.parse_pr_zip(path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    prices.to_parquet(p_file, index=False)
    actions.astype({"symbol": str, "purpose": str}).to_parquet(a_file, index=False)
    return prices, actions


def build(pr_dir: Path = config.PR_DIR, renames: dict[str, str] | None = None,
          manual: pd.DataFrame | None = None,
          cache_dir: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse every PR bundle under pr_dir. Returns (adjusted prices, events)."""
    files = sorted(pr_dir.glob("*/PR*.zip"), key=parse.pr_date)
    if not files:
        raise FileNotFoundError(f"no PR bundles under {pr_dir}; run `fetch` first")
    price_frames, action_frames = [], []
    for path in files:
        prices, actions = _parse_cached(path, cache_dir)
        price_frames.append(prices)
        action_frames.append(actions)
    renames = renames or {}
    prices = combine_days([apply_renames(f, renames) for f in price_frames])
    actions = apply_renames(pd.concat(action_frames, ignore_index=True), renames)
    if manual is not None:
        manual = apply_renames(manual, renames)
    stocks = prices[prices["series"] != parse.INDEX_SERIES]
    events = ca.build_events(actions, stocks, manual)
    return ca.adjust_prices(prices, events), events


def save(prices: pd.DataFrame, events: pd.DataFrame,
         prices_path: Path = config.PRICES_PATH,
         actions_path: Path = config.ACTIONS_PATH) -> None:
    prices_path.parent.mkdir(parents=True, exist_ok=True)
    prices.to_parquet(prices_path, index=False)
    events.to_csv(actions_path, index=False)


def load_prices(path: Path = config.PRICES_PATH, symbols: list[str] | None = None) -> pd.DataFrame:
    filters = [("symbol", "in", symbols)] if symbols else None
    return pd.read_parquet(path, filters=filters)


def ohlcv(prices: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Adjusted daily bars for one symbol, indexed by date."""
    df = prices[prices["symbol"] == symbol].sort_values("date").set_index("date")
    out = df[["adj_open", "adj_high", "adj_low", "adj_close", "adj_volume"]]
    out.columns = ["Open", "High", "Low", "Close", "Volume"]
    return out


def read_manual(path: Path = config.MANUAL_ACTIONS_PATH) -> pd.DataFrame | None:
    if not path.exists():
        return None
    df = pd.read_csv(path, dtype={"symbol": str, "note": str})
    return df if len(df) else None
