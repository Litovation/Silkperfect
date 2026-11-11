"""Parsers that turn NSE files into one common price table.

Common price columns: date, symbol, series, open, high, low, close,
prev_close, volume, value, trades.
"""
from __future__ import annotations

import io
import re
import zipfile
from datetime import date, datetime
from pathlib import Path

import pandas as pd

PRICE_COLUMNS = ["date", "symbol", "series", "open", "high", "low", "close",
                 "prev_close", "volume", "value", "trades"]
ACTION_COLUMNS = ["symbol", "ex_date", "purpose"]
STOCK_SERIES = ("EQ", "BE")  # BE = trade-for-trade; stocks move between the two
INDEX_SERIES = "INDEX"


def pr_date(path: Path) -> date:
    m = re.fullmatch(r"PR(\d{6})\.zip", Path(path).name, flags=re.IGNORECASE)
    if not m:
        raise ValueError(f"not a PR bundle name: {path}")
    return datetime.strptime(m.group(1), "%d%m%y").date()


def _member(z: zipfile.ZipFile, prefix: str) -> str | None:
    """Find a member by prefix; NSE changed the case and date style of names."""
    for name in z.namelist():
        if re.fullmatch(rf"{prefix}\d{{6,8}}\.csv", name, flags=re.IGNORECASE):
            return name
    return None


def _read_csv(raw: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(raw), encoding="latin1", dtype=str,
                     skipinitialspace=True, on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    return df.apply(lambda col: col.str.strip()).fillna("")


def _num(col: pd.Series) -> pd.Series:
    return pd.to_numeric(col, errors="coerce")


def parse_pd(raw: bytes, day: date) -> pd.DataFrame:
    """Parse the Pd price file: stocks plus index rows."""
    df = _read_csv(raw)
    is_stock = (df["MKT"] == "N") & df["SERIES"].isin(STOCK_SERIES) & (df["SYMBOL"] != "")
    is_index = (df["MKT"] == "Y") & (df["SYMBOL"] == "") & (df["SECURITY"] != "")
    df = df[is_stock | is_index].copy()
    index_rows = df["SYMBOL"] == ""
    df.loc[index_rows, "SYMBOL"] = df.loc[index_rows, "SECURITY"].str.upper()
    df.loc[index_rows, "SERIES"] = INDEX_SERIES
    out = pd.DataFrame({
        "date": pd.Timestamp(day),
        "symbol": df["SYMBOL"],
        "series": df["SERIES"],
        "open": _num(df["OPEN_PRICE"]),
        "high": _num(df["HIGH_PRICE"]),
        "low": _num(df["LOW_PRICE"]),
        "close": _num(df["CLOSE_PRICE"]),
        "prev_close": _num(df["PREV_CL_PR"]),
        "volume": _num(df["NET_TRDQTY"]),
        "value": _num(df["NET_TRDVAL"]),
        "trades": _num(df["TRADES"]),
    })
    out = out.dropna(subset=["open", "high", "low", "close"])
    return out[out["close"] > 0].reset_index(drop=True)


def parse_bc(raw: bytes) -> pd.DataFrame:
    """Parse the Bc corporate-actions file (equity series only)."""
    try:
        df = _read_csv(raw)
    except pd.errors.EmptyDataError:   # NSE ships an empty file on some days
        return pd.DataFrame(columns=ACTION_COLUMNS)
    df = df[df["SERIES"].isin(STOCK_SERIES)]
    out = pd.DataFrame({
        "symbol": df["SYMBOL"],
        "ex_date": pd.to_datetime(df["EX_DT"], format="%d/%m/%Y", errors="coerce"),
        "purpose": df["PURPOSE"].str.upper(),
    })
    return out.dropna(subset=["ex_date"]).drop_duplicates().reset_index(drop=True)


def parse_pr_zip(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (prices, corporate actions) for one PR bundle."""
    day = pr_date(path)
    with zipfile.ZipFile(path) as z:
        pd_name, bc_name = _member(z, "pd"), _member(z, "bc")
        if pd_name is None:
            raise ValueError(f"no Pd price file in {path}")
        prices = parse_pd(z.read(pd_name), day)
        actions = (parse_bc(z.read(bc_name)) if bc_name
                   else pd.DataFrame(columns=ACTION_COLUMNS))
    # Remember which day's file listed each action: NSE revises dates and
    # wording, and only the last listing before the ex-date is final.
    actions = actions.assign(seen=pd.Timestamp(day))
    return prices, actions


def _first_csv(path: Path) -> bytes:
    with zipfile.ZipFile(path) as z:
        return z.read(z.namelist()[0])


def parse_legacy_bhavcopy(path: Path) -> pd.DataFrame:
    """Old bhavcopy (cmDDMONYYYYbhav.csv), published until 5 July 2024."""
    df = _read_csv(_first_csv(path))
    df = df[df["SERIES"].isin(STOCK_SERIES)]
    return pd.DataFrame({
        "date": pd.to_datetime(df["TIMESTAMP"], format="%d-%b-%Y"),
        "symbol": df["SYMBOL"], "series": df["SERIES"],
        "open": _num(df["OPEN"]), "high": _num(df["HIGH"]), "low": _num(df["LOW"]),
        "close": _num(df["CLOSE"]), "prev_close": _num(df["PREVCLOSE"]),
        "volume": _num(df["TOTTRDQTY"]), "value": _num(df["TOTTRDVAL"]),
        "trades": _num(df["TOTALTRADES"]),
    }).reset_index(drop=True)


def parse_udiff_bhavcopy(path: Path) -> pd.DataFrame:
    """New UDiFF bhavcopy (BhavCopy_NSE_CM_...), published from 2024."""
    df = _read_csv(_first_csv(path))
    df = df[df["SctySrs"].isin(STOCK_SERIES)]
    return pd.DataFrame({
        "date": pd.to_datetime(df["TradDt"], format="%Y-%m-%d"),
        "symbol": df["TckrSymb"], "series": df["SctySrs"],
        "open": _num(df["OpnPric"]), "high": _num(df["HghPric"]), "low": _num(df["LwPric"]),
        "close": _num(df["ClsPric"]), "prev_close": _num(df["PrvsClsgPric"]),
        "volume": _num(df["TtlTradgVol"]), "value": _num(df["TtlTrfVal"]),
        "trades": _num(df["TtlNbOfTxsExctd"]),
    }).reset_index(drop=True)


def parse_symbol_changes(path: Path) -> dict[str, str]:
    """Map every old symbol to its current symbol, following chains of renames."""
    df = pd.read_csv(path, encoding="latin1", dtype=str, skipinitialspace=True)
    df.columns = [c.strip().upper() for c in df.columns]
    df["when"] = pd.to_datetime(df["EFFECTIVE DATE"].str.strip(), format="%d-%b-%Y",
                                errors="coerce")
    df = df.dropna(subset=["when"]).sort_values("when")
    direct: dict[str, str] = {}
    for old, new in zip(df["OLD SYMBOL"].str.strip(), df["NEW SYMBOL"].str.strip()):
        if old and new and old != new:
            direct[old] = new
    resolved = {}
    for old in direct:
        cur, seen = old, set()
        while cur in direct and cur not in seen:
            seen.add(cur)
            cur = direct[cur]
        if cur != old:
            resolved[old] = cur
    return resolved
