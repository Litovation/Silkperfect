# Open-source deep research agents, frameworks and open-weight models (as of 24 Nov 2026)

Collection method note: all GitHub star counts were read from the live repo pages via fetch on 2026-11-24 (the fetch tool summarises pages, so counts are approximate, e.g. "about 20.2k"). Network limits in this session blocked arxiv.org, leaderboard.steel.dev, llm-stats.com, digitalapplied.com, glukhov.org, venturebeat.com, hn.algolia.com and tongyi-agent.github.io, so those sources are only known via search-result snippets. Reddit and HN threads could not be read directly (see Gaps).

## Q1. Which open-source tools are notable as of late 2026 (repo, license, stars, what they are)?

### Takeaway
The field splits into three families. (a) Report-writing orchestration frameworks that need a paid frontier LLM and a search API: GPT-Researcher (~30.9k stars), DeerFlow 2.0 (~85.7k), STORM (~31.9k), LangChain open_deep_research (~12.7k, now archived), Local Deep Research (~9.6k). (b) Open-weight agentic "search-agent" models trained with RL or synthetic data: Alibaba Tongyi DeepResearch 30B-A3B (~20.2k stars), MiroThinker v1.0-v1.7 (~8.5k), WebThinker (~1.5k), Search-R1 (~5.6k). (c) General open-weight frontier LLMs with strong built-in agentic search: Kimi K2 Thinking / K2.5 / K2.6, GLM-5, Qwen3.5, DeepSeek V3.2. Several once-popular projects look stale: STORM (last news Jan 2025), open_deep_research (archived), MiroFlow (last release v0.3 Sept 2025), OWL (last news Sept 2025).

### Cited Findings

