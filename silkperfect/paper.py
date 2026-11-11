"""Plans in plain terms, and a pretend (paper) account.

A plan is: how much money, how shares are picked, how many are held and how
often they are swapped. The same plan can be replayed over the past ("what
would have happened") or run forward from a start date as a pretend account.

The pretend account keeps no hidden state. Its start date and plan are saved
in one small file, and its trades are replayed from the price data every time,
so the same data always gives the same account.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from . import config, dataset, ranking
from .costs import CostModel
from .forecasters import Chronos, TimesFM

FUND_SYMBOL = "NIFTYBEES"     # a Nifty 50 fund that trades like a share
BANK_RATE = 0.065             # assumed yearly interest on a bank deposit

METHODS = {
    "momentum": "Shares that rose the most over the past year",
    "low_volatility": "The steadiest shares",
    "timesfm": "TimesFM computer forecast",
    "chronos": "Chronos computer forecast",
}
MODEL_METHODS = ("timesfm", "chronos")


@dataclass
class Plan:
    amount: float = 10_000.0
    method: str = "momentum"
    shares_held: int = 5
    swap_every_days: int = 63        # trading days; 63 is about three months

    def settings(self) -> ranking.RankSettings:
        return ranking.RankSettings(capital=self.amount, top_n=self.shares_held,
                                    rebalance_days=self.swap_every_days)


def make_signal(method: str, context: int) -> ranking.Signal:
    if method == "momentum":
        return ranking.Momentum()
    if method == "low_volatility":
        return ranking.LowVolatility()
    if method == "timesfm":
        return ranking.ForecastSignal(TimesFM(max_context=context))
    if method == "chronos":
        return ranking.ForecastSignal(Chronos(max_context=context))
    raise ValueError(f"unknown method {method!r}")


def buy_and_hold(bars: pd.DataFrame, amount: float, start: pd.Timestamp,
                 costs: CostModel) -> pd.Series:
    """Buy whole units at the first open after `start` and keep them."""
    after = bars[bars.index > start]
    if after.empty:
        return pd.Series({start: amount})
    price = float(after["Open"].iloc[0])
    units = np.floor(amount / price)
    while units > 0 and units * price + costs.cost("buy", units, price) > amount:
        units -= 1
    cash = amount - units * price - (costs.cost("buy", units, price) if units else 0.0)
    value = cash + units * after["Close"]
    return pd.concat([pd.Series({start: amount}), value])


def bank_deposit(index: pd.DatetimeIndex, amount: float, rate: float = BANK_RATE) -> pd.Series:
    years = (index - index[0]).days / 365.25
    return pd.Series(amount * (1 + rate) ** years, index=index)


def _worst_fall(equity: pd.Series) -> tuple[float, float, float]:
    """(peak value, low value after it, percent fall) for the deepest fall."""
    peak = equity.cummax()
    low_day = (equity / peak - 1).idxmin()
    return float(peak[low_day]), float(equity[low_day]), float((equity[low_day] / peak[low_day] - 1) * 100)


@dataclass
class Outcome:
    plan: Plan
    method_name: str
    equity: pd.Series           # the plan
    everything: pd.Series       # all 200 liquid shares, scaled to the same money (not buyable with little money)
    fund: pd.Series             # one Nifty 50 fund, bought once
    bank: pd.Series             # bank deposit at an assumed rate
    trades: pd.DataFrame
    fees: float
    holdings: pd.DataFrame      # what is held now
    cash: float
    picks_waiting: list[str]    # chosen on the latest day, bought at the next open
    days_to_next_swap: int      # trading days until shares are next swapped
    start: pd.Timestamp
    end: pd.Timestamp
    worst_fall: tuple[float, float, float]
    rank_t_stat: float


def run_plan(panel: ranking.Panel, prices: pd.DataFrame, plan: Plan,
             start: pd.Timestamp | None = None, cache_dir: Path | None = None,
             progress=None) -> Outcome:
    """Replay a plan. `start` None means as far back as the data allows."""
    s = plan.settings()
    first = None
    if start is not None:
        first = int(panel.close.index.searchsorted(pd.Timestamp(start)))
        first = min(first, len(panel.close) - 1)
    signal = make_signal(plan.method, s.context)
    result = ranking.run(panel, [signal], s, cache_dir=cache_dir, progress=progress,
                         first_index=first)
    sim = result.sims[signal.name]
    equity = sim["equity"]
    begin, end = result.start, panel.close.index[-1]

    # "Everything" is run with large money and scaled down: it shows what the
    # 200 shares did, which small money cannot actually buy.
    big = ranking.RankSettings(capital=1e7, top_n=s.top_n, rebalance_days=s.rebalance_days)
    wide = ranking.run(panel, [], big, first_index=first).equity[ranking.HOLD_ALL]
    everything = wide / wide.iloc[0] * plan.amount

    fund = buy_and_hold(dataset.ohlcv(prices, FUND_SYMBOL), plan.amount, begin, s.costs)
    index = panel.close.index[panel.close.index >= begin]
    bank = bank_deposit(index, plan.amount)

    close = panel.close.ffill().iloc[-1]
    trades = sim["trades"]
    rows = []
    for symbol, count in sim["shares"].items():
        buys = trades[(trades["symbol"] == symbol) & (trades["action"] == "Buy")]
        last_buy = float(buys["price"].iloc[-1]) if len(buys) else np.nan
        rows.append({"Share": symbol, "How many": int(count), "Price now (Rs)": float(close[symbol]),
                     "Worth now (Rs)": float(count * close[symbol]),
                     "Last bought at (Rs)": last_buy})
    holdings = pd.DataFrame(rows, columns=["Share", "How many", "Price now (Rs)",
                                           "Worth now (Rs)", "Last bought at (Rs)"])

    dates = sorted(result.holdings[signal.name])
    latest = dates[-1]
    waiting = result.holdings[signal.name][latest] if latest == end else []
    since = len(panel.close) - 1 - panel.close.index.get_loc(latest)
    next_swap = s.rebalance_days - since
    summary = result.summary.set_index("method")
    t_stat = summary.loc[signal.name].get("rank_t_stat", np.nan) if signal.name in summary.index else np.nan
    return Outcome(plan, METHODS[plan.method], equity, everything, fund, bank, trades,
                   float(sim["costs"]), holdings, float(sim["cash"]), waiting, next_swap,
                   begin, end, _worst_fall(equity), float(t_stat) if pd.notna(t_stat) else np.nan)


# ---- the pretend account file -------------------------------------------------

def load_account(path: Path = config.PAPER_PATH) -> dict | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return {"start": pd.Timestamp(data["start"]), "plan": Plan(**data["plan"])}


def start_account(plan: Plan, start: pd.Timestamp, path: Path = config.PAPER_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"start": f"{pd.Timestamp(start):%Y-%m-%d}",
                                "plan": asdict(plan)}, indent=2))


def close_account(path: Path = config.PAPER_PATH) -> None:
    if path.exists():
        path.unlink()
