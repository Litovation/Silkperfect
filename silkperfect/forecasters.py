"""Forecasters. Each one sees only past closes and returns a future price path.

TimesFM will be added as one more class with the same `predict` method.
"""
from __future__ import annotations

import numpy as np


class Forecaster:
    name = "forecaster"

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


def default_forecasters() -> list[Forecaster]:
    return [NoChange(), Drift(250), MovingAverage(20)]
