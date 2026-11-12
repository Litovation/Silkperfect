# Day-trade rule test (opening-range breakout)

The rule comes from the day-trader-skill pack (github.com/jakeschincariol/day-trader-skill),
applied unchanged to NSE shares with NSE hours and Indian intraday costs.

- Period: 14 Aug 2026 to 11 Nov 2026 (60 trading days; Yahoo's 5-minute history goes back no further)
- Shares: the 200 most traded NSE shares that had data
- Rule: buy the first 5-minute close above the first 15 minutes' high; stop at the middle of that range; target 1 times the risk; no entries after 15:00; out by 15:20
- Costs: intraday brokerage, taxes and charges plus 5 basis points of slippage per side, on Rs 10,000 per trade

## Result

| Measure | Value |
| --- | ---: |
| Trades taken | 6,529 |
| Share-days where the rule fired | 55% |
| Hit the target | 42.5% |
| Hit the stop | 42.3% |
| Closed at 15:20 | 15.2% |
| Average distance to the stop | 0.76% of the price |
| Average result before costs | -0.001 R (+0.012% of the money in the trade) |
| Costs per trade | 0.432 R |
| Average result after costs | -0.433 R (-0.242%) |
| Strength before costs (t, needs 2) | -1.84 |
| Strength after costs (t, needs 2) | -13.89 |
| Days that made money after costs | 3% |

Verdict: **no reliable edge even before costs**.

R is the amount risked on a trade: +1 R is a win of that amount, -1 R a loss of it.
Strength treats each day as one observation, since trades on the same day move together.

Best day: 26 Oct 2026 (+0.09 R a trade over 181 trades). Worst day: 21 Oct 2026 (-1.19 R over 43 trades).

## Limits of this test

- Sixty trading days is one stretch of market weather, not a full cycle.
- Yahoo's bars are free and unofficial; a stop is assumed to fill exactly at its price,
  which is kinder than real trading when the price gaps through it.
- Buying only, as in the original rule.
