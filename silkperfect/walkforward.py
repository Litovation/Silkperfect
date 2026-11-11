"""Walk-forward (rolling-origin) forecast evaluation.

For every forecast date the forecaster is handed a copy of the closes up to
and including that date and nothing else, so it cannot see the future.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .forecasters import Forecaster


def walk_forward(close: pd.Series, forecaster: Forecaster, horizon: int,
                 min_history: int, max_context: int | None = None,
                 stride: int = 1, batch: int = 256) -> pd.DataFrame:
    """Forecast `horizon` days ahead from every `stride`-th date.

    Returns a frame indexed by forecast date with: close, pred_price,
    pred_ret and actual_ret (log returns over the horizon). actual_ret is NaN
    for the last `horizon` dates, where the outcome is not known yet.
    """
    values = close.to_numpy(dtype=float)
    n = len(values)
    origins = list(range(min_history - 1, n, stride))
    preds = np.empty(len(origins))
    for start in range(0, len(origins), batch):
        chunk = origins[start:start + batch]
        histories = []
        for i in chunk:
            lo = 0 if max_context is None else max(0, i + 1 - max_context)
            histories.append(values[lo:i + 1].copy())
        paths = np.asarray(forecaster.predict(histories, horizon), dtype=float)
        if paths.shape != (len(chunk), horizon):
            raise ValueError(f"{forecaster.name} returned shape {paths.shape}, "
                             f"expected {(len(chunk), horizon)}")
        preds[start:start + len(chunk)] = paths[:, -1]
    idx = np.array(origins)
    now = values[idx]
    future = np.full(len(idx), np.nan)
    known = idx + horizon < n
    future[known] = values[idx[known] + horizon]
    return pd.DataFrame({
        "close": now,
        "pred_price": preds,
        "pred_ret": np.log(preds / now),
        "actual_ret": np.log(future / now),
    }, index=close.index[idx])


def accuracy(frame: pd.DataFrame) -> dict[str, float]:
    """Score forecasts whose outcome is known.

    skill_vs_no_change is 1 - MAE / MAE of the no-change forecast: above zero
    means better than assuming the price stays where it is.
    """
    df = frame.dropna(subset=["actual_ret"])
    err = df["pred_ret"] - df["actual_ret"]
    naive_mae = df["actual_ret"].abs().mean()
    called = df[(df["pred_ret"] != 0) & (df["actual_ret"] != 0)]
    hit = (np.sign(called["pred_ret"]) == np.sign(called["actual_ret"])).mean() if len(called) else np.nan
    mae = err.abs().mean()
    return {
        "forecasts": len(df),
        "mae_pct": mae * 100,
        "rmse_pct": float(np.sqrt((err ** 2).mean())) * 100,
        "skill_vs_no_change": 1 - mae / naive_mae if naive_mae else np.nan,
        "direction_hit_pct": hit * 100,
    }


def forecast_signal(pred_ret: pd.Series, entry: float, exit: float = 0.0) -> pd.Series:
    """Long/flat target from forecasts.

    Go long when the forecast return clears `entry` (the round-trip cost);
    stay long until the forecast return falls below `exit`.
    """
    out = np.zeros(len(pred_ret), dtype=int)
    held = False
    for i, r in enumerate(pred_ret.to_numpy()):
        if not held and r > entry:
            held = True
        elif held and r < exit:
            held = False
        out[i] = int(held)
    return pd.Series(out, index=pred_ret.index)


def sma_signal(close: pd.Series, fast: int, slow: int) -> pd.Series:
    """Long while the fast average is above the slow one."""
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    return (f > s).astype(int)
