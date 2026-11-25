"""Indian equity-delivery trading costs.

Rates are the published ones for NSE cash-market delivery trades. Brokerage
and the depository (DP) charge are broker-specific defaults: check them
against a real Upstox contract note before trusting small edges.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    brokerage_flat: float = 20.0       # rupees per order ...
    brokerage_pct: float = 0.025       # ... or this share of turnover, whichever is lower
    stt: float = 0.001                 # securities transaction tax, buy and sell
    stt_buy: float | None = None       # set when the buy side differs (zero for intraday)
    exchange_txn: float = 0.0000297    # NSE transaction charge
    sebi_fee: float = 0.000001         # 10 rupees per crore
    stamp_duty_buy: float = 0.00015    # buy side only
    gst: float = 0.18                  # on brokerage, exchange charge, SEBI fee, DP charge
    dp_charge_sell: float = 20.0       # depository charge per stock per sell day, before GST
    slippage_bps: float = 5.0          # price given up per side, in hundredths of a percent

    def cost(self, side: str, quantity: float, price: float) -> float:
        """Total rupee cost of one order. side is 'buy' or 'sell'."""
        turnover = abs(quantity) * price
        if turnover == 0:
            return 0.0
        brokerage = min(self.brokerage_flat, self.brokerage_pct * turnover)
        exchange = self.exchange_txn * turnover
        sebi = self.sebi_fee * turnover
        taxable = brokerage + exchange + sebi
        stt = self.stt_buy if side == "buy" and self.stt_buy is not None else self.stt
        total = taxable + stt * turnover + self.slippage_bps / 10_000 * turnover
        if side == "buy":
            total += self.stamp_duty_buy * turnover
        elif side == "sell":
            taxable += self.dp_charge_sell
            total += self.dp_charge_sell
        else:
            raise ValueError("side must be 'buy' or 'sell'")
        return total + self.gst * taxable

    @classmethod
    def intraday(cls, **overrides) -> "CostModel":
        """Costs for a trade bought and sold the same day (no shares delivered)."""
        base = dict(brokerage_flat=20.0, brokerage_pct=0.0005, stt=0.00025, stt_buy=0.0,
                    stamp_duty_buy=0.00003, dp_charge_sell=0.0)
        return cls(**{**base, **overrides})

    def round_trip(self, quantity: float, price: float) -> float:
        return self.cost("buy", quantity, price) + self.cost("sell", quantity, price)

    def round_trip_fraction(self, capital: float) -> float:
        """Round-trip cost as a fraction of the money put into one position."""
        return self.round_trip(capital, 1.0) / capital

    def per_leg(self, quantity: float, price: float) -> float:
        """Half a round trip.

        backtesting.py calls its commission hook with the same sign on entry
        and exit of a long trade, so buys and sells cannot be told apart
        there. Every long round trip has one of each, so charging the average
        on both legs gives the right total.
        """
        return self.round_trip(quantity, price) / 2
