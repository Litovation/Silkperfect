"""Microsoft Qlib's Alpha158 + LightGBM recipe as a share-picking method.

The 158 features and the LightGBM settings are taken from Qlib (MIT licence,
github.com/microsoft/qlib: qlib/contrib/data/loader.py and
examples/benchmarks/LightGBM). Qlib itself is not installed: it expects its
own data format and Chinese market data, so the same formulas are computed
here from NSE prices.

Two things differ from Qlib's example, and both are forced by this test:
- The label is the return over the holding period (bought the next day),
  not the next single day, because shares are held between rebalances.
- The model is retrained as time moves forward, using only days whose
  outcome was already known on the decision date.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from .ranking import Panel, Signal

WINDOWS = (5, 10, 20, 30, 60)
EPS = 1e-12
# Qlib's benchmark settings for LightGBM on Alpha158.
LGB_PARAMS = dict(objective="mse", colsample_bytree=0.8879, learning_rate=0.2, subsample=0.8789,
                  subsample_freq=1, lambda_l1=205.6999, lambda_l2=580.9768, max_depth=8,
                  num_leaves=210, num_threads=4, seed=0, deterministic=True, verbosity=-1)
MAX_ROUNDS, EARLY_STOP = 1000, 50


def _windows(a: np.ndarray, d: int) -> np.ndarray:
    """(T, N) -> (T, N, d) trailing windows; the first d-1 rows are NaN."""
    pad = np.full((d - 1, a.shape[1]), np.nan)
    return sliding_window_view(np.vstack([pad, a]), d, axis=0)


def _regression(close: pd.DataFrame, d: int):
    """Slope, R-squared and last-point residual of close against time over d days."""
    w = _windows(close.to_numpy(dtype=float), d)
    x = np.arange(d, dtype=float)
    xc = x - x.mean()
    ym = w.mean(axis=2)
    slope = (w * xc).sum(axis=2) / (xc ** 2).sum()
    yc = w - ym[:, :, None]
    var_y = (yc ** 2).sum(axis=2)
    with np.errstate(invalid="ignore", divide="ignore"):
        rsq = np.where(var_y > 0, slope ** 2 * (xc ** 2).sum() / var_y, np.nan)
    resi = w[:, :, -1] - (ym + slope * xc[-1])
    mk = lambda v: pd.DataFrame(v, index=close.index, columns=close.columns)
    return mk(slope), mk(rsq), mk(resi)


def _position(df: pd.DataFrame, d: int, largest: bool) -> pd.DataFrame:
    """1-based position inside the window of its largest (or smallest) value."""
    w = _windows(df.to_numpy(dtype=float), d)
    bad = np.isnan(w).any(axis=2)
    filled = np.where(np.isnan(w), -np.inf if largest else np.inf, w)
    idx = (filled.argmax(axis=2) if largest else filled.argmin(axis=2)) + 1.0
    return pd.DataFrame(np.where(bad, np.nan, idx), index=df.index, columns=df.columns)


def alpha158(panel: Panel) -> dict[str, pd.DataFrame]:
    """All 158 Alpha158 features as {name: dates x symbols}. Uses past data only."""
    c, o, h, l, v = panel.close, panel.open, panel.high, panel.low, panel.volume
    vwap = (panel.value / v.where(v > 0)).fillna(c)        # rupees traded per adjusted share
    f: dict[str, pd.DataFrame] = {}
    top, bottom, span = np.maximum(o, c), np.minimum(o, c), h - l + EPS
    f["KMID"], f["KLEN"], f["KMID2"] = (c - o) / o, (h - l) / o, (c - o) / span
    f["KUP"], f["KUP2"] = (h - top) / o, (h - top) / span
    f["KLOW"], f["KLOW2"] = (bottom - l) / o, (bottom - l) / span
    f["KSFT"], f["KSFT2"] = (2 * c - h - l) / o, (2 * c - h - l) / span
    f["OPEN0"], f["HIGH0"], f["LOW0"], f["VWAP0"] = o / c, h / c, l / c, vwap / c

    prev_c, prev_v = c.shift(1), v.shift(1)
    up, down = (c - prev_c).clip(lower=0), (prev_c - c).clip(lower=0)
    move = (c - prev_c).abs()
    v_up, v_down, v_move = (v - prev_v).clip(lower=0), (prev_v - v).clip(lower=0), (v - prev_v).abs()
    higher = (c > prev_c).astype(float).where(prev_c.notna())
    lower = (c < prev_c).astype(float).where(prev_c.notna())
    log_v = np.log(v + 1)
    ret_ratio, vol_ratio = c / prev_c, np.log(v / prev_v.where(prev_v > 0) + 1)
    weighted = (c / prev_c - 1).abs() * v

    for d in WINDOWS:
        f[f"ROC{d}"] = c.shift(d) / c
        f[f"MA{d}"] = c.rolling(d).mean() / c
        f[f"STD{d}"] = c.rolling(d).std() / c
        slope, rsq, resi = _regression(c, d)
        f[f"BETA{d}"], f[f"RSQR{d}"], f[f"RESI{d}"] = slope / c, rsq, resi / c
        hi, lo = h.rolling(d).max(), l.rolling(d).min()
        f[f"MAX{d}"], f[f"MIN{d}"] = hi / c, lo / c
        f[f"QTLU{d}"] = c.rolling(d).quantile(0.8) / c
        f[f"QTLD{d}"] = c.rolling(d).quantile(0.2) / c
        f[f"RANK{d}"] = c.rolling(d).rank(pct=True)
        f[f"RSV{d}"] = (c - lo) / (hi - lo + EPS)
        imax, imin = _position(h, d, True), _position(l, d, False)
        f[f"IMAX{d}"], f[f"IMIN{d}"], f[f"IMXD{d}"] = imax / d, imin / d, (imax - imin) / d
        f[f"CORR{d}"] = c.rolling(d).corr(log_v)
        f[f"CORD{d}"] = ret_ratio.rolling(d).corr(vol_ratio)
        p, n = higher.rolling(d).mean(), lower.rolling(d).mean()
        f[f"CNTP{d}"], f[f"CNTN{d}"], f[f"CNTD{d}"] = p, n, p - n
        total = move.rolling(d).sum() + EPS
        sp, sn = up.rolling(d).sum() / total, down.rolling(d).sum() / total
        f[f"SUMP{d}"], f[f"SUMN{d}"], f[f"SUMD{d}"] = sp, sn, sp - sn
        f[f"VMA{d}"] = v.rolling(d).mean() / (v + EPS)
        f[f"VSTD{d}"] = v.rolling(d).std() / (v + EPS)
        f[f"WVMA{d}"] = weighted.rolling(d).std() / (weighted.rolling(d).mean() + EPS)
        v_total = v_move.rolling(d).sum() + EPS
        vp, vn = v_up.rolling(d).sum() / v_total, v_down.rolling(d).sum() / v_total
        f[f"VSUMP{d}"], f[f"VSUMN{d}"], f[f"VSUMD{d}"] = vp, vn, vp - vn
    return {k: val.replace([np.inf, -np.inf], np.nan) for k, val in f.items()}


class QlibSignal(Signal):
    """Rank shares with a LightGBM model on Alpha158, retrained as time passes."""
    name = "Qlib Alpha158 + LightGBM"

    def __init__(self, panel: Panel, members: dict[pd.Timestamp, list[str]],
                 retrain_every: int = 3, sample_step: int = 5):
        """`members` maps dates to the liquid universe on that date; training
        uses each day's most recent universe, so it is never chosen with hindsight."""
        self.cache_key = f"qlib158-lgb-v1-r{retrain_every}-s{sample_step}"
        self.retrain_every, self.sample_step = retrain_every, sample_step
        self.members = dict(sorted(members.items()))
        names = sorted({n for group in self.members.values() for n in group})
        self.panel = Panel(*(None if df is None else df[names] for df in
                             (panel.close, panel.open, panel.value, panel.high, panel.low, panel.volume)))
        self._features: dict[str, pd.DataFrame] | None = None
        self._model, self._model_day, self._calls = None, None, 0
        self._horizon: int | None = None

    def _ensure_features(self) -> None:
        if self._features is None:
            self._features = alpha158(self.panel)
            self._columns = list(self._features)

    def _rows(self, day_pos: int, names: list[str]) -> np.ndarray:
        return np.column_stack([self._features[k].iloc[day_pos][names].to_numpy(dtype=float)
                                for k in self._columns])

    def _universe_on(self, day: pd.Timestamp) -> list[str]:
        past = [d for d in self.members if d <= day]
        return self.members[past[-1]] if past else []

    def _train(self, today_pos: int, horizon: int):
        import lightgbm as lgb
        close = self.panel.close
        # Outcome of a decision on day p: bought on p+1, measured at p+1+horizon.
        last_known = today_pos - horizon - 1
        X, y, when = [], [], []
        for p in range(60, last_known + 1, self.sample_step):
            names = self._universe_on(close.index[p])
            if not names:
                continue
            fwd = (close.iloc[p + 1 + horizon][names] / close.iloc[p + 1][names] - 1).to_numpy(dtype=float)
            ok = ~np.isnan(fwd)
            if ok.sum() < 20:
                continue
            z = (fwd[ok] - fwd[ok].mean()) / (fwd[ok].std() + EPS)      # Qlib's CSZScoreNorm on the label
            X.append(self._rows(p, names)[ok])
            y.append(z)
            when.append(np.full(ok.sum(), p))
        if len(X) < 10:
            return None
        X, y, when = np.vstack(X), np.concatenate(y), np.concatenate(when)
        days = np.unique(when)
        cut = days[int(len(days) * 0.8)]
        # Leave a gap of one holding period so validation outcomes do not overlap training ones.
        train, valid = when < cut - horizon, when >= cut
        if train.sum() < 500 or valid.sum() < 100:
            train, valid = when < cut, when >= cut
        booster = lgb.train(LGB_PARAMS, lgb.Dataset(X[train], y[train]), num_boost_round=MAX_ROUNDS,
                            valid_sets=[lgb.Dataset(X[valid], y[valid])],
                            callbacks=[lgb.early_stopping(EARLY_STOP, verbose=False)])
        return booster

    def score(self, close, horizon):
        return self.score_bars(Panel(close, close, close), horizon)

    def score_bars(self, past: Panel, horizon: int) -> pd.Series:
        self._ensure_features()
        day = past.close.index[-1]
        pos = self.panel.close.index.get_loc(day)
        if self._model is None or self._horizon != horizon or self._calls % self.retrain_every == 0:
            model = self._train(pos, horizon)
            if model is not None:
                self._model, self._model_day, self._horizon = model, day, horizon
        self._calls += 1
        names = [n for n in past.close.columns if n in self.panel.close.columns]
        if self._model is None:
            return pd.Series(0.0, index=names)
        pred = self._model.predict(self._rows(pos, names), num_iteration=self._model.best_iteration)
        return pd.Series(pred, index=names)
