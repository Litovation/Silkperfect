# Ranking test

- Period: 10 Feb 2021 to 09 Nov 2026, 68 rebalances
- Every 21 trading days: take the 200 most liquid NSE stocks (no ETFs), buy the top 20 by score in equal amounts at the next open
- Starting money Rs 10,000,000; full Indian delivery costs on every trade
- The bar: holding all 200 equally, which returned 16.1% a year
- Last 252 trading days (from 03 Nov 2025) are shown separately as a check on recent behaviour

## Returns after costs

| Method | Per year (%) | vs hold-all (pts) | Worst drop (%) | Sharpe | Before holdout, per year (%) | Holdout return (%) | Turnover per rebalance (%) | Costs (Rs) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hold all equally | 16.1 | +0.0 | -23.8 | 0.95 | 20.5 | -2.8 | 7 | 728,050 |
| Momentum (12-1 month) | 25.9 | +9.8 | -32.5 | 1.02 | 32.9 | -2.7 | 31 | 1,887,008 |
| Low volatility (12 month) | 10.4 | -5.7 | -18.8 | 0.91 | 13.4 | -2.8 | 14 | 522,017 |
| Nifty 50 index (no costs, no dividends) | 9.2 | -6.9 | -17.2 | 0.71 | n/a | n/a | 0 | 0 |

## Does the ranking carry information?

Rank correlation compares each method's ordering of the stocks with how they then
performed. Zero means no information. A t-statistic above about 2 means the result
is unlikely to be luck.

| Method | Avg rank correlation | t-statistic | Rebalances where its picks beat hold-all (%) |
| --- | ---: | ---: | ---: |
| Momentum (12-1 month) | +0.036 | +1.73 | 59 |
| Low volatility (12 month) | +0.011 | +0.41 | 47 |
