# Commercial / hosted deep research agents (as of 24 Nov 2026)

Method note for the report writer: most primary hosts (openai.com, blog.google, arxiv.org, wikipedia, the-decoder, perplexity research, deepresearch-bench.github.io) were NOT fetchable from this session (DNS blocked), so nearly all findings come from web-search result summaries of primary and secondary pages, plus one direct fetch of Anthropic's support page. Each finding is tagged [V] = vendor-reported, [I] = independent/academic, [S] = secondary press/blog (unverified numbers). Several 2026 pricing/limit figures conflict across sources; conflicts are flagged. Some model names in 2026 trackers (e.g. "GPT-5.6 Sol", "Atria Dawn Preview", "Kimi K3.1 Pro") could not be verified and are treated as low-reliability.

## 1. Which products are notable as of late 2026, and what does each do / how does it work?

### Takeaway
The field splits into (a) chat-integrated "deep research" modes from the frontier labs (OpenAI, Google, Anthropic, xAI, Perplexity, Alibaba Qwen, Moonshot), (b) general "super agents" that bundle research with execution (Manus, Genspark, Perplexity Computer, ChatGPT agent/Atlas, Comet), and (c) enterprise/API research infrastructure (You.com ARI, Exa Websets, Gemini Deep Research via API, Qwen-Deep-Research API, open-weight Tongyi DeepResearch). All run a plan -> multi-query search -> read/follow links -> reflect -> write-cited-report loop; differences are the underlying model, tooling (browser vs API), connectors, and controls.

### Cited Findings

