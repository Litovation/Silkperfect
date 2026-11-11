"""Kronos: a forecasting model trained on stock price bars (MIT licence).

Its code is kept in third_party/kronos. It reads open, high, low, close and
volume, and its forecasts are drawn at random, so several draws are averaged
and the random seed is fixed per date to make reruns repeatable.

Daily bars are too slow without a graphics card (hours per test), so prices
are grouped into 5-trading-day bars, which the model also supports.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from . import config
from .ranking import Panel, Signal

KRONOS_DIR = config.ROOT / "third_party" / "kronos"
BAR_DAYS = 5


def weekly_bars(past: Panel, symbol: str) -> pd.DataFrame:
    """Group one stock's past days into 5-day bars, counting back from the latest day."""
    close = past.close[symbol].to_numpy(dtype=float)
    n = len(close) // BAR_DAYS * BAR_DAYS
    def col(df):
        values = close if df is None else df[symbol].to_numpy(dtype=float)
        values = np.where(np.isnan(values), close, values)
        return values[-n:].reshape(-1, BAR_DAYS)
    volume = (np.zeros_like(close) if past.volume is None
              else np.nan_to_num(past.volume[symbol].to_numpy(dtype=float)))
    return pd.DataFrame({
        "open": col(past.open)[:, 0], "high": col(past.high).max(axis=1),
        "low": col(past.low).min(axis=1), "close": col(past.close)[:, -1],
        "volume": volume[-n:].reshape(-1, BAR_DAYS).sum(axis=1)})


class KronosSignal(Signal):
    MODEL = "NeoQuasar/Kronos-small"
    MODEL_REVISION = "901c26c1332695a2a8f243eb2f37243a37bea320"
    TOKENIZER = "NeoQuasar/Kronos-Tokenizer-base"
    TOKENIZER_REVISION = "0e0117387f39004a9016484a186a908917e22426"
    name = "Kronos"

    def __init__(self, samples: int = 5, batch_size: int = 100):
        self.samples, self.batch_size = samples, batch_size
        self.cache_key = f"kronos-small-{self.MODEL_REVISION[:8]}-bar{BAR_DAYS}-s{samples}"
        self._predictor = None

    def _load(self):
        try:
            import torch  # noqa: F401
            if str(KRONOS_DIR) not in sys.path:
                sys.path.insert(0, str(KRONOS_DIR))
            from model import Kronos, KronosPredictor, KronosTokenizer
        except ImportError as exc:
            raise SystemExit("Kronos needs extra packages. Run: "
                             "pip install -r requirements-timesfm.txt") from exc
        tokenizer = KronosTokenizer.from_pretrained(self.TOKENIZER, revision=self.TOKENIZER_REVISION)
        model = Kronos.from_pretrained(self.MODEL, revision=self.MODEL_REVISION)
        return KronosPredictor(model, tokenizer, device="cpu", max_context=512)

    def score(self, close, horizon):
        return self.score_bars(Panel(close, close, close), horizon)

    def score_bars(self, past: Panel, horizon: int) -> pd.Series:
        import torch
        if self._predictor is None:
            self._predictor = self._load()
        steps = max(1, round(horizon / BAR_DAYS))
        names = list(past.close.columns)
        last_day = past.close.index[-1]
        bars = [weekly_bars(past, n) for n in names]
        count = len(bars[0])
        stamps = pd.Series(pd.date_range(end=last_day, periods=count, freq="7D"))
        ahead = pd.Series(pd.date_range(start=last_day + pd.Timedelta(days=7), periods=steps, freq="7D"))
        torch.manual_seed(last_day.toordinal())      # same date, same draws
        out = {}
        for start in range(0, len(names), self.batch_size):
            chunk = bars[start:start + self.batch_size]
            preds = self._predictor.predict_batch(
                chunk, [stamps] * len(chunk), [ahead] * len(chunk), pred_len=steps,
                T=1.0, top_p=0.9, sample_count=self.samples, verbose=False)
            for name, frame, pred in zip(names[start:], chunk, preds):
                out[name] = float(pred["close"].iloc[-1] / frame["close"].iloc[-1] - 1)
        return pd.Series(out)
