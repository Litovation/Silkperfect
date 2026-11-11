"""Run long/flat signals through backtesting.py with Indian costs."""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy

from .costs import CostModel

TRADING_DAYS = 252


class TargetPosition(Strategy):
    """Hold the stock while the Signal column is 1, hold cash while it is 0.

    A signal seen at one day's close is acted on at the next day's open.
    """

    def init(self):
        pass

    def next(self):
        want = self.data.Signal[-1] > 0.5
        if want and not self.position:
            self.buy(size=0.99)
        elif not want and self.position:
            self.position.close()


def run_signal(bars: pd.DataFrame, signal: pd.Series, capital: float,
               costs: CostModel) -> dict:
    """Backtest one symbol. `bars` has Open/High/Low/Close/Volume by date."""
    data = bars.copy()
    data["Signal"] = signal.reindex(data.index).fillna(0).astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bt = Backtest(data, TargetPosition, cash=capital, commission=costs.per_leg,
                      trade_on_close=False, finalize_trades=True)
        stats = bt.run()
    return {
        "equity": stats["_equity_curve"]["Equity"],
        "trades": int(stats["# Trades"]),
        "costs": float(stats.get("Commissions [$]", 0.0) or 0.0),
        "exposure_pct": float(stats["Exposure Time [%]"]),
        "trade_log": stats["_trades"],
    }


def combine_equity(curves: list[pd.Series], capital: float) -> pd.Series:
    """Add up per-symbol equity curves into one portfolio curve.

    A symbol with a shorter history sits in cash until its first bar.
    """
    index = sorted(set().union(*(c.index for c in curves)))
    total = pd.Series(0.0, index=index)
    for c in curves:
        total += c.reindex(index).ffill().fillna(capital)
    return total


def curve_metrics(equity: pd.Series) -> dict[str, float]:
    start, end = float(equity.iloc[0]), float(equity.iloc[-1])
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    daily = equity.pct_change().dropna()
    vol = daily.std() * np.sqrt(TRADING_DAYS)
    drawdown = (equity / equity.cummax() - 1).min()
    return {
        "total_return_pct": (end / start - 1) * 100,
        "cagr_pct": ((end / start) ** (1 / years) - 1) * 100,
        "max_drawdown_pct": drawdown * 100,
        "volatility_pct": vol * 100,
        "sharpe": (daily.mean() * TRADING_DAYS / vol) if vol > 0 else np.nan,
    }
