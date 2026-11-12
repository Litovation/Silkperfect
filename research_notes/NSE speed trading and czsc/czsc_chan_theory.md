# czsc (缠中说禅 / Chan theory Python library by zengbin93, repo waditu/czsc) — state as of 12 November 2026

Verification legend used throughout:
- **[P]** primary source read directly this session (repo file fetched from raw.githubusercontent.com, PyPI JSON API, GitHub page).
- **[RUN]** verified by installing `czsc==1.0.2` from PyPI into a clean Python 3.13 virtualenv (Linux x86_64) and running it on a synthetic 1,800-bar daily OHLCV series labelled `RELIANCE.NS`. Synthetic data was a random walk, so the run verifies the API and behaviour, not profitability.
- **[S]** secondary source (search-result summary, forum post, third-party page); not confirmed against the original.

Sources that could NOT be opened from this session (network allow-list): bigquant.com, m.fx361.com. Their content below is from search snippets only.

---

## 1. What exactly does czsc compute? (Chan theory building blocks)

### Takeaway
czsc turns a list of OHLCV bars into: merged bars (包含处理) → fractals (分型, `FX`) → strokes (笔, `BI`) → pivot zones (中枢, `ZS`), then evaluates about 220–246 named "signal functions" on those structures and on ordinary indicators (MACD, MA, BOLL, candlestick patterns). It does **not** build a formal segment (线段) layer: strokes are the base unit, and divergence (背驰) and the three classes of buy/sell points exist only as individual signal functions with the author's own rule definitions, not as one canonical algorithm.

