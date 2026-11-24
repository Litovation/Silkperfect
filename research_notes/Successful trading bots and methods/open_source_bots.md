# Open-source and retail trading bots/frameworks: real-world evidence, and how to use them (India focus)

Research date: 24 Nov 2026. Method note: in this sandbox only WebSearch snippets and github.com page fetches worked. Every other host failed DNS (hummingbot.org, sebi.gov.in, businesstoday.in, mdpi.com, arxiv.org (www.), dev.to, algotest.in, redlib mirrors); reddit.com is blocked by the tool; the `gh` API was refused for non-attached repos. So **all figures that came only from a search snippet are marked "(snippet, unverified)"**, and Reddit, HN, Trustpilot, G2 and YouTube were never read directly, only seen as search-result titles/snippets. Direct GitHub page reads are marked "(GitHub page, read 24 Nov 2026)".

Headline for the report writer: I found **no independently verified, aggregate live track record** for any of Freqtrade, Jesse, Hummingbot, QuantConnect/LEAN, NautilusTrader, vectorbt, Backtrader, OpenBB, Superalgos, Zenbot, 3Commas, Pionex or TradingView strategies. Public "profit" evidence is almost entirely vendor marketing, self-published dry-run results, or anecdotes. The strongest independent evidence found is negative or neutral (zero-expectation grid result, LLM-agent contest losses, SEBI retail loss data). This matches the Silkperfect finding that retail rule/ML bots do not beat buy-and-hold after costs.

---

## 1. What do live (not backtest) results look like for Freqtrade, Jesse, Hummingbot, QuantConnect/LEAN, NautilusTrader, vectorbt, Backtrader, OpenBB, Superalgos, Zenbot, Gekko, 3Commas/Pionex, TradingView? Any verified track records or leaderboards?

### Takeaway
No framework publishes verified live P&L for its user base. What exists: project popularity stats, vendor volume/payout figures (Hummingbot, QuantConnect), and self-reported anecdotes, the best-documented of which are paper-trading only. The frameworks themselves are tools; the evidence of "bots that work" is evidence about specific strategies and market structure, not the software.

### Cited Findings

