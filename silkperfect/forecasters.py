"""Forecasters. Each one sees only past closes and returns a future price path.

TimesFM needs extra packages: pip install -r requirements-timesfm.txt
"""
from __future__ import annotations

import numpy as np


class Forecaster:
    name = "forecaster"
    cache_key: str | None = None   # set on slow forecasters so results are saved to disk

    def predict(self, histories: list[np.ndarray], horizon: int) -> np.ndarray:
        """Return an array of shape (len(histories), horizon) of forecast prices.

        Each history is a 1-D array of past adjusted closes, oldest first,
        ending at the forecast date.
        """
        raise NotImplementedError


class NoChange(Forecaster):
    """Tomorrow's price equals today's. The baseline every model must beat."""
    name = "No change"

    def predict(self, histories, horizon):
        return np.array([np.full(horizon, h[-1]) for h in histories], dtype=float)


class Drift(Forecaster):
    """Extend the average daily log return of the last `lookback` days."""

    def __init__(self, lookback: int = 250):
        self.lookback = lookback
        self.name = f"Drift ({lookback}d)"

    def predict(self, histories, horizon):
        steps = np.arange(1, horizon + 1)
        out = []
        for h in histories:
            window = np.log(h[-(self.lookback + 1):])
            mu = (window[-1] - window[0]) / max(len(window) - 1, 1)
            out.append(h[-1] * np.exp(mu * steps))
        return np.array(out, dtype=float)


class MovingAverage(Forecaster):
    """Price returns to its `window`-day average."""

    def __init__(self, window: int = 20):
        self.window = window
        self.name = f"Moving average ({window}d)"

    def predict(self, histories, horizon):
        return np.array([np.full(horizon, h[-self.window:].mean()) for h in histories],
                        dtype=float)


class TimesFM(Forecaster):
    """Google's TimesFM 2.5 (200M), used as published with no training on our data.

    The weights are pinned to one revision so a rerun gives the same numbers.
    Version 2.5 is Apache-2.0; do not swap in 3.0, whose weights are
    non-commercial.
    """
    REPO = "google/timesfm-2.5-200m-pytorch"
    REVISION = "1d952420fba87f3c6dee4f240de0f1a0fbc790e3"
    name = "TimesFM 2.5"

    def __init__(self, max_context: int = 1024, batch_size: int = 64):
        self.max_context = max_context
        self.batch_size = batch_size
        self.cache_key = f"timesfm25-{self.REVISION[:8]}-ctx{max_context}"
        self._model = None

    def _load(self):
        try:
            import timesfm
            import torch
        except ImportError as exc:
            raise SystemExit("TimesFM is not installed. Run: "
                             "pip install -r requirements-timesfm.txt") from exc
        torch.manual_seed(0)
        model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(self.REPO, revision=self.REVISION)
        model.compile(timesfm.ForecastConfig(
            max_context=self.max_context, max_horizon=64, normalize_inputs=True,
            use_continuous_quantile_head=True, force_flip_invariance=True,
            infer_is_positive=True, fix_quantile_crossing=True,
            per_core_batch_size=self.batch_size))
        return model

    def predict(self, histories, horizon):
        if self._model is None:
            self._model = self._load()
        inputs = [np.asarray(h[-self.max_context:], dtype=np.float32) for h in histories]
        point, _ = self._model.forecast(horizon=horizon, inputs=inputs)
        return np.asarray(point, dtype=float)[:, :horizon]


class Chronos(Forecaster):
    """Amazon's Chronos-Bolt (base), used as published. Apache-2.0."""
    REPO = "amazon/chronos-bolt-base"
    REVISION = "5d9f166d69f47aef3401367a7b842e78fe97b121"
    name = "Chronos-Bolt"

    def __init__(self, max_context: int = 1024, batch_size: int = 128):
        self.max_context = max_context
        self.batch_size = batch_size
        self.cache_key = f"chronosbolt-{self.REVISION[:8]}-ctx{max_context}"
        self._pipe = None

    def _load(self):
        try:
            import torch
            from chronos import BaseChronosPipeline
        except ImportError as exc:
            raise SystemExit("Chronos is not installed. Run: "
                             "pip install -r requirements-timesfm.txt") from exc
        torch.manual_seed(0)
        return BaseChronosPipeline.from_pretrained(self.REPO, revision=self.REVISION,
                                                   device_map="cpu")

    def predict(self, histories, horizon):
        import torch
        if self._pipe is None:
            self._pipe = self._load()
        out = []
        for start in range(0, len(histories), self.batch_size):
            chunk = [torch.tensor(np.asarray(h[-self.max_context:], dtype=np.float32))
                     for h in histories[start:start + self.batch_size]]
            quantiles, _ = self._pipe.predict_quantiles(chunk, prediction_length=horizon,
                                                        quantile_levels=[0.5])
            out.append(quantiles[:, :, 0].numpy())
        return np.concatenate(out).astype(float)


def default_forecasters() -> list[Forecaster]:
    return [NoChange(), Drift(250), MovingAverage(20)]
