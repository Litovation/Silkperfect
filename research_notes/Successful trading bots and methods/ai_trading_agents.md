# AI / LLM / ML Trading Agents and Models: Honest Out-of-Sample and Live Evidence (as of 24 Nov 2026)

**Method and evidence-quality note.** Research done 24 Nov 2026 with WebSearch (snippet-level summaries) and WebFetch. WebFetch worked only for github.com / raw.githubusercontent.com. It failed (DNS "ENOTFOUND", host not on the session allowlist) for **arxiv.org, alphaxiv.org, gncrypto.news, docs.numer.ai**. So every arXiv number below comes from WebSearch result summaries, NOT from reading the paper, and is marked **[snippet-only, unverified]**. GitHub README facts were read directly **[read]**. Also not reachable/not read: nof1.ai itself, Reddit, Hacker News (no r/algotrading, r/quant or HN thread surfaced in any search), Kaggle, Numerai forum pages (only titles seen), sec.gov/cftc.gov pages (only search summaries).

Evidence-quality scale used: **A** = independent, out-of-sample or live, peer-reviewed or primary data; **B** = independent but short/unreviewed/preprint, or primary but self-reported with audit-like structure; **C** = vendor/author claim or press repeating it; **D** = anecdote/marketing.

Dates matter: the Silkperfect REPORT (12 Nov 2026) found Chronos, TimesFM, Kronos, Qlib recipe all behind equal-weight buy-and-hold on NSE; only momentum won. Everything below is consistent with that, and nothing I found contradicts it.

---

## 1. LLM trading agents (TradingAgents, AI Hedge Fund, FinGPT, FinRL/FinRL-Meta, FinMem, FinAgent, StockAgent): reported returns and independent critique

### Takeaway
Every headline LLM-agent return I found is an author-run backtest on a few stocks over weeks to months. The independent long-horizon test (FINSABER, KDD 2026) found buy-and-hold beat FinMem and FinAgent, and 2026 critiques say contamination, costs and short windows explain the rest. I found no independent, costed, out-of-sample evidence of lasting alpha from any of these systems.

### Cited Findings

