# Plan

Last updated: 11 Nov 2026

## Goal

Find out whether TimesFM 2.5 forecasts of NSE stocks are good enough to trade,
by testing them against simple baselines with real costs, then paper trading,
and only then real money. No crypto.

The test TimesFM must pass: beat "the price stays where it is" on forecast
accuracy, and beat buy-and-hold after costs. Most forecasting models fail the
first one on stock prices, so that is checked before anything else.

## Phases

| Phase | What | Status |
| --- | --- | --- |
| 1 | Data pull, price adjustment, cost model, baselines, scoreboard | Done |
| 2 | TimesFM 2.5 added as one more forecaster on the same scoreboard | Done: it failed the test (see below) |
| 3 | Streamlit dashboard: forecast against actual, scoreboard | Done (`streamlit run dashboard.py`) |
| 4 | Paper trading | Built into the dashboard as a pretend account on NSE closing prices. OpenAlgo and Upstox are only needed for real orders. |
| 5 | Real money through Upstox orders via OpenAlgo | Only if paper passes |

## What changed from the first plan, and why

1. **One NSE file instead of two bhavcopy formats.** NSE's daily "PR" bundle
   has kept the same layout from 2019 to today and holds prices, index values
   and corporate actions in one zip. It is now the main source. The two
   bhavcopy formats (old, and UDiFF from 2024) are still parsed, but only as
   an independent cross-check.
2. **Split and bonus adjustment comes from NSE's own corporate-actions file.**
   The bhavcopy does not flag splits: on a 10-for-1 split day its
   "previous close" is still the old price. Each split or bonus is applied
   only if the price really moved by that ratio on the ex-date.
3. **A "no change" baseline was added.** Buy-and-hold and moving average are
   trading baselines. A forecast needs a forecast baseline.
4. **Two scoreboards, not one.** Forecast accuracy and after-cost trading
   results are separate tables, because a forecast is not a strategy.
5. **A fixed rule turns any forecast into trades.** Buy when the forecast gain
   over 5 days exceeds the round-trip cost; sell when the forecast turns
   negative. Long or cash only, since cash-market shares cannot be shorted
   overnight.
6. **No daily Upstox login for data.** Upstox's Analytics Token is read-only
   and lasts a year. The daily login only matters for paper and live orders.
7. **Data is checksummed.** `data/manifest.csv` records the SHA-256 of every
   downloaded file, so a result can be tied to the exact data behind it.
8. **TimesFM 2.5 specifically.** TimesFM 3.0 weights are under a
   non-commercial licence.

## Tools

| Job | Tool | Note |
| --- | --- | --- |
| History | NSE PR bundle | Free, no login |
| 5-minute prices | Yahoo Finance chart data | Free and unofficial; last 60 trading days only |
| Cross-check | NSE bhavcopy (old and UDiFF) | 12 random days, 23,392 prices, 0 differences |
| Live and intraday prices | Upstox API, Analytics Token | Phase 2 onward |
| Forecasting | TimesFM 2.5 | Apache-2.0 |
| Backtests | backtesting.py | AGPL-3.0: fine for own use, matters only if the software is given to others |
| Dashboard | Streamlit | Phase 3 |
| Paper trading | OpenAlgo Analyzer mode | Rs 1 crore virtual capital; an order simulator, so fills will look better than live |
| Live orders | Upstox via OpenAlgo | Needs a whitelisted static IP and daily two-factor login |

## Rules that keep the test fair

- A forecaster is handed prices up to the forecast date and nothing later.
  A test changes the future and checks earlier forecasts do not move.
- A signal seen at the close is traded at the next day's open.
- Every strategy is judged on the same period with the same capital and costs.
- Costs are the Indian delivery set: brokerage, STT, exchange charge, SEBI
  fee, stamp duty, GST, depository charge, plus 5 basis points of slippage per side.
- Once TimesFM settings are being tuned, the last 12 months are held back and
  looked at once.

## First results (5 Jan 2021 to 9 Nov 2026, 11 symbols)

Full tables: [reports/scoreboard.md](../reports/scoreboard.md).

- No baseline forecaster beats "no change". Drift is slightly worse
  (skill -0.007) and the moving-average forecast is much worse (-0.51).
- After costs, buy-and-hold returned 12.9% a year. The moving-average
  crossover returned 3.6% and paid Rs 3.4 lakh in costs on Rs 55 lakh.
- So the bars for TimesFM are: skill above 0, and more than 12.9% a year
  after costs or a clearly smaller worst drop.

## TimesFM 2.5 result (same period, same 11 symbols)

Run as published, with no training on our data and all settings fixed before
the run: 5-day horizon, 1,024 days of context, daily adjusted closes.

