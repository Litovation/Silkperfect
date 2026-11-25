"""Paths and default settings. Everything here can be overridden from the CLI."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PR_DIR = RAW_DIR / "pr"
INTRADAY_DIR = RAW_DIR / "intraday"
CROSSCHECK_DIR = RAW_DIR / "crosscheck"
PROCESSED_DIR = DATA_DIR / "processed"
MANIFEST_PATH = DATA_DIR / "manifest.csv"
PRICES_PATH = PROCESSED_DIR / "prices.parquet"
DAY_CACHE_DIR = PROCESSED_DIR / "days"
PAPER_PATH = DATA_DIR / "paper_account.json"
FORECAST_CACHE_DIR = PROCESSED_DIR / "forecasts"
ACTIONS_PATH = PROCESSED_DIR / "corporate_actions.csv"
SYMBOL_CHANGE_PATH = RAW_DIR / "symbolchange.csv"
REPORTS_DIR = ROOT / "reports"
UNIVERSE_PATH = ROOT / "config" / "universe.txt"
MANUAL_ACTIONS_PATH = ROOT / "config" / "corporate_actions_manual.csv"

DEFAULT_START = "2019-01-01"
BENCHMARK = "NIFTY 50"

# Scoreboard defaults
HORIZON = 5            # trading days ahead that each forecast targets
MIN_HISTORY = 500      # trading days of history required before the first forecast
MAX_CONTEXT = 1024     # most recent days handed to a forecaster
CAPITAL_PER_SYMBOL = 500_000.0  # rupees; 1 crore across ~20 names
SMA_FAST = 20
SMA_SLOW = 50


def load_universe(path: Path = UNIVERSE_PATH) -> list[str]:
    symbols = []
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip().upper()
        if line:
            symbols.append(line)
    return symbols