**Freqtrade (crypto, Python, GPL; no India support)**
- 57.2k stars, 11.8k forks, 33,465 commits on develop; spot/futures on Binance, Bybit, OKX, Kraken, Hyperliquid, Gate, Bitget etc. README says "educational purposes only", "Do not risk money which you are afraid to lose", start with dry-run, authors assume no responsibility for trading results. Includes FreqAI (self-training ML). (GitHub page, read 24 Nov 2026) — [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade)
- No aggregate live-performance statistic exists. A search for community stats found only individual blog posts and a "FrequentHippo" Grafana dashboard linked from the README for sharing dry/live runs; nothing aggregated. (snippet, unverified) — [search results](https://github.com/gcarq/freqtrade)
- Freqtrade's own docs/strategy-collection warn: the default template "will most likely not be profitable out of the box"; "it is not at all uncommon for a strategy to achieve fantastic results in backtesting, only to perform very badly in a live situation"; many-small-profit strategies "will become losses in live due to slippage, especially on low volume pairs". (snippet of docs/forks, unverified wording) — [freqtrade docs fork](https://github.com/glonlas/freqtrade/blob/develop/docs/strategy-customization.md), [berlinguyinca strategies](https://www.Github.com/freqtrade/berlinguyinca-trading-strategies), [Backtesting Traps blog, 2021](https://brookmiles.github.io/freqtrade-stuff/2021/04/12/backtesting-traps)
- The most detailed "live" Freqtrade track records surfaced were promoter blogs (TrendRider); their own repo says results are paper-trading only, no real money risked; one post reports -$0.06 over 13 days of dry-run on Bybit; another dev backtested seven strategies and all lost money over a 24-month window. All single-author dev.to posts. (snippet, unverified) — [13 days 48 trades](https://dev.to/trendrider/13-days-48-trades-breakeven-then-i-fixed-one-thing-1d6j), [darkvolg/Trading](https://github.com/darkvolg/Trading)
- Dry-run vs live mismatch reports: a strategy with 75% backtest win rate fired zero trades in 44 days of dry-run on Coinbase; a 2021 GitHub report said two identically configured bots bought different pairs in dry-run vs live. (snippet, unverified) — [dev.to guide](https://dev.to/itrade_icu_ae8778833e3e8c/article-2-start-live-trading-or-paper-trading-freqtrade-trade-command-explained-586k)

**Hummingbot (crypto market making, Apache-2.0)**
- 21.4k stars, 5.2k forks. README claims "Over the past year, Hummingbot users have generated over $34 billion in trading volume across 140+ unique trading venues" (vendor claim, volume not profit). Strategies/executors: PMM, Avellaneda MM, cross-exchange MM, grid, DCA, arbitrage, TWAP, LP. No mention of India. (GitHub page, read 24 Nov 2026) — [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot)
- Year-1 "Miner" recap (vendor): $376k total rewards paid, $837M filled volume, 1,622 users. Hummingbot's own blog says ~40% of new users still run bots after 1 month and infers (admittedly not measures) that they are profiting. Earlier marketing claimed 10-50% annual returns; the company admitted early reward yields looked "absurdly high" due to low participation. (snippet of vendor blog, unverified) — [Hummingbot blog: miner year 1 recap](https://hummingbot.org/blog/hummingbot-miner-year-1-recap/), [does community-based market making work](https://hummingbot.org/blog/does-community-based-market-making-work/)
- Hummingbot's own docs say rewards are not guaranteed, market making is "a marathon, not a sprint", and trading PnL is separate from rewards, so a bot can lose on trades while earning rewards. (vendor docs, snippet) — [Top beginner misconceptions](https://docs.hummingbot.org/academy-content/top-beginner-misconceptions-about-market-making/)
- User anecdotes in vendor-hosted interviews: one competition entrant -14.57 PnL (~-1.2%); a "liquidity miner" claims 0.5-3% per trade (self-described, unverified); another says 5 orders per side lets them "break even or even turn a profit". A Substack titled "How I lost 20% in 20 minutes" exists (content not read). (snippets, unverified) — [Hummingbot interview](https://hummingbot.org/blog/interview-with-liquidity-miner-david-salter/), [Substack](https://thecryptoquant.substack.com/p/how-i-lost-20-in-20-minutes)

**QuantConnect / LEAN (multi-asset, Apache-2.0 engine)**
- LEAN repo: 22.7k stars, Apache-2.0, 13,520 commits; repo page itself lists no brokerages. (GitHub page, read 24 Nov 2026) — [QuantConnect/Lean](https://github.com/QuantConnect/Lean)
- Vendor claim: >375,000 live strategies deployed since 2012 (deployments, not profits). Alpha Streams marketplace lets accounts as small as $10k license community algos; a forum user complains only very few algos are identifiable for licensing. Third-party "Miles Capital Management" page shows self-reported 2026 YTD Nasdaq futures live results run on QC (e.g. net profit $44,004.98) with a standard past-performance disclaimer. No aggregate profitable-share study found. (snippet, unverified) — [QuantConnect home](https://www.quantconnect.com/?lang=en), [forum](https://quantconnect.com/forum/discussion/8712/internfund-begins-live-trading/p1/comment-24554), [Miles Capital page](https://sempolmedia.github.io/Miles-Capital-Management/performance.html)

**NautilusTrader (Rust/Python, LGPL-3.0)**
- 31.8k stars, ~4.3k forks. Live adapters: Binance, Bybit, OKX, Coinbase, Kraken, Deribit, dYdX, Hyperliquid, Interactive Brokers, Betfair, Polymarket (Kalshi beta). No Indian broker. Describes itself "production-grade" but warns it is under active development with breaking changes, v2 release candidates not recommended for live capital, and live execution "may not reproduce" simulated behaviour. (GitHub page, read 24 Nov 2026) — [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)

**Gekko (dead) / HaasOnline commentary**
- Original Gekko repo archived Feb 2020; HaasOnline (a competitor) says the main developer moved to market-making services. I found no statement from the author that it was unprofitable; reason for abandonment is unverified. (snippet, competitor blog) — [HaasOnline: the fall of more trading bot companies](https://www.haasonline.com/the-fall-of-more-trading-bot-companies-and-projects/)

**3Commas / Pionex (commercial grid/DCA bots)**
- No audit or peer-reviewed study of realised after-fee returns for either. Claims like "grid bots 15-40% annualized in range-bound markets (60-70% of the time)" and ">80% of retail bot users fail to beat benchmark" are uncited blog assertions; Bitget's "grid 65-75% success rate" is a vendor estimate. (snippets, unverified) — [Altrady blog](https://www.altrady.com/blog/crypto-bots/are-ai-crypto-trading-bots-profitable-2026), [Bitget wiki](https://www.bitget.com/wiki/do-trading-bots-really-work)
- Trustpilot (self-selected, moderated): Pionex 2.5/5 from ~623 reviews, many complaints about frozen withdrawals/account restrictions; one user review says use spot grid but avoid futures grid. 3Commas 4.5/5 from ~1.75-2K reviews, mostly short positive reviews (company replies to all negatives). Ratings measure service experience, not trading P&L. (snippet, unverified) — [Pionex Trustpilot](https://www.trustpilot.com/review/Pionex.com), [3Commas Trustpilot](https://uk.trustpilot.com/review/3commas.io?page=4)

**LLM "AI agent" traders (relevant to the agent question)**
- Nof1 Alpha Arena Season 1 (17 Oct-3 Nov 2025, real $10k each on Hyperliquid perps): 4 of 6 LLMs ended in loss; ChatGPT (GPT-5) lost ~63% by one report; Qwen3 Max won; standings reversed multiple times mid-contest; Nof1 said early PnL was dominated by fees from over-trading (Qwen 1,418 trades vs another model 158). A separate US-tech-stock round: of 32 trading results only 6 gains, aggregate roughly -33%. Nof1's founder said "giving an LLM money right now and just having it go is not a thing yet". (snippets, unverified; figures differ by outlet) — [Forklog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/), [Protos](https://protos.com/llm-crypto-trading-contest-finds-llms-cant-trade-crypto), [KuCoin news summary](https://www.kucoin.com/news/flash/ai-trading-models-struggle-in-live-market-tests-majority-of-systems-report-losses), [ThinkAdvisor May 2026](https://www.thinkadvisor.com/amp/2026/05/06/why-ai-bots-arent-ready-to-replace-your-fund-manager/)

**OpenAlgo (India-specific, see Q3):** 3.0k stars, AGPL-3.0; no track record claims. (GitHub page, read 24 Nov 2026) — [marketcalls/openalgo](https://github.com/marketcalls/openalgo)

### Inferences
- Because no framework publishes verified aggregate P&L and survivorship bias is acute (losers switch bots off; a blog notes this), star counts and volume figures should not be read as evidence of profitability.
- Hummingbot's "volume" and "rewards paid" are revenue-to-the-ecosystem metrics; rewards are paid by token projects/exchanges to buy liquidity, so any user profit is a subsidy, not a market edge.
- LLM-agent contests (short, ~2 weeks, tiny sample) are noise-dominated; the consistent finding is that fees from over-trading dominate, mirroring Silkperfect's daily-vs-monthly result.

### Gaps
- Jesse, vectorbt, Backtrader, OpenBB, Superalgos, Zenbot, TradingView strategies: I did not run searches or fetches specific to them (research-budget limit and host blocks); no live-result evidence gathered. Background (not sourced here): Backtrader is unmaintained, vectorbt/OpenBB are research/backtest tools not execution engines, Zenbot and Gekko are effectively dead. Treat as unverified.
- Reddit r/algotrading, r/freqtrade, r/IndianStreetBets, HN, G2, YouTube audits: not read directly (blocked). Only thread titles/snippets seen (see Q4).
- Hummingbot blogs and docs could not be fetched (DNS); all Hummingbot vendor figures are from snippets.

---

## 2. Which strategy types survive live (market making, funding-rate arbitrage, grid, trend following, DCA)? What failed?

### Takeaway
Evidence for survival is strongest for structural/liquidity-provision carry (market making with rewards; basis/funding carry) and weakest for directional prediction. Even the carry strategies have shrinking, regime-dependent returns and tail risks. Plain grid has an academic zero-expectation result before fees.

### Cited Findings
- Grid: an arXiv preprint (June 2025, Chen, Chen, Jang, National Taiwan University; not peer reviewed) finds plain grid trading has roughly zero expected value without insight into market trends, so after fees investors risk losing money; it proposes a "Dynamic Grid" strategy that resets the grid; model uses 0.0008 maker fee. (snippet, unverified) — [arXiv 2506.11921](https://arxiv.org/abs/2506.11921v1)
- Grid failure mode in trends: bot sells all inventory on the way up or buys all the way down (BloFin Academy, exchange educational content). A Stevens Institute student project on Bybit grid bots reports ML overlays gave no significant improvement over plain grid (methodology unverified). — [BloFin Academy](https://blofin.com/academy/education/grid-trading-strategy), [Stevens FSC](https://fsc.stevens.edu/cryptocurrency-market-making-improving-grid-trading-strategies-in-bitcoin/)
- Funding-rate arbitrage: a Jan 2026 academic paper (MDPI Mathematics 14(2):346) reportedly finds only ~40% of top opportunities earn positive returns after transaction costs and spread reversals, with forced exits in 95% of opportunities. (snippet, unverified; page not readable) — [MDPI](https://www.mdpi.com/2227-7390/14/2/346)
- Funding yields low in the Nov 2025-May 2026 regime: one developer's log says average annualised rates 1.2-1.8% on most pairs, max observed under 11%; a Feb 2026 analysis puts BTC at 0.02% average rate = 3.99% APY while altcoins swing -1,577% to +335%. BitMEX Q2 2026 report cites internal carry ~+4% annualised unlevered and Hyperliquid paying ~7.17% more annualised funding than Binance on BTC (2023-2026). Both snippet-level; blogs are anecdotal. — [BitMEX Q2 2026 derivatives report](https://www.bitmex.com/blog/2026q2-derivatives-report), [askrubyai blog](https://askrubyai.github.io/blog/posts/2026-02-14-funding-rate-arbitrage), [jyotirmoy17 bot post](https://jyotirmoy17.github.io/post-crypto-bot.html)
- Delta-neutral retail products failed: Stream xUSD depegged >77% in early Nov 2025; an AlphaUSDC Morpho vault had ~$18M frozen in June 2026; Ledger notes the common failure is funding sign flip. (snippet, unverified) — [Ledger glossary](https://www.ledger.com/academy/glossary/funding-rate-arbitrage), search summary above.
- Market making: Hummingbot's own material says profit is distinct from rewards; user anecdotes range from -1.2% to break-even (see Q1). No independent aggregate.
- Over-trading kills returns in live LLM contests (Alpha Arena; see Q1).
- Crypto-bot "73% of automated crypto accounts fail within six months" is repeated across low-quality sources without a primary citation — do not rely on it. (snippet, unverified) — [lenz.io](https://lenz.io/q/are-retail-crypto-trading-bots-profitable)
- Trend following / DCA: no independent live evidence found in this search for retail bots specifically. (see Gaps)

### Inferences
- Strategies that "survive" are those paid for providing something (liquidity, hedging, risk transfer) rather than predicting price, consistent with Silkperfect's finding that only slow momentum (a risk premium, ~3-6 month holds) beat holding.
- Carry yields compress as capital crowds in (funding 1-4% in 2026 vs. much higher in 2021 bull markets, background unsourced), so a retail Indian team gains little from crypto carry, which is also hard to access from India.
- Grid/DCA are payoff reshapers, not edges: a zero-expectation result before fees means they lose after fees on average.

### Gaps
- No independent live data on trend following, DCA bots, or market-making profitability after inventory losses.
- Could not read the MDPI paper or arXiv grid paper in full (hosts blocked).

---

## 3. Costs, setup effort, and use with Indian markets (Kite Connect, Upstox, OpenAlgo, Dhan, Angel One SmartAPI, Streak, Tradetron, AlgoTest); what India users report

### Takeaway
For Indian equities the practical stack is a broker API (Kite/Upstox/Dhan/Angel) plus either OpenAlgo (unified REST bridge) or custom Python; Freqtrade/Hummingbot/Nautilus do not natively support NSE. Since 1 April 2026 the SEBI retail-algo framework (static IP, algo ID, broker-controlled environment) applies and changes how self-built bots connect. No independent evidence of Indian retail algo-platform profitability was found.

### Cited Findings

**Costs / tooling**
- Zerodha Kite Connect: free "personal" tier (orders, positions, holdings, funds; no live or historical market data); paid tier Rs 500/month per API key including live and historical data (cut from Rs 2,000 to Rs 500). Support page says from Oct 2026, paid users generating >= Rs 2,000 brokerage in a month get 500 Developer Credits covering the next month; sources describe the waiver slightly differently, verify on Zerodha. (snippet, unverified) — [Zerodha support: charges for Kite APIs](https://support.zerodha.com/category/trading-and-markets/kite-api/articles/what-are-the-charges-for-kite-apis), [Kite forum: fees to Rs 500](https://kite.trade/forum/discussion/comment/49597), [Zerodha Kite Connect](https://zerodha.com/products/api)
- Upstox and Dhan API pricing: not searched; gap.
- OpenAlgo (marketcalls, AGPL-3.0, free self-hosted): 39 broker plugins (incl. Zerodha, Upstox, Dhan, Angel One per sources; also Delta Exchange crypto); unified REST API (76 method/path pairs); Python strategy host, no-code Flow builder, "Analyzer Mode" sandbox with Rs 1 crore virtual capital, Telegram/MCP/ChartInk integrations, AI agent with order approval; needs Python 3.12+, `uv run app.py`, runs on 2GB RAM/1 vCPU; ~3.0k stars, 1.4k forks, 5,764 commits; the page says nothing about SEBI compliance. (GitHub page, read 24 Nov 2026) — [marketcalls/openalgo](https://github.com/marketcalls/openalgo). Other sources disagree on broker count (24+ to 36), i.e. count has grown over time. (snippet) — [OpenAlgo intro](https://www.marketcalls.in/openalgo/introducing-openalgo-v1-0-the-ultimate-open-source-algorithmic-trading-framework-for-indian-markets.html)
- Streak (Zerodha; no-code, TA-based, backtest + paper trade, no strategy marketplace; "deploying" a strategy does not necessarily auto-execute) vs Tradetron (no-code, strategy marketplace, NSE/BSE/MCX, many brokers) vs AlgoTest (options backtesting + execution, "NSE/BSE empanelled" per its own blog). Most comparison pages are by AlgoTest (vendor bias). Techjockey: AlgoTest 4.6/5 from 8 reviews; Tradetron 4.2/5 from 17 reviews (tiny samples). A TechEnclave forum post alleges Tradetron's marketplace has unvetted, unaudited strategies by self-styled gurus (single anonymous claim). — [AlgoTest vs Streak (vendor)](https://algotest.in/blog/algotest-vs-streak/), [Techjockey Tradetron](https://www.techjockey.com/reviews/tradetron), [Chittorgarh Streak review](https://www.chittorgarh.com/article/zerodha-streak-review-algo-trading-for-retail-investors/516/), [TechEnclave](https://techenclave.com/goto/post?id=2291022)
- Freqtrade, Hummingbot, NautilusTrader: no Indian equity broker adapters (Nautilus lists only Interactive Brokers as a stock broker). LEAN's brokerage list not visible on repo page; unverified. (GitHub pages, read 24 Nov 2026) — links in Q1.

**Regulation (SEBI retail algo framework)**
- Circular 4 Feb 2025 "Safer participation of retail investors in algorithmic trading"; delayed; brokers missing milestones barred from onboarding new retail API-algo clients from 5 Jan 2026; full framework applicable to all brokers from 1 Apr 2026. (snippet; Business Standard / SEBI notice) — [Business Standard](https://www.business-standard.com/markets/news/sebi-extends-retail-algo-trading-framework-rollout-to-2026-125093000956_1.html), [SEBI PDF Sep 2025](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2025/1759232056254.pdf)
- Per broker explainers: open APIs discontinued; access via client-specific API keys tied to a registered static IP (Angel One: orders accepted only from the registered primary static IP; NSE allows one IP plus backup); exchange-issued Algo ID per strategy; mandatory 2FA/audit trails from 1 Apr 2026; one blog claims black-box algos need a Research Analyst licence (single-source, unverified). — [Angel One SmartAPI changes](https://www.angelone.in/news/market-updates/what-s-changing-in-angel-one-s-smartapi-access-from-april-1-2026), [5paisa](https://www.5paisa.com/news/sebi-tightens-algo-trading-rules-with-mandatory-2fa-and-audit-trails-from-april-1), [Sahi](https://www.sahi.com/blogs/sebi-algo-trading-rules-2026-what-every-retail-trader-must-know-before-april), [Fyers](https://fyers.in/blog/sebi-algo-trading-rules-and-regulations-in-india/)

**India outcome data (not algo-specific)**
- SEBI F&O study FY2024-25 (July 2025): 91% of individuals lost money; net retail loss Rs 1.05 lakh crore, up 41% from Rs 74,812 crore. FY2025-26 (SEBI studies reported Aug 2026): ~87.7-88% of individuals lost, aggregate ~Rs 91,685 crore, active individual traders 98.1 lakh to 78.6 lakh (~-20%), options ~92% of losses; 99% of FPI and proprietary-trader profits earned by "algo entities" (any entity with >= 1 algo order in the year). NISM piece: 93% of 1.13 crore intraday traders lost money (2022-24). Algos = 57% of cash-equity trades (April, per NSE data cited) and ~70% of F&O in FY25. (snippets; SEBI PDF unreachable) — [Moneylife FY25](https://moneylife.in/article/91-percentage-of-retail-traders-lost-money-in-derivatives-losses-in-fo-surged-41-percentage-to-rs105-lakh-crore-in-fy25-sebi-study/77613.html), [Business Today FY26](https://www.businesstoday.in/markets/story/rs91685-cr-lost-88-of-individual-traders-lost-money-in-fy26-options-drove-92-of-losses-550474-2026-08-21), [Open Magazine](https://openthemagazine.com/business/sebi-fo-loss-study-explained-why-9-in-10-retail-traders-lost-91685-crore-in-fy26), [NISM](https://www.nism.ac.in/blog/equity-linked-exchange-traded-derivative-contracts-the-retail-rush-and-regulatory-measures/), [Outlook Business](https://www.outlookbusiness.com/markets/algos-have-rewritten-the-script-for-trading-in-india-its-time-for-retail-investors-to-play-it-smart)
- Persistence: one SEBI study reportedly found only ~1 in 200 traders profitable every year. (snippet, unverified)
- I found no SEBI figure for the share of retail *algo* users who are profitable.

### Inferences
- "Algo entities make 99% of FPI/prop profit" is about institutional speed/market-making infrastructure, not retail bots on Kite/Upstox; it does not imply retail algos profit.
- For Silkperfect, OpenAlgo + Upstox (already planned) is a sensible execution bridge, but the static-IP/algo-ID regime means a home connection or cloud VM needs a registered static IP and likely broker-side approvals; check each broker's April 2026 onboarding.
- Rs 500/month data fees are trivial vs the Rs 20-45 per-order costs already in Silkperfect's small-account results; infrastructure cost is not the binding constraint, trading cost is.

### Gaps
- Upstox, Dhan, Angel SmartAPI pricing and rate limits not retrieved.
- Streak/Tradetron/AlgoTest pricing and independent user P&L: none found (vendor comparisons only). Reddit r/IndianStreetBets and Trustpilot/MouthShut for these platforms not reached.
- SEBI primary PDFs unreachable; all SEBI numbers are from press snippets, and FY26 outlets give slightly different framing (87.7% vs "88%").

---

## 4. Public reviews: Reddit, HN, Trustpilot/G2, YouTube audits (independent vs vendor)

### Takeaway
Independent public commentary is overwhelmingly anecdotal and skeptical; the positive claims come from vendors, affiliate content and promoters. I could not read Reddit/HN/YouTube directly, so no thread-level evidence is quoted.

### Cited Findings
- Independent/skeptical: HN commenters (2012-era threads) describe retail as the flow professionals pick off, and note the common story is "how I lost $Xk"; a Blind thread from a trading engineer and an algo developer say they would not recommend retail algo trading; another says low-volume bots were profitable but not enough to live on. (snippet, unverified) — [HN item 4748624 mirror](https://home5.southeastasia.cloudapp.azure.com/item?id=4748624), [Blind: running trading bots personally](https://www.teamblind.com/post/running-trading-bots-personally-as-an-ex-professional-trading-engineer-uwekgmjs)
- r/algotrading threads exist on "I made and lost over 500k algotrading" (Mar 2025) and "what lesson learned the hard way" (Jun 2023), "lessons from live testing" (Jul 2024); contents not read. — [mirror 1](https://redlib.astrial.org/r/algotrading/comments/1jj15c5/i_made_and_lost_over_500k_algotrading/mjjvb3g), [mirror 2](https://axebps-redlib.hf.space/r/algotrading/comments/146nvvu/what_algo_trading_lesson_have_you_learned_the), [mirror 3](https://lr.sudovanilla.org/r/algotrading/comments/1e4xk9m/lessons_from_live_testing)
- Dev-blog post-mortems (single authors): ML crypto bot lost money, data leakage/curve fitting, leverage-ROI pitfall in Freqtrade (stoploss/ROI applied on leveraged profit ratio). (snippet, unverified) — [tildalice](https://dev.to/tildalice/my-ml-crypto-trading-bot-lost-money-2-hard-lessons-5e6a), [gilbran](https://dev.to/gilbran_laureano_fa15b79e/i-lost-80-on-my-trading-bot-heres-what-i-rebuilt-2m51)
- Vendor/affiliate (treat as marketing): Bitget wiki, MEXC-hosted and FXStreet press releases ("Do AI trading bots really work in 2026"), Altrady, Spark.money comparisons, AlgoTest comparison blogs, earthweb Gekko page. The "65% of volume automated / 3% came out ahead" figure came from a single MEXC-hosted blog with no source — do not use. — [FXStreet PR](https://www.fxstreet.com/press-releases/do-ai-trading-bots-really-work-in-2026-6-ai-crypto-trading-platforms-reviewed-for-profit-potential-202604281330), [MEXC](https://www.mexc.com/news/1150973)
- Academic: Cornell Tech paper on collective crypto trading schemes (pooled copy-trading) finds them inherently vulnerable to losses and insider exploitation (different from retail bots, but relevant to Tradetron-style marketplaces). — [Yahoo Finance summary](https://finance.yahoo.com/news/popular-collective-crypto-trading-strategy-154213773.html)
- Trustpilot/G2/Techjockey ratings summarized in Q1 and Q3 (service-quality ratings, small or self-selected samples).
- YouTube creator audits: none found or read.

### Inferences
- The lack of any large independent audit is itself informative: if retail bots reliably profited, platforms and exchanges would publish verified cohort data; none do.
- Selection bias (losers quit quietly) means positive anecdotes are overrepresented.

### Gaps
- Direct reading of Reddit (r/algotrading, r/freqtrade, r/IndianStreetBets), HN, G2 and YouTube was not possible; a follow-up with an environment that allows reddit.com, hn.algolia.com, trustpilot.com, g2.com, hummingbot.org, sebi.gov.in, arxiv.org would close this.
- No academic audit of 3Commas/Pionex/Freqtrade user outcomes found; I could not confirm a 3Commas 2022 API-key leak (search did not surface it) — not claimed here.
