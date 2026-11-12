# Chinese open-source trading strategies and strategy-generating software (excluding czsc, Qlib, Kronos), as of November 2026

Reading conventions used throughout:

- **[P]** = verified by me from the primary repository page or source file during this session (12 Nov 2026).
- **[S]** = secondary: taken from a search-result summary of a third-party write-up; the page itself could not be opened.
- Star counts are the rounded figures GitHub displayed on the day.
- Access limits that shape these notes: the session could not reach csdn.net, zhihu.com, joinquant.com, 10jqka.com.cn, cloud.tencent.cn, qingzhishi.com or arxiv.org (hosts not allowed in the session network), and the GitHub API was not available. So JoinQuant community posts, the Chinese blog write-ups and the alphagen / AlphaForge papers were NOT read first-hand. Everything from them is marked [S] or listed as a gap. Gitee was not searched.

## Which well-known strategies circulate in the Chinese retail quant community with open code, and what are the precise rules?

### Takeaway
The rules that are fully specified in open code and need only daily OHLCV are: the vnpy CTA set (Turtle, Bollinger+CCI, ATR+RSI, Keltner, Dual Thrust, double MA), the eleven screening rules in myhhub/stock, RSRS timing (N=18, M=600, threshold ±0.7; right-skewed variant N=16, M=300), 二八轮动 (20-day return comparison between two indices, else safe asset), and "annualised return × R²" ETF momentum rotation. 小市值 is the most hyped retail strategy but needs market-cap and financial-statement data, and its exact published parameters could only be gathered second-hand.

### Cited Findings

