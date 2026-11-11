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
| 4 | Paper trading with OpenAlgo Analyzer mode on live Upstox prices | On hold: nothing has earned it yet |
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
