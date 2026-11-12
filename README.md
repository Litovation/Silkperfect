# Silkperfect

Tests whether price forecasts of NSE stocks are good enough to trade.
Built so far: free NSE data, split/bonus/dividend adjustment, Indian trading
costs, baseline strategies, TimesFM 2.5 and a scoreboard. The plan and what comes
next are in [docs/PLAN.md](docs/PLAN.md). The latest results are in
[reports/scoreboard.md](reports/scoreboard.md).

## Run it

```bash
pip install -r requirements.txt
```

```bash
python -m silkperfect run
```

`run` does three steps, which can also be run one at a time:

| Command | What it does | Time |
| --- | --- | --- |
| `python -m silkperfect fetch` | Downloads NSE daily files from 2019 to today into `data/raw/` (about 730 MB). Later runs only fetch new days. | 5 min first time |
| `python -m silkperfect build` | Builds adjusted prices for every NSE stock into `data/processed/prices.parquet` | 4 min |
| `python -m silkperfect scoreboard` | Runs the baselines and writes `reports/scoreboard.md` | seconds |

To include TimesFM 2.5 on the scoreboard, install its packages once (a large
download: PyTorch plus about 900 MB of model weights on first use):

```bash
pip install -r requirements-timesfm.txt
```

```bash
python -m silkperfect scoreboard --timesfm
```

The first TimesFM run takes about 2 to 3 minutes per symbol on a laptop
without a graphics card. Forecasts are saved under `data/processed/forecasts/`,
so later runs take seconds unless the prices or settings change.

## Dashboard

One command updates the prices and opens the dashboard in your browser:

```bash
python -m silkperfect dashboard
```

Stop it with Ctrl+C in the terminal. It has three pages:

- **Simple view:** in plain words, what a sum of money (Rs 10,000 by default)
  would have become under a plan, next to a Nifty 50 fund and a bank deposit,
  with the fees and the worst fall. It also runs a **pretend account**: press
  one button and the plan is followed with pretend money from today onward.
  Run the command again on later days to see it move.
- **Pick-the-best test:** the ranking test results for every method.
- **Single-share forecast test:** the detailed forecast scoreboard.

How shares are picked is a dropdown: momentum, steadiest shares, and TimesFM
or Chronos when their packages are installed. Nothing in the dashboard places
a real order.

## Chinese rule-based methods

```bash
pip install -r requirements-chinese.txt
```

```bash
python -m silkperfect chinese
```

Tests Chan theory (缠论) buy and sell points from
[czsc](https://github.com/waditu/czsc) (Apache-2.0), RSRS timing, the turtle
breakout and one-month reversal on the 200 most traded NSE shares, against
simply holding the same shares. Results go to `reports/chinese_methods.md`.

## Day-trade rule test

```bash
python -m silkperfect daytrade
```

Tests the opening-range-breakout day trade from the
[day-trader-skill](https://github.com/jakeschincariol/day-trader-skill) pack
(MIT) on the 200 most traded NSE shares, using Yahoo Finance 5-minute bars
(the last 60 trading days, which is all Yahoo offers) and Indian intraday
costs. Results go to `reports/daytrade.md` and the dashboard's
"Day-trade rule test" page.

## Using a graphics card

TimesFM, Chronos and Kronos use an NVIDIA graphics card automatically when
PyTorch can see one, and are many times faster with it. Check with:

```bash
python -m silkperfect device
```

On Windows, `pip install torch` usually installs a processor-only build. To
switch to the graphics build:

```bash
pip uninstall -y torch
```

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

## Running it live (pretend money)

"Live" here means a pretend account that updates every day on real NSE
prices. No real order is ever placed.

Start the account once (Rs 10,000, NSE-style momentum, 5 shares, swapped
every 63 market days unless you pass other values):

```bash
python -m silkperfect paper start --amount 10000
```

Then once a day after about 7 pm, when NSE has published the day's prices:

```bash
python -m silkperfect daily
```

That downloads the new prices, rebuilds the table, updates the account and
writes `reports/live.md`. To have Windows do it automatically every evening,
run this once (adjust the path if the project is elsewhere):

```bash
schtasks /Create /SC DAILY /ST 19:30 /TN "Silkperfect daily" /TR "C:\Users\krish\Silkperfect\scripts\run_daily.bat"
```

`python -m silkperfect paper status` shows the account; `paper close` ends it.

## Ranking test

```bash
python -m silkperfect rank
```

Add `--models` to include TimesFM and Chronos, `--kronos` for Kronos (about
2 hours without a graphics card) and `--qlib` for Microsoft Qlib's Alpha158 +
LightGBM recipe (about 5 minutes). All are saved after the first run.
`--every 5` swaps weekly and `--every 1` daily instead of monthly. Results go to `reports/ranking.md`.

Optional check against NSE's official bhavcopy files:

```bash
python -m silkperfect crosscheck
```

Tests:

```bash
python -m pytest -q
```

## Change what is tested

- **Stocks:** edit `config/universe.txt`, one NSE symbol per line.
- **Horizon, history, capital:** `python -m silkperfect scoreboard --horizon 5 --min-history 500 --capital 500000`
- **Costs:** defaults are in `silkperfect/costs.py`.
- **A missed split, rights issue or demerger:** add a line to
  `config/corporate_actions_manual.csv` (`symbol,ex_date,factor,note`), then
  run `build` again. The factor is what earlier prices are multiplied by,
  for example 0.5 for a 1:1 bonus.

## How it fits together

| File | Job |
| --- | --- |
| `silkperfect/nse.py` | Downloads files, records checksums in `data/manifest.csv` |
| `silkperfect/parse.py` | Reads the NSE PR bundle and both bhavcopy formats |
| `silkperfect/corporate_actions.py` | Turns NSE corporate-action text into adjustment factors |
| `silkperfect/dataset.py` | Builds and loads the adjusted price table |
| `silkperfect/costs.py` | Indian delivery trading costs |
| `silkperfect/forecasters.py` | No change, drift, moving average, TimesFM 2.5 |
| `silkperfect/walkforward.py` | Forecasts day by day using only past data, and scores them |
| `silkperfect/backtest.py` | Runs buy/sell signals through backtesting.py with costs |
| `silkperfect/scoreboard.py` | Puts it together and writes the report |
| `silkperfect/ranking.py` | Pick-the-best test on the 200 most traded shares |
| `silkperfect/paper.py` | Plans in plain terms and the pretend account |
| `silkperfect/daytrade.py` | Opening-range-breakout day-trade test on 5-minute bars |
| `silkperfect/kronos_signal.py` | Kronos as a share-picking method |
| `silkperfect/chinese.py` | Chan theory (czsc), RSRS, turtle and reversal rules |
| `silkperfect/qlib_signal.py` | Qlib's 158 features and LightGBM model as a share-picking method |
| `dashboard.py` | Streamlit dashboard |

Downloaded data is not stored in git. `data/manifest.csv` lists the SHA-256
of every file used, and `build` refuses to run if a file no longer matches.

## Not financial advice

This is a research tool. Backtest results do not predict future returns.