- Forecast skill against "no change": -0.016. Worse than no change in every
  year from 2021 to 2026 and on all 11 symbols. Direction right 50.1% of the
  time, which is a coin toss.
- Trading rule after costs: -1.2% a year, against 12.9% for buy-and-hold.
  606 trades cost Rs 9.5 lakh on Rs 55 lakh of capital.

Verdict: in this form TimesFM 2.5 does not forecast these stocks well enough
to trade. It does not go to paper trading.

What must not be done next: changing horizons, thresholds or stock lists
until a good number appears. With enough tries something always looks good
on past data and then fails live.

Tests that are still fair, each to be decided in advance and judged with the
last 12 months held back:

1. Ranking instead of timing: forecast a few hundred stocks and hold the top
   few, judged against holding them all equally.
2. Using TimesFM's uncertainty range to size positions rather than to pick
   direction.
3. A longer horizon (20 days), where costs matter less.

## Ranking test result (10 Feb 2021 to 9 Nov 2026)

From the 200 most traded NSE shares (rebuilt each month from that day's data,
no ETFs), each method buys its top 20 monthly with Rs 1 crore. The bar is
holding all 200 equally: 16.1% a year. Full table: [reports/ranking.md](../reports/ranking.md).

| Method | Per year | Strength (t, needs 2) | Last 12 months |
| --- | ---: | ---: | ---: |
| Momentum (12-1 month) | 25.8% | 1.73 | -2.7% |
| Low volatility | 10.4% | 0.41 | -2.7% |
| TimesFM 2.5 | 13.0% | 0.99 | -10.2% |
| Chronos-Bolt | 15.4% | -0.08 | -13.1% |
| Kronos (small, 5-day bars) | 12.8% | -1.42 | +1.6% |
| Qlib Alpha158 + LightGBM | 13.3% | -0.45 | +4.6% |
| Momentum (NSE index style) | 26.6% | 1.51 | -1.4% |
| Hold all 200 | 16.1% | | -2.7% |

- TimesFM, Chronos and Kronos all fail as rankers: below hold-all, no reliable
  pattern. Kronos's ranking leaned slightly the wrong way.
- Momentum is the only method ahead, but its strength is under 2, its worst
  drop is deeper (-32%), and it added nothing in the last 12 months.
- Kronos was run with its small model on 5-day bars, 5 averaged draws, because
  daily bars take over 9 hours without a graphics card. The larger model on
  daily bars is untested.

## Day-trade rule test (14 Aug to 11 Nov 2026)

The opening-range-breakout rule from the day-trader-skill pack
(github.com/jakeschincariol/day-trader-skill, MIT): buy the first 5-minute
close above the first 15 minutes' high, stop at the middle of that range,
target the same distance above, out before the close. Its own example
(Tesla, 19 Oct 2026) was reproduced exactly from its test data first. Then
the rule was run unchanged on the 200 most traded NSE shares with NSE hours
and Indian intraday costs. Full table: [reports/daytrade.md](../reports/daytrade.md).

- 6,529 trades over 58 days. Hit the target 42.5%, hit the stop 42.3%.
- Average result before costs: -0.001 R, which is a coin toss.
- Costs are 0.43 R a trade, because the stop sits only 0.76% away and a
  round trip costs about 0.25%. After costs: -0.43 R a trade, and only 3% of
  days made money.
- Verdict: no edge before costs, a steady loss after them.
- Limits: 60 days is all Yahoo's free 5-minute data offers, and stops are
  assumed to fill exactly at their price.

### Every variant of the day-trade rule

All 48 settings the skill offers were run: buying or shorting, 15- or
30-minute range, stop at the middle or far edge, targets of 1, 2 or 3 times
the risk, with and without a volume filter. The days were split in half so a
lucky first half could be caught by the second. Table:
[reports/daytrade_variants.md](../reports/daytrade_variants.md).

- 0 of 48 made money after costs, in either half or overall.
- The best lost 0.12 R a trade. Shorting showed about +0.1 R before costs
  in a falling stretch, less than half of what costs take.

## Trading more often (same test, Rs 1 crore)

| Swap | Hold all 200 | Momentum (12-1) | Momentum (NSE style) | Qlib recipe | Momentum's costs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Monthly | 16.1% | 25.8% | 26.6% | 13.3% | Rs 18.7 lakh |
| Weekly | 14.3% | 24.8% | 23.2% | 2.3% | Rs 39.0 lakh |
| Daily | 8.5% | 20.2% | 16.8% | not run | Rs 86.5 lakh |

Swapping more often lowers every result and deepens the worst drop (momentum:
-32% monthly, -37% weekly, -40% daily). The same picks cost more to hold.
Microsoft Qlib's recipe (its 158 features and LightGBM settings, computed
on NSE data and retrained walk-forward) is below hold-all at both speeds.
Qlib's settings were tuned for Chinese shares and not re-tuned here.