**海龟交易法 (Turtle) — vnpy TurtleSignalStrategy [P]**
- Parameters: entry_window 20, exit_window 10, atr_window 20, fixed_size 1. Entry Donchian channel and ATR are recomputed only while flat and frozen while in a position; the exit channel is recomputed every bar. — [turtle_signal_strategy.py](https://raw.githubusercontent.com/vnpy/vnpy_ctastrategy/main/vnpy_ctastrategy/strategies/turtle_signal_strategy.py)
- Long pyramiding, up to 4 units, by stop orders at: 20-bar high; +0.5 ATR; +1.0 ATR; +1.5 ATR. Shorts mirrored below the 20-bar low. — same source
- Exit long at max(last fill price − 2 ATR, 10-bar low); exit short at min(last fill + 2 ATR, 10-bar high). The stop is re-based on the most recent fill. — same source
- A different "turtle" circulates in screeners: myhhub/stock defines 海龟 simply as today's close ≥ highest close of the last 60 days; Sequoia-X's TurtleTrade is "20-day new high + turnover value over 100 million yuan + up candle, ranked by gain". — [myhhub/stock](https://github.com/myhhub/stock); [sngyai/Sequoia-X](https://github.com/sngyai/Sequoia) [P]
- Rockyzsu/stock uses a 50-day high breakout, with the author's stated reason that the 60-day version is so widely used it is less reliable. — [Rockyzsu/stock](https://github.com/Rockyzsu/stock) [P]

**布林带 (Bollinger) — vnpy BollChannelStrategy [P]**
- Parameters: boll_window 18, boll_dev 3.4, cci_window 10, atr_window 30, sl_multiplier 5.2. Runs on 15-minute bars as shipped. — [boll_channel_strategy.py](https://raw.githubusercontent.com/vnpy/vnpy_ctastrategy/main/vnpy_ctastrategy/strategies/boll_channel_strategy.py)
- When flat: if CCI(10) > 0 place a buy stop at the upper band (18, 3.4 sd); if CCI(10) < 0 place a short stop at the lower band. Exit only by trailing stop: highest high since entry − 5.2 × ATR(30) for longs (mirror for shorts). No take-profit. — same source
- A mean-reversion Bollinger strategy ("布林线均值回归") is listed in Qbot but the README gives no parameters. — [UFund-Me/Qbot](https://github.com/UFund-Me/Qbot) [P]

**均线 (moving average) systems [P]**
- vnpy DoubleMaStrategy: SMA fast 10, slow 20; golden cross = go long (covering any short), death cross = go short (selling any long); no stop. — [double_ma_strategy.py](https://raw.githubusercontent.com/vnpy/vnpy_ctastrategy/main/vnpy_ctastrategy/strategies/double_ma_strategy.py)
- Hikyuu README example: EMA5 crossing above EMA10 buys, otherwise sells, fixed 1,000 shares, 300,000 starting cash; a portfolio example combines EMA5/MA60 (50% sizing, 5% stop), EMA3/MA10 and EMA10/MA30 sub-systems. — [fasiondog/hikyuu](https://github.com/fasiondog/hikyuu)
- myhhub/stock "均线多头": MA30 must be rising across the checkpoints 30, 20 and 10 days ago to today, and today's MA30 > 1.2 × MA30 of 30 days ago. — [myhhub/stock](https://github.com/myhhub/stock)

**Other vnpy CTA examples [P]**
- AtrRsiStrategy: atr_length 22, atr_ma_length 10, rsi_length 5, rsi_entry 16 (so long if RSI > 66, short if RSI < 34), trailing_percent 0.8. Entry allowed only when ATR(22) is above its own 10-bar mean. Exit by 0.8% trailing stop from the extreme since entry. Default bar is 1 minute. — [atr_rsi_strategy.py](https://raw.githubusercontent.com/vnpy/vnpy_ctastrategy/main/vnpy_ctastrategy/strategies/atr_rsi_strategy.py)
- KingKeltnerStrategy: kk_length 11, kk_dev 1.6, trailing_percent 0.8, 5-minute bars. When flat, place a buy stop at the upper Keltner band and a short stop at the lower band (one cancels the other); exit by 0.8% trailing stop. — [king_keltner_strategy.py](https://raw.githubusercontent.com/vnpy/vnpy_ctastrategy/main/vnpy_ctastrategy/strategies/king_keltner_strategy.py)
- DualThrustStrategy: k1 0.4, k2 0.6. Range = previous day's high − low. Long trigger = today's open + 0.4 × range; short trigger = today's open − 0.6 × range. Reverses at the opposite trigger, at most one long and one short entry per day, all positions closed at 14:55. Intraday by design. — [dual_thrust_strategy.py](https://raw.githubusercontent.com/vnpy/vnpy_ctastrategy/main/vnpy_ctastrategy/strategies/dual_thrust_strategy.py)
- The directory also holds multi_signal_strategy.py and multi_timeframe_strategy.py (not read). — [strategies directory](https://github.com/vnpy/vnpy_ctastrategy/tree/main/vnpy_ctastrategy/strategies)

**Pattern screens — myhhub/stock (all daily OHLCV + turnover value) [P]** — [myhhub/stock](https://github.com/myhhub/stock)
- 放量上涨: turnover value ≥ 200 million yuan and volume ≥ 2 × 5-day average volume (the page's wording of the price condition, "change below 2% or close below open", reads like the exclusion test; check the code).
- 停机坪: a gain above 9.5% on a volume surge within the last 15 days; next day gaps up and closes higher with open-to-close move under 3%; the following 2–3 days also open high and close higher, open-to-close under 3%, daily move within 5%.
- 回踩年线: uses MA250. Before the highest close of the last 60 days, price breaks up through MA250; afterwards it stays above MA250; the low and the high are 10–50 trading days apart; volume on the high day ÷ volume on the low day > 2; low price ÷ high price < 0.8.
- 突破平台: within 60 days, a day with open < MA60 ≤ close that is also a 放量上涨 day; before it, closes sit between −5% and +20% of MA60.
- 无大幅回撤: close less than 60% above the close 60 days ago, and in those 60 days no single-day drop over 7%, no high-open-to-close fall of 7%, no two-day cumulative drop of 10%.
- 高而窄的旗形: listed ≥ 60 days; close ÷ lowest low of the window from 24 to 10 days ago ≥ 1.9; two consecutive days of ≥ 9.5% gains inside that window.
- 放量跌停: drop over 9.5%, turnover value ≥ 200 million yuan, volume ≥ 4 × 5-day average.
- 低ATR成长: listed ≥ 250 days; highest close of last 10 days ≥ 1.1 × lowest close (despite the name, ATR is not used).
- Fundamentals screen (not OHLCV): 0 < P/E ≤ 20, P/B ≤ 10, ROE ≥ 15.
- Also 32+ indicators and 61 candlestick patterns with signed output (negative = sell, 0 = none, positive = buy).

**Pattern screens — Sequoia-X [P]** — [sngyai/Sequoia-X](https://github.com/sngyai/Sequoia)
- Six strategies: TurtleTrade (above), MaVolume (MA plus volume breakout), HighTightFlag, LimitUpShakeout (limit-up, shakeout, pullback confirmation), UptrendLimitDown (limit-down then engulfing recovery in an uptrend), RpsBreakout (O'Neil-style relative price strength breakout). Only TurtleTrade's rule is given in the README; the rest are in code I could not open (the path I tried returned 404).

**RSRS 择时 (光大证券, 2017)**
- Definition: regress daily high on daily low by ordinary least squares over the last N days, high = alpha + beta × low; beta is the RSRS value, N usually 18; the standard score is the z-score of beta over the last M days, M usually 600. — [TradingView open script "RSRS"](https://cn.tradingview.com/script/JOxeFQeX-RSRS-Resistance-Support-Relative-Strength) [S, search summary]
- Trading rule for the standard-score version: buy and hold when the score > S, sell to flat when the score < −S, with N=18, M=600, S=0.7. — [Tencent Cloud replication article](https://cloud.tencent.cn/developer/article/1495322) [S]
- Parameter origin: N tested from 10 to 30 and M from 400 to 800; N=18, M=600 gave the highest return, benchmark CSI 300. — [同花顺 SuperMind article](https://quant.10jqka.com.cn/view/article/1573) [S]
- Right-skewed standard-score version uses N=16, M=300. — [知乎 replication](https://zhuanlan.zhihu.com/p/631688107) [S]; consistent with the "右偏(16,300)" label in [cedric-runtaoxu/rsrs-timing](https://github.com/cedric-runtaoxu/rsrs-timing) [P]
- The cedric-runtaoxu replication: signal at close of day t executed at close of day t+1; a price-trend filter applied to entries only; a volume filter (prior 10-day volume positively correlated with the corrected score); N scanned 14–25, M scanned 450–800 in steps of 50. — [cedric-runtaoxu/rsrs-timing](https://github.com/cedric-runtaoxu/rsrs-timing) [P]
- hugo2046/QuantsPlaybook contains three RSRS versions (original, revised, and a "localised" JoinQuant version) plus CICC's QRS timing (2021). — [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) [P]

**ETF 轮动 — 二八轮动**
- Rule: each trading day after the close, compare CSI 300 and CSI 500 against their closes 20 trading days earlier; hold whichever rose more, switching the next trading day; if both fell, switch to a government-bond index (variants: cash or money-market fund). — [同花顺 strategy collection](https://quant.10jqka.com.cn/view/article/1521) and [中证网, 2017](https://www.cs.com.cn/tzjj/tjdh/201709/t20170914_5474374.html) [S]
- Variants: the 同花顺 example rebalances on the first trading day of each week rather than daily; a CSDN version moves to a money-market fund when both returns ≤ 0, adds a 10-day minimum holding period and charges 0.1% one-way cost; a JoinQuant version uses ETFs 510300 and 510500 with cash as the safe asset because the bond fund's fees exceeded its return. — [同花顺](https://quant.10jqka.com.cn/view/article/1521); [CSDN](https://blog.csdn.net/weixin_42219751/article/details/123556645) [S]
- The 蛋卷 (Xueqiu Danjuan) product version used 天弘沪深300, 天弘中证500 and 天弘永利债券E. — [简书](https://www.jianshu.com/p/8d83495cf892) [S]

**ETF 轮动 — slope / R² momentum**
- The current retail standard is: momentum score = annualised return × R² from a (weighted) linear regression of log price, hold the top-scoring ETF. solary2014/etf-signal applies it to four ETFs (gold, Nasdaq, ChiNext, SSE 180), top 1, checked each weekday at 13:59 Beijing time. — [solary2014/etf-signal](https://github.com/solary2014/etf-signal) [P]
- deliluo-long/quant_model_project: same score with recent data weighted more; a three-factor version (bias momentum, slope momentum, efficiency momentum, each z-scored, weights 0.35 / 0.35 / 0.30); risk filters on volume ratio, short-term sharp fall, R² threshold, holding-period protection. Lookbacks, thresholds and ETF pool are not in the README. — [deliluo-long/quant_model_project](https://github.com/deliluo-long/quant_model_project) [P]
- YaoBa-Quant/etf-momentum-board uses a 20-day weighted least-squares slope of log price multiplied by weighted R². — [YaoBa-Quant/etf-momentum-board](https://github.com/YaoBa-Quant/etf-momentum-board) [S, search summary]

**小市值 (small-cap rotation)**
- 果仁网-style rule replicated on 掘金: exclude ST and STAR Market, sort by total market value ascending, rebalance period 1, maximum 5 holdings. — [CSDN article](https://blog.csdn.net/qq_46262068/article/details/146705780) [S, and the summary's attribution between two CSDN articles is uncertain]
- JoinQuant "国九条" variants: weekly rebalance on Tuesday; one version starts from 深证成长 index constituents, keeps market value of 5–30亿元 (0.5–3.0 billion yuan), sorts ascending, takes 50 candidates and holds the 5 smallest; filters ST, new listings, STAR Market and Beijing exchange; stays out in January and April (one version parks in 银华日利 ETF); financial filter net profit > 0 and revenue > 100 million yuan plus audit-opinion check; stop-loss 9% per stock in one version, 7% per stock plus 5% market stop in another; one version varies holdings between 3 and 6 by the index's gap to its 10-day average. — [CSDN "国九条后中小板微盘小改"](https://blog.csdn.net/2501_94017608/article/details/155808123); [CSDN "年化96%的小市值策略"](https://blog.csdn.net/hehehaha2025/article/details/149823379); [轻知量化 listing](https://www.qingzhishi.com/archives/1297.html) [S]
- Qbot lists 小市值 ('2021) and charliedream1/ai_quant_trade lists "Small-Cap + Multi-MA" as a JoinQuant strategy; neither README gives the rule. — [UFund-Me/Qbot](https://github.com/UFund-Me/Qbot); [charliedream1/ai_quant_trade](https://github.com/charliedream1/ai_quant_trade) [P]

**多因子选股 (multi-factor)**
- A fully specified OHLCV-plus-turnover example: osnddwqd-hub/a-share-multifactor-backtest. Factors: mid-term momentum P[t−20]/P[t−60] − 1 (skips the latest 20 days); short-term reversal −(P[t]/P[t−5] − 1); low volatility −(20-day return standard deviation × √252); low turnover −(20-day mean turnover rate). Daily cross-sectional winsorising at 1%/99% then z-score. Weights proportional to the positive part of each factor's mean training-period Rank IC (equal weights as fallback). Walk-forward 252 training days / 63 test days. Top 5 of 30 fixed main-board shares, equal weight, monthly rebalance at next day's open. — [osnddwqd-hub/a-share-multifactor-backtest](https://github.com/osnddwqd-hub/a-share-multifactor-backtest) [P]
- QuantsPlaybook replicates brokerage factor reports including Kaiyuan Securities' A-share reversal microstructure (2019), momentum (2020), amplitude "hidden structure" (2020), smart money (2020), APM (2020), MA convergence/divergence (2022); Dongwu's upper/lower shadow and idiosyncratic volatility (2020); Dongfang's buying/selling pressure (2019); GF's chip distribution and disposition effect; Huatai/Tianfeng multi-factor index enhancement (2018). — [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) [P]
- Other repos surfaced but not opened: JoshuaQYH/TIDIBEI (RandomForest, GBDT, AdaBoost, XGBoost, MLP, LSTM multi-factor selection), zhangjinzhi/Wind_Python (needs Wind), ThreshoLdnnis/QuantitativeTeamProject1 (19-step tutorial that records results which did not beat the benchmark). — [TIDIBEI](https://github.com/JoshuaQYH/TIDIBEI); [Wind_Python](https://github.com/zhangjinzhi/Wind_Python); [QuantitativeTeamProject1](https://github.com/ThreshoLdnnis/QuantitativeTeamProject1) [S, search summary]

**动量 / 反转 (momentum versus reversal in A-shares)**
- A 2014 《财经研究》 paper on 1994–2011 data finds no significant monthly momentum in A-shares, but stable momentum profits with a 2–4 week formation period and 1–3 week holding period; size, book-to-market and industry explain about half of it. — [财经研究 (SUFE journal)](https://qks.sufe.edu.cn/J/ArticleQuery/A160824000397/CN) [S, search summary]
- A Tsinghua PBC School study on 2000–2016 data attributes the missing monthly momentum to intraday and overnight momentum that reverse against each other under the T+1 rule. — [SciOpen article PDF](https://www.sciopen.com/local/article_pdf/10.26599/CJE.2022.9300405.pdf) [S, search summary]
- A Chinese literature review reports reversal within holding periods up to 6 months on 2000–2009 data (王璞), with the caveat that momentum and reversal each appear only for particular formation/holding windows and studies disagree. — [sinoss.net paper](https://www.sinoss.net/uploadfile/2010/1130/5534.pdf) [S, search summary]

**网格交易 (grid)**
- kapibaLa7/grid-backtest compares three grids on dividend ETF 515180: equal-distance static, geometric (labelled 1.5%), and ATR-adaptive, against buy-and-hold. Base price, level count and lot size are in code/grid_515180_backtest.py, not the README. — [kapibaLa7/grid-backtest](https://github.com/kapibaLa7/grid-backtest) [P]
- TruthHun/grid-trading (掘金 gm.api, rebar futures) is not a fixed grid: it bands price by the mean and standard deviation of the last 300 bars and sets position by band. — [TruthHun/grid-trading](https://github.com/TruthHun/grid-trading) [S, search summary]
- Qbot lists grid trading under futures; kuangdd2024/grid-trading-system offers simulation, parameter search and backtest for stocks, funds and FX. — [UFund-Me/Qbot](https://github.com/UFund-Me/Qbot) [P]; [kuangdd2024/grid-trading-system](https://github.com/kuangdd2024/grid-trading-system) [S]

**缠论 other than czsc**
- Vespa314/chan.py computes 笔 (bi_algo normal or fx, strict option), 线段 (seg_algo chan, 1+1 or break), 中枢 (zs_algo normal, over_seg or auto), form-based buy/sell points of types 1, 1p, 2, 2s, 3a, 3b, segment-of-segment levels, multi-level 区间套, with thresholds divergence_rate, min_zs_cnt, max_bs2_rate, bs1_peak, macd_algo. — [Vespa314/chan.py](https://github.com/Vespa314/chan.py) [P]
- Only about 5,300 of roughly 22,000 lines are public: the public part is "basic static calculation"; strategy classes, 400+ features, XGBoost/LightGBM/MLP scoring, AutoML and the Futu trading link are withheld. — same source [P]
- abu (阿布量化) advertises 缠论 first/second/third buy and sell points among its signal families, alongside Elliott wave, harmonic patterns and chart patterns; the README gives no parameters. — [bbfamily/abu](https://github.com/bbfamily/abu) [P]

### Inferences
- "Turtle" means two different things in this community: a full futures-style system with ATR pyramiding (vnpy) and a bare N-day-high stock screen (myhhub 60-day, Sequoia-X 20-day, Rockyzsu 50-day). A re-implementation must say which.
- All vnpy CTA defaults were tuned for Chinese futures on minute bars with shorting. Rules port to daily bars mechanically, but the defaults (for example a 0.8% trailing stop, or 3.4 standard deviations) should not be expected to transfer.
- The retail ETF-rotation rule has migrated from 二八轮动 (simple 20-day return, two indices) to slope × R² momentum over a wider cross-asset pool; every 2026-dated repo found uses the latter.
- The published small-cap variants keep adding guards (January/April out, audit filters, stop-losses) after the 2024 "国九条" delisting rules, which suggests the bare "smallest market value" rule stopped being presented on its own.
- The academic evidence found supports "monthly momentum is weak in A-shares, short-horizon effects are window-dependent" rather than a clean "reversal works" statement; the open multi-factor repo above encodes this as 5-day reversal plus 20–60 day momentum that skips the latest month.

### Gaps
- The 光大证券 RSRS report itself was not read. The exact right-skewed formula, the corrected-score formula and the MA-based trend filter parameters are therefore not confirmed here. My recollection (unverified this session) is: corrected score = z-score × R²; right-skewed score = corrected score × slope; trend filter compares MA20 with its value some days earlier. Check against the report or the QuantsPlaybook notebook.
- JoinQuant 精选 strategy posts could not be opened, so no small-cap or ETF-rotation rule is quoted from the original author's code.
- 米筐, 优矿, BigQuant and 果仁网 community posts were not reached; no findings.
- Gitee was not searched.
- WonderTrader demo strategy rules (DualThrust and stock demos in wtpy/demos) were not visible on the repo front page and were not opened.
- Lookback windows and thresholds for the slope × R² ETF rotation repos are in code, not READMEs; the commonly cited 25-day window was not confirmed.

## Which GitHub or Gitee repositories by Chinese small developers publish these strategies with code?

### Takeaway
Strategy-bearing repos by individuals or small teams with meaningful adoption are myhhub/stock, Sequoia-X, QuantsPlaybook, Qbot, ai_quant_trade, abu, chan.py and the vnpy CTA examples; most of the famous names (QUANTAXIS, easyquant, Hikyuu, AKQuant, wtpy, zvt) are infrastructure with at most toy examples. Three licences need care: Qbot (MIT badge but README says CC BY-NC-SA 4.0), abu (GPL-3.0) and TradingAgents-CN (part proprietary); QuantsPlaybook, AlphaForge and alphagen showed no licence on the page.

### Cited Findings

**Repositories with concrete strategy logic** (all [P] unless noted)

| Repository | Author | Stars | Licence | What it contains |
|---|---|---|---|---|
| [vnpy/vnpy_ctastrategy](https://github.com/vnpy/vnpy_ctastrategy/tree/main/vnpy_ctastrategy/strategies) (part of [vnpy/vnpy](https://github.com/vnpy/vnpy)) | VeighNa team | 46.3k (main repo) | MIT (main repo; plugin repo licence not shown) | AtrRsi, BollChannel, DoubleMa, DualThrust, KingKeltner, MultiSignal, MultiTimeframe, TurtleSignal |
| [myhhub/stock](https://github.com/myhhub/stock) | myhhub | 15.2k | Apache-2.0 | 11 screening rules, 32+ indicators, 61 candlestick patterns, selection "validation" backtest |
| [sngyai/Sequoia-X](https://github.com/sngyai/Sequoia) | sngyai | 8.6k | MIT | 6 after-close screens, baostock data, Feishu push |
| [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) | hugo2046 | 6.9k | none shown | About 60 brokerage-report replications: ~30 timing, ~22 factor, 2 value, 2 portfolio. Needs JoinQuant jqdata and Tushare Pro |
| [UFund-Me/Qbot](https://github.com/UFund-Me/Qbot) | Charmve | 18.8k | conflicting: sidebar MIT, README CC BY-NC-SA 4.0, commercial use needs paid Pro | Long list of classical and machine-learning strategies; README has names, not rules |
| [charliedream1/ai_quant_trade](https://github.com/charliedream1/ai_quant_trade) | Yi Li | 6.7k | Apache-2.0 | Tutorials, JoinQuant-only strategy code, tsfresh factor mining, reinforcement-learning demos |
| [bbfamily/abu](https://github.com/bbfamily/abu) | bbfamily (阿布) | 19.2k | GPL-3.0 | Buy/sell factor framework, pattern and 缠论 signal families, machine-learning "umpire" |
| [Vespa314/chan.py](https://github.com/Vespa314/chan.py) | Vespa314 | 2.3k | MIT | 缠论 structure and buy/sell-point computation; strategy and model layers closed |
| [Rockyzsu/stock](https://github.com/Rockyzsu/stock) | Rockyzsu | 9.0k | BSD-3-Clause | Scripts: 50-day high breakout, limit-up statistics, convertible-bond monitors; mostly data tools |
| [cedric-runtaoxu/rsrs-timing](https://github.com/cedric-runtaoxu/rsrs-timing) | cedric-runtaoxu | 0 | MIT | RSRS replication report with cost scenarios |
| [osnddwqd-hub/a-share-multifactor-backtest](https://github.com/osnddwqd-hub/a-share-multifactor-backtest) | osnddwqd-hub | 0 | MIT (code only) | 4-factor walk-forward backtest with costs |
| [kapibaLa7/grid-backtest](https://github.com/kapibaLa7/grid-backtest) | kapibaLa7 | 1 | none shown | Three grid types on ETF 515180 |
| [deliluo-long/quant_model_project](https://github.com/deliluo-long/quant_model_project) | deliluo-long | 1 | none shown | ETF slope × R² rotation variants, CSI 1000 selection, JoinQuant strategies |
| [solary2014/etf-signal](https://github.com/solary2014/etf-signal) | solary2014 | 0 | none shown | Daily four-ETF momentum signal |
| [testtestme123/awesome-quant-strategies](https://github.com/testtestme123/awesome-quant-strategies) | testtestme | 0 | MIT | Grid, MA cross, Bollinger, RSI reversal, Dual Thrust scripts |

**Infrastructure-only or toy-example projects (one line each)** [P]
- QUANTAXIS — yutiansut, 11.4k stars, MIT, v2.1.0-alpha2 (2025-10-25): data storage, backtest suite, account protocol, Rust core; README shows no strategy with entry/exit logic. — [QUANTAXIS](https://github.com/QUANTAXIS/QUANTAXIS)
- easyquant — shidenggui, 3.7k stars, MIT: event-driven live framework on easytrader; demo strategies only log quotes. — [easyquant](https://github.com/shidenggui/easyquant)
- Hikyuu — fasiondog, 3.7k stars, Apache-2.0: C++/Python framework with swappable Signal, Money-management, Stop, Take-profit, Selector, Allocation, Multi-factor parts and walk-forward; examples are EMA crosses only. — [hikyuu](https://github.com/fasiondog/hikyuu)
- AKQuant — akfamily (Albert King and others), 2.6k stars, MIT: Rust-core backtester; examples are "buy if close > open" and a bracket order (stop 98%, target 104% of close). — [akquant](https://github.com/akfamily/akquant)
- wtpy (WonderTrader Python layer) — wondertrader, 1.5k stars, MIT: demos folder exists; front page names only infrastructure demos. — [wtpy](https://github.com/wondertrader/wtpy)
- zvt — zvtvz (foolcage), 4.3k stars, MIT: modular data/factor framework; examples are a follow-the-fund-holdings trader (buy if holding rises > 5%, sell if falls > 50%), an ROE > 8% and revenue growth > 8% screen, and a MACD "bull" factor. — [zvt](https://github.com/zvtvz/zvt)
- vnpy.alpha — inside vnpy 4.0: Alpha 158 features (credited to Qlib), Lasso / LightGBM / MLP models, cross-sectional and time-series signal strategies; needs RQData or Xuntou data in the shipped notebooks. — [vnpy/vnpy](https://github.com/vnpy/vnpy)

### Inferences
- Star count does not track how much re-implementable logic a repo holds: the best-specified rules found are in a 15k-star screener (myhhub/stock), the vnpy examples, and three repos with 0–1 stars.
- Several 2026-dated zero-star repos (rsrs-timing, a-share-multifactor-backtest, grid-backtest, awesome-quant-strategies) have the tidy structure of AI-assisted student or portfolio projects. Their honesty varies sharply: two report losing to the benchmark, one prints an unsourced table of winners.
- QuantsPlaybook is the single richest source of Chinese brokerage timing and factor ideas with code, but it shows no licence, which by default means no reuse rights, and it depends on JoinQuant and Tushare data.

### Gaps
- easytrader (broker automation) was not opened; it is a trading gateway by the same author as easyquant.
- Licences for hugo2046/QuantsPlaybook, deliluo-long, solary2014, kapibaLa7 and vnpy_ctastrategy were "not shown" on the page; the LICENSE files were not opened.
- Exact star counts (not rounded) and last-commit dates were unavailable without the GitHub API.
- The fetch of "sngyai/Sequoia" returned a page titled Sequoia-X, and "RL-MLDM/alphagen" returned a page headed ICT-FinD-Lab/alphagen. These look like renames or redirects; confirm the canonical names.
- No Gitee-hosted project was examined.

## For AI-based small-creator projects, what do they actually output, and what compute and data do they need?

### Takeaway
They fall into three output types: formula miners (alphagen, AlphaForge, RD-Agent) emit factor expressions that still need a ranking-and-holding rule on top; classic machine-learning stacks (vnpy.alpha, Qbot, TIDIBEI) emit per-stock scores; and LLM agent systems (TradingAgents-CN) emit prose research with no backtest. None of the READMEs states hardware needs or contains a performance table.

### Cited Findings
- **alphagen**: outputs pools of formulaic alpha expressions in human-readable JSON, plus reinforcement-learning checkpoints (stable-baselines3) and TensorBoard logs; quality measured by IC and Rank IC against a target such as 20-day return. — [alphagen](https://github.com/RL-MLDM/alphagen) [P]
- alphagen data: Qlib for metadata, baostock for price/volume via data_collection/fetch_baostock_data.py, or a user-written AlphaCalculator adapter for other data. Only a PyTorch `device` parameter is mentioned; no GPU requirement stated. Baselines: modified gplearn (genetic programming) and a minimal deep symbolic regression. A Qlib-based backtest exists but is labelled experimental. Includes an `alphagen_llm` module for LLM-driven alpha generation. 1.3k stars; maintained by the MLDM group at ICT, Chinese Academy of Sciences (Hongyan Xue, Shuo Yu); paper at KDD 2023; follow-up HARLA in Frontiers of Computer Science 2026. — same source [P]
- alphagen README contains no results and states no licence. — [alphagen README](https://raw.githubusercontent.com/RL-MLDM/alphagen/master/README.md) [P]
- **AlphaForge**: "official implementation for AAAI 2025". Stage 1 (train_AFF.py) mines a factor "zoo"; stage 2 (combine_AFF.py) picks n_factors per day over a rolling window and combines them; stage 3 is a results notebook. Data in Qlib format from baostock; universes csi300 and csi500; default split train 2010–2020, validation 2021, test 2022; multiple seeds. Baselines GP, RL, DSO, XGBoost, LightGBM, MLP. 444 stars; no licence shown; no performance numbers or hardware needs in README. — [DulyHao/AlphaForge](https://github.com/DulyHao/AlphaForge) [P]
- **TradingAgents-CN**: 32.9k stars, by hsliuping, derived from Tauric Research's TradingAgents. Outputs multi-agent debate-style research reports with "multi-scenario views", natural-language Q&A, stock screening over 6,000+ shares and paper trading. The page says it does NOT give target prices, stop-loss/take-profit levels or timing instructions. No backtest or return claims. — [hsliuping/TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) [P]
- TradingAgents-CN needs: user-supplied LLM API key (OpenAI, DeepSeek, Qwen named), Tushare / AKShare / BaoStock tokens, Python 3.11, Node.js 18+, MongoDB 7+, Redis 6+. Licence is mixed: Apache-2.0 for tradingagents/, cli/, docs/, tests/; app/, frontend/, core/ are "source available", proprietary, no commercial use or redistribution; a paid Pro edition exists. — same source [P]
- **RD-Agent** (Microsoft Research Asia; included only for its community-used finance recipes): fin_factor proposes and implements factors on Qlib, fin_model does models, fin_quant evolves both jointly, fin_factor_report extracts factors from research-report PDFs. Needs Linux, Docker, Python 3.10/3.11, and an LLM with chat, JSON mode and embeddings via LiteLLM (OpenAI, Azure, DeepSeek examples). — [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) [P]
- **vnpy.alpha**: per-instrument machine-learning signals from Lasso, LightGBM or MLP on Alpha 158 features, fed to cross-sectional or time-series strategies. — [vnpy/vnpy](https://github.com/vnpy/vnpy) [P]
- **Qbot**: lists LightGBM, SVM, LSTM, random forest, Q-learning, reinforcement learning, a sparrow-search optimiser, and a Qlib-style model zoo (XGBoost, CatBoost, DoubleEnsemble, TabNet, GRU, ALSTM, TFT, GATs, Transformer, TRA, HIST and others); ChatGPT and FinGPT are linked without detail. — [UFund-Me/Qbot](https://github.com/UFund-Me/Qbot) [P]
- **ai_quant_trade**: claims "ML auto-mining 5,000 alphas" with tsfresh, a FinRL tutorial, a stable-baselines3 A-share prototype with no results, and a 2025 LLM price-reasoning entry claiming a "20% accuracy boost" with no baseline or dataset. — [charliedream1/ai_quant_trade](https://github.com/charliedream1/ai_quant_trade) [P]
- **chan.py (closed part)**: XGBoost / LightGBM / MLP scoring of 缠论 buy/sell points over 400+ features with a score threshold; not public. — [Vespa314/chan.py](https://github.com/Vespa314/chan.py) [P]

### Inferences
- For a daily-OHLCV test, formula miners are the only AI category whose output is directly testable: an expression over open/high/low/close/volume can be evaluated on any market. The agent systems produce text and have nothing to backtest.
- alphagen and AlphaForge are wired to Qlib data layout and Chinese index universes; using them on another market means writing a data adapter (alphagen explicitly provides the AlphaCalculator interface for this), not changing the method.
- Both are research-group code (ICT/CAS; AAAI paper), not individual hobby projects, and neither README shows a licence, so reuse terms are unclear.

### Gaps
- The alphagen (KDD 2023) and AlphaForge (AAAI 2025) papers could not be opened (arxiv.org blocked), so the input feature list, IC results, backtest returns, training time and whether costs were included are not recorded here. My unverified recollection is that both use only open, high, low, close, volume and vwap as inputs.
- No FinGPT-style Chinese fork was examined. FinGPT itself (AI4Finance) was not opened.
- No "RD-Agent community recipe" by a Chinese individual was found; only the upstream scenarios are described.
- Per-run LLM cost for TradingAgents-CN is not stated anywhere I could read.

## Which of these are testable using only daily OHLCV for about 200 liquid shares over 2019–2026, with no fundamentals, no intraday data and no shorting?

### Takeaway
Directly testable: the vnpy trend rules on their long side re-cast to daily bars, the myhhub and Sequoia-X price/volume screens, RSRS timing applied per share or to an index built from the 200, short-reversal and momentum-skip factors, low-volatility, and the slope × R² rotation treated as cross-sectional stock ranking. Not testable as published: small-cap (needs market value and financial filters), Dual Thrust and the minute-bar defaults (intraday), 二八轮动 and ETF rotation in their original form (need index ETFs and a bond or cash leg), and anything using turnover rate unless shares outstanding are available.

### Cited Findings
- Needs only OHLCV: Turtle 20/10/ATR20 with 4-unit pyramiding and 2-ATR stop; Bollinger(18, 3.4) + CCI(10) breakout with 5.2 × ATR(30) trailing stop; double MA 10/20; ATR(22)>mean10 + RSI(5) 66/34 with 0.8% trail; Keltner(11, 1.6). All ship with short legs and (except Turtle and double MA) intraday bar settings. — [vnpy_ctastrategy strategies](https://github.com/vnpy/vnpy_ctastrategy/tree/main/vnpy_ctastrategy/strategies) [P]
- Dual Thrust closes everything at 14:55 and uses the day's open plus a fraction of yesterday's range as an intraday trigger; it is intraday by construction. — [dual_thrust_strategy.py](https://raw.githubusercontent.com/vnpy/vnpy_ctastrategy/main/vnpy_ctastrategy/strategies/dual_thrust_strategy.py) [P]
- myhhub/stock screens use close, open, high, low, volume, turnover value (成交额) and listing age; thresholds such as "gain above 9.5%" and "turnover ≥ 200 million yuan" are tied to China's 10% daily price limit and to yuan liquidity. Its eleventh rule needs P/E, P/B and ROE. — [myhhub/stock](https://github.com/myhhub/stock) [P]
- Sequoia-X screens use backward-adjusted daily bars from baostock only; LimitUpShakeout and UptrendLimitDown depend on China's limit-up/limit-down mechanism. — [sngyai/Sequoia-X](https://github.com/sngyai/Sequoia) [P]
- RSRS needs only daily high and low, and was designed and parameterised on indices (CSI 300, SSE 50, CSI 500). — [cedric-runtaoxu/rsrs-timing](https://github.com/cedric-runtaoxu/rsrs-timing) [P]; M=600 implies about 2.4 years of warm-up before the first signal — [TradingView RSRS script](https://cn.tradingview.com/script/JOxeFQeX-RSRS-Resistance-Support-Relative-Strength) [S]
- The four-factor repo uses three price-only factors (momentum 60→20, 5-day reversal, 20-day volatility) plus turnover rate, which needs float shares. It is long-only, top-N, monthly. — [osnddwqd-hub/a-share-multifactor-backtest](https://github.com/osnddwqd-hub/a-share-multifactor-backtest) [P]
- Small-cap variants need total market value, ST status, audit opinions, net profit and revenue. — [CSDN 国九条 write-up](https://blog.csdn.net/2501_94017608/article/details/155808123) [S]
- 二八轮动 needs two index series or ETFs and a bond/cash leg. — [同花顺](https://quant.10jqka.com.cn/view/article/1521) [S]
- QuantsPlaybook depends on JoinQuant and Tushare Pro data; several factors (smart money, high-frequency price-volume correlation, intraday ETF momentum) need minute data, and others (northbound capital, fund holdings, analyst picks, FFScore) need non-price data. — [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) [P]
- chan.py's public part needs only OHLC bars with timestamps and can read CSV; it outputs structure and typed buy/sell points, with multi-level analysis optional. — [Vespa314/chan.py](https://github.com/Vespa314/chan.py) [P]
- alphagen accepts custom data through an adapter and targets forward returns such as 20-day. — [alphagen](https://github.com/RL-MLDM/alphagen) [P]

### Inferences
Testability sort, my assessment from the rules above:

| Strategy | Daily OHLCV only? | Long-only OK? | Notes for a 200-share, 2019–2026 test |
|---|---|---|---|
| Turtle (vnpy 20/10, ATR 20) | Yes | Yes, drop short leg | Stop orders assume fills at the breakout level; on daily data model gap opens |
| Donchian screen (20/50/60-day high close) | Yes | Yes | Needs an exit rule; none is published with the screens |
| Double MA 10/20 | Yes | Yes (flat instead of short) | Baseline |
| Bollinger + CCI + ATR trail | Yes | Yes | Defaults tuned on 15-minute futures bars |
| ATR-filter + RSI(5), Keltner | Yes | Yes | 0.8% trailing stop is a minute-bar setting; needs rescaling |
| Dual Thrust | No | — | Intraday |
| myhhub pattern screens | Mostly | Yes | Replace 9.5% limit-up tests and yuan turnover floors with local equivalents; screens have no exit |
| RSRS (18, 600, ±0.7) | Yes | Yes (designed long/flat) | Index-level timing; 600-day warm-up means data from about mid-2016 for signals from 2019 |
| 5-day reversal, 60→20 momentum, 20-day low volatility | Yes | Yes, top-N | Directly testable cross-section on 200 shares |
| Low turnover factor | Needs float shares | Yes | Volume alone is a weak substitute |
| Slope × R² rotation | Yes | Yes | Published for ETFs, top 1; on shares becomes a top-N momentum rank |
| 二八轮动 | Needs indices + safe asset | Yes | Could be mimicked with large-cap versus mid-cap baskets and cash |
| Grid | Yes | Yes | Published evidence shows it lags buy-and-hold in a rising market |
| Small-cap | No | Yes | Needs market value and fundamentals; a 200 liquid-share universe excludes the micro-caps it relies on |
| chan.py structure / buy-sell points | Yes | Yes | Only signal typing is public; entry/exit strategy must be written |
| alphagen / AlphaForge formulas | Yes with adapter | Yes, top-N | Needs GPU-class training run and a held-out period; 200 shares is a small cross-section for IC estimation |
| TradingAgents-CN | No | — | Text output, China data sources, not backtestable |

- Anything defined by the 10% price limit (停机坪, 高而窄的旗形, 放量跌停, limit-up shakeout) is a China-market-structure rule; in a market with different or no price bands the threshold has to be redefined, and the behaviour it was built to catch may not exist.

### Gaps
- No source tested any of these rules on a non-Chinese market; portability is my inference, not a finding.
- Whether alphagen-mined formulas trained on Chinese data transfer to other markets was not addressed by any source read.

## What performance claims are attached, by whom, over what period, and were costs included?

### Takeaway
Most of the well-known repos make no numeric performance claim at all; where numbers exist they come from tiny personal repos, and the two that included costs and an out-of-sample design both show the strategy losing to buy-and-hold on return. The eye-catching figures (annualised 96–135% small-cap, QuantsPlaybook's 12.8–15.2% averages, awesome-quant-strategies' table) carry no cost basis or methodology.

### Cited Findings
- **RSRS replication, CSI 300, 2005-04-08 to 2017-04-28, no trading costs in the main table** (claimant: repo author cedric-runtaoxu): buy-and-hold 11.25% a year, Sharpe 0.514, max drawdown −72.30%; slope 23.74% / 1.172 / −48.20%; standard score 21.72% / 1.135 / −50.50%; corrected score 21.44% / 1.126 / −45.12%; right-skewed (16, 300) 22.97% / 1.069 / −56.40%; right-skewed with price filter 22.23% / 1.359 / −16.55%; with volume filter 22.41% / 1.323 / −17.85%. Cost scenarios of 0.2% and 0.3% one-way exist; the author says the work does not claim to reproduce the original report's numbers. — [cedric-runtaoxu/rsrs-timing](https://github.com/cedric-runtaoxu/rsrs-timing) [P]
- **Four-factor multi-factor, out-of-sample 2024-01-02 to 2025-12-31, costs included** (3 bp commission + 5 bp slippage per side + 5 bp sell tax; 192 trades): strategy +18.50% cumulative, 9.22% a year, max drawdown −6.56%, Sharpe 0.97; CSI 300 +35.13%, 16.93%, −15.66%, 0.94; CSI 500 +37.45%, 17.97%, −19.90%, 0.79. Author states no excess return is shown and flags survivorship bias in the fixed 30-share universe. — [osnddwqd-hub/a-share-multifactor-backtest](https://github.com/osnddwqd-hub/a-share-multifactor-backtest) [P]
- **Grid on ETF 515180, 2019-11-26 to 2026-06-05, commission 0.01%, no stamp duty**: static grid +5.17% total (0.78% a year, max drawdown 1.26%, 73 trades); geometric 1.5% grid +11.06% (1.62%, 1.66%, 308 trades); ATR grid +18.15% (2.59%, 2.86%, 57 trades); buy-and-hold +75.91% (9.04%, 17.55%). — [kapibaLa7/grid-backtest](https://github.com/kapibaLa7/grid-backtest) [P]
- **QuantsPlaybook** README summary table, no period, benchmark, costs or method given: timing strategies average 12.8% a year, max drawdown 18.5%, Sharpe 0.85, win rate 58%; factor 15.2% / 22.3% / 0.92 / 62%; portfolio 10.5% / 15.8% / 0.78 / 55%. It also claims "100+" strategies against roughly 60 listed. — [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) [P]
- **awesome-quant-strategies** table, "2023–2025 A-share data", no cost basis: grid 15.2% a year / −8.3% drawdown / Sharpe 1.42; dual MA 18.7% / −12.1% / 1.28; Bollinger 12.5% / −6.8% / 1.55; Dual Thrust 21.3% / −15.6% / 1.35. — [testtestme123/awesome-quant-strategies](https://github.com/testtestme123/awesome-quant-strategies) [P]
- **ai_quant_trade** JoinQuant strategies, periods not stated: dynamic factor selection 12.3% return / 38.93% drawdown; small-cap + multi-MA 58.4% / 46.61%; Dragon-Tiger list 41.82% / 26.89%; strong stocks + trend line 10.09% / 21.449%. README caveat: valid only for the backtest periods described, not tuned or verified over the full period. FinRL tutorial on Dow 30: 53.1% a year, −10.4%, Sharpe 2.17. — [charliedream1/ai_quant_trade](https://github.com/charliedream1/ai_quant_trade) [P]
- **Small-cap JoinQuant variants**: post titles advertise annualised 96%, 98%, 100.5% and 135.40%, and "5 years 18 times". Claimants are anonymous community posters and resellers of strategy code; periods and cost assumptions were not visible. — [CSDN "年化96%"](https://blog.csdn.net/hehehaha2025/article/details/149823379); [轻知量化 "年化135.40"](https://www.qingzhishi.com/archives/1297.html); [知乎 "5年18倍的小市值策略？"](https://zhuanlan.zhihu.com/p/2019740166974121152) [S, titles only]
- **二八轮动**: a 2017 write-up credits the timing rule with being out of the market through the 2015 crash; later articles ask why it "stopped making money", and a 2017 Sina piece warns fees erode it. — [简书](https://www.jianshu.com/p/e98ef23fc0f1); [新浪财经](http://finance.sina.com.cn/stock/t/2017-04-25/doc-ifyepsra5550505.shtml) [S]
- **RD-Agent(Q)**: authors claim about 2× the annualised return of benchmark factor libraries with over 70% fewer factors at under 10 US dollars of cost in "real stock markets"; period, market and baselines not on the page. — [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) [P]
- **abu**: claims 18,496 buy/sell signal strategies and that its machine learning "beats the market" in live trading; no metrics. — [bbfamily/abu](https://github.com/bbfamily/abu) [P]
- **chan.py**: author reports unattended simulated trading on Hong Kong and US shares since 14 October (year not given), shown only as screenshots, and says it is unclear whether market or strategy drove the result and that the framework does not prove 缠论 is useful. — [Vespa314/chan.py](https://github.com/Vespa314/chan.py) [P]
- **No numeric trading-performance claim in README**: vnpy CTA examples, myhhub/stock, Sequoia-X, Qbot (charts only; example setup 603186, 2010-01-01 to 2020-04-21, commission 0.1%), QUANTAXIS, Hikyuu (speed only: 3,547 shares 2015–2026 EMA5/10 in about 13 s on an Orange Pi 5 Plus), AKQuant, zvt, alphagen, AlphaForge, TradingAgents-CN, Rockyzsu/stock (title jokes "亏钱", losing money), deliluo-long, solary2014. — sources as linked above [P]

### Inferences
- The pattern is consistent: the more careful the test (costs, out-of-sample, benchmark), the weaker the result. The only cost-inclusive, walk-forward numbers found show underperformance on return with lower drawdown.
- RSRS's strong replicated numbers end in April 2017, exclude costs in the headline table, and the parameters (18, 600, 0.7) were chosen as the best of a scan on the same index; they are in-sample. No post-2017 result was found.
- The small-cap return claims are marketing-grade: they appear in post titles on sites that also sell strategy code, cover a period that includes the 2021–2023 micro-cap run, and could not be checked.
- QuantsPlaybook's round averages across ~60 heterogeneous strategies with no period are not usable as evidence.

### Gaps
- The original 光大证券 RSRS figures and the alphagen / AlphaForge paper results (IC, returns, cost treatment) were not obtained.
- No JoinQuant post was readable, so no claim there is tied to a named author, period or cost setting.
- No independent third-party audit of any of these claims was found.
- No live (real-money) track record was found for any project.
