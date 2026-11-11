# Silkperfect

Tests whether price forecasts of NSE stocks are good enough to trade.
Phase 1 is built: free NSE data, split/bonus/dividend adjustment, Indian
trading costs, baseline strategies and a scoreboard. The plan and what comes
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
| `silkperfect/forecasters.py` | No change, drift, moving average. TimesFM goes here. |
| `silkperfect/walkforward.py` | Forecasts day by day using only past data, and scores them |
| `silkperfect/backtest.py` | Runs buy/sell signals through backtesting.py with costs |
| `silkperfect/scoreboard.py` | Puts it together and writes the report |

Downloaded data is not stored in git. `data/manifest.csv` lists the SHA-256
of every file used, and `build` refuses to run if a file no longer matches.

## Not financial advice

This is a research tool. Backtest results do not predict future returns.
