"""Turn NSE corporate-action text into price adjustment factors.

A factor is what earlier prices are multiplied by so the series is continuous
across the event: 0.1 for a 10-to-1 face-value split, 0.5 for a 1:1 bonus.

Splits and bonuses are only applied when the price on the ex-date actually
moved by about the expected ratio. Anything that cannot be confirmed is left
unapplied and listed for review.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

NUM = r"(\d+(?:\.\d+)?)"
SPLIT_RE = re.compile(rf"FV\s*SPL\w*\D*?{NUM}\D*?TO\D*?{NUM}")
BONUS_RE = re.compile(r"BON\w*\D*?(\d+)\s*:\s*(\d+)")
DIVIDEND_RE = re.compile(r"DIV|SPDV|SP\s*DV")
UNHANDLED_RE = re.compile(r"RIGHT|CAP\s*RED|CONSOL|SCHEME|AMALGAM")
DEMERGER_RE = re.compile(r"DEMERG")

CONFIRM_TOLERANCE = 0.20   # |ln(observed / expected)| allowed for a split or bonus
MAX_DIVIDEND_YIELD = 0.20  # a larger "dividend" is treated as a parsing error
LISTING_GRACE_DAYS = 7     # an action must still be listed this close to its ex-date
GAP_ALERT = 0.30           # unexplained overnight |ln move| worth a manual look


@dataclass(frozen=True)
class ParsedAction:
    kind: str                 # split, bonus, dividend, demerger, unhandled, other
    ratio: float | None = None     # price factor for split/bonus
    amount: float | None = None    # rupees per share for dividends


def parse_purpose(purpose: str) -> list[ParsedAction]:
    """Read one PURPOSE string. A string can describe more than one action."""
    text = purpose.upper().strip()
    found: list[ParsedAction] = []
    m = SPLIT_RE.search(text)
    if m:
        old, new = float(m.group(1)), float(m.group(2))
        if old > 0 and new > 0 and old != new:
            found.append(ParsedAction("split", ratio=new / old))
    m = BONUS_RE.search(text)
    if m:
        new_shares, held = int(m.group(1)), int(m.group(2))
        if new_shares > 0 and held > 0:
            found.append(ParsedAction("bonus", ratio=held / (new_shares + held)))
    if DEMERGER_RE.search(text):
        found.append(ParsedAction("demerger"))
    if UNHANDLED_RE.search(text):
        found.append(ParsedAction("unhandled"))
    if not found and DIVIDEND_RE.search(text):
        # Drop ordinals such as "2ND INT DIV" so they are not read as rupees.
        cleaned = re.sub(r"\d+\s*(?:ST|ND|RD|TH)\b", " ", text)
        amounts = [float(x) for x in re.findall(NUM, cleaned)]
        found.append(ParsedAction("dividend", amount=sum(amounts) if amounts else None))
    return found or [ParsedAction("other")]


def latest_listing(actions: pd.DataFrame) -> pd.DataFrame:
    """Keep, for each symbol and ex-date, only the wording from its last listing.

    Adds a `superseded` flag for actions that dropped out of NSE's file more
    than LISTING_GRACE_DAYS before their ex-date: the date was revised or the
    action cancelled. Without a `seen` column every row is taken as final.
    """
    if "seen" not in actions.columns:
        return actions.drop_duplicates(["symbol", "ex_date", "purpose"]).assign(superseded=False)
    last = (actions.groupby(["symbol", "ex_date", "purpose"], as_index=False)["seen"].max())
    newest = last.groupby(["symbol", "ex_date"])["seen"].transform("max")
    last = last[last["seen"] == newest].copy()
    gap = (last["ex_date"] - last["seen"]).dt.days
    last["superseded"] = gap > LISTING_GRACE_DAYS
    return last


def build_events(actions: pd.DataFrame, prices: pd.DataFrame,
                 manual: pd.DataFrame | None = None) -> pd.DataFrame:
    """Decide a factor for every corporate action and say whether it is applied.

    `prices` needs date, symbol, open, close (unadjusted). Returns one row per
    action with columns symbol, ex_date, purpose, kind, factor, status.
    `actions` may carry a `seen` column (date of the file that listed it).
    Status is one of: applied, estimated, manual, unconfirmed, unparsed,
    no_price, duplicate, superseded, ignored.
    """
    px = prices.sort_values(["symbol", "date"])
    px = px.assign(prior_close=px.groupby("symbol")["close"].shift(1))
    lookup = px.set_index(["symbol", "date"])[["open", "prior_close"]]

    rows = []
    actions = latest_listing(actions)
    for (symbol, ex_date), group in actions.groupby(["symbol", "ex_date"], sort=True):
        superseded = bool(group["superseded"].iloc[0])
        parsed, seen_keys = [], set()
        for purpose in group["purpose"]:
            for act in parse_purpose(purpose):
                # The same action is often listed twice with different wording.
                key = (act.kind, None if act.ratio is None else round(act.ratio, 6),
                       None if act.amount is None else round(act.amount, 4))
                duplicate = key in seen_keys and act.kind != "other"
                seen_keys.add(key)
                parsed.append((purpose, act, duplicate))
        try:
            bar = lookup.loc[(symbol, ex_date)]
            open_, prior = float(bar["open"]), float(bar["prior_close"])
        except KeyError:
            open_ = prior = math.nan
        has_price = prior > 0 and open_ > 0
        observed = open_ / prior if has_price else math.nan

        # Splits and bonuses on the same day are confirmed together.
        ratio_actions = [a for _, a, dup in parsed if a.kind in ("split", "bonus") and not dup]
        expected = math.prod(a.ratio for a in ratio_actions) if ratio_actions else 1.0
        confirmed = (has_price and ratio_actions
                     and abs(math.log(observed / expected)) < CONFIRM_TOLERANCE)
        has_amount = any(a.kind == "dividend" and a.amount for _, a, _ in parsed)

        for purpose, act, duplicate in parsed:
            factor, status = 1.0, "ignored"
            if act.kind == "other":
                pass
            elif superseded:
                status = "superseded"
            elif duplicate:
                status = "duplicate"
            elif act.kind in ("split", "bonus"):
                if not has_price:
                    status = "no_price"
                elif confirmed:
                    factor, status = act.ratio, "applied"
                else:
                    status = "unconfirmed"
            elif act.kind == "dividend":
                if not has_price:
                    status = "no_price"
                elif act.amount is None and has_amount:
                    status = "duplicate"   # same dividend, listed without its amount
                elif act.amount is None or not 0 < act.amount / prior < MAX_DIVIDEND_YIELD:
                    status = "unparsed"
                else:
                    factor, status = 1 - act.amount / prior, "applied"
            elif act.kind == "demerger":
                # No ratio is published; the ex-date opening price is the best
                # estimate of what the remaining business is worth.
                if not has_price:
                    status = "no_price"
                elif ratio_actions or not 0.3 < observed < 0.995:
                    status = "unconfirmed"
                else:
                    factor, status = observed, "estimated"
            elif act.kind == "unhandled":
                status = "unparsed"
            rows.append({"symbol": symbol, "ex_date": ex_date, "purpose": purpose,
                         "kind": act.kind, "factor": factor, "status": status})

    events = pd.DataFrame(rows, columns=["symbol", "ex_date", "purpose", "kind",
                                         "factor", "status"])
    if manual is not None and len(manual):
        m = manual.copy()
        m["ex_date"] = pd.to_datetime(m["ex_date"])
        keys = set(zip(m["symbol"], m["ex_date"]))
        # A manual entry replaces everything detected for that symbol and day.
        keep = [key not in keys for key in zip(events["symbol"], events["ex_date"])]
        events = events[keep]
        manual_rows = pd.DataFrame({
            "symbol": m["symbol"], "ex_date": m["ex_date"],
            "purpose": m.get("note", pd.Series("", index=m.index)).fillna("").astype(str),
            "kind": "manual", "factor": m["factor"].astype(float), "status": "manual"})
        events = pd.concat([events, manual_rows], ignore_index=True)
    return events.sort_values(["symbol", "ex_date"]).reset_index(drop=True)


APPLIED = ("applied", "estimated", "manual")


def adjust_prices(prices: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Add adj_factor and adjusted OHLCV columns.

    Each bar is multiplied by the product of the factors of all events with an
    ex-date after it, so the latest prices are left as traded.
    """
    df = prices.sort_values(["symbol", "date"]).reset_index(drop=True)
    used = events[events["status"].isin(APPLIED)]
    per_day = (used.groupby(["symbol", "ex_date"])["factor"].prod()
               .rename("event_factor").reset_index()
               .rename(columns={"ex_date": "date"}))
    df = df.merge(per_day, on=["symbol", "date"], how="left")
    own = df["event_factor"].fillna(1.0)
    # Product of this bar's factor and every later one, then drop this bar's own.
    inclusive = own[::-1].groupby(df["symbol"][::-1]).cumprod()[::-1]
    df["adj_factor"] = inclusive / own
    for col in ("open", "high", "low", "close"):
        df[f"adj_{col}"] = df[col] * df["adj_factor"]
    df["adj_volume"] = df["volume"] / df["adj_factor"]
    return df.drop(columns="event_factor")


def unexplained_gaps(adjusted: pd.DataFrame, threshold: float = GAP_ALERT) -> pd.DataFrame:
    """Overnight jumps that remain after adjustment: likely missed actions."""
    df = adjusted.sort_values(["symbol", "date"])
    prior = df.groupby("symbol")["adj_close"].shift(1)
    move = np.log(df["adj_open"] / prior)
    out = df.loc[move.abs() > threshold, ["symbol", "date"]].copy()
    out["overnight_move_pct"] = (np.exp(move[move.abs() > threshold]) - 1) * 100
    return out.reset_index(drop=True)
