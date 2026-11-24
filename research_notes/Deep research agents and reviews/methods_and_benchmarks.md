# Methods and benchmarks for deep, multi-hop internet research agents (as of 2026-11-24)

Research-process caveats for the report writer:
- Only anthropic.com could be fetched in full. openai.com, arxiv.org, allenai.org, benchlm.ai and leaderboard.steel.dev failed DNS resolution in this sandbox (not in the allowed network domains). Most other findings therefore come from WebSearch result summaries that quote those pages, not from reading the full pages. Each finding says so where it matters.
- Leaderboard aggregators disagree with each other and name models (e.g. "GPT-5.6 Sol", "Atria Dawn Preview", "Kimi K3.1 Pro", "Claude Opus 5") that I could not confirm from a primary vendor page. Treat those as unverified.
- Dating: Anthropic multi-agent post is June 2025; OpenAI Deep Research and BrowseComp are Feb/Apr 2025; most RL-on-search papers are mid/late 2025. Anything from those dates is "older" relative to Nov 2026.

---

## 1. Core architectures and which gave measurable gains

### Takeaway
Orchestrator-worker with parallel subagents, explicit effort-scaling rules, external memory and a separate citation pass is the best-documented architecture. Anthropic reports +90.2% over a single agent on its internal eval, but at about 15x chat token cost, and its own analysis says token spend is the dominant driver of BrowseComp performance. All of these are vendor-reported.

