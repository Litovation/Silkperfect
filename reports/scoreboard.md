# Scoreboard

- Period judged: 05 Jan 2021 to 09 Nov 2026
- Symbols (11): RELIANCE, HDFCBANK, ICICIBANK, INFY, TCS, ITC, SBIN, BHARTIARTL, LT, HINDUNILVR, NIFTYBEES
- Capital: Rs 500,000 per symbol, long or cash only, whole shares
- Forecast horizon: 5 trading days; first 500 days are history only
- Entry rule: buy when the forecast gain exceeds the round-trip cost (0.34%); sell when the forecast turns negative
- Trades fill at the next day's open. Prices are adjusted for splits, bonuses and dividends.

## Forecast accuracy

Skill above zero means the forecaster beats assuming the price stays where it is.
TimesFM has to clear that bar to be worth trading.

| Forecaster | Forecasts | Avg error (%) | Skill vs no change | Direction right (%) |
| --- | ---: | ---: | ---: | ---: |
| No change | 15,906 | 2.346 | +0.0000 | n/a |
| Drift (250d) | 15,906 | 2.362 | -0.0066 | 51.7 |
| Moving average (20d) | 15,906 | 3.545 | -0.5109 | 50.4 |

## Trading results after costs

| Strategy | Total return (%) | Per year (%) | Worst drop (%) | Sharpe | Trades | Costs (Rs) | Time invested (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Buy and hold | 103.3 | 12.9 | -17.7 | 0.98 | 11 | 26,624 | 100 |
| Moving-average crossover (20/50) | 23.3 | 3.6 | -15.1 | 0.45 | 189 | 340,586 | 59 |
| Forecast rule: No change | 0.0 | 0.0 | 0.0 | n/a | 0 | 0 | 0 |
| Forecast rule: Drift (250d) | 49.7 | 7.1 | -10.9 | 0.75 | 33 | 62,954 | 63 |
| Forecast rule: Moving average (20d) | 15.1 | 2.4 | -12.9 | 0.34 | 763 | 1,400,115 | 48 |
| Nifty 50 index (no costs, no dividends) | 76.4 | 10.2 | -17.2 | 0.76 | 0 | 0 | 100 |

The index row is a reference only: it pays no costs and leaves out dividends,
while the strategies pay full costs and include dividends.

## Data checks

- Dividends applied: 110
- Splits, bonuses and demergers applied: 6
  - HDFCBANK 2019-09-19: FV SPLT FRM RS 2 TO RS 1 (factor 0.5000, applied)
  - HDFCBANK 2025-08-26: BONUS 1:1 (factor 0.5000, applied)
  - ITC 2025-01-06: DEMERGER (factor 0.9460, estimated)
  - NIFTYBEES 2019-12-19: FVSPLT FRM RS 10 TO RS 1 (factor 0.1000, applied)
  - RELIANCE 2023-07-20: DEMERGER (factor 0.9079, estimated)
  - RELIANCE 2024-10-28: BONUS 1:1 (factor 0.5000, applied)
- Events needing a manual look: 3
  - BHARTIARTL 2019-04-23: RIGHTS 19:67@PRM RS 215 (unparsed)
  - BHARTIARTL 2021-09-27: RIGHTS 1:14 @PRM RS 530 (unparsed)
  - RELIANCE 2020-05-13: RIGHTS 1:15 PARTLY PAID (unparsed)
- Unexplained overnight jumps over 30%: 0
