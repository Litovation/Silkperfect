# Ranking test

- Period: 10 Feb 2021 to 09 Nov 2026, 1426 rebalances
- Every 1 trading day(s): take the 200 most liquid NSE stocks (no ETFs), buy the top 20 by score in equal amounts at the next open
- Starting money Rs 10,000,000; full Indian delivery costs on every trade
- The bar: holding all 200 equally, which returned 8.5% a year
- Last 252 trading days (from 03 Nov 2025) are shown separately as a check on recent behaviour

## Returns after costs

| Method | Per year (%) | vs hold-all (pts) | Worst drop (%) | Sharpe | Before holdout, per year (%) | Holdout return (%) | Turnover per rebalance (%) | Costs (Rs) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hold all equally | 8.5 | +0.0 | -27.7 | 0.55 | 12.4 | -8.4 | 1 | 6,457,421 |
| Momentum (12-1 month) | 20.2 | +11.7 | -39.6 | 0.84 | 27.3 | -8.4 | 7 | 8,654,137 |
| Momentum (NSE index style) | 16.8 | +8.4 | -42.9 | 0.78 | 23.7 | -10.8 | 8 | 10,412,536 |
| Low volatility (12 month) | 8.2 | -0.2 | -20.4 | 0.74 | 11.7 | -6.6 | 2 | 2,427,096 |
| Nifty 50 index (no costs, no dividends) | 9.2 | +0.7 | -17.2 | 0.71 | n/a | n/a | 0 | 0 |

## Does the ranking carry information?

Rank correlation compares each method's ordering of the stocks with how they then
performed. Zero means no information. A t-statistic above about 2 means the result
is unlikely to be luck.

| Method | Avg rank correlation | t-statistic | Rebalances where its picks beat hold-all (%) |
| --- | ---: | ---: | ---: |
| Momentum (12-1 month) | +0.005 | +1.22 | 52 |
| Momentum (NSE index style) | +0.005 | +1.12 | 52 |
| Low volatility (12 month) | +0.023 | +3.93 | 45 |