### Cited Findings
Anthropic multi-agent research system (June 2025, vendor-reported, read in full from the primary post):
- Architecture: a LeadResearcher plans, saves the plan to Memory (context is truncated beyond 200,000 tokens), spawns parallel subagents, synthesizes, and decides whether more research is needed. Subagents run web searches and evaluate results with interleaved thinking. A separate CitationAgent attributes claims to sources before the final report. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Gain: lead Claude Opus 4 plus Claude Sonnet 4 subagents outperformed single-agent Opus 4 by 90.2% on Anthropic's internal research eval. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Strongest on breadth-first queries; domains needing shared context across agents are a poor fit — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system); [Simon Willison](https://simonwillison.net/2025/Jun/14/multi-agent-research-system/) (listed in search results as commentary; I did not open it)
- Variance analysis on BrowseComp: three factors explained 95% of performance variance; token usage alone explained 80%; the other two were number of tool calls and model choice. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Cost: agents use about 4x the tokens of chat; multi-agent systems about 15x. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Speed: parallelization cut research time by up to 90% on complex queries; lead spawns 3-5 subagents in parallel, and subagents use 3+ tools in parallel. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Effort-scaling rules embedded in the prompt: simple fact-finding = 1 agent, 3-10 tool calls; direct comparisons = 2-4 subagents, 10-15 calls each; complex research = more than 10 subagents with divided responsibilities. Without this, agents over-invested (failure mode: spawning 50 subagents for simple queries). — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Eight prompting principles: think like your agents (simulate step by step); teach the orchestrator to delegate (objective, output format, tool guidance, task boundaries; vague instructions caused duplicated work); scale effort to complexity; tool design (distinct purposes, clear descriptions); let agents improve themselves (a tool-testing agent that rewrote tool descriptions cut task completion time by 40% for later agents); start wide then narrow (agents default to long, specific queries); guide thinking with extended/interleaved thinking; parallelize tool calling. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Evaluation method: start with about 20 representative queries because effect sizes are large; LLM-as-judge with a single prompt scoring 0.0-1.0 on five criteria (factual accuracy, citation accuracy, completeness, source quality, tool efficiency) was most consistent with humans; human testers caught the system preferring SEO content farms over authoritative sources. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Context management: summarize completed phases, store info externally, spawn fresh subagents with clean contexts with handoffs; subagents write outputs to external artifacts (filesystem) and pass lightweight references back to cut token overhead and information loss. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Operational: resume-from-failure with checkpoints, tell the agent when a tool fails so it adapts, rainbow deployments, and synchronous lead-waits-for-subagents is a bottleneck. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Counter-view: LangChain's analysis pairs the Anthropic post with Cognition's "Don't Build Multi-Agents" essay and stresses context engineering (from search result listing only; not opened) — [LangChain](https://blog.langchain.com/how-and-when-to-build-multi-agent-systems)

Context management (vendor-reported, from search summary of Anthropic's announcement, autumn 2025):
- On an internal agentic-search eval, memory tool plus context editing improved performance 39% over baseline; context editing alone 29%. In a 100-turn web-search eval, context editing cut token use 84% and let agents finish workflows that would otherwise fail from context exhaustion. Self-reported, not independently verified. Context editing was beta, using beta header `context-management-2025-06-27`. — [Anthropic news](https://www.anthropic.com/news/context-management); [platform docs](https://platform.claude.com/docs/en/build-with-claude/context-editing)

OpenAI Deep Research (Feb 2025, older, vendor-reported):
- Powered by an early version of o3 optimized for browsing; system card dated Feb 25, 2025, focuses on safety including prompt injection. — [OpenAI system card](https://openai.com/index/deep-research-system-card/)
- Launch numbers: HLE 26.6% (browsing + python); GAIA average 67.36 pass@1 and 72.57 cons@64 (i.e. majority-vote over 64 samples adds about 5 points); BrowseComp 51.5% per OpenAI's BrowseComp page. — [OpenAI intro](https://openai.com/index/introducing-deep-research/); [BrowseComp page](https://openai.com/index/browsecomp/) (figures via search-result summaries; one result said the 51.5% appears on OpenAI's page, another said it only found it on a secondary blog — Galileo — so verify against the primary page)

Google (vendor-reported):
- Gemini Deep Research agent (Dec 2025, Interactions API) scored 66.1% on DeepSearchQA (900 hand-crafted tasks, 17 fields; scores answer completeness and recall) vs 56.6% for Gemini 3 Pro; third-party coverage puts GPT-5 Pro at 65.2%. Google open-sourced DeepSearchQA. — [Google blog](https://blog.google/technology/developers/deep-research-agent-gemini-api/); [Analytics India](https://analyticsindiamag.com/ai-news-updates/googles-new-deep-research-agent-scores-sota-results-on-benchmarks)

Test-time compute / scaffolding:
- BrowseComp paper plots accuracy against test-time compute on a log scale (accuracy rises with more browsing effort); paper has 1,266 problems. I did not retrieve the surrounding text. — [BrowseComp paper](https://arxiv.org/abs/2504.12516)
- Tongyi DeepResearch "Heavy" mode and DR-style parallel research/synthesis (see Section 2) and Anthropic's multi-agent result both indicate that parallel samples plus synthesis scales accuracy; aggregators list Claude multi-agent configurations (e.g. "Opus 4.8 multi-agent" 88.5% vs single-agent 84.3%; a 10-agent Opus 5 config at 93.6%) — [BenchLM via search summary](https://benchlm.ai/benchmarks/browsecomp). Aggregator data; names unverified.
- One 2026 tracker notes scores vary with scaffolding, e.g. one model scoring 91.2 on BrowseComp with one context-compaction strategy and 90.4 without — [secondary tracker via search summary](https://codersera.com/blog/ai-agent-benchmarks-state-of-leaderboard-may-2026/)

Retriever quality matters as much as the agent (independent academic, ACL 2026):
- BrowseComp-Plus fixes the corpus (~100K human-verified docs, 830 queries from BrowseComp). With a BM25 retriever Search-R1 gets 3.86% and GPT-5 gets 55.9%; GPT-5 with Qwen3-Embedding-8B gets 70.1% with fewer search calls. Best retriever alone reaches 20.3 nDCG@10. — [BrowseComp-Plus paper](https://arxiv.org/pdf/2508.06600); [ACL 2026](https://aclanthology.org/2026.acl-long.1023/)

### Inferences
- The clearest evidence-backed levers: (1) parallel subagents for breadth, (2) effort-scaling rules in the lead prompt, (3) external notes/memory to survive context limits, (4) separate citation/verification pass, (5) better retrieval tools. The 80% variance-by-tokens finding implies much of the multi-agent gain is "more compute spent in parallel", not architecture magic; that also explains the 15x cost.
- Anthropic's own caveat (shared-context tasks) matches Cognition's critique; for tightly coupled reasoning, a single agent with good context management is likely better.
- Majority-vote (cons@64) and multi-agent gains on BrowseComp/GAIA suggest parallel sampling plus synthesis is a reliable test-time scaling method, at proportional cost.

### Gaps
- Ablations isolating the citation agent, reflection steps, or memory file individually on public benchmarks: none found; Anthropic reports only whole-system numbers.
- Full text of the OpenAI system card and BrowseComp page were not readable (domain blocked); primary-page verification of 51.5% outstanding.
- Google's research-side papers (e.g. Test-Time Diffusion Deep Researcher) were not searched; no Google-paper numbers beyond DeepSearchQA.
- I did not open Simon Willison's or Cognition's posts.

---

## 2. Training methods (RL on search, synthetic data, test-time scaling)

### Takeaway
Open models trained with outcome-reward RL plus synthetic hard-question data closed much of the gap in 2025-26 (e.g. Tongyi DeepResearch 43.4 on BrowseComp with 3.3B active params), and RL with rubric rewards (DR Tulu) makes long-form research agents about 3 orders of magnitude cheaper per query than OpenAI Deep Research on one benchmark. All are author-reported.

### Cited Findings
- Search-R1 (Mar 2025; RL where the model emits search queries mid-reasoning, retrieved-token masking, simple outcome reward): v5 (Aug 2025) reports +41% (Qwen2.5-7B) and +20% (Qwen2.5-3B) over RAG baselines across seven QA datasets; earlier versions reported +26%/+21%/+10% and v4 24%/20%, so figures depend on version. — [arXiv 2503.09516](https://arxiv.org/abs/2503.09516) (via search summary)
- Kimi-Researcher (Moonshot, June 2025): end-to-end agentic RL; HLE Pass@1 rose from 8.6% to 26.9% (Pass@4 40.17%) almost entirely through RL; xbench-DeepSearch 69% pass@1 (avg of 4 runs). Tested 17-18 June 2025. About 23 reasoning steps and 200+ URLs per task per a Chinese-language report. No BrowseComp number found. — [Moonshot](https://moonshotai.github.io/Kimi-Researcher); [ifeng report](https://tech.ifeng.com/c/8kMNNR6XZJO)
- WebSailor (Alibaba, July 2025): post-training on hard synthetic data; WebSailor-72B reported matching a top proprietary agent (Doubao) on BrowseComp-zh. WebSailor-V2 (ICLR 2026): Qwen3-30B-A3B variant 35.3 BrowseComp-EN, 44.1 BrowseComp-ZH, 30.6 HLE. — [WebSailor arXiv 2507.02592](https://arxiv.org/abs/2507.02592); [WebSailor-V2 ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9760f18785acf535321e50405fd36578-Abstract-Conference.html) (via search summaries)
- WebDancer (May 2025): ReAct-based, multi-stage pipeline ending in RL; evaluated on GAIA and WebWalkerQA, not BrowseComp. — [arXiv 2505.22648](https://arxiv.org/pdf/2505.22648) (via search summary)
- Other open results: DeepDive-32B 15.3% BrowseComp, 22.2% after RL stage (knowledge-graph synthetic questions + multi-turn RL); WebExplorer-8B 15.7% BrowseComp-en, 32.0% BrowseComp-zh. — [DeepDive](https://arxiv.org/html/2509.10446v2) (via search summary)
- Tongyi DeepResearch (Alibaba, arXiv 2510.24701, Oct 28 2025, rev. Nov 4 2025): 30.5B total / 3.3B active params on Qwen3-30B-A3B-Base; agentic mid-training plus post-training; largely automatic synthetic data pipeline; 43.4 on BrowseComp, 46.7 on BrowseComp-ZH; open-sourced. — [arXiv 2510.24701](https://arxiv.org/abs/2510.24701) (via search summary; competitor comparison numbers not retrievable)
- DR Tulu (Ai2 et al., arXiv 2511.19399, Nov 24 2025; ICML 2026): Qwen3-based 8B; SFT on naturally occurring information-seeking queries then online RL with Evolving Rubrics (RLER, rubrics co-evolve with the policy and incorporate newly explored information). Authors report it beats open deep-research models on four long-form benchmarks (science, healthcare, general) and matches or exceeds OpenAI Deep Research, Perplexity Deep Research and Gemini 3 Pro + Search; on ScholarQA-CS2 about USD 1.8 per query for OpenAI Deep Research vs USD 0.0019 for DR Tulu. Open model, data, rubrics, infra. Not independently verified. — [arXiv 2511.19399](https://arxiv.org/abs/2511.19399); [Ai2 blog](https://allenai.org/blog/dr-tulu)
- BrowseComp-Plus shows open Search-R1 at 3.86% under BM25 versus GPT-5 at 55.9% (see Section 1), i.e. small search-RL models trained on simple QA transfer poorly to hard multi-hop browsing. — [arXiv 2508.06600](https://arxiv.org/pdf/2508.06600)
- OpenAI notes its Deep Research model was trained on data that teaches BrowseComp-style tasks, so BrowseComp is partly in-distribution for it. — [OpenAI BrowseComp page](https://openai.com/index/browsecomp/) (via search summary)

### Inferences
- The recipe repeated across Tongyi/WebSailor/DeepDive: build hard questions via graph/obfuscation (so answers need many hops), SFT on trajectories from a stronger model, then GRPO-style RL with verifiable outcome reward. Training data difficulty appears to matter more than model size (3.3B-active model at 43.4).
- For non-verifiable long-form reports, rubric rewards (DR Tulu) replace exact-match reward.
- These are relevant to a practitioner mainly as signals (what to prompt for), not as something to replicate with Claude Code; API frontier models already lead (Section 3).

### Gaps
- Kimi-Researcher BrowseComp score: not found.
- WebDancer, WebSailor, Tongyi: full results tables (GAIA, HLE, xbench, FRAMES) not retrieved because arXiv was blocked.
- Tongyi/DR Tulu training updates in 2026 (e.g. later versions) not searched.
- Independent reproduction of any of these RL results: none found.

---

## 3. Benchmark landscape and leaderboards (Nov 2026)

### Takeaway
Frontier BrowseComp scores are now about 84-93% depending on source and setup, but nearly all are vendor-reported and there is no official public BrowseComp leaderboard; aggregator rankings conflict, so no single "leader" can be asserted with confidence. Independent, controlled benchmarks (BrowseComp-Plus, Agents' Last Exam, DeepResearch Bench) are where outside verification exists.

### Cited Findings
Vendor-reported BrowseComp (earlier-2026):
- OpenAI GPT-5.5 launch table: GPT-5.5 84.4%; GPT-5.5 Pro 90.1%; Claude Opus 4.7 79.3%; Gemini 3.1 Pro 85.9%. Third-party write-ups citing 90.1% are citing the Pro variant. — [OpenAI GPT-5.5](https://openai.com/index/introducing-gpt-5-5/) (via search summary; page not fetchable). Note this table is OpenAI's own comparison across vendors.
- Gemini 3 Pro 59.2% (older, Nov 2025 era). — via [scholarcompass summary](https://scholarcompass.net/en/tasks/deep-research-agents/benchmarks/browsecomp)

Aggregator snapshots (unverified; conflicting; treat as indicative):
- BenchLM Nov 2026 (64 models, all "lab-reported"): "Atria Dawn Preview" 92.5%, "GPT-5.6 Sol" 92.2%, "Kimi K3.1 Pro" 92.1%; also lists Claude Opus 5 at 90.8% (Anthropic-reported) and a 10-agent Opus 5 prerelease config at 93.6%; Opus 4.8 84.3% single-agent. — [BenchLM](https://benchlm.ai/benchmarks/browsecomp)
- Steel's leaderboard: GPT-5.6 Sol Ultra (system setup) 92.2% tracked leader; counts system setups (model + tools + policy). — [Steel](https://leaderboard.steel.dev/leaderboards/browsecomp/)
- TensorFeed (Oct 19 2026): "GPT-6 Astra" 91.5% (vendor-reported). AnotherWrapper (Sep 6 2026): Kimi K3 91.2%. Codesota (older snapshot): DeepSeek-V4-Pro Max 83.4%. BenchLeader (Oct 2026) shows Gemini 3.1 Pro at 31.2%, likely a different variant/setup. — [TensorFeed](https://tensorfeed.ai/benchmarks/browsecomp); [AnotherWrapper](https://anotherwrapper.com/tools/llm-pricing/evals/browsecomp); [Codesota](https://www.codesota.com/benchmark/browsecomp); [BenchLeader](https://www.benchleader.com/benchmarks/kaggle_browsecomp)
- Several of those model names (GPT-5.6, GPT-6 Astra, Atria Dawn, Claude "Opus 5.5"/"Mythos 5") did not turn up in any primary vendor page I could read; an additional search for GPT-5.6 found nothing. Flag as unconfirmed.
- Caveat on comparability: multi-agent and large-token-budget runs (e.g. 10M-token budget) are ranked alongside single-agent ones on some boards. — [Scholar Compass](https://scholarcompass.net/en/tasks/deep-research-agents/benchmarks/browsecomp)
- No official BrowseComp leaderboard; scores in circulation are vendor self-reports and vary with scaffolding. — [codersera Jan-May 2026 roundup](https://codersera.com/blog/ai-agent-benchmarks-state-of-leaderboard-may-2026/)

Independent / controlled:
- BrowseComp-Plus (ACL 2026 main): fixed corpus, official HF leaderboard at tevatron-browsecomp-plus.hf.space; results must be fully model-generated. Paper numbers: GPT-5 55.9% (BM25) / 70.1% (Qwen3-Embedding-8B). I could not read the current leaderboard, and an aggregator figure (llm-stats "Mercury 3" 0.552) looked unreliable. — [paper](https://arxiv.org/pdf/2508.06600); [leaderboard](https://tevatron-browsecomp-plus.hf.space); [llm-stats](https://llm-stats.com/benchmarks/browsecomp-plus)
- DeepResearch Bench (RACE, 100 PhD-level tasks; June 2025): Gemini-2.5-Pro Deep Research top at 48.88 overall RACE and 111.21 effective citations/task; later leaderboard entry ThinkDepth.ai 0.5249 (about 52.5 if same scale; unconfirmed). README says that after 1 June 2026 only a GPT-5.5-judged leaderboard is maintained; entries by email submission. — [paper](https://arxiv.org/abs/2506.06287); [README](https://raw.githubusercontent.com/Ayanami0730/deep_research_bench/main/README.md); [HF leaderboard](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard)
- HLE: tool-enabled rankings tracked separately; llm-stats lists 5 tool-variant models, 0 verified, all self-reported; no-tools leader listed as Tencent Hy3 47.0% (aggregator). A 2025 study (Scale AI, "Search-Time Data Contamination") found for about 3% of HLE questions search agents found a public copy with answers. — [llm-stats](https://llm-stats.com/benchmarks/humanity's-last-exam-(with-tools%2C-text-only)); [arXiv 2508.13180](https://arxiv.org/html/2508.13180v1)
- Agents' Last Exam (UC Berkeley RDI): private tasks rotated into public pool as they age to resist contamination. — [HF paper 2606.05405](https://huggingface.co/papers/2606.05405.md) (via search summary)
- DeepResearchGym: not covered in my searches.
- GAIA: no independent contamination-controlled 2026 leaderboard found; OpenAI DR launch (Feb 2025) 67.36 pass@1 is the only number I have, and it is old.

### Inferences
- A sensible statement for the report: "As of Nov 2026, frontier vendors report 84-93% on BrowseComp; the top is a cluster within ~1-2 points (92.1-92.5% on BenchLM), differences are within noise and setup variation, and none are independently verified." The BrowseComp ceiling is close, so BrowseComp is losing discriminative power; expect attention to move to BrowseComp-Plus, DeepSearchQA, HLE-with-tools, and long-form report benchmarks.
- Multi-agent / large-budget configurations should be compared separately from single-agent runs.

### Gaps
- Primary-source verification of any 2026 model score above (domains blocked; some model names unconfirmed).
- Current official BrowseComp-Plus leaderboard standings.
- GAIA, DeepResearchGym, xbench, HLE-with-tools current independent top scores.
- Current RACE/FACT top score on DeepResearch Bench.

---

## 4. Known failure modes

### Takeaway
Citation fabrication and unsupported statements remain common, source-quality bias (SEO farms) is acknowledged by Anthropic, and indirect prompt injection and poisoning of user-generated content are demonstrated attacks on deep research agents; cost and runaway behavior are controlled mainly by prompt-level effort rules.

### Cited Findings
- Hallucinated URLs: across commercial LLMs and deep research agents, hallucinated URL rates 3-13% and 5-18% non-resolving overall; deep research agents generate more citations per query but hallucinate URLs at higher rates; the open-source `urlhealth` tool in a self-correction loop cut non-resolving URLs 6-79x to under 1%. Preprint (arXiv 2604.03173, April 2026), Wayback-based method biases counts. — [arXiv 2604.03173](https://arxiv.org/abs/2604.03173)
- ReportBench: two failure types - statement hallucination (content deviates from cited source) and citation hallucination (fabricated reference). — [arXiv 2508.15804](https://arxiv.org/pdf/2508.15804)
- DeepTRACE (Microsoft Research): citation accuracy 40-80% across deep research systems; large fractions of unsupported statements; one-sided answers on debate queries; deep research modes reduce overconfidence. — [Microsoft Research](https://microsoft.com/en-us/research/publication/deeptrace-auditing-deep-research-ai-systems-for-tracking-reliability-across-citations-and-evidence)
- DeepHalluBench argues end-to-end evaluation hides mid-trajectory errors, recommends auditing planning and intermediate steps. — [arXiv 2601.22984](https://arxiv.org/pdf/2601.22984)
- SEO / source quality: Anthropic human testers found the system preferring SEO-optimized content farms over authoritative sources; other documented behaviors: endless search for nonexistent sources, continuing after sufficient results, verbose queries, duplicated work across subagents, and agents "not finding obvious information". — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Cost: multi-agent about 15x chat tokens; token usage explains 80% of BrowseComp variance (Anthropic, above). DR Tulu authors estimate OpenAI Deep Research at about USD 1.8 per query on ScholarQA-CS2 vs USD 0.0019 for DR Tulu. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system); [arXiv 2511.19399](https://arxiv.org/abs/2511.19399)
- Prompt injection / poisoning: TRAP benchmark (ICML 2026): six frontier models are susceptible in 25% of tasks on average (13% GPT-5 to 43% DeepSeek-R1), small interface/context changes often doubling success. StakeBench: indirect injections in ordinary web content achieved 41.67%-68.16% attack success. WARP (arXiv 2605.24245, May 2026): deep research systems STORM, Co-STORM, OmniThink poisoned via user-generated content (Reddit, Wikipedia) that they repeatedly retrieve. ZombieAgent (Radware, Jan 2026): server-side prompt-injection paths against OpenAI's Deep Research. Web-scale measurement (arXiv 2604.27202): 1.2B URLs / 24.8M hosts analyzed for agent-directed instructions. — [arXiv 2512.23128](https://arxiv.org/abs/2512.23128); [arXiv 2605.24245](https://arxiv.org/abs/2605.24245); [CSA note](https://labs.cloudsecurityalliance.org/research/csa-research-note-pleasefix-agentic-browser-exploits-2026032/); [arXiv 2604.27202](https://arxiv.org/html/2604.27202v1); [CSO Online](https://www.csoonline.com/article/4184455/prompt-injection-breaks-todays-ai-agents-study-warns.html) (figures via search summaries)
- Search-time contamination: agents can find answer-bearing copies of benchmark questions online (about 3% of HLE questions). — [arXiv 2508.13180](https://arxiv.org/html/2508.13180v1)
- Overconfidence: no hard numbers found beyond DeepTRACE's claim that deep research modes reduce it relative to plain search-LLMs.

### Inferences
- A cheap, high-yield mitigation is a mechanical post-pass: resolve every cited URL (HTTP check) and verify the quoted claim appears on the page, as `urlhealth`-style loops and Anthropic's CitationAgent suggest.
- Treat all fetched web text as untrusted data; give subagents minimal tools (no write/exec) when browsing arbitrary pages.

### Gaps
- Quantified overconfidence/calibration for deep research agents.
- Specific numbers on SEO-spam bias beyond Anthropic's anecdote.
- Whether injection rates differ for Claude-based agents in 2026 (TRAP lists only GPT-5 and DeepSeek-R1 extremes in the summary).

---

## 5. Practical recipe (Claude Code / subagents / MCP)

### Takeaway
Practitioners replicate Anthropic's pattern as: lead plans and fans out parallel researcher subagents, each writes findings to notes files, a final pass synthesizes and checks citations. Most public write-ups are community material rather than controlled evidence; the quantitative backing comes from Anthropic's post.

### Cited Findings
- Community Claude Code pattern: subagents write findings to markdown notes in a shared folder; a report-writer agent reads them; agents do not message each other; the filesystem is the handoff. — [PromptLayer](https://blog.promptlayer.com/using-claude-code-to-run-deep-research/)
- claudekit `/research`: spawns subagents in a single message; depth-first (2-4 subagents) vs breadth-first (5-10); claims a 10-subagent ceiling (unverified). — [claudekit](https://cdn.jsdelivr.net/npm/claudekit@0.9.5/src/commands/research.md)
- Community skills add verification: MindStudio `/deep` describes agents voting on claims; Nimbalyst skill returns citations plus confidence levels; daymade skill keeps a Gaps section for what was searched but not found. — [MindStudio](https://www.mindstudio.ai/blog/what-is-deep-research-command-claude-code); [Nimbalyst](https://nimbalyst.com/skills/deep-research/); [daymade](https://lobehub.com/skills/daymade-claude-code-skills-deep-research)
- Parallel subagents make token spend scale quickly (community commentary). — [paddo.dev](https://paddo.dev/blog/three-ways-deep-research-claude/) (listed in results only)
- Evidence-backed prompt patterns from Anthropic (all above): explicit effort-scaling table; delegation briefs with objective, output format, tool guidance and boundaries; short broad queries first then narrowing; interleaved thinking; parallel tool calls; plan persisted to a file/memory; subagent output to files with references returned; separate citation step; LLM-judge rubric (accuracy, citations, completeness, source quality, efficiency) on about 20 test queries; agent-rewritten tool descriptions (-40% time). — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Context hygiene: clear stale tool results and keep key findings in a memory file; reported +39% and -84% tokens on Anthropic's eval. — [Anthropic news](https://www.anthropic.com/news/context-management)
- Retrieval tool quality: stronger retrieval (dense embeddings over BM25) improved GPT-5 from 55.9% to 70.1% with fewer searches, so give agents a good search/fetch MCP and tell them how to choose tools. — [arXiv 2508.06600](https://arxiv.org/pdf/2508.06600)
- Citation checking: run a URL-resolution/self-correction pass; reported reduction of non-resolving URLs to under 1%. — [arXiv 2604.03173](https://arxiv.org/abs/2604.03173)

### Inferences
Suggested workflow for Claude Code (synthesized from the above, not independently tested):
1. Lead writes a plan file (question decomposition, effort tier per the 1/2-4/10+ subagent rule).
2. Fan out researchers in parallel, one message, each with objective, boundaries, output file path and format, source-quality guidance (prefer primary sources; flag SEO/aggregators), and a tool-call budget.
3. Each researcher starts with short broad queries, fetches full pages instead of relying on snippets, records claims with URL, and lists gaps.
4. Lead reads notes, spawns follow-ups for gaps/conflicts (iterative loop with a stop condition), avoids shared-context-heavy splitting.
5. Verification pass: separate agent/script resolves each URL and checks the claim against page text; treat web text as untrusted; minimal tool permissions for browsing agents.
6. Final synthesis with source-conflict notes; keep a small eval set (about 20 queries) with an LLM-judge rubric to iterate on prompts.
7. Budget: expect roughly 15x token cost vs chat for multi-agent; use cheaper model for subagents (Anthropic used Sonnet subagents under an Opus lead).

### Gaps
- No controlled study comparing Claude Code skill-based research workflows to benchmarks; community write-ups are anecdotal.
- Could not verify Claude Code subagent limits from official docs.
- Simon Willison's and Latent Space's practitioner write-ups were not opened.
