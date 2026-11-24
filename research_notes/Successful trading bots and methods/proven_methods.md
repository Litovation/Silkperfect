# Systematic investing/trading methods with the strongest long-run evidence after costs (momentum focus), and India implementability

Compiled 24 Nov 2026.

**Reliability warning (read first).** Every WebFetch call failed with DNS errors, so no primary page was opened. Blocked hosts: niftyindices.com, econpapers.repec.org, alphaarchitect.com, nber.org, aqr.com, kotakmf.com. Everything below comes from WebSearch result summaries, i.e. snippets, and is **unverified against the primary document** unless stated. Figures from different dates and aggregator sites often disagree; conflicts are flagged. Numbers I recalled from memory, with no source found this session, appear only under "Gaps" and are labelled as recalled, not verified. To fix this, allow niftyindices.com, nber.org, aqr.com, alphaarchitect.com and econpapers.repec.org in the session network settings and re-run.

Evidence ranking used (strongest first, my judgement from the cited material): (1) cross-sectional momentum and time-series trend, which are multi-century, multi-asset and survive cost studies; (2) value, quality and low-vol, which are well documented but with long dry spells and decay; (3) covered calls/put-write, which are a risk transformation more than extra return; (4) post-earnings drift and short-term reversal, which have decayed or are cost-limited; (5) stat arb/pairs, which are institutional-only and have almost no retail-net evidence found.

---

## 1. Momentum: long-run evidence, and how it crashes

### Takeaway
Price momentum is the most replicated anomaly: it is documented in US stocks from 1965, in other countries, across asset classes, and in data back to 1800. It has negative skew. It crashes in "panic" rebounds after market declines with high volatility, and those crashes are partly forecastable. Costs reduce but do not eliminate it in large-cap, liquid universes.

