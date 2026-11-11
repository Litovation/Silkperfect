# Ranking test

- Period: 10 Feb 2021 to 09 Nov 2026, 68 rebalances
- Every 21 trading days: take the 200 most liquid NSE stocks (no ETFs), buy the top 20 by score in equal amounts at the next open
- Starting money Rs 10,000,000; full Indian delivery costs on every trade
- The bar: holding all 200 equally, which returned 16.1% a year
- Last 252 trading days (from 03 Nov 2025) are shown separately as a check on recent behaviour

## Returns after costs

| Method | Per year (%) | vs hold-all (pts) | Worst drop (%) | Sharpe | Before holdout, per year (%) | Holdout return (%) | Turnover per rebalance (%) | Costs (Rs) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hold all equally | 16.1 | +0.0 | -23.5 | 0.95 | 20.5 | -2.7 | 7 | 690,096 |
| Momentum (12-1 month) | 25.8 | +9.7 | -32.4 | 1.02 | 32.8 | -2.7 | 31 | 1,871,062 |
| Low volatility (12 month) | 10.4 | -5.7 | -18.8 | 0.91 | 13.4 | -2.7 | 14 | 519,998 |
| TimesFM 2.5 | 13.0 | -3.1 | -29.4 | 0.71 | 18.5 | -10.2 | 68 | 2,617,363 |
| Chronos-Bolt | 15.4 | -0.7 | -36.7 | 0.77 | 22.5 | -13.1 | 73 | 3,119,696 |
| Nifty 50 index (no costs, no dividends) | 9.2 | -6.9 | -17.2 | 0.71 | n/a | n/a | 0 | 0 |

## Does the ranking carry information?

Rank correlation compares each method's ordering of the stocks with how they then
performed. Zero means no information. A t-statistic above about 2 means the result
is unlikely to be luck.

| Method | Avg rank correlation | t-statistic | Rebalances where its picks beat hold-all (%) |
| --- | ---: | ---: | ---: |
| Momentum (12-1 month) | +0.036 | +1.73 | 59 |
| Low volatility (12 month) | +0.011 | +0.41 | 47 |
| TimesFM 2.5 | +0.012 | +0.99 | 47 |
| Chronos-Bolt | -0.001 | -0.08 | 51 |
