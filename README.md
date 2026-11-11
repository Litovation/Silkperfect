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

## Ranking test

```bash
python -m silkperfect rank
```

Add `--models` to include TimesFM and Chronos, and `--kronos` to include
Kronos (about 2 hours without a graphics card; all are saved after the first run). Results go to `reports/ranking.md`.

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
| `dashboard.py` | Streamlit dashboard |

Downloaded data is not stored in git. `data/manifest.csv` lists the SHA-256
of every file used, and `build` refuses to run if a file no longer matches.

## Not financial advice

This is a research tool. Backtest results do not predict future returns.