**TradingAgents (TauricResearch)**
- Paper (arXiv 2412.20138) claims at least 23.21% cumulative and 24.90% annual return on sampled stocks. Project-page/paper table, as parsed by search: AAPL 26.62 / 30.5 / Sharpe 8.21 / MDD 0.91; GOOGL 24.36 / 27.58 / 6.39 / 1.69; AMZN 23.21 / 24.90 / 5.60 / 2.11. Column labels are my inference (cum. return, annual return, Sharpe, max drawdown). **[snippet-only; author claim = C]** — [arXiv 2412.20138](https://arxiv.org/pdf/2412.20138), [project page](https://tradingagents-ai.github.io)
- Backtest window per search summary: 1 Jan to 29 Mar 2024 (about 3 months), baselines Buy-and-Hold, MACD, KDJ+RSI, ZMR, SMA. The FINSABER paper classifies TradingAgents as "3 months, 3 symbols". Window differs across paper versions (one critique cites 19 Jun to 19 Nov 2024). **[snippet-only]** — [WebSearch summary of arXiv 2412.20138](https://arxiv.org/pdf/2412.20138), [FINSABER v4](https://arxiv.org/pdf/2505.07078v4)
- A dev.to blogger recomputed the paper's AAPL buy-and-hold figure: paper says -5.23% (19 Jun to 19 Nov 2024), blogger gets about +9.12% from dividend-adjusted closes, and calls the Sharpe 8.21 an evaluation artifact. One blogger's check, not verified by me. **[snippet-only; evidence B-/C]** — [dev.to critique](https://dev.to/trow126/the-most-starred-llm-trading-paper-claims-buy-and-hold-lost-523-it-actually-gained-912-1jj6)
- Repo README **[read]**: about 123.6k stars; says it is "designed for research purposes", "not financial advice", publishes **no** return figures, says backtest results "are not guaranteed to match any published figure" and calls itself a "research scaffold rather than a strategy with a fixed, replicable return". v0.7.1 released Oct 2026; separate Trading-R1 v0.1.0 (Nov 2026) in early access. — [GitHub TradingAgents](https://github.com/TauricResearch/TradingAgents)
- GitHub issue #805 **[read]** (opened May 2026): reporter says date-aware data fetching does not remove leakage from the LLM's weights. Maintainer (Jun 2026): data-level leakage fixed (commit 0c1231a); model-level leakage is "a separate, fundamental limitation a code change can't fully eliminate"; issue still open. A commenter's test on 3,708 earnings announcements across 12 models found 10 showed measurable recall of 2023-2024 outcomes, 2 none (community test, unreviewed). — [Issue #805](https://github.com/TauricResearch/TradingAgents/issues/805)
- Anecdote: a LinkedIn post reports two runs on same ticker/date/models gave Overweight and Underweight; a small Apple/Nvidia pilot lost vs buy-and-hold. **[snippet-only; D]** — [search summary](https://bg.linkedin.com/in/rafat-hamud)

**FINSABER (Li, Kim, Cucuringu, Ma), the key independent test** — KDD 2026 (reported as accepted; README says oral, 7 of 92 Cycle-1 submissions)
- Evaluates FinMem, FinAgent, FinCon (LLM) and FinRL (RL) against buy-and-hold on S&P 500 data 2000-2025 (about 20 years in latest version), with commission 0.0049/share, $0.99 minimum, 0.05% slippage, liquidity cap. **[README read]** — [FINSABER README](https://raw.githubusercontent.com/waylonli/FINSABER/main/README.md)
- Headline: previously reported LLM advantages "deteriorate significantly" under longer, broader tests; LLM strategies are over-conservative in bull markets and take heavy losses in bear markets. **[snippet-only]** — [arXiv 2505.07078](https://arxiv.org/html/2505.07078v3)
- Numbers per search summary: in a 63-symbol "volatility effect" setup buy-and-hold Sharpe 0.703 vs FinAgent 0.241 and FinMem -0.228. In an 84-symbol momentum setup FinAgent had the highest annual return (13.95%) but Sharpe 0.104 and max drawdown -20.675%. Regime Sharpe: FinAgent 0.12 bull / -0.38 bear; FinMem -0.19 / -0.97. Paired t-tests: buy-and-hold significantly beats both across robust setups. **[snippet-only; exact table not read]** — [search summary of arXiv 2505.07078](https://arxiv.org/pdf/2505.07078v4)
- Evidence quality: **B+** (independent, long window, costs, but I did not read tables; authors are academics who built the benchmark).

**"The Alpha Illusion" (arXiv 2605.16895, May 2026)**
- Position paper plus reproduction: reported alpha from FinCon, FinMem, TradingAgents, FinAgent, QuantAgent, FLAG-Trader should not be treated as deployment evidence until temporal contamination, friction and short-window statistics are ruled out; "the vast majority of real-world frictions are completely ignored" in five frameworks analysed; gross returns often become net losses or trail buy-and-hold. One summary says a gross-profitable portfolio's Sharpe fell from 0.43 to 0.22 after costs on a one-year 2025-26 window, but a second search could not confirm those numbers. **[snippet-only; Sharpe figures doubly unverified]** — [alphaxiv overview](https://www.alphaxiv.org/overview/2605.16895), [abs](https://www.alphaxiv.org/abs/2605.16895)
- Evidence quality: **B** (preprint, critical, not peer reviewed).

**Contamination / look-ahead literature (all snippet-only)**
- "Profit Mirage" (arXiv 2510.07920): LLM-agent back-tested returns "evaporate" after the model's knowledge window ends; introduces FinLake-Bench and FactFin mitigation. Secondary commentary (UT McCombs) says best agents lose half or more out of sample. — [arXiv 2510.07920](https://arxiv.org/html/2510.07920v1), [McCombs](https://news.mccombs.utexas.edu/?p=19255)
- Look-Ahead-Bench (arXiv 2601.13770): reports alpha decay worse than -15 percentage points between periods for standard LLMs while point-in-time-trained models stayed stable. — [arXiv 2601.13770](https://arxiv.org/pdf/2601.13770)
- "Summoning the Oracle to Slay It" (arXiv 2605.24564): "parametric" look-ahead bias lives in model weights and is missed by input-data audits. — [arXiv 2605.24564](https://arxiv.org/pdf/2605.24564)
- TradeTrap (arXiv 2512.02261) examines reliability/faithfulness of LLM trading agents (no results seen). — [arXiv 2512.02261](https://arxiv.org/pdf/2512.02261)

**StockBench (arXiv 2510.02209)**: contamination-aware benchmark, 3 Mar to 30 Jun 2025 (82 trading days), $100k start. Most LLM agents (incl. GPT-5, Claude-4, Qwen3, Kimi-K2, GLM-4.5) failed to beat passive buy-and-hold on return and risk-adjusted return; best (Kimi-K2 per one summary) had much lower drawdown. Performance fell as universe grew from 5 to 30 stocks. Exact figures not retrieved. **[snippet-only; B]** — [arXiv 2510.02209](https://arxiv.org/html/2510.02209v1)

**LiveTradeBench (arXiv 2511.03628)**: 50-day live evaluation of 21 LLMs; headline: high LMArena scores do not imply better trading outcomes. **AI-Trader (arXiv 2512.10971, HKU)**: "live, data-uncontaminated" benchmark across US stocks, A-shares, crypto; says excess returns come more readily in liquid US markets than policy-driven markets. No numbers retrieved. **[snippet-only]** — [LiveTradeBench](https://arxiv.org/html/2511.03628v1), [AI-Trader](https://www.arxiv.org/pdf/2512.10971)

**AI Hedge Fund (virattt)**: README states educational/research proof-of-concept that "does not actually make any trades"; has a `--backtest` CLI flag; I found **no** published performance claims for it (forks/mirrors may show examples; unverified). — [search results](https://raw.githubusercontent.com/virattt/ai-hedge-fund/HEAD/README.md)

**FinGPT (AI4Finance)** README **[read]**: benchmarked only on sentiment tasks (weighted F1: FinGPT v3.3 FPB 0.882, FiQA-SA 0.874, TFNS 0.903, NWGI 0.643 vs GPT-4 0.833/0.630/0.808; its own table shows OpenAI fine-tune higher on FiQA-SA 0.887). FinGPT-Forecaster (next-week movement, Dow 30) is "not benchmarked"; disclaimer "NOT a recommendation to trade real money". So there is no trading-return claim to evaluate. — [FinGPT README](https://raw.githubusercontent.com/AI4Finance-Foundation/FinGPT/master/README.md)

**FinRL / FinRL-Meta** README **[read]**: no performance figures; "academic purposes"; "Nothing herein constitutes financial advice"; classic repo's last version entry 0.3.5 (2022-06-25), and it points users to FinRL-X / FinRL-Trading for live deployment. FinRL-Meta paper itself lists low signal-to-noise, survivorship bias and backtest overfitting as core challenges; a FinRL-ecosystem crypto paper (arXiv 2209.05559) says earlier DRL work "optimistically reported increased profits in backtesting" that may be overfit false positives. FINSABER includes FinRL as a tested RL baseline (no number retrieved). — [FinRL README](https://raw.githubusercontent.com/AI4Finance-Foundation/FinRL/master/README.md), [FinRL-Meta](https://arxiv.org/pdf/2211.03107), [arXiv 2209.05559](https://arxiv.org/pdf/2209.05559)

**FinMem / FinAgent** (author papers: FinMem arXiv 2311.13743, FinAgent arXiv 2402.18485): author-reported results; independent view is FINSABER above (both beaten by buy-and-hold on Sharpe). I did not read the original papers' numbers. — [FinMem](https://arxiv.org/pdf/2311.13743), [FinAgent](https://arxiv.org/pdf/2402.18485)

### Inferences
- The pattern is consistent across systems: short window (about 3 months), few tickers, no or low costs, LLM that may have seen the test period. Authors' own repos (TradingAgents, FinRL, FinGPT, Kronos, AI Hedge Fund) all disclaim real-money use.
- The single most credible independent number for Silkperfect's purposes is FINSABER's finding that buy-and-hold beats FinMem/FinAgent over about 20 years; it matches Silkperfect's own result that AI predictors trail an equal-weight hold.
- LLM agents tested on Indian equities would face an extra problem: LLM training data on NSE news is thinner, so contamination may be lower but also signal quality is untested.

### Gaps
- StockAgent: **not researched** (no query was run on it specifically and it did not surface in any other search); no data.
- FinMem/FinAgent/FinCon exact FINSABER tables, TradingAgents' own paper tables and dates could not be read (arxiv.org blocked); numbers above are snippet-level.
- No Reddit r/algotrading, r/quant or Hacker News threads were reachable or surfaced; community sentiment is not documented here beyond GitHub issues and blogs.
- No independent live out-of-sample test of TradingAgents or AI Hedge Fund found.

---

## 2. nof1 Alpha Arena and other live LLM trading contests

### Takeaway
Alpha Arena Season 1 (crypto perpetuals, 17 days, one run per model) crowned Qwen3-Max at about +22% while GPT-5 and Gemini 2.5 Pro lost over 55%; Season 1.5 (US-stock tokens) was won by an unreleased "mystery" model later identified as Grok 4.20. Even nof1's own founder says results may be luck; a Bloomberg-reported tally of 11 public contests found only 2 had a profitable median model.

### Cited Findings
- **Season 1:** six models (Qwen3-Max, DeepSeek V3.1, GPT-5, Gemini 2.5 Pro, Claude Sonnet 4.5, Grok 4), $10,000 each, crypto perpetual futures on Hyperliquid, autonomous, ended 3 Nov 2025 (about 17 days). — [Forklog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/), [KuCoin news](https://www.kucoin.com/news/flash/ai-trading-competition-alpha-arena-to-conclude-on-november-4) **[press, snippet-only]**
- Qwen3-Max finished first at about $12,231.82 (about +22%); other press tables: DeepSeek about +4.89%, GPT-5 about -62.66%, Gemini 2.5 Pro about -56.71%. No final Claude/Grok figures retrieved. Reports disagree on which models were profitable at the end (some say only Qwen and DeepSeek). **[secondary press; C]** — [PANews via MEXC](https://www.mexc.com/news/153114), [aurpay](https://aurpay.net/?p=23782), [GNcrypto](https://www.gncrypto.news/news/qwen-wins-alpha-arena-season-1-with-22-percent-returns/)
- nof1's own caveats: early results "may be the result of luck"; founder Jay Azhang: "Giving an LLM money right now and just having it go — that's not a thing yet." Commentators: results may be indistinguishable from a random walk; needs long runs and replication. **[press, snippet-only]** — [Forklog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/), [Bitcoin Magazine](https://bitcoinmagazine.com/business/alpha-arena-reveals-ai-trading-flaws-western-models-lose-80-capital-in-one-week)
- **Season 1.5** started 20 Nov 2025: eight models, four simultaneous competition modes (including "Monk Mode" and "Max Leverage"), US stock tokens on trade.xyz, about two weeks. A "Mystery Model" (later identified as xAI Grok 4.20) won, about +12% on average and profitable in all four modes; GPT-5.1 second, Gemini 3 third. Reported figures conflict: +12.11% ($12,193), 22.38% on a trade.xyz leaderboard, and a claim that "only Grok 4.20 has turned a profit". Winner identification rests largely on Forklog. **[press; unreconciled; C]** — [Forklog](https://forklog.com/en/ai-model-grok-4-2-triumphs-in-trading-tournament/), [GNcrypto](https://www.gncrypto.news/news/mystery-model-alpha-arena-season-1-5-winner/)
- **Season 2:** announced as adding web search, longer reasoning, more data sources, multi-step execution, "stronger statistical rigor". I found **no published Season 2 results, winner or dates** as of 24 Nov 2026. — [search summary](https://forklog.com/en/new-season-of-ai-trading-tournament-kicks-off/)
- **Bloomberg, 6 May 2026** ("AI Bots Auditioning for Wall Street Trading Are Mostly Losing", Justina Lee): most systems lose money, trade too much, and give wildly different decisions on identical instructions; contests "far from academically rigorous". Research blog Flat Circle (Jim Moran) tracked 11 public contests: each had at least one profitable model, but only 2 had a profitable median. Article text not fully read. **[snippet-only; B]** — [Bloomberg](https://www.bloomberg.com/news/articles/2026-05-06/ai-bots-auditioning-for-wall-street-trading-are-mostly-losing?srnd=all), [Bloomberg Law copy](https://news.bloomberglaw.com/banking-law/ai-bots-auditioning-for-wall-street-trading-are-mostly-losing), [ZeroHedge summary](https://www.zerohedge.com/markets/wall-street-keeps-testing-ai-traders-most-are-still-underperforming)
- Skeptic quoted by Bloomberg coverage: Alexander Izydorczyk (ex-Coatue) says none of the AI bots he tracks has shown sustained alpha. **[snippet-only]** — same Bloomberg search results above.
- Other live-style benchmarks: LiveTradeBench (50-day live, 21 LLMs), AI-Trader (HKU), StockBench (82 days) — see Section 1; all short windows.

### Inferences
- With six or eight models and 2-3 weeks, a top-ranked finish is what chance alone produces: one of N noisy runs must be first. Season 1's range (+22% to -63%) is mostly leverage and direction bets on a crypto sell-off, not demonstrated skill. Nothing here supports "an LLM trading agent has an edge".
- Because only the winner is publicised, survivorship bias applies to the "AI beat the market" headlines.

### Gaps
- nof1.ai leaderboard and methodology posts not reachable; Season 1 Claude/Grok final numbers, fees paid, and trade counts unknown.
- Season 2 results: none found. Other contests tracked by Flat Circle (names, dates) not retrieved.
- Prophet Arena and similar prediction-market arenas not searched.

---

## 3. Time-series foundation models for finance (Kronos, TimesFM, Chronos, Moirai, Lag-Llama)

### Takeaway
Independent preprints find zero-shot TimesFM/Chronos/Moirai give weak or negative out-of-sample R-squared on returns and generally fail to beat a random walk or simple baselines. Kronos's strong numbers are the authors' own and I found no independent replication or live results. This agrees with Silkperfect's NSE test.

### Cited Findings
- Rahimikia & Ni, "Re(Visiting) Time Series Foundation Models in Finance" (arXiv 2511.18578): off-the-shelf models weak at zero-shot daily excess-return forecasting, trailed CatBoost/LightGBM; Chronos-large out-of-sample R-squared -1.37%, TimesFM-500M -2.80%, directional accuracy about 51% or below. **[snippet-only; B]** — [arXiv 2511.18578](https://arxiv.org/html/2511.18578v1)
- Noguer i Alonso & Franklin (arXiv 2606.27100): TimeGPT, TimesFM-2.5, Moirai-2.0, Chronos, Chronos-2 on five US large caps; gains over random walk "small and sparse"; a supervised iTransformer beat them on META. **[snippet-only; B]** — [arXiv 2606.27100](https://arxiv.org/pdf/2606.27100)
- A preregistered evaluation on index futures (arXiv 2611.12141) cites: Konat & Sarwas (2026): four pretrained TSFMs did not beat the random walk on 19 fixed-income/FX instruments; Zhong et al. (2026): TSFMs did not beat simple volatility benchmarks on 5,000 Chinese stocks. Marconi (2025, arXiv 2507.07296): zero-shot TTM/Chronos competitive on some tasks but matched by specialised models. **[snippet-only, second-hand]** — [arXiv 2611.12141](https://arxiv.org/pdf/2611.12141), [arXiv 2507.07296](https://arxiv.org/pdf/2507.07296)
- Kronos (Tsinghua; AAAI 2026; NeurIPS 2025 listing) claims 93% RankIC improvement over the leading time-series foundation model and 87% over the best non-pretrained baseline (authors' benchmark). **[author claim; C]** — [NeurIPS page](https://neurips.cc/virtual/2025/132504), [arXiv 2508.02739](https://arxiv.org/abs/2508.02739)
- Kronos README **[read]**: no numeric backtest results given; backtest uses Qlib on China A-shares with a "simple top-K strategy"; "a demonstration... not a production-ready quantitative trading system"; says high-fidelity backtests should model costs, slippage, impact and does not say its demo does; model sizes mini 4.1M, small 24.7M, base 102.3M (open), large 499.2M (not open). — [Kronos README](https://raw.githubusercontent.com/shiyu-coder/Kronos/HEAD/README.md)
- A search for independent Kronos evaluation, live results or replication returned none. — [search results above](https://github.com/shiyu-coder/Kronos)
- Lag-Llama: no financial-return evaluation surfaced in any search.

### Inferences
- A daily-return forecast with R-squared below zero cannot be traded, whatever the direction hit-rate; the 51% hit rate is within noise and would be eaten by costs.
- Kronos is trained on candlestick data (not univariate returns) and its RankIC gains over other TSFMs may be real in-sample against weak baselines, but a RankIC edge on A-shares says nothing about NSE net returns; Silkperfect's own result (Kronos 12.8% vs 16.1% hold) is currently the only independent test I know of on India.

### Gaps
- No independent Kronos replication; no Moirai or Lag-Llama finance tests found; no NSE/India-specific TSFM study found.
- Papers not read in full (arxiv blocked).

---

## 4. Deep learning / RL in quant funds and academic evidence (Qlib, Gu-Kelly-Xiu, Renaissance/Two Sigma/Jane Street, Numerai, Kaggle)

### Takeaway
The strongest legitimate evidence for ML in markets is academic cross-sectional return prediction (Gu-Kelly-Xiu) and the secretive, capacity-limited Medallion fund; neither is a recipe a small team can copy. Numerai is the only open crowd system with an audited-looking track record, but its numbers are self-reported. Qlib's published benchmark shows modest (about 9-12% annual) returns on China data with caveats.

### Cited Findings
- **Gu, Kelly & Xiu (2020), Review of Financial Studies 33(5): 2223-2273** (NBER w25398): trees and neural nets perform best; gains come from nonlinear interactions; dominant signals are momentum, liquidity and volatility variants; an earlier draft reports ML-forecast portfolios with annualised Sharpe above 2.0 (gross, US equities, value-weighted deciles incl. small stocks; I could not verify the paper's 0.40% monthly out-of-sample R-squared or the NN long-short Sharpe). **[peer reviewed; A- for academic setting, but gross of costs and tilt to small/illiquid names per general critique, not verified here]** — [NBER](https://nber.org/papers/w25398), [RFS record](https://econpapers.repec.org/RePEc:oup:rfinst:v:33:y:2020:i:5:p:2223-2273.)
- **Qlib benchmarks (Microsoft)** **[README read]**: Alpha158 on CSI300 (China A-shares), mean over 20 seeds: LightGBM IC 0.0448, Rank IC 0.0469, annualised return 0.0901, information ratio 1.0164, max drawdown -0.1038; XGBoost 0.0780 / IR 0.907; LSTM 0.0381 / 0.556; Transformer 0.0273 / 0.397; TabNet 0.0227 / 0.368; DoubleEnsemble 0.1158 / IR 1.343 / MDD -0.092. README gives no test dates, says backtest changed at v0.8.0 (not comparable with older versions), and results are "for the entire workflow". Mirrors of older versions show LightGBM 0.11-0.13 annual return, so numbers are version-dependent. Notably the deep models (LSTM/Transformer/TabNet) are **worse** than gradient boosting. **[vendor benchmark; C+, in-sample-period unspecified]** — [Qlib benchmarks README](https://raw.githubusercontent.com/microsoft/qlib/main/examples/benchmarks/README.md)
- **Renaissance Medallion:** commonly cited about 66% gross / 39% net annualised 1988-2018, from Zuckerman's book; unaudited, closed to outsiders; Cornell (2019) estimated gross growth of $100 to about $398.7M. Renaissance's outside-investor funds did much worse (Institutional Equities +21.5% in 2016, Diversified Alpha +10.7% vs Medallion +25% after higher fees). **[journalistic, unaudited; C]** — [Morningstar](https://www.morningstar.com/columns/rekenthaler-report/medallion-fund-is-like-no-other), [Institutional Investor](https://www.institutionalinvestor.com/article/2bswymr8cih3jeaslxc00/portfolio/famed-medallion-fund-stretches-explanation-to-the-limit-professor-claims), [Business Insider India](https://businessinsider.in/finance/news/a-secretive-120-billion-hedge-fund-has-bested-warren-buffett-again-and-again-these-are-its-10-biggest-holdings-/articleshow/72159770.cms)
- **Two Sigma / Jane Street (firm-level):** no returns data found for Two Sigma; Jane Street publishes none (it is a market maker; consistent with Silkperfect's WHO_MAKES_MONEY note).
- **Numerai (fund, company-reported):** 2024 net return 25.45%, Sharpe 2.75 (net of fees, 0% risk-free), one down month; mid-2025 founder said about +6% net YTD; no full-year 2025 figure found; JPMorgan committed up to $500M (Aug 2025); AUM about $560M end-2025 and about $700M by Jul 2026 (company); one third-party 13F tracker shows different (equity-holdings-only) estimate. A viral "51% audited return" story belongs to a different firm (Vertus), not Numerai. **[self-reported; C; no independent audit found]** — [Numerai blog](https://blog.numer.ai/jpmorgan-secures-500m-capacity/), [The Block](https://www.theblock.co/news/business/2025-08-26-ai-hedge-fund-numerai-secures-up-to-500-million-from-jpmorgan-368342), [Hedgeweek](https://hedgeweek.com/news/quant-hedge-fund-numerai-secures-500m-jpmorgan-allocation), [Entrepreneur UK (Vertus mix-up)](https://uk.entrepreneur.com/?p=6415)
- **Numerai tournament payouts (company):** about $182,039 NMR paid in Jan 2026 and $325,564 in Feb 2026; over 1.1M NMR staked and treasury about 3.1M NMR (Jul 2026); $3.2M cumulative buybacks. Mechanics: stake NMR on your model, earn more NMR when predictions score well on later live data, **burn** part of the stake when they score badly. **[company; C]** — [Numerai monthly blog](https://blog.numer.ai/numerai-monthly-numercon-agents-staking-risk-1m-nmr-buyback/), [CryptoSlate release (Jul 2026)](https://cryptoslate.com/press-releases/numerai-completes-third-strategic-nmr-buyback-bringing-total-repurchases-to-3-2-million/), [Numerai staking docs via search](https://docs.numer.ai/numerai-tournament/staking)
- **Numerai criticism (forum/blog, dated, anecdotal; D):** returns for stakers largely track NMR token price; payout ratio shrinks as total stake grows; a former participant quit in 2023 citing falling NMR value and need to "win more and more just to keep up". No independent statistic for average payout vs burn found. — [Forum: Sustainable Payouts?](https://forum.numer.ai/t/sustainable-payouts/2561), [Why I quit Numerai](https://henders.one/2023/01/23/why-i-quit-numerai/), [Forum: Thoughts on Numerai](https://forum.numer.ai/t/thoughts-on-numerai/6556) (titles/snippets only)
- **Jane Street Kaggle competitions:** the 2020-21 Market Prediction contest used an anonymised-feature utility score with a live-evaluation private leaderboard; the later Real-Time Market Data Forecasting contest (2025) drew over 3,700 teams, $120k prize pool. I found no source documenting private-leaderboard shake-up magnitudes or whether winning models traded profitably. — [mlcontests.com summary](https://hn.jakechampion.name/reader/https://mlcontests.com/state-of-machine-learning-competitions-2025), [participant write-up](https://www.besthub.dev/articles/kaggle-jane-street-market-prediction-competition-summary-and-model-insights-accb0dc2927c)
- **Public "AI" fund products:** EquBot's AIIQ ETF (international) was liquidated in 2022; AIEQ (US) still trading in Mar 2026 (about $122M AUM, 0.75% expense ratio) with mixed/undated performance reports and Seeking Alpha criticism ("6 red flags"). I found no verified long-term comparison with the S&P 500. **[C/D]** — [AIIQ closure (SEC filing)](https://www.sec.gov/Archives/edgar/data/1540305/000089418922004560/equbotaiiqliquidationstick.htm), [Seeking Alpha](https://seekingalpha.com/article/4653759-aieq-deep-learning-etf-with-6-red-flags)

### Inferences
- The consistent academic finding (momentum, liquidity, volatility dominate; trees beat deep nets on tabular data) supports Silkperfect's observation that momentum worked and generic DL did not. Qlib's own table has LightGBM beating LSTM/Transformer.
- Numerai's own press metrics (Sharpe 2.75, JPMorgan allocation) are the best "ML crowd actually earned money" signal available but are not independently audited, and the token-denominated staker economics are separate from fund performance.

### Gaps
- Gu-Kelly-Xiu exact tables and later critiques (e.g., cost-adjusted, post-2016 decay) not retrieved.
- Two Sigma performance data not found. Numerai full 2025 return and per-stake ROI not found; Numerai docs unreachable (docs.numer.ai blocked).
- Jane Street Kaggle outcomes (shake-up, winners' real performance) not found.

---

## 5. Retail "AI trading bots" for sale: regulator warnings, audits, verified track records

### Takeaway
Regulators (CFTC, SEC, FTC, ASIC, EU/Asian authorities) have repeatedly warned that "AI trading bot" sales pitches with guaranteed or very high returns are a fraud pattern, and have brought enforcement cases. I found no credible study giving the percentage of retail EAs/bots that are profitable, and Myfxbook-verified results are mostly short, vendor-run and unaudited for forward performance.

### Cited Findings
- **CFTC customer advisory (Jan 2024) "AI Won't Turn Trading Bots into Money Machines":** fraudsters exploit AI interest to sell bots and signals promising unreasonably high or guaranteed returns; "AI technology can't predict the future or sudden market changes"; cites the Mirror Trading International case (bot promised at least 10% monthly). FINRA issued parallel guidance on the same day. **[regulator; A for the warning, not for any performance fact]** — [CFTC advisory](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/aitradingbots.html), [CFTC release 8854-24](https://www.cftc.gov/PressRoom/PressReleases/8854-24), [Orrick note](https://infobytes.orrick.com/2024-02-02/securities-regulators-issue-guidance-and-rfc-ai-trading-scams/)
- **SEC "AI washing" (18 Mar 2024):** Delphia paid $225,000 and Global Predictions $175,000 (total $400,000, neither admitting nor denying) for unsubstantiated claims about AI use (e.g., "first regulated AI financial advisor"); first SEC AI-washing actions. — [SEC release 2024-36](https://www.sec.gov/newsroom/press-releases/2024-36), [WilmerHale](https://www.wilmerhale.com/insights/client-alerts/20240327-sec-brings-two-more-ai-washing-enforcement-actions-against-investment-advisers-continuing-its-pursuit-of-misstatements-related-to-ai)
- **SEC 2026 actions** (reported Sept 2026): charges against seven firms over $14M WhatsApp "investment club" schemes promising AI-generated crypto returns, and a separate case over AI trading bots, fake SEC credentials and online relationships taking at least $15.3M; one advertised bot claimed $6.3M profit in 360 days. **[press summaries; B]** — [IBTimes](https://www.ibtimes.co.uk/fake-sec-credentials-ai-trading-bots-investment-scam-15-million-1823921), [WealthManagement](https://www.wealthmanagement.com/regulation-compliance/sec-charges-two-firms-with-15m-crypto-fraud-scheme), [Claims Journal (30 Sep 2026)](https://www.claimsjournal.com/news/national/2026/09/30/340451.htm)
- **FTC "Operation AI Comply" (Sept 2024):** sweep on deceptive AI claims; includes a business-opportunity scheme promising guaranteed income from "AI-powered" online stores (court halted it, receiver appointed) and DoNotPay ($193,000). I found no FTC action specific to a trading bot. — [FTC release](https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes), [Orrick](https://www.orrick.com/en/Insights/2024/10/FTC-Targets-Unfair-or-Deceptive-AI-Practices-With-Five-New-Enforcement-Actions)
- **Other regulators:** ASIC warning (May 2026) on fake crypto trading groups on WhatsApp/Telegram; NZ FMA warning about the "Txex/Whalefall" WhatsApp scam with fake participants; Austria FMA and Romania ASF warnings (2025) on bot-populated fake investment communities; US state attorneys general (Apr 2026) on AI-driven investment scam ads. — [ASIC via Cryptonews AU](https://cryptonews.com.au/news/asic-sounds-alarm-as-crypto-scammers-trap-investors-through-fake-trading-groups-133906/), [FMA NZ/Austria listing](https://www.fma.gv.at/en/?p=25408576), [FastBull on AGs](https://www.fastbull.com/brokersview/news/us-attorneys-general-warn-of-surge-in-aidriven-investment-scams-across-social-media-322953)
- **India/SEBI:** SEBI press release PR 20/2022 (10 Jun 2022) cautioned investors against unregulated platforms offering algo trading and not to share sensitive details. On 18 May 2026 SEBI chair Tuhin Kanta Pandey said SEBI is working on a framework for AI-based trading; a blog says a retail algo framework requiring registered strategies via brokers became mandatory 1 Apr 2026 (secondary, unconfirmed). I found no 2026 SEBI warning specific to AI "bots". SEBI's 91% of individual F&O traders lost money (2024-25) is cited in Silkperfect's REPORT, not re-verified here. — [Business Standard (2022)](https://bsppd.business-standard.com/article/markets/sebi-warns-investors-against-unregulated-platforms-offering-algo-trading-122061000769_1.html), [Newkerala (18 May 2026)](https://www.newkerala.com/news/a/sebi-working-framework-ai-based-trading-amid-growing-cyber-151.htm), [Sahi blog](https://www.sahi.com/blogs/sebi-algo-trading-rules-2026-what-every-retail-trader-must-know-before-april)
- **Myfxbook / FX-Blue verified EAs:** no rigorous study of what share of retail EAs are profitable found. Myfxbook itself warns real results are "almost always vastly worse" than hypothetical and that figures omit some fees/spreads/commissions. A verified account proves the history was imported from the broker, not that it will continue; most "verified" examples found are vendor posts on MQL5 with windows of weeks (e.g., a 14-day, 28-trade account) or self-described "fourth year" accounts. Evidence quality **D** (marketing) apart from the general caveats. — [MQL5 EA verification post](https://www.mql5.com/en/blogs/post/772467), [vendor 14-day post](https://www.mql5.com/en/blogs/post/776378), [DEV: how to read a Myfxbook record](https://dev.to/xauusdrobot/how-to-read-a-myfxbook-record-before-trusting-any-trading-ea-cc7)
- Scam pattern also appears in contest-adjacent form: Bloomberg's contest coverage and nof1's own founder both say turn-key "give an LLM money" is not ready (Section 2).

### Inferences
- For India specifically, any Telegram/WhatsApp "AI bot" asking for broker login or deposits matches the regulator-described pattern; nothing I found supports paying for a retail AI bot.
- A Myfxbook-verified record is a necessary filter (long live history, real broker, drawdown disclosed, not a gold-martingale), not evidence of an edge.

### Gaps
- No FTC/SEC/CFTC/SEBI quantification of retail bot loss rates; no academic audit of retail EA performance found; no named long-lived Myfxbook EA with independent audit identified.
- Regulator pages (sec.gov, cftc.gov, ftc.gov) read only through search summaries.

---

## 6. Public reviews and critiques: replicability and community sentiment

### Takeaway
The most useful public critique is academic and preprint-based (FINSABER, Alpha Illusion, Profit Mirage, StockBench), plus press scepticism of arena contests. I could not reach or surface Reddit/HN threads, so community sentiment is a gap rather than a finding.

### Cited Findings
- FINSABER (KDD 2026): LLM-strategy gains "deteriorate significantly" under long, broad tests; code and data at github.com/waylonli/FINSABER ('reproduce' branch holds the exact commands). — [arXiv 2505.07078](https://arxiv.org/html/2505.07078v3), [GitHub](https://github.com/waylonli/FINSABER)
- The Alpha Illusion, Profit Mirage, Look-Ahead-Bench, "Summoning the Oracle", TradeTrap: see Section 1. A substack review also covers the Alpha Illusion paper. — [Harbourfront Quant substack](https://harbourfrontquant.substack.com/p/how-effective-are-llm-trading-agents)
- GitHub #805 (TradingAgents) documents maintainers conceding model-level leakage cannot be removed by code. — [Issue #805](https://github.com/TauricResearch/TradingAgents/issues/805)
- dev.to critique of the TradingAgents buy-and-hold baseline (Section 1). — [dev.to](https://dev.to/trow126/the-most-starred-llm-trading-paper-claims-buy-and-hold-lost-523-it-actually-gained-912-1jj6)
- Press: Bloomberg 6 May 2026 and 1 May 2026 ("AI Agents Are Becoming Day Traders, But Gains Are Elusive"), ThinkAdvisor 6 May 2026, BabyPips explainer 9 May 2026, StartupFortune 14 Jul 2026. Titles/headlines only seen. — [Bloomberg 1 May](https://www.bloomberg.com/news/articles/2026-05-01/ai-tools-for-stock-trading-put-up-mixed-results?rand=299), [ThinkAdvisor](https://www.thinkadvisor.com/amp/2026/05/06/why-ai-bots-arent-ready-to-replace-your-fund-manager/), [BabyPips](https://babypips.com/news/explainer-ai-trading-bots-what-they-can-and-cant-do-2026-05-09), [StartupFortune](https://startupfortune.com/ai-trading-bots-are-losing-money-and-the-market-is-exposing-what-agentic-hype-hides/)
- Qlib outputs vary by version/data source (YahooFinance data "not very stable"), an independent replicability warning from a mirror README. — [Qlib mirror README](https://gh.hhj520.top/microsoft/qlib/blob/867667531dcf7d1f49cb98972ae2256abe790ddf/examples/benchmarks/README.md)

### Inferences
- Replicability problems are structural: non-deterministic LLM outputs (same prompt, different action), moving model versions, and unfixable weights-level leakage mean an LLM-agent backtest cannot be reproduced bit for bit even by the authors.
- Reviews are overwhelmingly sceptical; the only "success" claims come from the builders or from short contests.

### Gaps
- No r/algotrading, r/quant or Hacker News thread was reachable or returned by search; their consensus is not documented here.
- Several press pieces were seen only as headlines.

---

## 7. Practical: how a small team could use the ones with real evidence (cost and effort)

### Takeaway
Of everything surveyed, only three things have credible evidence and are usable by a small team: (1) simple momentum/factor signals (Gu-Kelly-Xiu's dominant signals; Silkperfect's own result), (2) Numerai as a no-capital ML competition with self-reported fund results, (3) Qlib as a free research framework, not an alpha source. LLM agents, FinRL, FinGPT and TSFMs are research tools with no demonstrated live edge.

### Cited Findings
- Qlib is open source, with Alpha158/Alpha360 pipelines and LightGBM/XGBoost/LSTM/Transformer/TabNet/DoubleEnsemble baselines; its own results are 0.078-0.116 annualised on CSI300 (details Section 4). — [Qlib benchmarks](https://raw.githubusercontent.com/microsoft/qlib/main/examples/benchmarks/README.md)
- Numerai: stake NMR to earn/burn; payouts come from Numerai treasury; Jan/Feb 2026 total payouts $182k and $326k across all participants (company figures), so rewards are small relative to the number of participants. — [Numerai monthly](https://blog.numer.ai/numerai-monthly-numercon-agents-staking-risk-1m-nmr-buyback/)
- FinRL repo says production use belongs to FinRL-X / FinRL-Trading and that the classic repo is educational. — [FinRL README](https://raw.githubusercontent.com/AI4Finance-Foundation/FinRL/master/README.md)
- FINSABER is released as a benchmarking framework with realistic costs and 20 years of S&P 500 data that Silkperfect could adapt as a **test harness** for any LLM-agent idea before spending on live data. — [FINSABER README](https://raw.githubusercontent.com/waylonli/FINSABER/main/README.md)
- AI Hedge Fund and TradingAgents run via LLM API calls; TradingAgents v0.7.1 offers `run_backtest` scoring decisions on realised alpha vs a regional benchmark with entry at the first close after the decision; its README says backtests are not replicable to published figures. — [TradingAgents README](https://github.com/TauricResearch/TradingAgents)

### Inferences (my judgement, not sourced; costs are rough guesses to be confirmed)
- **Numerai:** about 1-3 weeks to a first submission using free data and a LightGBM/ensemble pipeline; participation without a stake is possible per general knowledge (unverified here); staking real NMR adds crypto-price risk and burn risk; expected gain is small and not scaled to Silkperfect's capital. Treat as a skills-validation exercise, not an income source. Does not touch NSE data.
- **Qlib:** 1-2 weeks to reproduce on NSE data (Silkperfect already did); no reason to expect more than a LightGBM-on-factors result; best value is as a cross-sectional factor research harness for momentum-plus-quality/low-volatility combos listed in Silkperfect's "next" table.
- **LLM agents:** API cost per run is modest, but even a correct backtest on pre-cutoff data is contaminated. Only forward (paper) trading from today with a model whose cutoff precedes the test, logged and costed, would give usable evidence; budget at least 6-12 months of paper trading to see anything and still expect noise (see Alpha Arena sample-size issue).
- **FinRL / RL:** high effort and high overfitting risk (FinRL-Meta's own caveats); not recommended before simpler tests.
- **Retail bots:** avoid.
- Evidence ranking for a small Indian-equities team: (1) momentum with long holds, (2) factor/ML cross-section via Qlib as a research harness, (3) Numerai as a side learning project, (4) paper-trade an LLM agent as a long, low-priority experiment, (5) nothing else.

### Gaps
- Numerai participation cost/minimum stake and whether non-US (India) users can stake or be paid: docs unreachable; not verified.
- Actual API/compute cost per LLM-agent run and Numerai staking returns for a small stake not found.
- No evidence found that any of these has been applied successfully to NSE-listed equities.