### Cited Findings
- Momentum was first documented in US common stocks for 1965–1989 by Jegadeesh and Titman (1993) and Asness (1994), per a citing paper in the search results. — [NBER search results, Daniel-Moskowitz cites](https://www.nber.org/system/files/working_papers/w20439/w20439.pdf) (snippet only)
- Daniel and Moskowitz, "Momentum Crashes" (JFE 2016, vol 122, pp 221–247; NBER w20439): momentum has strong average returns but is negatively skewed, with infrequent and persistent strings of losses. Crashes occur in "panic" states, following market declines and when market volatility is high, and are partly forecastable. The named crash episodes are July/August 1932 and March–May 2009; the past three-year market return was negative at the start of each. — [NBER w20439](https://www.nber.org/papers/w20439) (snippet only)
- The same paper's dynamic strategy scales WML (winners-minus-losers) exposure so conditional volatility is proportional to the conditional Sharpe ratio, and gets roughly double the unconditional Sharpe of static momentum. The authors also say a strategy using forward-looking betas to time crashes is not implementable, and that real-time betas do not improve performance. — [NBER w20439 / Columbia copy](https://business.columbia.edu/sites/default/files-efs/pubfiles/4607/mom11.pdf) (snippet only)
- Geczy and Samonov, "215 Years of Global Multi-Asset Momentum: 1800–2014": the dataset covers 47 country equity indices, 48 currencies, 43 government bond indices, 76 commodities, 301 global sectors and 34,795 US stocks. Momentum is significant gross within all asset classes except commodity spot prices. Average monthly long-short gross return is largest in country equity markets (0.88% per month) and smallest in country bond series (0.13% per month). Cross-asset-class correlations of momentum returns are low over the long run but have risen significantly recently. — [Alpha Architect summary](https://alphaarchitect.com/the-worlds-longest-multi-asset-momentum-investing-backtest/), [Quantpedia](https://quantpedia.com/amazing-paper-related-to-several-momentum-strategies/) (secondary summaries; paper is SSRN 2607730 per the search tool)
- A separate US-stock study built a 1801–1926 out-of-sample test of momentum discovered in post-1927 data. — [Alpha Architect, "Momentum has serious mojo"](https://alphaarchitect.com/2013/07/momentum-has-serious-mojo/) (snippet only; the search result describes it, but the effect size was not given)
- Asness, Moskowitz and Pedersen, "Value and Momentum Everywhere" (JF 2013, 68(3), 929–985): value and momentum premia exist across eight markets and asset classes. Each is positively correlated with itself across markets. Value and momentum are negatively correlated with each other. Value loads positively on liquidity risk and momentum loads negatively. — [Pedersen paper PDF](https://pages.stern.nyu.edu/~lpederse/papers/ValMomEverywhere.pdf) (snippet only)
- A 2023 Pacific-Basin Finance Journal paper on Indian stocks reports significant intermediate- and long-term price momentum (see section 4). — [IDEAS](https://ideas.repec.org/a/eee/pacfin/v82y2023ics0927538x23002640.html)

### Inferences
- Silkperfect's result (momentum beats equal-weight, with deep falls and a lag in recent years) is consistent in shape with the literature. Negative skew, crashes after drawdowns, and a long dry spell are expected features, not evidence the method is broken.
- The 2025–26 lag follows a market with weak or negative returns (Silkperfect's equal-weight 200 returned +4.9% in 2025 and -1.1% in 2026). Daniel-Moskowitz would predict momentum suffers most in the rebound after a market decline, which is worth checking in the data around the 2025 and 2026 turns.
- Six years and t=1.5–1.8 cannot confirm or reject a premium. The multi-century evidence is what supports the prior; the local backtest only checks that nothing is badly broken in India's liquid names.

### Gaps
- Primary-source effect sizes (Jegadeesh-Titman monthly spread, Daniel-Moskowitz WML worst-month and drawdown figures, century-of-momentum Sharpe) could not be retrieved. From memory and unverified: JT 1993 reported roughly 1% a month for 6-month formation/holding; Daniel-Moskowitz report WML losing over 90% in 1932 and about 70% in 2009. Treat these as recalled, not sourced.
- No data on whether the premium is concentrated in the long (winner) leg versus the short leg. This matters for India, where long-only is the retail reality.

---

## 2. Fixes for momentum's weaknesses

### Takeaway
Best-supported fixes, in rough order: (a) volatility scaling or dynamic risk-managing of the momentum portfolio, which cuts crashes; (b) residual/idiosyncratic momentum, which improves Sharpe but may not reduce crash risk; (c) information-discreteness ("frog-in-the-pan") and 52-week-high variants, which improve the signal but are less tested net of costs; (d) market-state or trend filters, which are intuitive but have the thinnest independent evidence in my results. Almost every fix was evaluated long-short and gross, not in a long-only Indian retail portfolio.

### Cited Findings
- **Volatility-managed momentum.** Barroso and Santa-Clara, "Momentum has its moments" (JFE 2015): momentum's own risk varies strongly over time, from 3% to 128% annualized volatility per a CFA Institute blog by Barroso. Managing this risk "virtually eliminates crashes and nearly doubles the Sharpe ratio". — [CFA Institute blog](https://blogs.cfainstitute.org/blog/2018/01/17/timing-the-market-momentum-and-beyond), [UCP repository](https://ciencia.ucp.pt/en/publications/momentum-has-its-moments/) (snippets; the absolute Sharpe values I tried to confirm (0.53 to 0.97) were not found)
- A crash-indicator study reports raw momentum monthly crashes up to 77%, reduced to about 28% by conditional volatility scaling, and the risk-managed strategies survived reasonable transaction cost estimates (breakeven turnover costs above 15%). — [search result, repositories on volatility scaling](https://repositorio.ucp.pt/bitstreams/af97b540-c2c4-4687-b028-f620347b2d44/download) (snippet only; exact source paper not confirmed)
- Bianchi et al. (2022, "Taming momentum crashes") report a dynamic, skewness-adjusted max-Sharpe strategy that improves significantly on popular volatility scaling approaches. — [Strathclyde repository](https://strathprints.strath.ac.uk/90217/1/Bianchi-etal-SSRN-2022-Taming-momentum-crashes.pdf) (snippet only)
- **Residual momentum.** Blitz, Huij and Martens: ranking on residual (factor-adjusted) rather than total returns gives risk-adjusted profits about twice as large as total-return momentum, more consistency over time, and smaller time-varying factor exposures, so less volatility. Quantpedia notes a higher long-run Sharpe. — [Quantpedia residual momentum](https://quantpedia.com/strategies/residual-momentum-factor)
- Critiques of residual momentum: a later five-factor study finds better risk-adjusted performance but no meaningful reduction in crash risk; a Swedish 1990–2022 master's thesis found lower volatility that did not compensate for lost return. Quantpedia's entry states no transaction-cost, bid-ask, impact or borrow adjustment is applied to the reported residual-momentum returns. — [Quantpedia](https://quantpedia.com/strategies/residual-momentum-factor), [Gothenburg thesis](https://gupea.ub.gu.se/server/api/core/bitstreams/d5a80c6f-4c44-4009-a0de-8e95370185f8/content) (student thesis; low authority)
- **Frog-in-the-pan.** Da, Gurun and Warachka (RFS 2014, vol 27 issue 7): investors underreact to information arriving in small, steady pieces. Sorting by "information discreteness" (relative frequency of small signals), one summary reports six-month momentum of about 5.94% for continuous-information stocks versus about -2.07% for discrete-information stocks. — [Alpha Architect](https://alphaarchitect.com/frog-in-the-pan-identifying-the-highest-quality-momentum-stocks/), [Da paper PDF](https://www3.nd.edu/%7Ezda/Frog.pdf) (snippet only; the unit and period of these figures were not confirmed)
- **52-week-high.** George and Hwang (2004) propose that the ratio of current price to 52-week high captures anchoring-driven underreaction. A 2023 Management Science supplement uses 52-week-high momentum factors with several horizons. I found no performance numbers, no crash comparison and no net-of-cost result. — [Management Science supplement](https://pubsonline.informs.org/doi/suppl/10.1287/mnsc.2023.4904/suppl_file/mnsc.2023.4904.sm1.pdf) (snippet only)
- **NSE's own construction** already includes a volatility adjustment: Nifty200 Momentum 30 ranks Nifty 200 stocks on 6- and 12-month returns adjusted for daily volatility, with semi-annual reconstitution. — [freefincal search result summarizing NSE method](https://freefincal.com/nifty200-momentum-30-index-a-new-strategy-index-from-the-nse/)
- **Market-state/trend filter.** Daniel-Moskowitz's crash states (after market declines, high volatility) are the theoretical basis. I found no independent backtest of a 200-day-average filter on Indian momentum. A freefincal article "Momentum index fund: Will tactical entry/exit give better results?" exists but its content was not read. — [freefincal](https://freefincal.com/?p=93180) (title only)

### Inferences
- The best evidence-per-complexity fix for Silkperfect is volatility scaling of the momentum sleeve (scale exposure to the trailing realized volatility of the momentum portfolio, with cash in the remainder). It uses only prices, already in the repo, and is the fix with the most direct crash-reduction evidence.
- A trend filter on the market is a cruder cousin of the same idea. It can be tested now, but the test is on one short sample, so overfitting is a real risk; use few parameters and several lookbacks.
- Residual momentum needs a factor model on Indian data. This is more work, and the evidence says it helps Sharpe but not necessarily crashes.
- Because Silkperfect is long-only, the Daniel-Moskowitz crash (short leg of beaten-down stocks rallying) hurts less directly, but the long leg still falls in market sell-offs. Max falls of 26–41% mostly reflect market beta plus high-beta winners, so a beta or volatility cap on the long leg may matter more than the long-short crash literature suggests.

### Gaps
- No net-of-cost, long-only, emerging-market test of vol-scaling or residual momentum found.
- The Barroso-Santa-Clara absolute Sharpe numbers and the crash magnitudes were not retrievable.
- Nothing found on interaction between the "volatility-adjusted" ranking used by NSE and a further vol-scaling overlay (possible double counting).

---

## 3. Post-publication decay, trading costs and capacity

### Takeaway
Published anomalies decay (McLean-Pontiff: return predictability falls after publication), and many anomaly returns shrink further after realistic costs. Momentum is one of the few that large-scale studies find survives costs, mainly because live institutional trading costs are far below older estimates. Short-term reversal is the main exception.

### Cited Findings
- McLean and Pontiff, "Does Academic Research Destroy Stock Return Predictability?" (JF 2016, 71(1), 5–32): 97 variables in the published version (82 in the earlier working paper); the search tool could confirm the earlier version's ~35% post-publication decay but could not confirm the published-abstract numbers. — [Fortune 2012 coverage](https://fortune.com/2012/11/02/academics-academia-destroys-stock-picking-strategies/), [Ivey copy](https://ivey.uwo.ca/media/3775549/pontiff.pdf) (snippets)
- Frazzini, Israel and Moskowitz (AQR), "Trading Costs of Asset Pricing Anomalies": using live AQR trading data, actual costs are less than a tenth of those assumed in the prior literature; size, value and momentum capacity can be large, with short-term reversal the exception. A 2020 critique (JFE 137(2), "What you see is not what you get: the costs of trading market anomalies") is more skeptical, and a Federal Reserve paper says other studies (Novy-Marx and Velikov 2016, Briere et al. 2019) also find size, B/M and momentum survive trading costs, while its own estimates show net returns dropping considerably in some sample periods. — [Alpha Architect](https://alphaarchitect.com/surprise-the-size-value-and-momentum-anomalies-survive-after-trading-costs/), [JFE 2020 via IDEAS](https://ideas.repec.org/a/eee/jfinec/v137y2020i2p515-549.html), [Fed paper](https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf) (snippets; note the AQR paper's authors run a momentum business)
- NSE-indices dashboard figures in Oct 2026 show the Nifty200 Momentum 30 with weak recent returns (see section 4), consistent with a live decay or just a regime lull; the data cannot separate these.
- Momentum ETF portfolio turnover can be high: one source reports 124.24% per annum for Nifty 200 Momentum 30 funds as of 31 May 2025. — [Kotak Neo / Business Standard snippet via search](https://www.business-standard.com/finance/news/momentum-funds-may-deliver-high-long-term-returns-for-aggressive-investors-125070300678_1.html) (snippet only)

### Inferences
- Plan for a published-anomaly haircut. A rule of thumb from McLean-Pontiff is that a third to a half of the in-sample edge may not survive going forward; Silkperfect's +10 points a year over equal-weight should not be extrapolated.
- Silkperfect's own cost finding (monthly 25.8%, weekly 24.8%, daily 20.2%, costs Rs 18.7/39.0/86.5 lakh on Rs 1 crore) matches the literature on turnover as the enemy. Quarterly or semi-annual rebalancing (as NSE does) is the sensible default for retail.

### Gaps
- Capacity numbers for India (how much capital before impact eats the edge in the top-200) were not found. Indian AMC momentum AUM is small relative to the market per the sources reviewed, but no figure was captured.
- Published-version McLean-Pontiff numbers not confirmed.

---

## 4. Momentum in India: academic evidence, NSE indices, AMC funds

### Takeaway
Academic evidence for Indian momentum is positive but mixed (one major cross-country study found it insignificant), and the strongest recent paper says liquidity amplifies it. NSE's long index history (backtested before 2020s launch) shows strong outperformance, but recent live returns of the Nifty200 Momentum 30 and its index funds are weak, and one skeptical practitioner backtest says the premium vanishes in the most liquid stocks.

### Cited Findings
**Academic**
- NSE research paper using 1995–2008 data finds momentum profits at 6- and 12-month horizons and longer-run reversal, consistent with Jegadeesh-Titman. — [NSE paper](https://nsearchives.nseindia.com/content/research/res_paperfinal223.pdf) (snippet only)
- Ansari and Khan (2012, Managerial Finance), 1995–2006 data: strong momentum profits that CAPM and Fama-French do not explain. — [Emerald](https://emerald.com/insight/content/doi/10.1108/03074351211193730/full/html)
- Griffin et al. (2005), 39 countries: price and earnings momentum profits were insignificant for India (dissenting evidence). — cited in [search summary of Indian studies](https://core.ac.uk/download/154383453.pdf) (snippet only)
- Chui, Ranganathan, Rohit and Veeraraghavan (2023), Pacific-Basin Finance Journal 82, 102193, 3,956 BSE stocks, 2000–2021: significant intermediate- and long-term momentum; liquidity (turnover) amplifies momentum; reversals among the most illiquid portfolios did not persist. — [IDEAS](https://ideas.repec.org/a/eee/pacfin/v82y2023ics0927538x23002640.html), [Manipal](https://researcher.manipal.edu/en/publications/momentum-reversals-and-liquidity-indian-evidence/)
- A Nifty 500 study of 2015–2024 (academia.edu listing, unverified) says momentum abnormal returns disappear once the momentum factor is included in Carhart, suggesting the premium is not spurious; and a time-series momentum study reports significant TSMOM in India not captured by traditional models. — [academia.edu listing](https://independent.academia.edu/DeepakKedia4) (abstract only; low reliability)

**NSE index track record**
- NSE's April 2026 whitepaper: Nifty200 Momentum 30 returned 19.19% a year versus 15.08% for Nifty since April 2005 to 27 Feb 2026, and beat the Nifty 200 in 15 of the last 20 calendar years. The index was launched much later than 2005, so the history before launch is a backtest. — [NSE whitepaper 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) (snippet only; host blocked)
- NSE Index Dashboard, October 2026: Nifty200 Momentum 30 columns read -3.12, -6.41, -8.48, 9.41, 7.93, 19.42; interpreted by the search tool as 1M, 3M, 1Y, 3Y, 5Y and one more (likely longer-term/since-inception); label order and price versus total-return basis are not confirmed. September 2026 dashboard: -5.78, -4.24, -0.47, 9.21, 9.28, 18.63. — [Oct 2026 dashboard](https://niftyindices.com/Index_Dashboard/Index_Dashboard_OCT2026.pdf), [Sep 2026 dashboard](https://niftyindices.com/Index_Dashboard/Index_Dashboard_SEP2026.pdf) (snippet only; treat as unverified)
- 2022–23 correction: Nifty 50 -13.2% versus Nifty200 Momentum 30 -14.8%. — [Substack analysis](https://curiousinvestinginsights.substack.com/p/momentum-or-mayhem-unpacking-the) (snippet only; blog)
- A March 2025 NSE factsheet extract showed a one-year index return of -14.05%; Tickertape showed a trailing one-year return of -11.33% as of 18 Dec 2025. — [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf), [Tickertape](https://www.tickertape.in/indices/nifty-200-momentum-30-index-.NIFMOM) (snippets)
- HDFC AMC's June 2026 review says the momentum index has produced higher average rolling returns than the Nifty 200 TRI, with higher volatility. — [HDFC MF](https://www.hdfcfund.com/learn/macros-markets-more/index-insider/nifty200-momentum-30-index-june-2026-portfolio-review-capitalizing-ongoing-market-trends) (AMC marketing; not neutral)

**Practitioner skeptical evidence (freefincal, March 2026)**
- "Is Indian Momentum Investing Just a Liquidity Illusion?": high-turnover (liquid) momentum stocks, the ones large funds hold, returned 8.51% net CAGR over about 19 years versus 10.41% for the Nifty 50, with a -75% max drawdown that took over 8 years to recover; the low-turnover momentum bucket returned 19.43%. A follow-up says low volatility is the only factor unaffected by turnover. — [freefincal](https://freefincal.com/is-indian-momentum-investing-just-a-liquidity-illusion/), [follow-up](https://freefincal.com/does-factor-investing-outperformance-fail-for-high-turnover-stocks/) (snippet only; single blog backtest, directly contradicted by the 2023 peer-reviewed paper that finds liquidity amplifies momentum)
- Same author's hypothetical backtest, Dec 2006–Jun 2025: base Momentum 30 at 14.60% net CAGR with a -70.61% max drawdown. — [freefincal](https://freefincal.com/does-factor-investing-outperformance-fail-for-high-turnover-stocks/) (snippet only)
- Earlier freefincal work on the S&P BSE Momentum Index concluded the method works in India but with higher drawdowns than market-cap indices. — [freefincal](https://freefincal.com/momentum-investing-india/) (snippet only)

**AMC funds**
- Expense ratios (various dates, snippet-level, conflicting by site and plan): UTI Nifty200 Momentum 30 about 0.44–0.49%; Motilal Oswal Nifty200 Momentum 30 direct about 0.31%; Bandhan Nifty200 Momentum 30 direct 0.42%; SBI direct 0.4%; Nippon Nifty 500 Momentum 50 direct about 0.21–0.28% (regular 0.88%); Motilal Oswal Nifty 500 Momentum 50 regular 1.09–1.34%. A Baroda BNP Paribas listing showed 1.61 (plan not stated). — [Groww/Alice Blue/IndMoney listings as returned by search](https://groww.in/mutual-funds/bandhan-nifty200-momentum-30-index-fund-direct-growth)
- Live fund returns are short and weak: Bandhan direct 1-year return -2.38% as of 16 Jul 2026; Motilal Oswal Nifty200 Momentum 30 regular -6.39% 1-year as of mid-Oct 2026; Nippon Nifty 500 Momentum 50 direct 1-year -2.28% (date unclear); SBI Nifty200 Momentum 30 had a -14.22% max drawdown from 28 Nov 2025 to 3 Apr 2026 and had not recovered its peak as of 3 Aug 2026; UTI's 1-year return varied from 7.46% to -1.74% across snapshots. — [Sharpely/Bandhan](https://sharpely.in/mutual-funds/bandhan-nifty200-momentum-30-index-fund-directgrowth/42496/performance), [SBI fund at IndMoney](https://www.indmoney.com/mutual-funds/sbi-nifty200-momentum-30-index-fund-direct-growth-1051814) (snippets; aggregators)
- ICICI Pru Nifty 200 Momentum 30 Index Fund: 1-year tracking difference -1.01 (direct) as of 31 Aug 2026. — [ICICI Pru factsheet](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/Index%20Schemes/ICICI%20Prudential%20Nifty%20200%20Momentum%2030%20Index%20Fund.pdf) (snippet only)
- Value Research has reported that about two-thirds of a momentum-index change happens in a single day, a pointer to front-running or rebalance-day costs for index funds; and a "which strategy works best" piece exists. Contents not read. — [Value Research](https://www.valueresearchonline.com/stories/225617/two-thirds-momentum-index-changes-just-one-day/), [Value Research](https://www.valueresearchonline.com/stories/227073/if-want-momentum-this-strategy-works-best/) (titles only)
- I found no r/IndiaInvestments or r/algotrading threads in the search results; Reddit sentiment is unavailable.

### Inferences
- The most important cross-check for Silkperfect: freefincal's 2006–2025 hypothetical -70% drawdown, versus Silkperfect's 26–41% falls over 2021–2026. The short sample omits a 2008-style crash. Silkperfect's start in Feb 2021 also catches the +86.9% first year, which dominates the average; the NSE 5Y figure (~7.9–9.3% annualized for Sep/Oct 2026 dashboard, unverified) is far below Silkperfect's 25.8%, which suggests start-date and basket (30 stocks versus 20 of 200) sensitivity is large.
- Silkperfect's universe (top 200 by turnover) is exactly the "high-turnover" universe where the freefincal skeptic claims momentum fails. The local result (+10 points) goes the other way for 2021–2026, but the two should be reconciled using a longer history. This is the strongest argument for the "back to 2010" test, and the test should include a turnover-tercile split.
- The live record of momentum index funds since their 2021–2024 launches is short and currently unflattering; a 0.3–0.5% expense ratio plus index-rebalance costs is cheap relative to a retail DIY portfolio at small sizes (Silkperfect found a Rs 10,000 account pays Rs 20–45 per order).

### Gaps
- No clean calendar-year table for Nifty200 Momentum 30 versus Nifty 50 (2020, 2022, 2025); the NSE factsheet and whitepaper could not be opened.
- Nifty Midcap150 Momentum 50 index/ETF figures not found (only the existence of a Tata fund by that name was seen). Motilal Oswal Midcap 100 Momentum-style fund details not found.
- Exact column labels and total-return versus price basis of NSE dashboard figures.
- No Indian peer-reviewed test of vol-scaled, residual, or 52-week-high momentum found.

---

## 5. Other methods with strong evidence, and how much survives for a small retail account

### Takeaway
Time-series trend following has the longest and broadest evidence but the lowest retail accessibility in India; quality and low-vol have decent evidence and ready-made Indian index funds, with long relative-underperformance spells; PEAD has largely decayed; risk parity and covered calls are risk-shaping rather than alpha sources. Stat arb and pairs need shorting and low costs that Indian retail lacks.

### Cited Findings
**Trend following / CTA**
- Hurst, Ooi and Pedersen, "A Century of Evidence on Trend Following Investing" (JPM Fall 2017, vol 44 no 1): 67 markets over four asset classes, back to 1880; strong positive returns and low correlation to traditional assets for more than a century; returns strongest in extreme equity years (a "smile"). — [AQR library](https://www.aqr.com/library/journal-articles/a-century-of-evidence-on-trend-following-investing), [Oxford Strategic copy](https://oxfordstrat.com/coasdfASD32/uploads/2016/03/A-Century-of-Evidence-on-Trend-Following-Investing.pdf) (snippet only; Sharpe figures not retrieved)
- Recent CTA record: SG CTA Index +20.13% in 2022 (one source, ambiguous on SG Trend); 2023 described as consolidation with sharp reversals causing two of the worst CTA days in SG Trend Index history; 2025 described as transitional. — [The Full FX](https://thefullfx.com/year-end-drop-fails-to-dampen-stellar-2022-for-trend-followers/), [AlphaSimplex 2023 review](https://www.alphasimplex.com/assets/files/2024.01---themes-of-2023---kaminski-and-sun.pdf), [Top Traders Unplugged](https://www.toptradersunplugged.com/?p=20381) (snippets). Annual SG Trend Index values for 2023–2025 were not found.
- Cambridge Associates published "Does Trend-Following's Recent Struggle Signal That the Strategy Is Structurally Broken?" — title seen, content not read. — [Cambridge Associates](https://publishedresearch.cambridgeassociates.com/?p=19140)
- US retail managed-futures ETFs: DBMF (expense ratio 0.85%) calendar returns 21.53% (2022), -8.94% (2023), 7.25% (2024), 13.84% (2025) per Yahoo; one analysis attributes much of 2025 to long short-duration US government bond positions, not only trend signals. KMLM max drawdown -29.1% and 2024 weak, per PortfoliosLab (undated snapshot). — [Yahoo Finance](https://finance.yahoo.com/quote/DBMF/performance/), [Seeking Alpha](https://seekingalpha.com/article/4836506-dbmf-a-portfolio-idea-to-boost-risk-adjusted-performance), [PortfoliosLab](https://portfolioslab.com/tools/stock-comparison/DBMF/KMLM) (snippets)

**Quality / profitability**
- Novy-Marx (2012), gross profits-to-assets (1962–2010 sample) has roughly the same power as book-to-market in predicting average returns. Asness-Frazzini-Pedersen "Quality Minus Junk" defines quality by profitability, growth and safety; the price paid for quality varies over time. — [Swedroe/ETF.com](https://www.etf.com/node/94104.md), [NBER w24039 search listing](https://www.nber.org/system/files/working_papers/w26060/w26060.pdf) (snippets; check the correct working-paper number)

**Low volatility / betting against beta**
- Frazzini-Pedersen BAB factor earns 0.9% per month, t = 5.73, per a later paper that cites it. — [conference.nber.org search result](https://conference.nber.org/conf_papers/f69835.pdf) (snippet only; the Sharpe ratio I asked about was not found)
- India: Nifty Alpha Low-Volatility 30 index (backtest from April 2005, launched July 2017 per freefincal) showed 19.0% CAGR to Sept 2020 versus 13.2% for Nifty 100, with volatility 18.5% versus 22.6%. — [NSE whitepaper 2020](https://www.niftyindices.com/docs/default-source/indices/nifty-alpha-low-volatility-30/nifty-alpha-low-volatility-30-whitepaper_2020.pdf), [freefincal review](https://freefincal.com/nippon-india-nifty-alpha-low-volatility-30-index-fund-review/) (snippets)
- Nifty500 Low Volatility 50 TRI: 17.5% CAGR Mar 2005–Jul 2026 versus 14.2% for Nifty 500 (Axis MF article; AMC source). — [Axis MF](https://www.axismf.com/mutual-fund-knowledge-centre/articles/low-volatility-index-vs-nifty-500-index)
- Live: Nippon Alpha Low Vol 30, as of 30 Jun 2026: 1-year index TRI about -2.5% versus about -5.4% for Nifty 50 TRI; 3-year about 12.4% versus about 8.8%. Nifty 100 Low Volatility 30 (4 Nov 2026): 1-year -4.43%. Freefincal flagged "return difference at an all-time low" for Nifty 100 Low Vol 30 versus Nifty 50 (date not captured), and Value Research has a piece titled "Low-volatility index funds fell more than market". — [Nippon](https://mf.nipponindiaim.com/FundsAndPerformance/Pages/Nippon-India-Nifty-Alpha-Low-Volatility-30-Index-Fund.aspx), [Tickertape](https://www.tickertape.in/indices/nifty-100-low-volatility-30-index-.NIFTY100L30), [freefincal](https://freefincal.com/nifty-100-low-volatility-30-vs-nifty-50-return-difference-at-an-all-time-low/), [Value Research](https://www.valueresearchonline.com/stories/230032/low-volatility-index-funds-fell-more-than-market/) (snippets)
- Freefincal Nifty 500 study, Dec 2006–Dec 2025: low-volatility low-turnover half 14.11% net CAGR, Sharpe 0.87, max drawdown -42.80%. — [freefincal](https://freefincal.com/does-factor-investing-outperformance-fail-for-high-turnover-stocks/) (snippet only)

**Post-earnings announcement drift**
- Martineau, "Rest in Peace Post-Earnings Announcement Drift" (Critical Finance Review 2022): drift began disappearing for non-microcap stocks around 2001 and was essentially zero for large caps by 2006. Chan and Marsh (2024) argue the demise is premature (drift appears in overnight returns after extreme misses). — [CFR](https://nowpublishers.com/article/Details/CFR-0122), [UCLA Anderson review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again)

**Short-term reversal**
- Short-term reversal is the capacity-limited exception in the AQR trading-cost study (see section 3). Silkperfect's own test: last month's biggest fallers earned 7.7% versus 16.1% for hold-all (a loss, as expected under momentum-like regimes). — [Alpha Architect](https://alphaarchitect.com/surprise-the-size-value-and-momentum-anomalies-survive-after-trading-costs/); Silkperfect REPORT (provided file)

**Covered calls / put-write**
- CBOE BXM (buy-write) June 1988–Aug 2006 (Callan): monthly Sharpe 0.22 versus 0.16 for S&P 500, Stutzer 0.20 versus 0.15; Hewitt EnnisKnupp (Jun 1986–Jan 2012) found higher Sharpe and Sortino for BXM than three stock indices, with negative skew. One study found returns near-identical (12.39% BXM versus 12.20% S&P 500), so the advantage is lower risk, not higher return. BXM lags in strong bull markets. — [Callan/CBOE](https://cdn.cboe.com/resources/education/research_publications/Callan_CBOE.pdf), [HEK/CBOE](https://cdn.cboe.com/resources/education/research_publications/HewittEnnisKnupp-BXM-(2012).pdf) (snippets)

**Risk parity, stat arb / pairs**
- Not covered. My searches did not return any source on risk parity performance or on stat arb/pairs net returns for retail. See Gaps.

### Inferences
- For a small Indian retail account, the net-of-cost ranking I would defend from the sources: (1) momentum/low-vol/quality through low-cost index funds; (2) systematic trend rules applied to Indian equity index exposure (cash versus index) rather than a futures CTA; (3) covered calls only if tax/STT drag is acceptable; everything involving shorts, intraday or high turnover is last.
- Low volatility looks like the best complement to momentum: it is the factor freefincal found robust to turnover/liquidity splits, it has the cheapest live products, and a momentum plus low-vol mix targets Silkperfect's deep drawdowns. Its live record is also uneven (lagged the market in some 2026 windows).
- PEAD is not worth a retail build (decayed in large caps, needs earnings data).

### Gaps
- Value (HML/value-in-India) evidence: not found this session beyond Asness et al. (above); no Indian value index returns.
- Risk parity (e.g. Asness-Frazzini-Pedersen "Leverage Aversion and Risk Parity"; Bridgewater All Weather) and stat arb/pairs (Gatev-Goetzmann-Rouwenhorst) performance: not found.
- Annual SG Trend Index returns; Hurst-Ooi-Pedersen Sharpe and fee/cost-adjusted numbers.
- Quality factor India index (Nifty200 Quality 30, Nifty500 Value 50) performance and live fund data: not found.
- Retail-after-tax comparisons across methods: no source.

---

## 6. Implementability in India: ETFs/funds, futures costs, shorting, STT and tax

### Takeaway
Long-only factor index funds and ETFs are the practical retail route, and they are cheap. Shorting is limited to intraday cash and F&O-eligible names (carry via SLB or futures); derivatives became more expensive in April 2026. Capital gains tax is 12.5% long-term (over 12 months) and 20% short-term on listed equity; frequent rebalancing converts gains into the 20% bucket.

### Cited Findings
- STT hike (Budget 2026, effective 1 April 2026): STT on futures raised from 0.02% to 0.05%; STT on options premium raised from 0.1% to 0.15%. The Income Tax Department clarified the change applies to F&O only. Two Angel One pages and a Sahi blog said it was commodity futures, which conflicts with the majority of sources (likely an error on their side). — [Free Press Journal](https://www.freepressjournal.in/business/big-announcement-for-stock-market-traders-stt-hiked-in-budget-2026-fo-tax-raised-to-005-015), [Business Today](https://www.businesstoday.in/markets/stocks/story/budget-2026-fm-sitharaman-raises-stt-on-fo-trades-signals-tighter-market-oversight-513932-2026-02-01), [Deccan Herald](https://www.deccanherald.com/business/markets/union-budget-2026-stt-on-futures-hiked-by-150-options-by-50-markets-tank-3882160) (snippets)
- Capital gains: LTCG on equity and equity-oriented mutual funds is 12.5% for FY 2026-27 (rate set by Budget 2024, unchanged in 2026); STCG on equity is 20%. — [Business Standard](https://www.business-standard.com/budget/news/budget-2026-ltcg-tax-rates-unchanged-for-fy27-fm-sitharaman-126020100424_1.html), [Fyers](https://fyers.in/blog/union-budget-2026-highlights/) (snippets; the LTCG exemption threshold and holding-period details were not captured)
- Shorting: short selling in the cash segment is allowed only on an intraday basis; positional shorts go through derivatives or SLB; naked shorting is prohibited; in practice cash short selling is generally limited to F&O stocks. Sources disagree on whether retail can carry overnight shorts via SLB. Borrowers may need collateral up to 130%. SEBI's January 2026 consultation (and press reports) proposes nearly doubling SLB-eligible stocks, and one report says only 176 NSE stocks can currently be shorted; implementation status of the reform was not confirmed. — [Anand Rathi](https://anandrathi.com/ar-finshala/share-market/what-is-short-selling), [5paisa](https://www.5paisa.com/blog/sebi-short-selling-slbm-expansion), [Nifty Trader](https://www.niftytrader.in/markets/only-176-nse-stocks-can-be-shorted-sebi/), [SEBI consultation annex Jan 2026](https://www.sebi.gov.in/sebi_data/commondocs/jan-2026/Consultation%20paper%20Annexure_A_p.pdf) (snippets)
- SEBI studies: individual traders' net equity-derivative losses were about Rs 1.06 lakh crore in FY25 (up 41% from Rs 74,812 crore in FY24), with over 91% of traders losing money, after transaction costs; one secondary source says a later SEBI revision put FY25 at Rs 1,11,788 crore. The FY26 study reports about 9 in 10 lost money and about Rs 91,685 crore in individual losses; proprietary traders had the highest gross profit at about Rs 44,000 crore, and 99% of FPI/prop profits came from algo entities. — [Business Standard](https://www.business-standard.com/markets/news/net-losses-of-traders-in-fo-widens-in-fy25-sebi-study-125070701221_1.html), [Open Magazine](https://openthemagazine.com/business/sebi-fo-loss-study-explained-why-9-in-10-retail-traders-lost-91685-crore-in-fy26), [Finnovate](https://www.finnovate.in/learn/blog/sebi-fno-trader-losses-fy26-individual-derivatives) (snippets; the FY26 number is not directly comparable)
- Indian momentum products available: Nifty200 Momentum 30 index funds (UTI, Motilal Oswal, Bandhan, SBI, HDFC, ICICI Pru, Kotak, Baroda BNP Paribas), Nifty 500 Momentum 50 funds (Nippon, Motilal, Kotak), Nifty Midcap 150 Momentum 50 (Tata), and an active quant momentum fund. Alpha/low-vol products include Nippon Nifty Alpha Low Volatility 30 and ICICI Alpha Low Vol 30 ETF. — [Groww/Alice Blue/Kotak Neo listings](https://www.kotakneo.com/mutual-funds/compare/sbi-nifty200-momentum-30-index-fund-vs-tata-nifty-midcap-150-momentum-50-index-fund/)

### Inferences
- Silkperfect's DIY quarterly momentum at Rs 1 lakh+ pays STCG at 20% on most trades that are held under 12 months, whereas an index fund's internal turnover (124%/yr per one source) is not taxed in the investor's hands until redemption. That favours the fund route for after-tax results, at roughly 0.3–0.5% a year expense.
- Long-short momentum, vol-managed with leverage, trend following in futures, and stat arb are effectively off the table for retail owing to SLB scarcity, margins and the April 2026 STT increase. Stay long-only; for a downside hedge, use cash/liquid fund or a Nifty trend filter rather than shorts.
- SEBI's findings (91% of F&O traders lose) support Silkperfect's own conclusion to avoid options.

### Gaps
- Delivery STT (0.1%), brokerage, stamp duty and exchange fees were not confirmed in this session; Silkperfect's own cost model uses its own defaults (per the REPORT, not confirmed against a contract note).
- Futures margin requirements and lot sizes post-2026 not found.
- Whether the SEBI short-selling reform is in force by November 2026 not confirmed.
- Tax treatment of ETFs versus fund-of-funds exits, and the exemption limit on LTCG, not captured.

---

## 7. Where critics say each method fails

### Takeaway
The generic critiques are data mining and multiple testing (Harvey-Liu-Zhu), post-publication decay (McLean-Pontiff), and cost/capacity (Novy-Marx-Velikov, Fed critique). Method-specific: momentum crashes and concentration, low-vol/quality crowding and valuation drift, PEAD disappearing, residual momentum untested net of costs.

### Cited Findings
- Harvey, Liu and Zhu (RFS 2016, 29(1), 5–68): new factors should clear a t-ratio hurdle above 3.0, and most claimed research findings in financial economics are likely false. They catalogue about 316 factor candidates in 313 papers (another citing paper says 314). The 3.0 cutoff is framed as a minimum because the number of tests tried is unobservable. — [NBER w20592](https://nber.org/papers/w20592), [IDEAS](https://ideas.repec.org/a/oup/rfinst/v29y2016i1p5-68..html)
- McLean-Pontiff: investors learn from academic publication, and predictability decays after (section 3). — [Fortune](https://fortune.com/2012/11/02/academics-academia-destroys-stock-picking-strategies/)
- Novy-Marx and Velikov: transaction costs always reduce profitability and increase data-snooping concerns. — [Novy-Marx paper](https://mysimon.rochester.edu/novy-marx/research/ToAatTC.pdf) (snippet only)
- Momentum-specific: crash-prone (section 1); the Indian cross-country result (Griffin et al.) found it insignificant; freefincal says it vanishes in liquid names (section 4); recent US momentum returns were concentrated: five stocks led by Palantir explained over half of momentum's 2025 year-to-date performance. — [Benzinga](https://www.benzinga.com/etfs/sector-etfs/25/06/46030895/the-palantir-effect-momentum-stocks-are-making-a-killing-like-never-before?mod=mw_quote_news) (snippet only)
- Business Standard on Indian factor funds: over 7–10 years, factor funds are bound to have long, sometimes prolonged stretches of drastic underperformance versus market-cap indices; DSIJ warns momentum rules can create hidden sector concentration. — [Business Standard](https://www.business-standard.com/finance/personal-finance/invest-in-multiple-single-factor-funds-with-a-7-10-year-horizon-123101701045_1.html), [DSIJ](https://insights.dsij.in/hi/dsijarticledetail/momentum-funds-are-they-worth-chasing-now-59110)
- PEAD critique: decayed to near zero in large caps by about 2006 (Martineau), but disputed (section 5).
- Residual momentum: does not necessarily reduce crash risk; gross-of-cost reporting (section 2).
- Trend following: periodic multi-year struggle (Cambridge Associates title; DBMF -8.94% in 2023, KMLM 2024 weak and a -29% drawdown snapshot).

### Inferences
- With a t-stat of 1.5–1.8, Silkperfect's local momentum result fails the Harvey-Liu-Zhu bar of 3.0 by itself. Its credibility comes from the external literature (an a priori hypothesis, not a data-mined one), so any additional variants tested should be few and declared in advance, to avoid manufacturing the very data-mining the critics describe.
- Testing five candidate fixes on six years each creates a multiple-testing problem; the pre-registered list should be short, and each fix judged by robustness across parameters and sub-periods, not best-case numbers.

### Gaps
- Specific skeptical papers on value, quality (e.g. QMJ robustness) and low-vol (BAB leverage dependence) not retrieved.
- Reddit/r/algotrading commentary not found by search.

---

## 8. Implications for Silkperfect's proposed next tests (synthesis)

### Takeaway
The evidence ranking supports, in this order: (1) extend history to 2010 or earlier with a turnover-tercile split; (2) volatility-scale (or beta/vol-cap) the momentum sleeve; (3) momentum plus low-volatility screen; (4) a simple market trend filter with minimal parameters; (5) quality/value only if accounts data is cheap to obtain. Treat the first as the highest priority because it tests the claim that the edge is real in liquid Indian names.

### Cited Findings
- The inputs for these points are cited in sections 1–7 above; no new facts are introduced here.

### Inferences
- **Longer history (to 2010 or earlier):** directly addresses the t=1.5–1.8, small-sample and 2021-start problems, and the freefincal contradiction (-75%/-70% drawdowns, 8.5% net CAGR for liquid momentum). Report calendar-year returns, drawdown, and results by turnover tercile.
- **Vol-targeted momentum:** best-supported crash fix; compare against NSE's volatility-adjusted ranking already in use.
- **Momentum plus low-vol:** matches section 5's robust low-vol evidence and Indian products; expect smoother returns and lower upside; check 2021 versus 2025–26 separately.
- **Trend filter:** cheap to test; weakest independent evidence; avoid tuning.
- **Value/quality:** academically strong (Novy-Marx, QMJ, Asness-Moskowitz-Pedersen) but needs fundamentals data; defer.
- **Realistic expectation:** after McLean-Pontiff-type decay, Indian costs, and 20% STCG on short holds, an edge of a few points a year over a low-cost index fund is plausible; +10 points is not a safe forecast. A momentum index fund (0.3–0.5% expense ratio) gives most of the exposure with less operational burden.

### Gaps
- No live data on whether any method delivers after-tax returns for a retail Indian account over 10+ years; the sources are index backtests and short fund records.

---

## Source-access log
- Failed with DNS errors (not allowed in the session): niftyindices.com, econpapers.repec.org, alphaarchitect.com, nber.org, aqr.com, kotakmf.com. All other URLs above were only seen as WebSearch results (the search tool returned summaries, not page text). Every figure is therefore snippet-derived and should be re-verified before use in a report; the highest-priority items to verify are the NSE whitepaper/dashboard numbers, the freefincal liquidity analysis, the Budget 2026 STT rates, and the McLean-Pontiff published abstract.
