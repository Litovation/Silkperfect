# Chinese rule-based methods on NSE shares

- Period: 10 Feb 2021 to 09 Nov 2026
- Shares: the 200 most traded NSE shares as they stood at the start, Rs 500,000 each, bought or held in cash, full delivery costs
- The bar: holding those same shares throughout, 15.7% a year with a worst drop of -21.4%
- Chan theory points come from czsc (Apache-2.0). RSRS and turtle use their published settings.

## Timing rules

| Rule | Per year (%) | vs holding (pts) | Worst drop (%) | Sharpe | Trades | Costs (Rs) | Time invested (%) | Shares where it beat holding (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hold the same shares | 15.7 | +0.0 | -21.4 | 1.01 | 200 | 520,817 | 100 | n/a |
| Chan theory: all buy and sell points | 4.4 | -11.3 | -13.7 | 0.59 | 8,847 | 16,426,023 | 53 | 18 |
| Chan theory: first-class points only | 4.1 | -11.6 | -10.9 | 0.68 | 662 | 1,255,493 | 39 | 25 |
| Chan theory: third-class points only | 11.7 | -4.0 | -13.8 | 1.05 | 513 | 1,130,563 | 63 | 28 |
| RSRS timing (18, 600, 0.7) | 5.7 | -10.0 | -11.4 | 0.80 | 4,898 | 9,417,698 | 51 | 16 |
| Turtle breakout (20, 10) | 3.9 | -11.8 | -12.6 | 0.62 | 4,415 | 8,184,987 | 42 | 16 |

A timing rule sits in cash part of the time, so a lower return with a much smaller
worst drop can still be a fair trade. Cash earns nothing in this test.

## One-month reversal (picking, not timing)

Each month, from the 200 most traded shares, buy the 20 that fell most over the past month.

| Method | Per year (%) | Worst drop (%) | Strength (t, needs 2) |
| --- | ---: | ---: | ---: |
| Hold all equally | 16.1 | -23.5 | n/a |
| Momentum (12-1 month) | 25.8 | -32.4 | +1.73 |
| One-month reversal | 7.7 | -29.3 | -0.33 |
