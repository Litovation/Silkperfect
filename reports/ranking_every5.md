# Ranking test

- Period: 10 Feb 2021 to 09 Nov 2026, 286 rebalances
- Every 5 trading day(s): take the 200 most liquid NSE stocks (no ETFs), buy the top 20 by score in equal amounts at the next open
- Starting money Rs 10,000,000; full Indian delivery costs on every trade
- The bar: holding all 200 equally, which returned 14.3% a year
- Last 252 trading days (from 03 Nov 2025) are shown separately as a check on recent behaviour

## Returns after costs

| Method | Per year (%) | vs hold-all (pts) | Worst drop (%) | Sharpe | Before holdout, per year (%) | Holdout return (%) | Turnover per rebalance (%) | Costs (Rs) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hold all equally | 14.3 | +0.0 | -24.4 | 0.86 | 18.4 | -3.6 | 3 | 1,973,714 |
| Momentum (12-1 month) | 24.8 | +10.6 | -37.1 | 0.99 | 31.5 | -2.3 | 15 | 3,902,105 |
| Momentum (NSE index style) | 23.2 | +8.9 | -33.8 | 1.00 | 29.4 | -2.1 | 18 | 4,858,689 |
| Low volatility (12 month) | 9.3 | -5.0 | -18.9 | 0.82 | 12.7 | -5.4 | 7 | 1,045,895 |
| Qlib Alpha158 + LightGBM | 2.3 | -11.9 | -35.1 | 0.22 | 8.0 | -21.8 | 53 | 6,467,215 |
| Nifty 50 index (no costs, no dividends) | 9.2 | -5.1 | -17.2 | 0.71 | n/a | n/a | 0 | 0 |

## Does the ranking carry information?

Rank correlation compares each method's ordering of the stocks with how they then
performed. Zero means no information. A t-statistic above about 2 means the result
is unlikely to be luck.

| Method | Avg rank correlation | t-statistic | Rebalances where its picks beat hold-all (%) |
| --- | ---: | ---: | ---: |
| Momentum (12-1 month) | +0.018 | +1.84 | 57 |
| Momentum (NSE index style) | +0.015 | +1.58 | 57 |
| Low volatility (12 month) | +0.019 | +1.32 | 47 |
| Qlib Alpha158 + LightGBM | +0.013 | +1.88 | 48 |