## Chinese rule-based methods (10 Feb 2021 to 9 Nov 2026)

The 200 most traded shares as of the start, Rs 5 lakh each, each rule
deciding when to hold a share and when to sit in cash. The bar is holding
the same shares throughout. Settings are the published defaults.
Table: [reports/chinese_methods.md](../reports/chinese_methods.md).

| Rule | Per year | Worst drop | Shares where it beat holding |
| --- | ---: | ---: | ---: |
| Hold the same shares | 15.7% | -21.4% | |
| Chan theory, third-class points only (czsc) | 11.7% | -13.8% | 28% |
| RSRS timing | 5.7% | -11.4% | 16% |
| Chan theory, all points (czsc) | 4.4% | -13.7% | 18% |
| Chan theory, first-class points only (czsc) | 4.1% | -10.9% | 25% |
| Turtle breakout | 3.9% | -12.6% | 16% |

Every rule earned less than holding. All of them fell less at the worst,
because they sit in cash about half the time. Chan theory's third-class
points are the least bad: about three quarters of the return for two thirds
of the drop. One-month reversal, the pattern reported for Chinese shares,
returned 7.7% a year against 16.1% for holding all 200: on NSE the winners
kept winning rather than the losers bouncing.

## Momentum under different definitions (Rs 1 crore, same period)

To check that momentum's lead is not an accident of one setting, it was run
two ways (12-1 month return, and the 6- and 12-month volatility-adjusted
score NSE's Nifty200 Momentum 30 index uses) across five holding and
swap schedules.

| Hold | Swap | Hold all 200 | Momentum (12-1) | Momentum (NSE style) |
| --- | --- | ---: | ---: | ---: |
| 20 | monthly | 16.1% | 25.8% | 26.6% |
| 30 | monthly | 16.1% | 24.4% | 24.1% |
| 20 | 3 months | 17.0% | 26.4% | 25.0% |
| 30 | 6 months | 17.3% | 25.4% | 26.4% |
| 10 | monthly | 16.1% | 26.3% | 26.8% |

Ahead in all ten cases by 7 to 11 points a year, so the lead does not hinge
on one setting. It is still one 5.7-year period with a strong run in mid-size
shares, the worst drops are 26% to 41%, and the rank strength stays under 2.

## Small money (Rs 10,000)

Each order costs roughly Rs 20 to Rs 45 whatever its size, and only whole
shares can be bought. Momentum with Rs 10,000 on past prices:

| Hold | Swap | Rs 10,000 became | Fees paid |
| --- | --- | ---: | ---: |
| 5 shares | monthly | 5,885 | 12,400 |
| 5 shares | every 3 months | 28,656 | 6,875 |
| 3 shares | every 3 months | 17,591 | 4,525 |
| 10 shares | every 3 months | 15,817 | 10,804 |
| One Nifty 50 fund, bought once | never | 17,514 | about 30 |

The spread between rows is the finding: at this size the outcome depends more
on fees and on which few shares happened to be affordable than on the method.
For small sums a single low-cost fund is the sound comparison, and momentum
funds exist that follow the same idea in one purchase.

## Known gaps

- **Rights issues are not adjusted.** Three are flagged in the current
  universe (Bharti Airtel 2019 and 2021, Reliance 2020). Fix by adding a
  factor to `config/corporate_actions_manual.csv`.
- **Demerger factors are estimates** taken from the ex-date opening price
  (ITC 2025, Reliance 2023).
- **Brokerage and depository charge are defaults** (Rs 20 an order, Rs 20 per
  sell). Check them against a real Upstox contract note.
- **The universe is today's large caps**, picked with hindsight. That flatters
  buy-and-hold. A point-in-time universe is possible later, since the price
  table holds every NSE stock.
- **Forecasts overlap.** A 5-day forecast is made every day, so the 15,906
  forecasts are not independent, and small skill differences need care.
- **Cash earns nothing** in the backtest, which is slightly unfair to
  strategies that sit in cash.
- **backtesting.py details:** it starts on the second day, and a position still
  open at the end is closed at the last day's open. Buy and sell costs are
  averaged across the two legs of a trade; the total per round trip is right.
- **Upstox:** whether data-only use needs a static IP is not confirmed by
  Upstox. Other brokers say it applies to orders only.

## Needed from the owner

- Create an API app in the Upstox developer console and generate an Analytics
  Token there. Keep the key, secret and token private: never in chat, never
  in this repository.
- Send one recent Upstox contract note's charge lines (no account details) so
  the cost defaults can be checked.