**OpenAI Deep Research (ChatGPT) + ChatGPT agent/Atlas**
- Launched 2 Feb 2025; powered by a model specifically trained for browsing; OpenAI's own BrowseComp page carries a caveat that the model "is trained on data that specifically teaches the model to be good at BrowseComp tasks" [V] — [OpenAI BrowseComp](https://openai.com/index/browsecomp/)
- ~10 Feb 2026 update: Deep Research now runs on GPT-5.2; adds connecting apps/MCP and restricting searches to specific sites, real-time progress tracking with ability to interrupt/add sources, and a full-screen report viewer; rolling out first to Plus/Pro, Free/Go later [S] — [The Decoder](https://the-decoder.com/openais-deep-research-now-runs-on-gpt-5-2-and-lets-users-search-specific-websites/); [Neowin](https://www.neowin.net/news/openai-upgrades-chatgpt-deep-research-with-gpt-52-and-real-time-controls/); [TechNews](https://technews.tw/2026/02/11/updates-to-deep-research-in-chatgpt/)
- OpenAI still warns Deep Research can make factual errors / incorrect inferences [S] — same Neowin/Decoder coverage above
- ChatGPT Atlas browser launched 21 Oct 2025 on macOS (Windows/iOS/Android "coming soon" at launch; current status not verified); browser is free; Agent mode was in preview for Plus, Pro, Business; asks permission before opening tabs/clicking; OpenAI calls it an early experience that can err on complex workflows [V/S] — [OpenAI Atlas](https://openai.com/blog/introducing-chatgpt-atlas); [PCWorld](https://www.pcworld.com/article/2950777/openai-launches-its-own-free-atlas-browser-with-chatgpt-built-in.html); [SiliconANGLE](https://siliconangle.com/?p=717440)

**Google Gemini Deep Research**
- Updated Gemini Deep Research agent exposed to developers via the Interactions API (public beta in Google AI Studio with a Gemini API key; API may still change); announced Dec 2025 alongside open-sourced DeepSearchQA benchmark (900 "causal chain" tasks, 17 fields) [V] — [Google blog](https://blog.google/technology/developers/deep-research-agent-gemini-api/); [The Decoder](https://the-decoder.com/google-opens-updated-deep-research-agent-to-developers-with-new-api/); [Gigazine, 12 Dec 2025](https://gigazine.net/gsc_news/en/20251212-gemini-deep-research)
- Consumer feature: "Use Deep Research in Gemini Apps" — [Google help](https://support.google.com/gemini/answer/15719111)

**Perplexity Deep Research / Comet / Computer**
- Deep Research launched Feb 2025 (HLE 21.1% at launch [V]); "Advanced" Deep Research for Max launched early Feb 2026 running on Claude Opus 4.5 inside Perplexity's own harness; open-sourced DRACO benchmark (100 tasks, 10 domains, drawn from real Perplexity user queries from fall 2025) [V] — [TestingCatalog](https://www.testingcatalog.com/perplexity-launches-advanced-deep-research-for-max-users); [Analytics India Mag](https://analyticsindiamag.com/ai-news/perplexity-releases-advanced-deep-research-upgrade-open-sources-draco-benchmark); [DRACO paper](https://arxiv.org/html/2602.11685v1)
- Comet browser: launched 9 Jul 2025 for Max only; free to everyone 2 Oct 2025 [S] — [Digital Citizen](https://www.digitalcitizen.life/perplexity-launches-advanced-deep-research-for-max-users-with-draco-ai-research-benchmark/) (as summarised by search tool); [Windows Central](https://www.windowscentral.com/artificial-intelligence/perplexity-launches-comet-ai-web-browser-to-take-on-chrome-and-edge-and-you-can-use-it-today-for-usd200-a-month)
- Perplexity Computer announced 25 Feb 2026: multi-model orchestration for long-running workflows; initially Max-only, reportedly opened to Pro 13 Mar 2026 (credit-based) [S] — [TechCrunch 27 Feb 2026](https://techcrunch.com/2026/02/27/perplexitys-new-computer-is-another-bet-that-users-need-many-ai-models); [DataCamp](https://datacamp.com/tutorial/perplexity-computer)

**Anthropic Claude Research**
- Multi-agent orchestrator-worker design (lead agent + parallel subagents); in Anthropic's internal eval, Opus 4 lead + Sonnet 4 subagents beat single-agent Opus 4 by 90.2%; multi-agent uses ~15x tokens of chat [V, 2025] — [Anthropic engineering post](https://www.anthropic.com/news/multi-agent-research-system); [The Decoder](https://the-decoder.com/anthropic-shares-blueprint-for-claude-research-agent-using-multiple-ai-agents-in-parallel/)
- Searches web + connected tools (Google Workspace, custom connectors); on mobile web only; cannot use local desktop MCP servers; web search must be on [V] — [Claude support article](https://support.claude.com/en/articles/11088861-using-the-research-feature)
- Per that support page (fetched Nov 2026, undated "updated over 3 weeks ago"): Research "always runs on Claude Opus 5.5, falling back to Claude Opus 4.8" — [Claude support article](https://support.claude.com/en/articles/11088861-using-the-research-feature)

**xAI Grok DeepSearch / DeeperSearch**
- DeepSearch = full; DeeperSearch = more iterations, deeper link traversal, longer synthesis; tier mapping not clearly documented [S] — [suprmind / secondary pricing guides via search](https://suprmind.ai/hub/grok/pricing.md)

**Manus**
- Meta announced acquisition of Manus ~30 Dec 2025 (reported >$2B; some outlets say ~$3B); Manus reported >$100M ARR (~$125M reported); stopped operating in China; customers keep subscriptions/pricing [S] — [TechRadar](https://www.techradar.com/pro/meta-buys-manus-for-usd2-billion-to-power-high-stakes-ai-agent-race); [The Decoder](https://the-decoder.com/meta-pays-3-billion-for-manus-ai-after-startup-cut-all-chinese-ties-to-clear-regulatory-hurdles/); [The Register](https://www.theregister.com/2025/12/30/meta_acquires_manus/)
- "Wide Research" (parallel many-agent research) reportedly on the $199/mo Pro plan [S] — [3DNews (Russian)](https://3dnews.ru/1127023/bolshe-100-iiagentov-obedinili-dlya-masshtabnih-issledovaniy-alternativa-deep-research-za-199/amp)

**Genspark**
- "Super Agent" with Deep Research drawing from a shared credit pool [S] — [eesel Genspark pricing](https://www.eesel.ai/blog/genspark-ai-pricing)

**Kimi-Researcher (Moonshot)**
- Agent trained end-to-end with RL; blog dated 20 Jun 2025 [V] — [Moonshot blog](https://moonshotai.github.io/Kimi-Researcher)

**Alibaba: Qwen Deep Research and Tongyi DeepResearch**
- Qwen-Deep-Research: Model Studio API/consumer product that plans, runs multi-round searches, writes structured reports; later upgrade adds live webpages and podcasts (Qwen3-Coder, Qwen-Image, Qwen3-TTS) [V/S] — [Alibaba Cloud docs](https://www.alibabacloud.com/help/en/model-studio/qwen-deep-research); [VentureBeat](https://venturebeat.com/ai/qwens-new-deep-research-update-lets-you-turn-its-reports-into-webpages); [Decrypt](https://decrypt.co/345517/alibabas-qwen-deep-research-live-webpages-podcasts-seconds?amp=1)
- Tongyi DeepResearch: open-weight 30.5B total / 3.3B active params agent (late 2025) [V] — [Tongyi tech report](https://arxiv.org/html/2510.24701v2); [VentureBeat](https://venturebeat.com/ai/the-deepseek-moment-for-ai-agents-is-here-meet-alibabas-open-source-tongyi)

**You.com ARI / ARI Enterprise**
- Enterprise research platform unifying web, internal and premium data; launched 15 May 2025; TIME Best Inventions 2025; Webby 2026 nominee [V] — [BusinessWire](https://www.businesswire.com/news/home/20250515467218/en); [You.com TIME post](https://you.com/resources/ari-named-on-times-list-of-the-best-inventions-of-2025)

**Exa Websets**
- Entity-list building ("find all X meeting criteria, with verified enrichments"), distinct from report-style research; Websets V2 reported ~4x faster at half the cost [S] — [AlphaSignal](https://alphasignal.ai/news/exa-s-websets-v2-runs-4x-faster-at-half-the-cost-for-web-research); one review says Exa docs now steer new list-building to its Agent — [Crustdata review](https://crustdata.com/reviews/exa)

**Z.ai (GLM) deep research**: no reliable source found (see Gaps).

### Inferences
- The consumer "deep research" button is converging across vendors; differentiation is shifting to connectors (MCP/Workspace), controllability mid-run, and agentic browsers/computers (Atlas, Comet, Computer, Manus, Genspark) rather than the core search loop.
- Perplexity's switch to running Deep Research on third-party frontier models (Opus 4.5) suggests research quality is increasingly driven by the base model plus harness, not proprietary search alone.

### Gaps
- No verified current description of ChatGPT agent (July 2025 launch) beyond Atlas; Atlas Windows availability as of Nov 2026 unverified.
- No reliable source found for Z.ai/GLM deep research, Grok DeepSearch internals, or Genspark architecture.
- Could not retrieve primary vendor pages (openai.com, blog.google, perplexity research) due to network restrictions.

## 2. Which are rated best on independent benchmarks, and why?

### Takeaway
No single independent benchmark crowns one product in late 2026. On the academic report-quality benchmark DeepResearch Bench (RACE), Gemini Deep Research led the original 2025 paper; on independent citation audits no system is reliably accurate. Vendor-reported results (Google, Perplexity, You.com, OpenAI) each favour their own product, often on benchmarks they authored. BrowseComp is increasingly questioned as a measure.

### Cited Findings
**DeepResearch Bench (academic, USTC; RACE score 0-100) [I]**
- Original paper: Gemini-2.5-Pro Deep Research led commercial agents with overall RACE 48.88 (mid-2025); a later leaderboard entry shows 49.71 and ThinkDepth.ai at 52.49 [I/S] — [DeepResearch Bench paper](https://arxiv.org/pdf/2506.11763); [HF leaderboard commit](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard/commit/b439fbabe80f84618fe7494b5b5ba2290dedcda7)
- Jan 2026 paper cites leaderboard values of Claude Researcher ~45 and Perplexity Research 40.46 (as of Jan 2026) [I] — [arXiv 2601.20843](https://arxiv.org/pdf/2601.20843)
- Search summary claims "after 1 June 2026 only the GPT-5.5 leaderboard is maintained" — flagged as unverified by the search tool itself — [project docs](https://docsearch.algolia.com/mcp/docs/repo/ayanami0730/deep_research_bench)
- I could not load the live leaderboard (HF space returned no data), so the current (Nov 2026) top of RACE is unknown.

**BrowseComp (OpenAI; 1,266 questions)**
- OpenAI Deep Research 51.5% at launch (Feb 2025) vs GPT-4o 0.6%, o1 9.9% [V, trained on BrowseComp-like data] — [OpenAI](https://openai.com/index/browsecomp/)
- Gemini Deep Research agent (Dec 2025): BrowseComp 59.2%, HLE 46.4%, DeepSearchQA 66.1% (Gemini 3 Pro: 49.4 / 43.2 / 56.6); GPT-5 Pro reported 59.5% on BrowseComp [V] — [Analytics India Mag](https://analyticsindiamag.com/ai-news-updates/googles-new-deep-research-agent-scores-sota-results-on-benchmarks); [Google blog](https://blog.google/technology/developers/deep-research-agent-gemini-api/)
- 2026 model-level (not product) BrowseComp figures from trackers: GPT-5.4 Pro 89.3%, GPT-5.4 82.7%, Claude Opus 5 90.8%, Kimi K3 91.2%, Gemini 3.1 Pro (high, w/ tools) 85.9; OpenRouter lists Claude Opus 5 + Perplexity search, 25 turns, 89.0% as of 11 Aug 2026; benchlm.ai dated 5 Nov 2026 lists "Atria Dawn Preview" 92.5%, "GPT-5.6 Sol" 92.2%, "Kimi K3.1 Pro" 92.1% (unverifiable names) [S, mixed self-reported] — [OpenRouter](https://openrouter.ai/benchmarks/browsecomp); [BenchLM](https://benchlm.ai/benchmarks/browseComp); [DeepLearning.AI Batch](https://www.deeplearning.ai/the-batch/openais-gpt-5-4-pro-and-gpt-5-4-thinking-challenge-googles-gemini-3-1-pro-preview-as-best-all-around-ai-model); [llm-stats](https://llm-stats.com/benchmarks/browsecomp)
- Caveat: LiveBrowseComp (May 2026) reports search-augmented scores fall 25-40 points vs BrowseComp and rankings no longer predict well; BrowseComp-Plus (fixed corpus): GPT-5 + Qwen3-Embedding-8B reached 70.1% [I] — [arXiv 2605.28721](https://arxiv.org/html/2605.28721); [BrowseComp-Plus](https://arxiv.org/html/2508.06600v1)

**Humanity's Last Exam**
- OpenAI Deep Research 26.6% (Feb 2025, tools on) [V] — [OpenAI intro](https://openai.com/index/introducing-deep-research/); [Fortune](https://fortune.com/2025/02/12/openai-deepresearch-humanity-last-exam/)
- Perplexity Deep Research 21.1% (Feb 2025) [V]; Perplexity later self-reports HLE 36.4%-50.5% for newer configurations [V, unverified independently]; see Perplexity section of search summary — [Perplexity pricing roundup](https://dev.to/techsifted/perplexity-ai-pricing-2026-free-vs-pro-vs-max-vs-enterprise-compared-1h30)
- Kimi-Researcher 26.9% (from 8.6% before RL; 20 Jun 2025) and xbench-DeepSearch 69% pass@1 [V] — [Moonshot blog](https://moonshotai.github.io/Kimi-Researcher)
- Tongyi DeepResearch 30B-A3B: HLE 32.9, BrowseComp 43.4, BrowseComp-ZH 46.7, WebWalkerQA 72.2, GAIA 70.9, xbench-DeepSearch 75.0 (late 2025) [V] — [Tongyi report](https://arxiv.org/html/2510.24701v2)

**GAIA**
- Third-party review: Genspark Super Agent 87.8% vs Manus 2.0 86% (Nov 2026 article) [S]; same source says GAIA validation answers are publicly leaked/saturated, top self-submissions >94% as of early Nov 2026 — [agentmarketcap, 1 Nov 2026](https://agentmarketcap.ai/blog/2026/11/01/manus-2-0-vs-genspark-vs-devin-gaia-generalist-sprint)

**Perplexity-authored benchmarks [V]**
- Advanced Deep Research claims 79.5% on Google DeepMind DeepSearchQA leaderboard (Feb 2026) — [Analytics India Mag](https://analyticsindiamag.com/ai-news/perplexity-releases-advanced-deep-research-upgrade-open-sources-draco-benchmark)
- DRACO: reported Perplexity 70.5% vs Gemini 59.0% vs OpenAI o3 52.1%; Perplexity authored the benchmark — [Digital Citizen](https://www.digitalcitizen.life/perplexity-launches-advanced-deep-research-for-max-users-with-draco-ai-research-benchmark/); [DRACO paper](https://arxiv.org/html/2602.11685v1)

**You.com [V]**
- DeepConsult (You.com-authored, o3-mini judge): ARI 76% win rate vs OpenAI Deep Research 14%; FRAMES 80% (May 2025) — [You.com](https://you.com/articles/o3-mini-judges-ari-enterprise-winner-over-openai-deep-research); [VentureBeat](https://venturebeat.com/ai/you-coms-ari-enterprise-crushes-openai-in-head-to-head-tests-aims-at-deep-research-market)

**Independent citation/factuality**
- FINDER/DEFT study: Gemini 2.5 Pro Deep Research top at only 51/100; OpenAI o3 ~66% of citations correct (2025 models) [I] — [The Decoder](https://the-decoder.com/?p=29784)
- Audit (reported Sep 2026): leading systems keep link validity >94% and source relevance >80% but only 39-77% factual accuracy against cited sources [I/S] — [IntuitionLabs](https://intuitionlabs.ai/pdfs/citation-reliability-ai-literature-reviews.pdf)
- Anecdotal test (TWiT/Hands-On AI): tools citing more official pages did better; Perplexity among stronger — [TWiT](https://twit.tv/posts/tech/chatgpt-vs-gemini-vs-claude-vs-perplexity-which-ai-does-deep-research-best-2026)

### Inferences
- Best independent evidence points to Gemini and OpenAI Deep Research as report-quality leaders (2025 data), with Perplexity/Claude mid-pack on RACE; but data are 6-12+ months stale versus Nov 2026 models.
- Every "we beat X" claim in this set (Perplexity DRACO, You.com DeepConsult, OpenAI BrowseComp) comes from benchmark authors; weight accordingly.
- Headline BrowseComp scores near 90% at model level suggest the benchmark is near saturation, consistent with LiveBrowseComp's critique.

### Gaps
- No current Nov 2026 RACE/FACT leaderboard top-10; no independent score found for Grok DeepSearch, Manus (research specifically), Genspark deep research, or Exa Websets.
- No independent evaluation of Claude Research with Opus 5.5 found.
- GAIA numbers come from a single secondary article.

## 3. Pricing, rate limits, and access requirements

### Takeaway
Basic Deep Research is bundled in $20/mo plans at nearly every vendor with monthly or daily caps; heavy use pushes to $200-300/mo tiers or API pay-per-use. Limits changed repeatedly in 2026 and sources conflict, so figures below must be verified at checkout.

### Cited Findings
- **OpenAI**: Original 2025 limits Plus 10/mo, Pro 100 -> 120/mo (2025, outdated); 2026 pricing page reportedly lists Deep Research as limited on Free/Go, included in Plus, "maximum" on Pro; no 2026 quota table found [S] — [Wikipedia summary via search](https://en.wikipedia.org/wiki/ChatGPT_Deep_Research); [BGR](https://bgr.com/tech/heres-how-often-you-can-use-deep-research-with-chatgpt-plus)
- **Google**: 2025 figures: Free 5 reports/mo, AI Pro 20/day, Ultra 200/day; a 2026 9to5Google item lists AI Pro 75/day (conflicts); May 2026 I/O raised Ultra tiers to 5x and 20x Pro limits — check official page [S] — [Google limits help page](https://support.google.com/gemini/answer/16275805); [9to5Google May 2026](https://9to5google.com/2026/05/25/google-ai-plus-pro-ultra-gemini-features/). API: Interactions API public beta with Gemini API key (pricing not found).
- **Perplexity**: Pro $20/mo ($17 annual), Max $200/mo ($2,000/yr). Deep Research caps conflict: ~20/month (Mar 2026 tracker), 20/day (Jun 2026 guide), 25/month Pro / 62 Enterprise Pro / 500 Enterprise Max (enterprise page cited in a petition); Max "higher limits" unspecified. Advanced Deep Research first for Max (Feb 2026). Computer: Max includes 10,000 monthly credits (+20,000 launch bonus expiring in 30 days); Ask and Deep Research don't consume credits [S] — [DEV Community](https://dev.to/techsifted/perplexity-ai-pricing-2026-free-vs-pro-vs-max-vs-enterprise-compared-1h30); [Finout](https://www.finout.io/blog/perplexity-pricing-in-2026); [TechCrunch](https://techcrunch.com/2026/02/27/perplexitys-new-computer-is-another-bet-that-users-need-many-ai-models)
- **Anthropic**: Research available on Pro, Max, Ultra, Team, Enterprise (Nov 2026 support page); uses the same usage limits as normal chat but drains them faster; originally Max/Team/Enterprise-only beta in Apr 2025 [V] — [Claude support](https://support.claude.com/en/articles/11088861-using-the-research-feature); [Maginative](https://www.maginative.com/article/anthropic-launches-research-beta-and-google-workspace-access-for-claude/)
- **xAI**: SuperGrok ~$30/mo (conflicting: $50/mo in one guide; SuperGrok Plus $100 and Heavy $300 reported); a June 2026 change reportedly moved to a shared weekly allowance; DeepSearch/DeeperSearch quotas undocumented [S] — [Engadget](https://www.engadget.com/2281213/spacexai-grok-free-features-2026/); [PricePerToken](https://pricepertoken.com/subscriptions/grok)
- **Manus** (Oct 2026 pricing page per one source): $20/mo 4,000 credits, $40/mo 8,000, $200/mo 40,000; other sources cite $19, $49, $199 Pro (Wide Research) [S, conflicting] — [AgentMarketCap](https://agentmarketcap.ai/blog/2026/11/01/manus-2-0-vs-genspark-vs-devin-gaia-generalist-sprint); [3DNews](https://3dnews.ru/1127023/bolshe-100-iiagentov-obedinili-dlya-masshtabnih-issledovaniy-alternativa-deep-research-za-199/amp)
- **Genspark** (2026): Free ~100 credits/day; Plus $24.99/mo ($19.99 annual) from 10,000 credits; Pro $249.99/mo ($199.99 annual) from 125,000 credits; no rollover; per-query Deep Research cost unconfirmed [S] — [eesel](https://www.eesel.ai/blog/genspark-ai-pricing); [Activepieces](https://www.activepieces.com/blog/genspark-pricing-2026-free-vs-plus-vs-pro-plans.md)
- **Exa Websets**: Subscription tiers (Starter $49/mo 8,000 credits; Pro $449/mo 100,000 credits) being replaced by pay-as-you-go with API access for all (Websets V2); separate credits from Search API; Exa reportedly dropped its Deep-Reasoning Search tier and renamed Instant to Lite on 26 Oct 2026 [S] — [Exa Websets billing](https://websets.exa.ai/billing); [AlphaSignal](https://alphasignal.ai/news/exa-s-websets-v2-runs-4x-faster-at-half-the-cost-for-web-research); [TinyFish](https://www.tinyfish.ai/blog/exa-pricing)
- **Qwen**: free Deep Research inside Qwen Chat (reported); API via Alibaba Model Studio — [VC.ru](https://vc.ru/ai/1984769-alibaba-deep-research-qwen-chat); [Alibaba docs](https://www.alibabacloud.com/help/en/model-studio/qwen-deep-research)
- **Tongyi DeepResearch**: open weights, self-hostable (30B-A3B) — [Tongyi report](https://arxiv.org/html/2510.24701v2)
- **You.com ARI**: enterprise-oriented; pricing not found.
- **Kimi-Researcher**: pricing not found.

### Inferences
- Cheapest real-world entry for a solo founder: a $20 plan from one of OpenAI/Google/Anthropic/Perplexity, plus free Qwen/Genspark tiers for spillover.
- Credit-based agents (Manus, Genspark, Perplexity Computer) meter by task complexity, so costs are less predictable than flat per-report quotas.

### Gaps
- Official, dated 2026 Deep Research quota tables for OpenAI, Google, Perplexity, xAI not retrievable; conflicts above unresolved.
- No pricing for You.com ARI, Kimi-Researcher; Gemini Deep Research API token pricing not found.

## 4. Strengths, weaknesses, best use cases, and how a solo founder / small team can use each

### Takeaway
Pick by job: Gemini/OpenAI for long, cited market or competitor reports; Perplexity for fast cited answers with generous caps; Claude Research for work that mixes web with Google Workspace/connected tools; credit-based agents (Manus, Genspark) when you want research plus deliverables (decks, sites); Exa Websets for lead/company lists; open-weight Tongyi for self-hosting. Always spot-check citations.

### Cited Findings
- Cross-vendor reliability caveat: audits show links usually resolve but claims often don't match sources (39-77% factual accuracy) [I/S] — [IntuitionLabs](https://intuitionlabs.ai/pdfs/citation-reliability-ai-literature-reviews.pdf)
- OpenAI: mid-run steering, source restriction and app connections (Feb 2026) are the main usability wins; still acknowledges factual errors [S] — [Neowin](https://www.neowin.net/news/openai-upgrades-chatgpt-deep-research-with-gpt-52-and-real-time-controls/)
- Gemini: strongest independent report-quality evidence in 2025 (RACE 48.88-49.71) but only 51/100 on FINDER and one secondary guide claims weak news-link accuracy (original test not located) [I/S] — [DeepResearch Bench](https://arxiv.org/pdf/2506.11763); [The Decoder](https://the-decoder.com/?p=29784); [tech-insider (unreliable site)](https://tech-insider.org/ca/?p=2411)
- Gemini API route lets a small team embed a research agent in its own app (Interactions API, beta) [V] — [Google blog](https://blog.google/technology/developers/deep-research-agent-gemini-api/)
- Perplexity: DRACO leader on its own benchmark; usage-limit changes drew criticism (petition over "unlimited" claims; reduced Pro advanced-AI limits) [S] — [Android Authority](https://www.androidauthority.com/perplexity-pro-advanced-ai-limits-reduced-3667942/); [Change.org](https://www.change.org/p/hold-perplexity-accountable-for-unlimited-claims/u/34307401)
- Claude Research: multi-agent parallelism gives breadth at ~15x token cost, burns plan limits quickly; can read Workspace/connectors, a differentiator for internal docs + web [V] — [Anthropic](https://www.anthropic.com/news/multi-agent-research-system); [Claude support](https://support.claude.com/en/articles/11088861-using-the-research-feature). TechRadar's hands-on judged it comparable to ChatGPT/Gemini (2025) — [TechRadar](https://www.techradar.com/computing/artificial-intelligence/i-tried-claudes-new-research-feature-and-its-just-as-good-as-chatgpt-and-google-geminis-deep-research-features)
- Manus / Genspark: traffic reportedly declining since launch; Meta ownership adds strategic uncertainty for Manus; credit-metered [S] — [AgentMarketCap](https://agentmarketcap.ai/blog/2026/11/01/manus-2-0-vs-genspark-vs-devin-gaia-generalist-sprint); [KR-Asia](https://kr-asia.com/chinese-ai-agents-made-a-splash-in-2025-but-can-they-go-the-distance)
- You.com ARI: positions as enterprise research with internal-data fusion and a claimed 76% win vs OpenAI on its own benchmark [V] — [VentureBeat](https://venturebeat.com/ai/you-coms-ari-enterprise-crushes-openai-in-head-to-head-tests-aims-at-deep-research-market)
- Exa Websets: best fit for building verified lists of companies/people (prospecting) rather than narrative reports [S] — [Modern Inbound](https://moderninbound.com/blog/best-exa-websets-alternatives); [G2](https://www.g2.com/products/exa-websets/reviews)

### Inferences
- Practical solo-founder stack: one $20 general plan (primary), a second vendor to cross-check high-stakes claims, Exa/Websets or Genspark for list-building, and manual verification of any number or quote used in decisions or public content.
- Run the same question through two vendors and diff the claims; disagreements locate hallucinations cheaply.

### Gaps
- Few rigorous per-product strengths/weaknesses from independent testers for Nov 2026 models; most commentary is 2025 vintage or affiliate-style blogs.
- No independent user-experience data found for Kimi-Researcher, Z.ai, You.com ARI at small-team scale.