### Cited Findings
- Self-description: "CZSC 是面向缠论分析与量化研究的开源工具：从 K 线出发，识别分型、笔与中枢，组织多周期信号，并连接策略回测与可视化." **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- Core objects exposed at top level: `CZSC`, `FX`, `BI`, `ZS`, `RawBar`, `NewBar`, `BarGenerator`, `Freq`, `Mark`, `Direction`, `Operate`, `Signal`, `Event`, `Position`, `CzscTrader`, `CzscSignals`; helper functions `check_fx`, `check_bi`, `remove_include`, `get_zs_seq`, `is_symmetry_zs`, `create_fake_bis`. All come from the Rust extension `czsc._native`. **[P]** — [czsc/__init__.py](https://raw.githubusercontent.com/waditu/czsc/master/czsc/__init__.py), [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- A `CZSC` object built from daily bars exposes: `bars_raw`, `bars_ubi` (bars of the unfinished stroke), `fx_list` (fractals), `bi_list` (strokes), `finished_bis`, `ubi` / `ubi_fxs` (unfinished stroke), `zs_list` (pivot zones, added in 1.0.1), `signals`, `update(bar)`, `to_plotly`, `to_echarts`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/); `zs_list` addition: [CHANGELOG 1.0.1](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md)
- Each stroke (`BI`) carries: `sdt`, `edt`, `direction` (向上/向下), `high`, `low`, `power` (price range), `power_price`, `power_volume`, `power_snr`, `length` (bar count), `change`, `slope`, `angle`, `rsq`, `SNR`, `fx_a`, `fx_b` (start/end fractal), `fxs`, `bars`, `raw_bars`, `fake_bis`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Each pivot zone (`ZS`) carries: `bis` (the strokes forming it), `zg` (upper edge), `zd` (lower edge), `zz` (middle), `gg` (highest high), `dd` (lowest low), `sdt`, `edt`, `sdir`, `edir`, `is_valid`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Stroke rule parameters: environment variable `CZSC_MIN_BI_LEN` (minimum stroke length, default 6) and `CZSC_MAX_BI_NUM` (maximum number of strokes kept, default 50). **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- Before 1.0.1 the `CZSC_MIN_BI_LEN` setting had no effect in the Rust core (the value 6 was hard-coded in `check_bi`); fixed in 1.0.1, which also added `CZSC(bars_raw, max_bi_num=0, min_bi_len=0)` constructor arguments (0 means "read env var, else default 50 / 6"). **[P]** — [CHANGELOG 1.0.1](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md)
- **Only the last 50 strokes are kept by default.** On 1,800 synthetic daily bars, `CZSC(bars)` returned 50 strokes and 143 fractals; `CZSC(bars, max_bi_num=10000)` returned 163 strokes. 7 pivot zones were found from the 50 kept strokes. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Segments (线段): the author's FAQ says czsc uses the stroke as its base level and does not build segments as a separate layer; he says segment content "并没有被丢弃" because segment endings show up in multi-stroke pattern signals, and that a 5-minute stroke strategy is roughly (not strictly) equivalent to a 1-minute segment strategy. **[P, via page summary]** — [Discussion #32 FAQ](https://github.com/waditu/czsc/discussions/32)
- In the installed 1.0.2 package the string "线段" appears in only one Python file, `aphorism.py` (quotations), i.e. there is no Python-side segment class. The catalogue has 7 signals in an `xl` namespace, but the one inspected (`xl_bar_position_V240328`) is a bar-position signal, not a segment builder. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/). Note: README case-study table text mentions "分型/笔/线段/中枢" for the charting example — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md); this conflicts with the FAQ and the object model (no segment object found).
- Divergence (背驰): the author's FAQ says czsc measures stroke strength by the stroke's price range (high minus low) rather than MACD area, for speed, and that results were "essentially the same" as MACD. **[P, via page summary]** — [Discussion #32 FAQ](https://github.com/waditu/czsc/discussions/32). Separate MACD-based divergence signals also exist: `tas_macd_bc_V221201`, `tas_macd_bc_V230803`, `tas_macd_bc_V230804`, `tas_macd_bc_V240307` (柱子背驰), `tas_macd_bc_ubi_V230804`, `tas_boll_bc_V221118`, `zdy_macd_bc_V230422` (MACD 面积背驰). **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Third buy point: the FAQ describes 三买 as a special five-stroke pattern; one factor takes only the first third-buy of an up-move to raise the win rate. **[P, via page summary]** — [Discussion #32 FAQ](https://github.com/waditu/czsc/discussions/32)
- The FAQ states the basic stroke needs "至少有7根无包含K线" (older wording); current default is `min_bi_len=6`. **[P]** — [Discussion #32 FAQ](https://github.com/waditu/czsc/discussions/32); [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- Original Chan theory material is the Sina blog of 缠中说禅 (http://blog.sina.com.cn/chzhshch), linked from the README with mirror sites. **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)

### Inferences
Plain-terms explanation of the building blocks (standard Chan theory definitions; these are background knowledge, not re-fetched from the original blog this session, mapped onto the czsc objects verified above):
- **包含处理 (bar merging)**: when one bar's high-low range sits inside its neighbour's, the two are merged into one `NewBar`, so every remaining bar clearly steps up or down. `remove_include` does this.
- **分型 (fractal, `FX`)**: three merged bars where the middle one has the highest high and highest low (top fractal, 顶分型, `Mark.G`) or the lowest low and lowest high (bottom fractal, 底分型, `Mark.D`). A local turning-point candidate.
- **笔 (stroke, `BI`)**: a move joining a top fractal to a bottom fractal (down stroke) or the reverse (up stroke), with a minimum number of merged bars between them (czsc default 6). Strokes alternate up/down. The latest stroke is provisional (`ubi`) and can be extended or redrawn as new bars arrive (`last_bi_extend`).
- **线段 (segment)**: in the original theory, at least three overlapping strokes form a segment, the next level up. czsc skips this layer and works with strokes directly.
- **中枢 (pivot zone, `ZS`)**: the price range where at least three consecutive strokes overlap. `zg`/`zd` are the upper/lower edges of the overlap. It marks a consolidation area; moves leaving it are trends.
- **背驰 (divergence)**: a new push away from a pivot zone makes a new price extreme but with less "force" than the previous push in the same direction. czsc measures force by stroke price range, or by MACD area/bars in the `tas_macd_bc_*` signals.
- **一类买卖点 (first-class buy/sell point)**: the end of a trend where the last leg diverges — a reversal bet at a new low (buy) or new high (sell). czsc: `cxt_first_buy_V221126`, `cxt_first_sell_V221126`.
- **二类买卖点 (second-class)**: after a first-class point, the first pullback that does not make a new low (buy) / first bounce that does not make a new high (sell). czsc: `cxt_second_bs_V230320`, `cxt_second_bs_V240524`.
- **三类买卖点 (third-class)**: price leaves a pivot zone and the first pullback does not re-enter the zone (buy above `zg`, sell below `zd`) — a trend-continuation entry. czsc: `cxt_third_buy_V230228`, `cxt_third_bs_V230318`, `cxt_third_bs_V230319`.
- Because czsc drops the segment layer and the level-recursion of the original theory, and each buy/sell point is one author-chosen coding among several versions (see the dated `V2xxxxx` suffixes), "czsc signals" are one interpretation of Chan theory, not the theory itself. Results cannot be transferred from other Chan implementations (for example chan.py or TradingView scripts, which offer several alternative stroke definitions) — [search result on implementations, S](https://cn.tradingview.com/script/4V66pXJ9-ChanLun-Pro).
- The default cap of 50 strokes means structure objects (`bi_list`, `zs_list`) are a rolling recent window. For historical labelling of 2019–2026 one must either pass a large `max_bi_num` or use the bar-by-bar signal generator.

### Gaps
- The exact rule text inside each Rust signal function (for example what stroke counts and price conditions define `cxt_first_buy_V221126`) was not read; the Rust sources are in `crates/czsc-signals/src/` in the repo and were not opened. The author's Feishu wiki "信号函数模块深入介绍" requires a browser session and was not read.
- Whether the charting layer draws any "segment" line (the README table mentions 线段) was not tested.

---

## 2. Licence, latest PyPI version, Python requirement, heavy dependencies

### Takeaway
The upstream repository is Apache License 2.0 (LICENSE file: "Copyright [2025] [zengbin93]"). The latest PyPI release is **czsc 1.0.2, uploaded 16 October 2026**, requiring Python ≥ 3.10; it ships as a ~19–23 MB prebuilt Rust (PyO3, abi3) wheel and pulls in pandas, numpy, polars, pyarrow, scipy, statsmodels, plotly and the author's `wbt` backtester.

### Cited Findings
- LICENSE at master is Apache License, Version 2.0, with the line "Copyright [2025] [zengbin93]". **[P]** — [LICENSE](https://raw.githubusercontent.com/waditu/czsc/master/LICENSE)
- `pyproject.toml`: `license = "Apache-2.0"`, classifier "License :: OSI Approved :: Apache Software License", `requires-python = ">=3.10"`, classifiers for Python 3.10–3.13, build backend maturin. **[P]** — [pyproject.toml](https://raw.githubusercontent.com/waditu/czsc/master/pyproject.toml)
- PyPI JSON API: latest version 1.0.2, `requires_python >=3.10`, `license_expression Apache-2.0`. Upload times: 1.0.2 on 2026-10-16; 1.0.1 on 2026-08-09; 1.0.0rc8 on 2026-05-29; 1.0.0rc7 on 2026-05-20; 1.0.0rc5 on 2026-05-18; 0.10.12 on 2026-03-09; 0.10.11 on 2026-02-24. 155 releases in total; the first on PyPI is 0.3.4 (2020-06-02). No final "1.0.0" appears in the release list — the series goes rc8 → 1.0.1. **[P]** — [PyPI JSON](https://pypi.org/pypi/czsc/json)
- Wheels for 1.0.2: `cp310-abi3` for macOS x86_64 and arm64, manylinux2014 x86_64 and aarch64, musllinux x86_64, Windows amd64; sizes 18.9–23.2 MB; sdist 0.59 MB. No Rust toolchain is needed for a wheel install. **[P]** — [PyPI JSON](https://pypi.org/pypi/czsc/json), [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- Runtime dependencies (pyproject): pandas>=1.0.0, numpy, pyarrow, openpyxl, polars>=0.20.0, requests>=2.24.0, urllib3>=2.8.0, requests_toolbelt, scipy, statsmodels, wbt>=0.2.1, plotly, tqdm>=4.66.4, loguru, dill, tenacity, typer>=0.12.0. scikit-learn was removed on 2026-05-17. TA-Lib is **not** a runtime dependency (talib-rs is test-only). **[P]** — [pyproject.toml](https://raw.githubusercontent.com/waditu/czsc/master/pyproject.toml)
- Clean install on Python 3.13.18 resolved to: czsc 1.0.2, wbt 0.9.2, pandas 3.1.1, numpy 2.5.4, polars 2.1.0, pyarrow 26.0.1, scipy 1.18.1, statsmodels 0.15.0, plotly 7.1.0. Import and all tests below worked with these. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Architecture: "CZSC 1.0 采用 Rust + Python 混合架构"; Rust workspace of 9 crates (`czsc`, `czsc-core`, `czsc-derive`, `czsc-signals`, `czsc-trader`, `czsc-utils`, `czsc-ta`, `czsc-signal-macros`, `czsc-python`). **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- Repository page: about 6.6k stars, 1.8k forks, 1,736 commits, default branch `master`, description "缠中说禅技术分析工具；缠论；股票；期货；Quant；量化交易". **[P, via page summary]** — [github.com/waditu/czsc](https://github.com/waditu/czsc)
- Author metadata: `zengbin93`, email in pyproject; `__date__ = "20260520"` in `__init__.py`. **[P]** — [czsc/__init__.py](https://raw.githubusercontent.com/waditu/czsc/master/czsc/__init__.py)
- The README carries a promotional banner and invite code for the author's commercial "胜可知" AI quant research platform (quant.shengkezhi.com). **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- The CHANGELOG on master still labels 1.0.2 "待发布" (pending) although PyPI shows it uploaded on 2026-10-16. **[P]** — [CHANGELOG](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md); [PyPI JSON](https://pypi.org/pypi/czsc/json)

### Inferences
- Apache-2.0 permits commercial use, modification and redistribution with notice and patent grant; there is no copyleft obligation for a private trading test.
- "Heavy" in practice means: a ~20 MB compiled wheel plus polars, pyarrow, scipy, statsmodels and plotly (several hundred MB installed). No C TA-Lib build is required, which removes the historical installation pain point.
- The licence of older releases (0.9.x and earlier) was not checked; only the current master LICENSE and current PyPI metadata were read.

### Gaps
- `github.com/zengbin93/czsc` returned HTTP 403 through this session's proxy, so whether it redirects to `waditu/czsc` was not confirmed. All PyPI project URLs point to `waditu/czsc` ([PyPI JSON](https://pypi.org/pypi/czsc/json)).
- GitHub Releases page and tag dates were not read (GitHub API access to this repo was denied in this session); dates above are PyPI upload dates.
- Licence history (whether it was MIT or other before 2025) not verified.

---

## 3. Minimal code: pandas daily bars → strokes and buy/sell point signals; import paths; API changes

### Takeaway
In czsc 1.0.2 everything is imported from the top-level `czsc` package (backed by `czsc._native`); the old module paths `czsc.signals`, `czsc.objects`, `czsc.analyze`, `czsc.enum` no longer exist. The code below was run end-to-end on a daily DataFrame in this session; note that the README's own signal-generation snippet does not run as written in 1.0.2.

### Cited Findings

**Input format**
- `format_standard_kline(df, freq)` requires exactly these eight columns: `dt`, `symbol`, `open`, `close`, `high`, `low`, `vol`, `amount`; missing any raises `ValueError`. `freq` is a `Freq` enum or a Chinese string such as `"日线"`; the default `Freq.F5` is a placeholder, so pass the frequency explicitly. It returns `list[RawBar]`. **[RUN, from the function docstring]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `RawBar(symbol, dt, freq, open, close, high, low, vol, amount, id=0)`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `Freq` members: `Tick, F1, F2, F3, F4, F5, F6, F10, F12, F15, F20, F30, F60, F120, F240, F360, D, W, M, S, Y`; `Freq.D.value == "日线"`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Since 1.0.0-rc.8: timezone-aware datetimes are rejected (`ValueError`; strip with `df['dt'].dt.tz_localize(None)`), and NaN in OHLCV raises an error in `BarGenerator` / trader updates. **[P]** — [CHANGELOG 1.0.0-rc.8](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md)

**Verified minimal script (ran successfully on czsc 1.0.2)** **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)

```python
import pandas as pd
from czsc import (CZSC, Freq, format_standard_kline, generate_czsc_signals,
                  get_signals_config, Position, Event, BarGenerator,
                  CzscTrader, WeightBacktest)

# df: one symbol, daily rows, tz-naive 'dt', no NaN
# required columns: symbol, dt, open, close, high, low, vol, amount
df["amount"] = df["vol"] * df["close"]          # if turnover is not available
bars = format_standard_kline(df, freq=Freq.D)   # list[RawBar]

# 1) structure: fractals, strokes, pivot zones
c = CZSC(bars, max_bi_num=10000)                # default keeps only the last 50 strokes
for bi in c.bi_list:
    print(bi.sdt, bi.edt, bi.direction, bi.high, bi.low, bi.power, bi.length)
for zs in c.zs_list:
    print(zs.sdt, zs.edt, zs.zg, zs.zd)

# 2) bar-by-bar signal table (one row per daily bar, one column per signal)
cfg = [
    {"name": "cxt_first_buy_V221126",  "freq": "日线", "di": 1},
    {"name": "cxt_first_sell_V221126", "freq": "日线", "di": 1},
    {"name": "cxt_second_bs_V240524",  "freq": "日线", "di": 1},
    {"name": "cxt_third_buy_V230228",  "freq": "日线", "di": 1},
    {"name": "cxt_third_bs_V230318",   "freq": "日线", "di": 1},
    {"name": "cxt_bi_status_V230101",  "freq": "日线"},
]
sig = generate_czsc_signals(bars, cfg, sdt="20200101", init_n=300, df=True)
# columns like '日线_D1B_BUY1V221126' with values like '一买_5笔_任意_0' or '其他_任意_任意_0'

# 3) Signal -> Event -> Position -> trader
B1 = "日线_D1B_BUY1V221126_一买_任意_任意_0"
S1 = "日线_D1B_SELL1V221126_一卖_任意_任意_0"
opens = [Event.from_dict(dict(name="一买开多", operate="LO",
                              signals_all=[B1], signals_any=[], signals_not=[]))]
exits = [Event.from_dict(dict(name="一卖平多", operate="LE",
                              signals_all=[S1], signals_any=[], signals_not=[]))]
pos = Position(symbol="RELIANCE.NS", opens=opens, exits=exits,
               interval=0, timeout=100, stop_loss=1000, name="日线一买一卖")

cfg2 = get_signals_config(pos.unique_signals)   # derives [{'name':..., 'freq':'日线', 'di':1}, ...]
bg = BarGenerator(base_freq="日线", freqs=[], max_count=5000)
for b in bars[:300]:
    bg.update(b)                                # warm-up
trader = CzscTrader(bg, [pos], cfg2)
rows = []
for b in bars[300:]:
    trader.on_bar(b)
    rows.append((b.dt, "RELIANCE.NS", trader.positions[0].pos, b.close))

p = trader.positions[0]
print(p.pairs)      # list of round trips: 开仓时间, 平仓时间, 开仓价格, 平仓价格, 盈亏比例 (in BP), 事件序列
print(p.operates)   # list of raw operations: dt, price, op ('LO'/'LE'), op_desc, pos

# 4) cost-aware performance from the position series
w = pd.DataFrame(rows, columns=["dt", "symbol", "weight", "price"])
wb = WeightBacktest(w, digits=1, fee_rate=0.001)   # fee_rate default is 0.0002 per unit turnover
print(wb.stats)     # 年化收益, 夏普比率, 最大回撤, 交易胜率, 单笔盈亏比, 交易次数 ...
```

**Details observed while running it**
- `generate_czsc_signals(bars, signals_config, sdt, init_n, df)`: `signals_config` must be a list of dicts; passing a list of strings raises `ValueError('signals_config 中每个元素必须是 dict')`. The signal `name` is accepted in three spellings: bare (`cxt_first_buy_V221126`), `czsc.signals.cxt_first_buy_V221126`, or `czsc._native.signals.cxt.cxt_first_buy_V221126`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- The README snippet (`signals_seq = ["czsc._native.signals.bar.bar_end_V230331", ...]; generate_czsc_signals(bars, signals_seq)`) therefore fails as written; and `get_signals_config` / `get_signals_freqs` expect full signal strings (for example `"日线_D1B_BUY1V221126_一买_任意_任意_0"`), returning `[]` when given function names. **[P + RUN]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md); [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Signal string format is seven fields joined by underscores: `k1_k2_k3_v1_v2_v3_score` (`Signal` has attributes `k1,k2,k3,v1,v2,v3,score,key,value`); `任意` means "any". Example: `日线_D1B_BUY1V221126_一买_任意_任意_0`. `di` means "the di-th stroke/bar counting back from the latest" (di=1 is the latest). **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `Event(operate, signals_all, signals_any, signals_not, name)`; `Event.from_dict` in 1.0.2 requires `operate` as the enum code — one of `HL, HS, HO, LO, LE, SO, SE` (hold-long, hold-short, hold-other, long-open, long-exit, short-open, short-exit). Passing the Chinese value `"开多"` raised `ValueError` even though `Operate.LO.value == "开多"`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `Position(symbol, opens, exits, interval=0, timeout=1000, stop_loss=1000.0, t0=False, name=None)`. `stop_loss` is in basis points: a test trade closed with reason "平多@1000BP止损" at about −13% (close-to-close gap past the 10% stop). `timeout` is in bars. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `CzscTrader(bg, positions, signals_config, ensemble_method=...)`, methods `on_bar`, `update`, `get_ensemble_pos`, `positions`, `kas` (dict freq → `CZSC`). `CzscSignals(bg, signals_config)` is the signals-only version. `BarGenerator(base_freq, freqs, max_count=2000, market=None)`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `WeightBacktest(data, digits=2, fee_rate=0.0002, n_jobs=1, weight_type='ts', yearly_days=252)` is re-exported from the separate `wbt` package; input columns `dt, symbol, weight, price`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/); [wbt repo](https://github.com/zengbin93/wbt)
- Strategy wrapper: subclass `czsc.CzscStrategyBase`, implement the `positions` property returning a list of `Position`; `signals_config`, `freqs`, `base_freq` are derived automatically; methods `replay`, `backtest`, `save_positions`, `load_positions`. `czsc.CzscJsonStrategy` loads positions from JSON files. Functional entry points: `czsc.run_replay(bars, strategy: dict, res_path=..., sdt=..., opts=...)`, `czsc.run_research`, `czsc.run_optimize_batch`. **[RUN, signatures and docstrings]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- A command-line tool `czsc` is installed with subcommands `analyze` (bars → fractals + strokes), `backtest`, `bench`, `schema`, `signals list` / `signals doc <name>`, `research`, `data`, `plot`. Example: `czsc signals doc cxt_first_buy_V221126` prints the parameter template `{freq}_D{di}B_BUY1V221126`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Signal catalogue helpers: `czsc._native.list_all_signals()` (246 entries with `name`, `param_template`, `category`, `namespace`), `czsc._native.list_signal_names()` (222), `czsc._native.get_signal_template(name)`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)

**API changes between major versions**
- "1.0.X 已迁移至 Rust 核心，与 0.9.X 不兼容"; the last 0.9 line is tag `v0.9.69`; a migration note is referenced at `docs/migration/cleanup-non-czsc-core.md`. **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- In 1.0.2 these imports fail with `ModuleNotFoundError`: `czsc.signals`, `czsc.objects`, `czsc.analyze`, `czsc.enum`, `czsc.sensors`, `czsc.svc`, `czsc.features`, `czsc.traders.base`. Tutorials written for 0.6–0.9 (for example `from czsc.objects import RawBar`, `from czsc.analyze import CZSC`, `czsc.signals.cxt_first_buy_V221126(c, di=1)`) will not run unchanged. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `czsc.traders.base` and `czsc.traders.sig_parse` removed on 2026-05-17; `czsc.traders.optimize` moved to `czsc.utils.optimize` (`OpensOptimize`, `ExitsOptimize`). **[RUN, module docstring]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Several plotting helpers (cumulative return, drawdown, monthly heat map) were removed in favour of `wbt.generate_backtest_report` or plain plotly; remaining chart entry points are `czsc.utils.plotting.lightweight.plot_czsc`, `plot_czsc_trader`, `plot_czsc_signals` and `czsc.utils.plotting.kline`. **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- 1.0.2 is explicitly "**不是兼容性修复版本**": 34 signal output keys were renamed (k3 now carries the version tag), with no aliases; strategies, saved signals and caches written for 1.0.1 must be migrated per `docs/signal_contracts.md`, otherwise old conditions silently never match. **[P]** — [CHANGELOG 1.0.2](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md)
- 1.0.2 also fixed duplicate adjacent same-type fractals (#347) and a `resample_to_daily` datetime-unit problem under pandas 2/3. **[P]** — [CHANGELOG 1.0.2](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md)
- The 0.9.x documentation (readthedocs, release 0.9.51, 26 May 2024) describes the older pure-Python API. **[S]** — [czsc 0.9.51 docs PDF](https://czsc.readthedocs.io/_/downloads/en/0.9.51/pdf/)

### Inferences
- Pin the version (`czsc==1.0.2`) for any test: the author changed signal keys inside a patch release, so results are not reproducible across 1.0.x versions without pinning.
- For yfinance/NSE data the mapping is: `Date`→`dt` (tz-naive), `Open/High/Low/Close`→lower-case, `Volume`→`vol`, add `symbol`, and compute `amount = vol*close`. Use split/dividend-adjusted prices, because czsc does no price adjustment itself (see section 5 and Issue #353). This mapping was not run against real NSE data here (only the synthetic frame with the same columns).
- Trades in the trader are booked at the signal bar's close (the test `operates` prices equalled bar closes). For a daily strategy that means "decide and fill at the same close"; a realistic test should shift execution to the next day's open or close.
- The pair field `盈亏比例` is in basis points (the sample showed 124.47 for a +1.24% trade and −1313.54 for a −13.1% trade).

### Gaps
- `docs/migration/cleanup-non-czsc-core.md` returned 404 at the path the README links to on master, so the official old→new mapping table was not read.
- `docs/signal_contracts.md` (the 34-key migration list) was not read.
- The official end-to-end examples live on the author's Feishu wiki (login/JS required) and were not read; the script above is this session's own working example, not the author's.
- Not tested: multi-symbol `run_research`, HTML report generation, weekly/monthly resampling from daily (`resample_bars`, `BarGenerator(base_freq="日线", freqs=["周线","月线"])`).

---

## 4. Ready-made signal functions and example strategies usable on daily bars only

### Takeaway
Almost the whole catalogue (222 bar-level signals, of which 43 are Chan-structure `cxt_*` signals) is frequency-agnostic and runs on `日线`; only a handful are intraday by design. There are no packaged named strategies in 1.0.2 — only the `CzscStrategyBase` / `CzscJsonStrategy` wrappers — so a "strategy" is whatever Event/Position you compose from signals.

### Cited Findings
- Catalogue size: `list_all_signals()` returns 246 (222 category `kline`, 24 category `trader`); by namespace: tas 58, bar 46, cxt 43, jcc 19, zdy 18, pos 16, xl 7, vol 6, byi 5, coo 5, pressure 4, cat 2, plus single-indicator ones (adtm, amv, asi, bias, cci, clv, cmo, cvolp, dema, emv, er, kcatr, obv, skdj …). README says "220+" in one place and "246" in another. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/); **[P]** [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- Namespace meaning: `cxt` = 缠论形态 (Chan structure), `tas` = TA indicators (MACD/MA/BOLL/KDJ/SAR…), `bar` = single/multi-bar price action, `jcc` = Japanese candlestick patterns (蜡烛图), `vol` = volume, `byi`/`zdy`/`xl`/`coo` = community-contributed sets, `pos` = position-state signals (need a trader). **[RUN for names; meanings inferred from templates]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Chan-structure signals verified to produce values on daily bars (counts from 1,500 synthetic daily bars, shown only to prove they fire, with their output vocabulary): **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
  - `cxt_first_buy_V221126` → key `日线_D1B_BUY1V221126`; values `一买_5笔|7笔|9笔|11笔|13笔|21笔` (first-class buy, tagged by how many strokes form the pattern) or `其他`. Fired on 127 of 1,500 bars.
  - `cxt_first_sell_V221126` → `日线_D1B_SELL1V221126`; values `一卖_N笔`. Fired on 80 bars.
  - `cxt_second_bs_V240524` → `日线_D1W9T2_第二买卖点V240524`; values `二买` (80 bars) / `二卖` (139 bars).
  - `cxt_third_buy_V230228` → `日线_D1_三买辅助V230228`; values `三买_6笔|8笔|10笔|12笔|14笔`. Fired on 145 bars.
  - `cxt_third_bs_V230318` (parameters `ma_type`, `timeperiod`; default gave `日线_D1#SMA#34_BS3辅助V230318`) → `三买` (70) / `三卖` (59).
  - `cxt_bs_V240526` → `日线_趋势跟随_BS辅助V240526`; values `买点` (72) / `卖点` (10).
  - `cxt_bi_status_V230101` → `日线_D1_表里关系V230101`; values `向上_顶分`, `向上_延伸`, `向下_底分`, `向下_延伸` (direction of the current stroke and whether a reversal fractal has appeared) — fires on every bar.
- Full list of the other `cxt_*` signals and their key templates (all take `{freq}`, so `日线` works): **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
  - Stroke-end helpers (笔结束辅助, "BE辅助"): `cxt_bi_end_V230104`, `_V230105` (MA-based), `_V230222`, `_V230224`, `_V230312` (MACD), `_V230320`, `_V230322` (fractal + MA), `_V230324` (MA break), `_V230618`, `_V230815` (fast break), `cxt_ubi_end_V230816` (unfinished stroke).
  - Stroke state/trend: `cxt_bi_base_V230228`, `cxt_bi_status_V230102`, `cxt_bi_trend_V230824`, `cxt_bi_trend_V230913`, `cxt_bi_zdf_V230601` (stroke change layering), `cxt_bi_stop_V230815` (stop-loss distance), `cxt_fx_power_V221107` (fractal strength 分型强弱).
  - N-stroke patterns (三/五/七/九/十一笔形态): `cxt_three_bi_V230618`, `cxt_five_bi_V230619`, `cxt_seven_bi_V230620`, `cxt_nine_bi_V230621`, `cxt_eleven_bi_V230622`.
  - Buy/sell points: `cxt_first_buy_V221126`, `cxt_first_sell_V221126`, `cxt_double_zs_V230311` (two pivot zones, BS1 helper), `cxt_second_bs_V230320`, `cxt_second_bs_V240524`, `cxt_third_buy_V230228`, `cxt_third_bs_V230318`, `cxt_third_bs_V230319`, `cxt_bs_V240526`, `cxt_bs_V240527` (trend-following BS).
  - Zones: `cxt_decision_V240526`, `_V240612`, `_V240613`, `_V240614` (decision zones 决策区域), `cxt_overlap_V240526`, `_V240612` (support/resistance), `cxt_range_oscillation_V230620` (range oscillation).
- MACD/indicator versions of buy/sell points and divergence, all `{freq}`-parametrised: `tas_macd_first_bs_V221201`, `tas_macd_first_bs_V221216`, `tas_macd_second_bs_V221201`, `tas_macd_bs1_V230312/313/411/412`, `tas_first_bs_V230217`, `tas_second_bs_V230228`, `tas_second_bs_V230303`, `byi_second_bs_V230324` (MACD pull-back to zero axis), `tas_macd_bc_V221201/V230803/V230804/V240307`, `tas_boll_bc_V221118`, `zdy_macd_bc_V230422`, `zdy_zs_V230423` (pivot shape), `zdy_zs_space_V230421`, `byi_symmetry_zs_V221107`. Generic price-action helpers: `bar_dual_thrust_V230403`, `bar_r_breaker_V230326`, `bar_td9_V240616` (神奇九转 / TD-9), `bar_trend_V240209`, `tas_double_ma_V230511`, `tas_atr_break_V230424`, `tas_sar_base_V230425`. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Signals that are intraday or multi-timeframe by design (not meaningful on daily-only data): `bar_time_V230327` (日内时间分段), `bar_operate_span_V221111` (time-of-day window), `bar_zdf_V221203` (t1 至 t2 window), `bar_end_V221211` (`{freq}_{freq1}结束`), `cxt_zhong_shu_gong_zhen_V221221` (`{freq1}_{freq2}_中枢共振`, two-timeframe pivot resonance), `zdy_vibrate_V230406` (`中枢震荡_{freq1}#{freq2}`). The two-timeframe ones can still be used with daily as base and weekly/monthly as the higher level. **[RUN, from templates]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Strategy layer shipped: `czsc.strategies` contains only `CzscStrategyBase` and `CzscJsonStrategy` (plus `run_replay`, `run_research` forwards). No named example strategy classes are present in the 1.0.2 wheel. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Built-in weight-style position generators exist in `czsc._native` (not Chan-specific): `single_sma_positions`, `single_ema_positions`, `double_sma_positions`, `triple_sma_positions`, `boll_positions`, `boll_reverse_positions`, `rsi_reverse_positions`, `mid_positions`, `mms_positions`, `rank_positions`, `tanh_positions`. **[RUN, names only]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Official worked examples are on the author's Feishu wiki: "基于 Event 的策略回测 + wbt HTML 报告", "lightweight_charts 缠论可视化", "把信号函数画到 K 线主图", "性能基准测试", "信号函数模块深入介绍 (246 个信号函数)". **[P, titles only]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- The author's older FAQ pointed to strategy examples in a `scripts_gm` folder (掘金 / GM platform). **[P, via page summary]** — [Discussion #32](https://github.com/waditu/czsc/discussions/32). No `examples` folder is in the current repo root (top-level: `.cargo, .claude, .github, .vscode, crates, czsc, docs, scripts, tests`). **[P]** — [github.com/waditu/czsc](https://github.com/waditu/czsc)

### Inferences
- A daily-only NSE test can be assembled from: opens on `一买` / `二买` / `三买` signals, exits on `一卖` / `二卖` / `三卖`, optionally filtered by `cxt_bi_status_V230101` (stroke direction) or a higher-level weekly signal generated from the same daily bars via `BarGenerator`.
- Each buy/sell-point signal stays "on" for several consecutive bars (for example 127 first-buy bars but only 9 round trips in the test), so events should be treated as states, not one-bar triggers; the `interval` parameter of `Position` controls re-entry spacing.
- Signals are computed incrementally bar by bar by the trader, so a signal seen at bar t uses only bars up to t; but the stroke it relies on is provisional and may later be redrawn, so charts drawn after the fact will look cleaner than what the trader saw live.

### Gaps
- Default parameters of each signal (for example `W9T2` in `cxt_second_bs_V240524`) and their meaning were not documented from source.
- The contents of the repo `docs/` and `scripts/` folders were not listed; there may be sample position JSON files there.
- The 16 `pos_*` and 2 `cat_*` trader-category signals were not examined.

---

## 5. Does it need Chinese data sources, or any OHLCV?

### Takeaway
No Chinese data source is needed. The core accepts any DataFrame with the eight standard columns; Tushare, 天勤 (TqSdk) and CCXT connectors are optional modules whose third-party packages are not installed as dependencies. Verified by running the full pipeline on a non-Chinese-labelled synthetic daily series with no data-vendor token.

### Cited Findings
- Connectors shipped under `czsc.connectors`: `tq_connector.py` (天勤 TqSdk, futures), `ts_connector.py` (Tushare, A-shares), `ccxt_connector.py` (crypto exchanges), `local_data.py` (reader for the author's shared research-data cache). **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- 聚宽 (JoinQuant), QMT and 掘金 connectors are **not** present in the 1.0.2 package directory listing (only the four files above). **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- `tushare`, `tqsdk` and `ccxt` are not in the dependency list; `ts_connector.py` imports `tushare` lazily inside functions; `tq_connector.py` and `ccxt_connector.py` import their SDK at module top (so importing those two modules without the SDK fails, but they are only loaded on demand). **[P + RUN]** — [pyproject.toml](https://raw.githubusercontent.com/waditu/czsc/master/pyproject.toml); [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- The Tushare real-data example requires a `TUSHARE_TOKEN`. **[P]** — [CHANGELOG 1.0.1](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md)
- Full pipeline (format → CZSC → signals → Position → CzscTrader → WeightBacktest) ran on a DataFrame with symbol `RELIANCE.NS` and business-day dates, no vendor package installed. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Mock data for demos: `czsc.mock.generate_symbol_kines(symbol, freq, sdt, edt, seed)` and `generate_klines_with_weights` (forwarded from `wbt`). **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- `BarGenerator(base_freq, freqs, max_count, market=None)` has a `market` argument and the core has `is_trading_time` / `freq_end_time` with market inference (`infer_market_from_bars`) designed around Chinese sessions; this matters for intraday bar synthesis. **[RUN signature; P]** — [CHANGELOG rc.8](https://raw.githubusercontent.com/waditu/czsc/master/CHANGELOG.md)
- A-share-specific assumptions reported by a third-party code review: a hard-coded 7% limit-up threshold in a bar signal (`bar.rs:936`), no price-adjustment (复权) handling, no suspension handling, fills at `bar.close` with no slippage model. **[S — unverified user analysis, likely AI-assisted]** — [Issue #353](https://github.com/waditu/czsc/issues/353)
- Signal keys, values, frequency names and `pairs` field names are in Chinese (`日线`, `一买`, `开仓时间`, `盈亏比例`). **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)
- Interactive HTML charts from `plot_czsc` need internet access to load chart libraries ("此绘图方式需联网加载图表依赖"). **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)

### Inferences
- For NSE daily bars the only preparation is column renaming, tz-stripping, NaN removal and using adjusted prices. Daily-only use sidesteps the Chinese-session logic that affects intraday bar synthesis.
- Any signal that encodes A-share limit-up/limit-down behaviour (涨停/跌停-type signals in the `bar` namespace) should be excluded for NSE, where price bands differ by stock.
- Code that filters on signal values must contain Chinese strings; this is cosmetic but affects maintainability for a non-Chinese-reading user.

### Gaps
- Weekly/monthly bar synthesis from non-Chinese daily data (holiday calendars, week boundaries) was not tested.
- Which specific signals embed A-share limit rules was not enumerated from source; the 7% claim comes only from Issue #353.

---

## 6. Evidence that czsc signals or Chan theory rules make money after costs

### Takeaway
No reliable, independent, cost-adjusted evidence of profitability was found. The author publishes no performance figures for czsc signals and explicitly says demo output "不代表实盘或策略收益" and that every signal must be validated by the user; the only numeric "results" located are (a) unverified estimates in a GitHub issue with no backtest behind them, (b) a brokerage-style report and (c) one short Chinese journal article, neither of which could be opened to check costs, sample or out-of-sample design.

### Cited Findings

**Author's own statements and material**
- README: demo GIF uses simulated data "仅用于功能演示，不代表实盘或策略收益"; closing line "项目开源仅用于技术交流，不构成投资建议". The README contains no backtest result for any signal or strategy; the `WeightBacktest` example runs on mock data. **[P]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- Author's FAQ: "每个因子信号都需要在个股的历史数据上验证"; no profitability claims or backtest numbers given; the first-third-buy restriction is described as intended "to improve win rate" with no figure. **[P, via page summary]** — [Discussion #32](https://github.com/waditu/czsc/discussions/32)
- The author's WeChat account "胜可知QUANT" lists an article titled "策略为什么会出现收益能力的衰减？" (why strategies' return ability decays) among recommended reading. **[P, title only; article not read]** — [README](https://raw.githubusercontent.com/waditu/czsc/master/README.md)
- The 0.9.51 docs define the metrics used (annual return = mean daily return × 252; Sharpe = mean/std × √252) but give formulas, not strategy results. **[S]** — [czsc 0.9.51 docs](https://czsc.readthedocs.io/_/downloads/en/0.9.51/pdf/)

**Third-party commentary on czsc itself**
- GitHub Issue #353 "实战性、成功率、漏洞、可靠性、逻辑方面全面分析" (user `jsvanyr`, opened 2 Sep 2026, still open, no maintainer reply visible): a qualitative code review, apparently AI-assisted (contains agent-style narration), with **no backtest shown**. Its numbers are stated as estimates for "typical signal combinations": daily-bar strategies win rate 48–55%, payoff ratio 1.2–2.0, max drawdown 20–30%; 30-minute win rate 45–52%, payoff 1.1–1.8; 5-minute and below win rate under 50%; multi-stock portfolio annual return 10–20% as a "reasonable expectation". It lists weaknesses: fills at bar close without slippage, no limit-up/limit-down fill blocking, hard-coded 7% limit threshold, no price adjustment, no suspension handling, no segment layer, last stroke redrawn after the fact ("事后确认"), overfitting risk (e.g. 5 signals × 3 parameters = 243 combinations), no built-in walk-forward. It assumes A-share costs of 0.025% commission, 0.1% stamp duty on sells, about 0.2% slippage per trade. **[S — unverified opinion; treat numbers as guesses, not measurements]** — [Issue #353](https://github.com/waditu/czsc/issues/353)
- That issue's claim that the framework has no fee simulation is only partly right: the bundled `WeightBacktest` takes `fee_rate` (default 0.0002), confirmed by running it; the `Position.pairs` profit figures themselves are gross. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/); contradicts part of [Issue #353](https://github.com/waditu/czsc/issues/353)
- A CSDN tutorial "用CZSC 0.6.8库实现缠论三买自动选股" shows third-buy stock screening code for the old 0.6.8 API; the search summary reported no return figures. **[S]** — [CSDN](https://blog.csdn.net/weixin_42531710/article/details/160438423)

**Studies of Chan theory rules in general (not czsc-specific)**
- Brokerage-style report "抽丝剥茧解缠论——技术形态选股系列报告之三", hosted on BigQuant: according to the search summary it tests the three classes of buy/sell points on A-share daily data and concludes the first-class buy/sell points perform best, leading on win rate and payoff ratio. Author, sample period, exact numbers and cost treatment could **not** be verified (bigquant.com blocked in this session). **[S, snippet only]** — [BigQuant report](https://bigquant.com/square/paper/4c21f656-703b-4dbe-94e7-48c8d727312f)
- 戴鹏 (2019), "基于'缠论'的中国A股市场技术分析的实证研究" (CNKI id CNKI:SUN:JRCF.0.2019-21-013): per the search summary, uses Shanghai/Shenzhen A-shares and concludes Chan theory "effectively reflects medium/long-term trends and fairly accurately depicts short-term trends and fluctuations". No return, cost or out-of-sample figures were available; the full text could not be opened. **[S, snippet only]** — [Baidu Scholar record](https://xueshu.baidu.com/usercenter/paper/show?paperid=1n1j0rc0xu5w0mt0jy1j0xe00n446241); [reprint](https://m.fx361.com/news/2019/1210/6161322.html)
- BigQuant-hosted "再读缠论：缠与禅" is a theoretical reading arguing Chan theory fits market behaviour; not a quantitative test. **[S, snippet only]** — [BigQuant](https://bigquant.com/square/paper/97728da5-199d-446a-820d-beb5788f9b35)
- English-language search for an empirical study of Chan theory / Chanlun profitability returned nothing specific to Chan theory; only general technical-analysis literature (for example moving-average and trading-range-break rules on Shanghai/Shenzhen composite indexes 1992–2013). **[S]** — [arXiv 1504.04254](https://ar5iv.arxiv.org/html/1504.04254)
- Open-source dashboards that backtest Chan rules exist (for example a Streamlit project scanning about 1,940 A-shares), but the search results showed no published performance numbers. **[S]** — [zinan92/backtest](https://github.com/zinan92/backtest)

**This session's own run (not evidence of profitability)**
- On a synthetic random-walk daily series (drift 0.03%/day, vol 1.5%/day), long on `一买`, exit on `一卖`, 10% stop, 100-bar timeout, fee 0.1% per unit turnover: 9 trades over 2020-02 to 2025-11, trade win rate 44.4%, payoff ratio 1.40, annualised return 0.64%, Sharpe 0.04, max drawdown 35.2%, 39% of time in the market. This only shows the pipeline works and that the signals do not manufacture profit from noise. **[RUN]** — [PyPI czsc 1.0.2](https://pypi.org/project/czsc/)

### Inferences
- The evidence base is thin and low quality: nothing found is simultaneously (i) quantitative, (ii) net of costs, (iii) out-of-sample, (iv) independent of people promoting Chan theory, and (v) about czsc's specific signal definitions. The honest prior for the NSE test is "unproven".
- The author's design choice — a toolkit with 200+ versioned signals plus built-in optimisers (`build_open_optim_positions`, `build_exit_optim_positions`, `run_optimize_batch`) — makes it easy to overfit: trying many signal/parameter combinations on 2019–2026 NSE data will almost surely find something that looks good in-sample. A split such as 2019–2023 fit / 2024–2026 untouched hold-out, plus a random-entry or buy-and-hold benchmark, is needed to say anything.
- Two mechanical sources of optimistic bias should be controlled in the NSE test: same-bar close fills (use next-bar execution) and the redrawing of the last stroke (only trust signals as generated bar-by-bar by `CzscTrader` / `generate_czsc_signals`, never structures read off a finished `CZSC` object).
- Indian delivery-trade costs (STT, stamp duty, exchange and brokerage charges, impact) are well above the library's default `fee_rate=0.0002`; the fee must be set explicitly.
- All located Chan-theory studies concern Chinese A-shares; nothing was found on Indian equities.

### Gaps
- bigquant.com and m.fx361.com have to be allowed in the session's network settings before the brokerage report and the 戴鹏 (2019) article can be read and their numbers (win rates, returns, cost assumptions, sample period) extracted.
- No JoinQuant (聚宽), Xueqiu (雪球), Zhihu (知乎) or 掘金 forum post with a reproducible, cost-adjusted czsc backtest was surfaced by the searches run; two targeted searches were made, so such posts may exist but were not found.
- The author's Zhihu / WeChat articles and Feishu wiki case studies were not read (not reachable or JS/login walled); any performance tables inside them are unknown.
- No peer-reviewed English-language study of Chan theory was found.
- No test on real NSE data was run in this session.