**Orchestration frameworks (bring your own LLM + search API)**
- GPT-Researcher: ~30.9k stars, 4.3k forks, Apache-2.0 (fetched 2026-11-24). Planner/execution agents plus publisher; creates task-specific agent, generates research questions, crawls sources per question, summarises, filters and aggregates into a cited report. Supports web and local documents; also installable as a Claude Skill (`npx skills add assafelovic/gpt-researcher`). No benchmark scores on the README other than a context-filter ("Jev") test on 28 tasks — [GitHub](https://github.com/assafelovic/gpt-researcher)
- DeerFlow (ByteDance): ~85.7k stars, 12.1k forks, MIT (fetched 2026-11-24). Version 2.0 is a "ground-up rewrite" sharing no code with v1 (v1 deep-research framework kept on `1.x` branch); now a "long-horizon SuperAgent harness that researches, codes, and creates" on LangGraph/LangChain with sub-agents, memory, skills, sandboxes, MCP, Feishu/Slack/Telegram/Discord/DingTalk channels. Reached #1 on GitHub Trending on 2026-02-28 after 2.0 launch. No benchmark claims on the page. Security note: can execute commands and read/write files; designed for local trusted environment — [GitHub](https://github.com/bytedance/deer-flow)
- LangChain open_deep_research: ~12.7k stars, 1.9k forks, MIT, repo ARCHIVED (read-only) as of fetch on 2026-11-24. Described as "simple, configurable, fully open source"; LangGraph; four LLM roles (summarisation, research, compression, report writing); default search Tavily, MCP and native OpenAI/Anthropic web search supported; legacy plan-and-execute and supervisor/multi-agent versions in `src/legacy/` — [GitHub](https://github.com/langchain-ai/open_deep_research)
- Stanford STORM / Co-STORM: ~31.9k stars, 3.0k forks, MIT (fetched 2026-11-24). Wikipedia-style article generation in pre-writing (research+outline) and writing stages; Co-STORM adds human-in-the-loop collaborative discourse with mind map (EMNLP 2024). Newest README news item is Jan 2025 (litellm integration v1.1.0); 64 open issues, 57 open PRs. README says it "cannot produce publication-ready articles" and gives no quantitative benchmark results — [GitHub](https://github.com/stanford-oval/storm)
- Local Deep Research (LearningCircuit): ~9.6k stars, 946 forks, MIT, 8,862 commits (fetched 2026-11-24). Agentic research with local or cloud LLMs, encrypted local DB, many search engines (arXiv, PubMed, Semantic Scholar, Wikipedia, SearXNG, GitHub, Tavily, Brave, Google via SerpAPI, local docs). Self-reported "~95% on SimpleQA": Qwen3.6-27B at 95.7% (287/300) with `langgraph-agent` strategy and Serper search on one RTX 3090; README itself notes small sample, grader noise and possible contamination — [GitHub](https://github.com/LearningCircuit/local-deep-research)
- Jina node-DeepResearch: ~5.2k stars, 464 forks, Apache-2.0 (fetched 2026-11-24). Iterative search-read-reason loop that answers hard questions (NOT long-form reports); "Beast Mode" final answer when token budget is exhausted; 50 open issues; README says not every LLM works (needs good structured output) and demo results were mixed (a query listing Jina employees was only partially correct) — [GitHub](https://github.com/jina-ai/node-DeepResearch)
- Hugging Face smolagents "Open Deep Research" example: CodeAgent (actions as Python code) + text-based browser (adapted from Microsoft Magentic-One) + text inspector. Launched Feb 2025 — older info. Reached 55.15% on GAIA validation vs OpenAI Deep Research 67.36% (blog); README states ~55% pass@1 vs 67%. Previous open-framework best (Magentic-One) ~46%. Same setup with JSON actions instead of code dropped to ~33% — [HF blog](https://huggingface.co/blog/open-deep-research), [GitHub example README](https://github.com/huggingface/smolagents/tree/main/examples/open_deep_research)
- OWL / CAMEL-AI: ~20.2k stars, 2.3k forks, Apache-2.0 (fetched 2026-11-24). Multi-agent framework on CAMEL for web, browser automation, doc parsing, code execution. README claims "69.09 average score on GAIA benchmark and ranks #1 among open-source frameworks" without naming the GAIA split; newest news is 2025.09.22 (NeurIPS 2025 acceptance); 90 open issues; recommends OpenAI GPT-4 or later and warns other models can do much worse; open-sourced OWL-optimized training data/checkpoints 2025-07-21 — [GitHub](https://github.com/camel-ai/owl)
- MiroFlow: ~3.2k stars, Apache-2.0 (fetched 2026-11-24). Agent framework from MiroMind; README table lists 82.4% on GAIA validation (separate 2025-08-26 news item: 73.94% pass@1); trails OpenAI Deep Research on BrowseComp-EN; latest dated release v0.3 (2025-09-15) — [GitHub](https://github.com/MiroMindAI/MiroFlow)
- Tencent Yunque DeepResearch (YunqueAgent): arXiv 2601.19578 (27 Jan 2026), orchestrator + context-management + supervisor design, claims SOTA on GAIA, BrowseComp, BrowseComp-ZH, HLE (self-reported; score tables not retrieved); code at github.com/Tencent-BAC/YunqueAgent — [search result for the arXiv paper](https://arxiv.org/abs/2601.19578)
- ODR+ (Allabadi et al., arXiv 2508.10152, Aug 2025, v2 Jan 2026): open-source agent reporting 10% on BrowseComp-Small, claimed SOTA among open systems on that small subset — [arXiv](https://arxiv.org/abs/2508.10152v1)

**Open-weight agentic models/RL recipes**
- Tongyi DeepResearch (Alibaba-NLP/DeepResearch): ~20.2k stars, 1.5k forks, Apache-2.0 (fetched 2026-11-24). Tongyi-DeepResearch-30B-A3B: 30.5B total / ~3.3B active params, 128K context; released 2025-09-17, on OpenRouter from 2025-09-20; ReAct mode plus IterResearch-based "Heavy" mode. Same repo hosts the WebAgent family: WebWalker, WebDancer, WebSailor (2507.02592), WebShaper, WebWatcher, WebResearcher, ReSum, WebWeaver, WebSailor-V2 (2509.13305), AgentFold, WebLeaper, ParallelMuse, AgentFrontier, Nested Browser-Use Learning (2512.23647); tech report arXiv 2510.24701 — [GitHub](https://github.com/Alibaba-NLP/DeepResearch), [GitHub WebAgent](https://github.com/Alibaba-NLP/WebAgent)
- MiroThinker (MiroMindAI): ~8.5k stars, 648 forks, Apache-2.0 on the repo (the v1.5 HF card says MIT) (fetched 2026-11-24). Versions: v1.0 (8B/30B/72B on Qwen3-8B / Qwen3-30B-A3B-Thinking-2507 / Qwen2.5-72B; 256K ctx; up to 600 tool calls), v1.5 (30B/235B on Qwen3-30B-A3B / Qwen3-235B-A22B-Thinking-2507; 256K; 400 calls), v1.7 (30B "mini" and 235B; 256K; 300 calls). Paper arXiv 2511.11793. Page also mentions proprietary MiroThinker-H1 as BrowseComp leader — [GitHub](https://github.com/MiroMindAI/MiroThinker), [HF v1.5-235B card](https://huggingface.co/miromind-ai/MiroThinker-v1.5-235B)
- WebThinker (RUC-NLPIR, NeurIPS 2025): ~1.5k stars, MIT. Lets a large reasoning model (QwQ-32B / R1-style) drive search, page exploration and report drafting inside its own reasoning; released WebThinker-QwQ-32B and WebThinker-R1-7B/14B/32B. Older (Apr 2025, arXiv 2504.21776); README numeric tables are images, not retrieved — [GitHub](https://github.com/RUC-NLPIR/WebThinker)
- Search-R1 (PeterGriffinJin): ~5.6k stars, 504 forks, Apache-2.0. RL (PPO/GRPO/REINFORCE, built on veRL) framework to train models that interleave reasoning with search calls; supports local BM25/dense retrievers or online APIs. Derivatives: DeepResearcher, ZeroSearch, ASearcher, ParallelSearch, Tree-GRPO. A training recipe, not an end-user tool; numbers on README are images — [GitHub](https://github.com/PeterGriffinJin/Search-R1)

**General open-weight LLMs with strong agentic search**
- Kimi K2 Thinking (Nov 2025): 1T total / 32B active MoE, 256K context, Modified MIT license, stable tool use over 200-300 sequential calls, native INT4 — [HF](https://huggingface.co/moonshotai/Kimi-K2-Thinking)
- Kimi K2.5 (changelog 2026-01-29, paper arXiv 2602.02276), Modified MIT — [HF](https://huggingface.co/moonshotai/Kimi-K2.5)
- Kimi K2.6 (same 1T/32B architecture, 256K, Modified MIT; release date not given on card) — [HF](https://huggingface.co/moonshotai/Kimi-K2.6)
- DeepSeek V3.2: 685B params, MIT; the chat template adds "thinking with tools" and a `developer` role for search-agent scenarios; V3.2-Speciale does not support tool calling; the card gives no BrowseComp number — [HF](https://huggingface.co/deepseek-ai/DeepSeek-V3.2)
- Other open-weight entries seen only in search snippets: GLM-5 at 75.9% BrowseComp (via a blog quoting Z.ai docs) and Qwen3.5-397B-A17B at 78.6% (discard-all context strategy) — [steel.dev snippet](https://leaderboard.steel.dev/leaderboards/browsecomp.md), [agentmarketcap](https://agentmarketcap.ai/blog/2026/06/04/browsecomp-glm5-open-weight-browser-agent-leadership). Not verified against primary model cards.

### Inferences
- Stars are a poor quality signal: DeerFlow's 85.7k reflects the 2.0 "SuperAgent" rewrite and trending, and it is no longer primarily a research-report tool. STORM, open_deep_research and OWL have big counts but stale or archived status.
- The "open-weight model" side moved quickly in 2026: dedicated 30B search agents (Tongyi, MiroThinker) were overtaken on BrowseComp by 1T-class general models (Kimi K2.5/K2.6) in raw scores, but the small models are the ones a small team can self-host.

### Gaps
- Exact Reddit/HN counts and thread contents were not retrievable; star counts for ASearcher, DeepResearcher, Skywork DeepResearchAgent, WebSailor-only repo, Magentic-UI, dzhng/deep-research, local-deep-researcher were not fetched.
- Yunque DeepResearch score tables, WebThinker and Search-R1 numeric results were not retrievable (images or blocked arXiv).
- Whether Tongyi released a successor model after the 30B-A3B (the HF card lists none; the repo lists later research papers up to Dec 2025) was not confirmed.

## Q2. Which perform best on independent benchmarks, and which do real users actually run successfully?

### Takeaway
On BrowseComp-style hard-search benchmarks, the best open-weight numbers are from general large models with agent scaffolds (Kimi K2.6 83.2 / 86.3 with Agent Swarm per Moonshot's own card), and among dedicated, self-hostable agents MiroThinker v1.7 (74.0 self-reported) and Tongyi DeepResearch (43.4; 58.3 Heavy). Nearly all numbers are vendor self-reported; independent replications are scarce and some users report failures to reproduce. For report-writing tools, the only third-party benchmark found is DeepResearch Bench (RACE) and LangChain's own open_deep_research results on it (0.4309 to 0.4943).

### Cited Findings

**BrowseComp family (vendor-reported; harness and context strategy vary a lot)**
- Kimi K2.6 card: BrowseComp 83.2; BrowseComp Agent Swarm 86.3; HLE-Full w/ tools 54.0; DeepSearchQA 92.5 F1 / 83.0 accuracy; WideSearch item-F1 80.8 — [HF Kimi-K2.6](https://huggingface.co/moonshotai/Kimi-K2.6)
- Kimi K2.5 card (Jan 2026): BrowseComp 74.9 (with context management, discard-all), 78.4 with Agent Swarm, 60.6 without context management; HLE-Full w/ tools 50.2; DeepSearchQA 77.1; WideSearch 72.7 (79.0 swarm) — [HF Kimi-K2.5](https://huggingface.co/moonshotai/Kimi-K2.5)
- Kimi K2 Thinking card (Nov 2025, older): BrowseComp 60.2, BrowseComp-ZH 62.3, Seal-0 56.3, FinSearchComp-T3 47.4, HLE w/ tools 44.9 (Heavy 51.0) — [HF Kimi-K2-Thinking](https://huggingface.co/moonshotai/Kimi-K2-Thinking)
- MiroThinker v1.7: BrowseComp 74.0, BrowseComp-ZH 75.3, GAIA-Val-165 82.7, HLE-Text 42.9 (mini model BrowseComp-ZH 72.3). v1.5: BrowseComp 69.8, BrowseComp-ZH 71.5, GAIA-Val-165 80.8, HLE-Text 39.2. v1.0: BrowseComp 47.1, BrowseComp-ZH 55.6, GAIA-Text-103 81.9, HLE-Text 37.7. Page notes proprietary MiroThinker-H1 leads on BrowseComp and also cites an unattributed "88.2" — [GitHub MiroThinker](https://github.com/MiroMindAI/MiroThinker)
- Tongyi DeepResearch 30B-A3B tech report (Avg@3): HLE 32.9; BrowseComp 43.4; BrowseComp-ZH 46.7; WebWalkerQA 72.2; xbench-DeepSearch 75.0; FRAMES 90.6; GAIA 70.9; xbench-DeepSearch-2510 55.0. Heavy mode: HLE 38.3, BrowseComp-ZH 58.1, BrowseComp 58.3 — [HF papers 2510.24701](https://huggingface.co/papers/2510.24701)
- Search-snippet-only (unverified): Qwen3.5-397B-A17B 78.6 BrowseComp, GLM-5 75.9, an unnamed open-weight system 91.2 dated 2026-07-16 flagged low confidence on one leaderboard; closed frontier for reference GPT-5.5 Pro 90.1 (June), GPT-5.6 Sol 92.2 (Sept) — [steel.dev](https://leaderboard.steel.dev/leaderboards/browsecomp.md), [BenchLM](https://benchlm.ai/md/benchmarks/browsecomp.md). Scores depend heavily on harness; a single model can score several times higher with a full multi-turn budget than with one search — [OpenRouter benchmarks](https://openrouter.ai/benchmarks/browsecomp)
- BrowseComp-Plus (fixed corpus, reproducible; ACL 2026): older illustrative result — Search-R1 + BM25 3.86% vs GPT-5 55.9%; README sample shows gpt-oss-20b 32.17% accuracy with 12.61 avg search calls (README example, 2025-08-09). Uses Qwen3-32B as judge; has run guides for Search-R1, Qwen3 and Tongyi-DeepResearch-30B-A3B; live leaderboard on HF Spaces (Tevatron/BrowseComp-Plus) not retrieved — [GitHub](https://github.com/texttron/BrowseComp-Plus), [snippet of paper](https://arxiv.org/html/2508.06600v1)

**GAIA**
- smolagents Open Deep Research 55.15% val (Feb 2025, older); OpenAI Deep Research 67.36% — [HF blog](https://huggingface.co/blog/open-deep-research)
- OWL claims 69.09 average (split unspecified) — [GitHub](https://github.com/camel-ai/owl)
- MiroFlow table 82.4% GAIA-val — [GitHub](https://github.com/MiroMindAI/MiroFlow); MiroThinker v1.7 82.7 GAIA-Val-165; Tongyi 70.9.

**Report-quality benchmark (DeepResearch Bench, 100 PhD-level tasks, RACE quality score + FACT citation accuracy)**
- LangChain open_deep_research on Deep Research Bench (RACE, LLM-judged): GPT-5 config 0.4943 (204.6M tokens); defaults (gpt-4.1) 0.4309 ($45.98, 58.0M tokens); Claude Sonnet 4 config 0.4401 ($187.09, 138.9M tokens); Bench submission config 0.4344 ($87.83, 207.0M tokens). Warning: full 100-task run costs roughly $20-$100 — [GitHub](https://github.com/langchain-ai/open_deep_research)
- Top entries cited from secondary sources: Gemini-2.5-Pro Deep Research 48.88 overall RACE (original paper); ThinkDepth.ai 52.49; a LinkedIn self-claim of 53.5 for "Deep Dog 1" — treat as unverified — [search result](https://arxiv.org/pdf/2506.11763), [HF leaderboard commit](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard/commit/b439fbabe80f84618fe7494b5b5ba2290dedcda7)
- Leaderboard maintenance: RACE judge moved from Gemini-2.5-Pro to GPT-5.5 (dual-acceptance until 31 May 2026; GPT-5.5 board "still under construction"; cleaning model changed to GPT-5.6 Luna 22 Sep 2026), so old and new RACE scores are not directly comparable — [GitHub deep_research_bench](https://github.com/Ayanami0730/deep_research_bench)

**What users actually run**
- Local Deep Research reports running fully local on one RTX 3090 with a 27B model — [GitHub](https://github.com/LearningCircuit/local-deep-research)
- Search-snippet commentary (secondary, not verified at source) says an r/LocalLLaMA roundup (May 2026) favoured GPT-Researcher and Local Deep Research as the healthiest local-friendly projects, and that GPT-Researcher + free search API + Ollama model is the most capable free configuration — [digitalapplied guide snippet](https://www.digitalapplied.com/blog/open-source-deep-research-agents-2026-guide)
- Tongyi DeepResearch can be run without GPUs via OpenRouter (requires editing `inference/react_agent.py`) — [GitHub](https://github.com/Alibaba-NLP/DeepResearch)

### Inferences
- Rough ranking of raw open-weight search capability (vendor-reported BrowseComp): Kimi K2.6 > Qwen3.5-397B / Kimi K2.5 / GLM-5 > MiroThinker v1.7 (235B) > MiroThinker v1.5 > Kimi K2 Thinking > Tongyi 30B-A3B. For something a small team can serve on 1-2 nodes, MiroThinker-30B and Tongyi 30B-A3B are the realistic choices; the 1T Kimi models need a multi-GPU node or a hosted API.
- None of these is an independent benchmark; the closest to independent are BrowseComp-Plus (academic, fixed corpus) and DeepResearch Bench (academic, but LLM-judged and in flux).
- Report-writing orchestrators (GPT-Researcher, open_deep_research, DeerFlow) are largely un-benchmarked in their own READMEs; their quality is governed by the backing LLM (GPT-5-class config scored best in LangChain's table).

### Gaps
- No independent leaderboard numbers were retrieved for GPT-Researcher, DeerFlow, STORM on DeepResearch Bench or BrowseComp.
- Could not confirm the HF BrowseComp-Plus leaderboard standings or the Kimi/GLM/Qwen figures from independent sources; llm-stats and steel.dev were blocked, so those come only from search snippets.
- No clear independent evidence of MiroThinker or Tongyi results being reproduced; see Q4 for a reproducibility complaint.

## Q3. Install steps and minimal usage for the top 3-4

### Takeaway
Easiest for a small team: GPT-Researcher (pip + two API keys, ~$0.08-$1.30 per report), then Tongyi DeepResearch via OpenRouter or vLLM (ReAct script, needs Serper + Jina keys), MiroThinker (SGLang + uv, Serper/Jina/E2B keys), and DeerFlow 2.0 (make setup + Docker) if you want a full agent workspace.

### Cited Findings

**1. GPT-Researcher** (Apache-2.0, Python 3.12+ per README)
- Install: `pip install gpt-researcher`, or clone and `pip install -r requirements.txt` then `python -m uvicorn main:app --reload` (UI at localhost:8000); Docker: `docker-compose up --build` (UI at localhost:3000)
- Required env vars: `OPENAI_API_KEY`, `TAVILY_API_KEY`; optional `OPENAI_BASE_URL` for any OpenAI-compatible endpoint (e.g. local models), `RETRIEVER` (e.g. `tavily,mcp`), `DOC_PATH` for local docs, `LANGCHAIN_API_KEY` for tracing
- Minimal code:
```python
from gpt_researcher import GPTResearcher
import asyncio
async def main():
    researcher = GPTResearcher(query="why is Nvidia stock going up?")
    await researcher.conduct_research()
    print(await researcher.write_report())
asyncio.run(main())
```
- Cost per README: standard report ~$0.08 and ~1 minute; deep research ~$1.30 and 7-12 minutes — [GitHub](https://github.com/assafelovic/gpt-researcher)

**2. Tongyi DeepResearch 30B-A3B** (Apache-2.0)
- Install: `conda create -n react_infer_env python=3.10.0`, activate, `pip install -r requirements.txt`, `cp .env.example .env`; set `MODEL_PATH`, `DATASET`, `OUTPUT_PATH` in `run_react_infer.sh`; run `bash run_react_infer.sh`. Input is JSON/JSONL with `question` and `answer` fields.
- Keys: `SERPER_KEY_ID` (search + Scholar), `JINA_API_KEYS` (page reading), OpenAI-compatible `API_KEY`/`API_BASE` (page summarisation), `DASHSCOPE_API_KEY` (file parsing), `SANDBOX_FUSION_ENDPOINT` (Python sandbox).
- Hardware not stated by README; weights ~30.5B so a 30B MoE (3.3B active) can fit on one 80GB-class GPU in 8-bit or quantised forms (inference; not stated on page). Alternative: use OpenRouter and edit `inference/react_agent.py`. HF model card: 8,219 downloads last month, 17 quantizations, Apache-2.0 — [GitHub](https://github.com/Alibaba-NLP/DeepResearch), [HF](https://huggingface.co/Alibaba-NLP/Tongyi-DeepResearch-30B-A3B)

**3. MiroThinker (v1.7 mini 30B or v1.5)** (Apache-2.0 repo)
- Needs Python 3.10+, uv. `git clone https://github.com/MiroMindAI/MiroThinker && cd MiroThinker/apps/miroflow-agent && uv sync && cp .env.example .env`
- Serve: `python3 -m sglang.launch_server --model-path miromind-ai/MiroThinker-1.7-mini --tp $NUM_GPUS --port 61002 --trust-remote-code` (vLLM also works)
- Run: `uv run python main.py llm=qwen-3 agent=mirothinker_1.7_keep5_max200 llm.base_url=http://localhost:61002/v1`
- Keys (minimal): `SERPER_API_KEY`, `JINA_API_KEY`, `E2B_API_KEY`; summary-LLM vars `SUMMARY_LLM_BASE_URL/MODEL_NAME/API_KEY`; `OPENAI_API_KEY` only for benchmark judging.
- 235B v1.5 serving example: `--tp 8`, `--max-model-len 262144`; recommended sampling temp 1.0, top_p 0.95, repetition_penalty 1.05, max_tokens 16384. The hosted demo (dr.miromind.ai) caps at 100 tool calls so it undersells the model. MiroFlow README says the MiroThinker model can serve a research agent on a single RTX 4090 (quantised, per MiroFlow page; unverified) — [GitHub](https://github.com/MiroMindAI/MiroThinker), [HF v1.5-235B](https://huggingface.co/miromind-ai/MiroThinker-v1.5-235B), [MiroFlow](https://github.com/MiroMindAI/MiroFlow)

**4. DeerFlow 2.0** (MIT)
- `git clone https://github.com/bytedance/deer-flow.git && cd deer-flow`; `make setup` (interactive wizard writing `config.yaml` and `.env`, ~2 min); then `make docker-init && make docker-start` (recommended) or `make check && make install && make dev` (needs Node.js 22+, pnpm, uv, nginx); `make doctor` validates keys; UI at http://localhost:2026. Works with any OpenAI-compatible LLM; recommends Doubao-Seed-2.0-Code, DeepSeek v3.2, Kimi 2.5. Security: runs commands/files on host, keep it local — [GitHub](https://github.com/bytedance/deer-flow)

**Other quick-start notes**
- LangChain open_deep_research: `uv venv && source .venv/bin/activate && uv sync && cp .env.example .env`, then `uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking` (API at 127.0.0.1:2024 with Studio UI). Archived, so no further fixes — [GitHub](https://github.com/langchain-ai/open_deep_research)
- Local Deep Research: `pip install local-deep-research` then `python -m local_deep_research.web.app` (UI at localhost:5000); needs Ollama or OpenAI-compatible endpoint plus SearXNG; Docker Compose CPU or NVIDIA GPU override available — [GitHub](https://github.com/LearningCircuit/local-deep-research)
- Jina node-DeepResearch: `git clone`, `npm install`, set `GEMINI_API_KEY` (or `OPENAI_API_KEY` + `LLM_PROVIDER=openai`) and `JINA_API_KEY` (free key with 1M tokens); `npm run dev "your query"` or `npm run serve` (OpenAI-compatible server, port 3000) — [GitHub](https://github.com/jina-ai/node-DeepResearch)
- smolagents: `git clone`, `cd smolagents/examples/open_deep_research`, `pip install -r requirements.txt`, `pip install -e ../../.[dev]`, set `SERPAPI_API_KEY` or `SERPER_API_KEY` and `OPENAI_API_KEY`; `python run.py --model-id "o1" "Your question"`; default o1 needs OpenAI tier-3 access — [GitHub](https://github.com/huggingface/smolagents/tree/main/examples/open_deep_research)
- STORM: `pip install knowledge-storm`; keys via `secrets.toml` (OpenAI/Azure, a retriever key such as You.com or Bing); use `STORMWikiRunner` — [GitHub](https://github.com/stanford-oval/storm)
- WebThinker: python 3.9 conda env, serve QwQ-32B and an aux Qwen2.5-32B-Instruct via vLLM, Serper key — [GitHub](https://github.com/RUC-NLPIR/WebThinker)
- OWL: Python 3.10-3.12, `python examples/run.py`, OpenAI key — [GitHub](https://github.com/camel-ai/owl)
- Search-R1: Python 3.9 + PyTorch 2.4.0 + vLLM 0.6.3 + flash-attn; separate retriever env with faiss-gpu; training only — [GitHub](https://github.com/PeterGriffinJin/Search-R1)

### Inferences
- Every "open" agent still depends on paid third-party APIs for search and page reading (Serper, Jina, Tavily, E2B); the open-weight models save LLM cost, not search cost. A fully free stack is possible only with SearXNG + Ollama (Local Deep Research, GPT-Researcher), with a quality penalty.
- For a small team, a sensible pilot: GPT-Researcher (or Local Deep Research) for report-style output with a hosted frontier LLM; Tongyi 30B-A3B or MiroThinker-30B via vLLM/SGLang for hard multi-hop fact-finding on a single GPU box.

### Gaps
- Minimum GPU memory for Tongyi 30B-A3B and MiroThinker-30B is not stated by the READMEs; my 80GB-class figure is an estimate from parameter count, not sourced.
- Per-query cost for Tongyi/MiroThinker with Serper+Jina+summary LLM was not found.

## Q4. What do GitHub issues, Reddit and HN say about reliability and cost?

### Takeaway
Direct Reddit/HN content was not retrievable in this session, so community sentiment is thin. GitHub issues show reproduction difficulty for Tongyi DeepResearch, stalls in GPT-Researcher and a benchmark-contamination warning; cost figures come from READMEs and secondary guides, with deep runs typically ~$1 to $30 per session depending on model.

### Cited Findings
- Tongyi DeepResearch: 80 open issues; of 20 visible, themes were failure to reproduce results ("Browsecomp-en无法复现" #218, "Reproducing xbench-deepsearch Performance" #223), dataset/answer problems (#216 WebWalkerQA answers not unique, #231), tool registration errors (#234, #245), vLLM empty responses (#206), GPT-5 summariser temperature incompatibility (#211), question on context-management implementation (#229), and "[Critical Bug] Answer Leakage via Search Tools in Deep Research Agents (Search-Time Data Contamination)" (#251). No cost-focused issue titles visible — [GitHub issues](https://github.com/Alibaba-NLP/DeepResearch/issues)
- GPT-Researcher: issue #1764 "Research is getting stucked every other time while giving no meaningful logs" (confirmed label, 6 comments). Only one open issue was visible on the fetched page — [GitHub issues](https://github.com/assafelovic/gpt-researcher/issues)
- Jina node-DeepResearch README admits mixed demo quality and that not all LLMs work; hosted API rate limited to ~10-30 req/min — [GitHub](https://github.com/jina-ai/node-DeepResearch)
- OWL README FAQ says results vary with network issues and randomness, and warns non-OpenAI models may be much worse on complex tasks — [GitHub](https://github.com/camel-ai/owl)
- Search-benchmark contamination caveat: Local Deep Research's own README flags small sample, grader noise and possible contamination for its 95.7% SimpleQA figure — [GitHub](https://github.com/LearningCircuit/local-deep-research)
- Cost: GPT-Researcher README ~$0.08 standard, ~$1.30 deep; documentation reportedly ~$0.40 per o3-mini deep run (search snippet); open_deep_research 100-task benchmark $20-$100 (LangChain results: $45.98 defaults, $187.09 Claude Sonnet 4 config); one guide estimates 500K-1M tokens and $5-$30 per deep session; an ODR comparison lists $2.36/report with OpenAI web search vs $0.32 with Wikipedia — [GitHub gpt-researcher](https://github.com/assafelovic/gpt-researcher), [GitHub open_deep_research](https://github.com/langchain-ai/open_deep_research), [digitalapplied snippet](https://www.digitalapplied.com/blog/open-source-deep-research-agents-2026-guide)
- Search snippets indicate an HN post (item 45789602, apparently on Tongyi DeepResearch) where a user tried it on a healthcare/EHR research task (verdict cut off), and VentureBeat described a "furor among AI power users" — [search result](https://hn.svelte.dev/item/45789602); content not verified
- Third-party summary: "open-source case is control, cost at volume and data residency, not a better report on day one" and HN volume on GPT-Researcher is modest but positive — secondary, unverified — [rywalker.com](https://rywalker.com/research/gpt-researcher), [digitalapplied snippet](https://www.digitalapplied.com/blog/open-source-deep-research-agents-2026-guide)
- DeerFlow security notice: a Gateway admin account equals code execution on the host; meant for local trusted environments — [GitHub](https://github.com/bytedance/deer-flow)

### Inferences
- Benchmarks for dedicated search agents are reproducible only with large tool-call budgets (MiroThinker notes >200 tool calls for BrowseComp), which means real cost is dominated by search/scrape API calls and long contexts, not GPU time.
- Answer leakage via search (#251) means reported BrowseComp-style numbers for any agent that can hit the open web may be inflated; prefer BrowseComp-Plus (fixed corpus) for fair comparison.

### Gaps
- No first-hand Reddit (r/LocalLLaMA, r/MachineLearning) or HN comment text was retrieved; "user sentiment" here is thin and partly secondhand.
- No GitHub issue data retrieved for MiroThinker, DeerFlow, STORM, open_deep_research, Local Deep Research or Kimi/DeepSeek repos.
- No measured per-query dollar cost for Tongyi/MiroThinker pipelines.
