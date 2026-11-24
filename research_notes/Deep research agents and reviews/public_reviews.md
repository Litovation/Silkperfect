# Public reviews and real-user sentiment on deep research agents (as of 24 Nov 2026)

**Method limits (read first).** In this session WebFetch could only reach github.com. cjr.org, simonwillison.net, arxiv.org, trustpilot.com, producthunt.com, tomsguide.com, dev.to and others failed DNS, so I could not open them. Almost every finding below comes from search-result summaries, with the URLs they pointed to, not from reading the full page. Treat exact numbers and quotes as "per search snippet, verify against source". I found no Reddit or Hacker News threads at all. The quotes marked "quote" are short fragments that appeared in the snippets. Many "best AI for research 2026" pages are SEO, affiliate or competitor-vendor content, and their dates and model names are inconsistent. They are flagged as such.

## 1. What do independent reviewers say about each tool?

### Takeaway
Independent reviewers broadly agree that deep research tools are genuinely useful but need human verification. Their warnings centre on confident-looking, citation-heavy reports. There is no consensus winner. OpenAI and Claude are praised for synthesis and structure, Perplexity for speed and citations, and Gemini for Google-ecosystem and academic sources. Evidence on Manus, Genspark, Kimi, Grok DeepSearch, GPT-Researcher and Tongyi from independent reviewers is thin.

### Cited Findings
- Simon Willison (2025): the Deep Research products from Google, OpenAI and Perplexity are all impressive, able to churn for several minutes and assemble lengthy reports. He argues AI-assisted search-based research "actually works now". Source is his tag page and Substack, seen only via snippet. — [simonwillison.net/tags/deep-research](https://simonwillison.net/tags/deep-research); [Substack: AI assisted search-based research actually works now](https://simonw.substack.com/p/ai-assisted-search-based-research)
- Willison, Feb 2025 (OpenAI launch), as summarised by search: warned that a multi-page document with headings, citations and confident arguments can give a misleading impression of a PhD-level research assistant. Paraphrase, not verified verbatim. — [simonwillison.net/2025/Feb/25/deep-research-system-card](https://simonwillison.net/2025/Feb/25/deep-research-system-card/)
- Willison, 18 Oct 2025, tested the o4-mini-deep-research API: the run cost about 53 cents, it did not return a comprehensive list, and there is a cap on tool calls per session. He suggested exhaustive lists may not play to deep research's strengths. — [simonwillison.net/2025/Oct/18/o4-mini-deep-research](https://simonwillison.net/2025/Oct/18/o4-mini-deep-research/); [TIL write-up](https://til.simonwillison.net/llms/o4-mini-deep-research)
- Ethan Mollick (Feb 2026 guide, per a third-party summary): for most people doing real work, the most important additional feature is Deep Research and connecting AI to your own content. He also says OpenAI and Anthropic have clear leads over Google in "harness capability" (code, files, extensive research). — [summary of Mollick guide](https://velikov-mihail.github.io/ai-econ-wiki/summaries/guide-which-ai)
- Mollick (July 2026, via a Willison link-blog summary): Gemini "has fallen off" his list because Google lacks an established entry in the Codex/ChatGPT Work/Cowork category. I could not verify this independently. — [simonwillison.net/2026/jul/27](https://simonwillison.net/2026/jul/27/an-opinionated-guide-to-which-ai-to-use-to-do-stuff)
- Mollick on OpenAI Deep Research at launch (early 2025) said it showed "where research tools were heading". He wrote this in "The End of Search, The Beginning of Research". I found no Mollick head-to-head of the products. — [One Useful Thing](https://www.oneusefulthing.org/p/the-end-of-search-the-beginning-of/comments); [3quarksdaily excerpt](https://3quarksdaily.com/?p=272919)
- TechRadar hands-on (2025) concluded Claude's Research feature is "just as good as ChatGPT and Google Gemini's Deep Research features". Only the headline was visible. — [TechRadar](https://www.techradar.com/computing/artificial-intelligence/i-tried-claudes-new-research-feature-and-its-just-as-good-as-chatgpt-and-google-geminis-deep-research-features)
- PCMag (via Yahoo) said both ChatGPT and Claude can produce well-sourced reports, and that the depth of research separates them, and named ChatGPT the winner. Snippet only. — [Yahoo/PCMag](https://tech.yahoo.com/ai/articles/chatgpt-vs-claude-ive-tested-130115195.html)
- A Substack writer on Claude Research: "I still prefer ChatGPT Deep Research". — [AI Goes to College](https://aigoestocollege.substack.com/p/claude-releases-deep-research)
- Gemini Deep Research, Android Authority hands-on (early 2025): positives in follow-up questions, but reading the report in detail the limitations became apparent. Verdict: "hit and miss". — [Android Authority](https://www.androidauthority.com/hands-on-gemini-deep-research-3508607)
- The Decoder (early 2025) reported Gemini's Deep Research "struggles with accuracy in early testing". — [the-decoder.com](https://the-decoder.com/geminis-ai-powered-deep-research-feature-struggles-with-accuracy-in-early-testing/)
- TechRadar on Gemini 2.5 Pro Deep Research: "I appreciated the thoroughness", though the piece also asks whether an AI can overthink. — [TechRadar](https://www.techradar.com/computing/artificial-intelligence/i-tried-using-the-deep-research-feature-with-googles-gemini-2-5-pro-model-and-now-i-wonder-if-an-ai-can-overthink)
- Tom's Guide's favourable Gemini pieces cite Google's own internal tests (users preferred Deep Research output over other tools by more than 2-to-1). That is vendor-sourced. — [Tom's Guide](https://www.tomsguide.com/ai/google-just-gave-gemini-a-major-research-upgrade-and-its-already-beating-the-competition)
- Perplexity: aggregators describe it as fast (about 2-4 minutes), well cited, but less deep than ChatGPT or Gemini. One blog says its research is not often factually wrong, it is lacking in detail or depth. These are blog opinions of unknown rigour. — [Nesyona](https://nesyona.com/articles/best-ai-for-research), [aimultiple](https://aimultiple.com/ai-deep-research)
- Grok DeepSearch: no independent head-to-head test of DeepSearch found. One third-party analysis says reports can contain subtle errors and depend on source reliability, and another notes it surfaces blogs alongside Reuters and viral X posts. Both are weak, secondary sources. — [codingmall](https://codingmall.com/knowledge-base/25-global/256714-what-are-the-limitations-of-grok-3s-deepsearch-feature); [suprmind](https://suprmind.ai/hub/grok/features/). AIMultiple reports Grok leads on "accuracy of the data provided" but its methodology was not visible. — [AIMultiple](https://research.aimultiple.com/ai-deep-research)
- Manus vs Genspark (one reviewer, same-week test, date unclear, Techpoint Africa): Manus stronger on depth and accuracy and needed less editing, while Genspark was faster and more visual but needed fact-checking and added citations. N=1 reviewer. — [Techpoint](https://techpoint.africa/guide/manus-vs-genspark/)
- Kimi Deep Research: only Moonshot's own materials (Kimi-Researcher blog, 20 June 2025; help pages). I found no independent hands-on review of Kimi-Researcher. — [Moonshot blog](https://moonshotai.github.io/Kimi-Researcher); [Kimi help](https://www.kimi.com/en/help/deep-research/deep-research-overview). Related but not the same product: [KDNuggets, "I Tried Kimi Agent"](https://kdnuggets.com/i-tried-kimi-agent-and-heres-what-i-found).
- Tongyi DeepResearch (Alibaba): technical report claims 30.5B total params (3.3B active), HLE 32.9, BrowseComp 43.4, FRAMES 90.6. All are vendor self-reports. VentureBeat's piece notes much of the evaluation relied on a simulated environment. — [arXiv 2510.24701](https://arxiv.org/html/2510.24701v2); [VentureBeat](https://venturebeat.com/ai/the-deepseek-moment-for-ai-agents-is-here-meet-alibabas-open-source-tongyi)
- GPT-Researcher: I found directory listings and install guides, no first-person test write-ups. Its pros are MIT licence, self-hosting, bring-your-own-model, and URL-cited reports. Cons are the "experimental, as-is" disclaimer and the need to check claims. — [andrew.ooo review](https://andrew.ooo/posts/gpt-researcher-deep-research-agent-review/); [GitHub](https://github.com/assafelovic/gpt-researcher). Review sites do not give figures. A skills guide cites 26k+ stars, unverified.
- Deep Research Bench II (arXiv, Jan 2026): 132 expert-grounded tasks, and even the strongest models meet fewer than 50% of rubrics. Not a product head-to-head. — [arXiv 2601.08536](https://arxiv.org/html/2601.08536v1)

### Inferences
- Willison and Mollick (the most credible individual voices) are positive on utility and consistently pair it with "verify" caveats. Mollick's tier placement shifted toward OpenAI and Anthropic and away from Google between Feb and Jul 2026 (the July item is second-hand).
- For Kimi, Grok DeepSearch, Genspark, GPT-Researcher and Tongyi, the public independent evidence is mostly absent. A report writer should say that rather than rank them.

### Gaps
- Could not read any primary page (blocked hosts), so no verbatim quotes were verified.
- No Ars Technica, Verge, TechCrunch or Wired hands-on review of any deep research product was surfaced by search.
- No independent hands-on of Kimi-Researcher or Genspark's research mode.

## 2. What do users say on Reddit, HN, X, G2, Trustpilot, Product Hunt and app stores?

### Takeaway
I could not retrieve Reddit, HN or X threads. Review-site data show a split. G2 scores are favourable (Perplexity about 4.4, Manus about 4.3) while Trustpilot is hostile for Perplexity, Manus and Genspark, driven by credits, billing, quotas and support rather than research quality. Trustpilot skews to people with complaints, so it is not a representative sample.

### Cited Findings
- Perplexity G2: about 4.4/5 across about 313 reviews (count varies by snapshot). Most frequent complaints were usage limits tied to subscription (63 reviews) and inaccurate data needing verification (34 reviews). Praise: ease of use, quick responses. — [G2 Perplexity reviews](https://g2.com/products/perplexity/reviews); [checkthat.ai summary, 890+ reviews](https://checkthat.ai/brands/perplexity/reviews)
- Perplexity Trustpilot: reported 1.5/5 from 674 reviews by one aggregator, and 820+ reviews with 79% one-star by Zemith. Zemith sells a competing product. Counts are inconsistent. — [Zemith Perplexity review](https://www.zemith.com/en/learn/perplexity-review)
- Perplexity Deep Research quota complaints: one G2 reviewer reported usage falling from 600 deep searches/day to 20/month. Single anecdote via a search summary. — [G2 Perplexity page 4](https://www.g2.com/products/perplexity/reviews?page=4)
- Perplexity on Capterra: about 4.2-4.3 from about 35 reviews, with support complaints. — [Capterra](https://www.capterra.com/p/10014721/Perplexity/reviews/)
- Manus on Trustpilot: reports of 88% one-star out of 210+ reviews (via Zemith, a competitor) and an AI-generated Trustpilot summary saying most reviewers were let down. Trustpilot pages show roughly 89 to 145 reviews depending on the regional page. G2 about 4.3 from 55+ reviews. — [Trustpilot Manus](https://www.trustpilot.com/review/manus.im?page=1); [Zemith Manus](https://www.zemith.com/en/learn/manus-review)
- Manus complaint themes: repeated automated refund replies; "$2,380 in credits deleted without warning" (a 1-star review); an App Store reviewer saying "One prompt to build a website used over 6000 credits"; a user reporting a 5% refund on 130k credits after failed fixes. — [Trustpilot](https://se.trustpilot.com/review/manus.im); [Preuve (competitor, discloses)](https://preuve.ai/blog/manus-ai-review); [botcrawl](https://botcrawl.com/manus-ai-refund-problem/) (unverified first-person accounts)
- Manus official refund policy: an AI review process; a refund is processed automatically if a bug is confirmed. — [Manus help center](https://help.manus.im/en/articles/12992237-how-does-our-ai-agent-s-credit-refund-policy-work)
- Genspark on Trustpilot: TrustScore 2.9 from 226 reviews on one regional page, and 3.5 from 310 on another. Complaints: credits burn fast ("$25 subscription used up in less than two hours"), credits charged for failed tasks, about 1,000 credits for one video, a billing after cancellation report (2026), poor support. Some reviewers praise refunds and extras. The company replied to about 3% of negative reviews. Fake-review accusations exist. — [Trustpilot Genspark](https://www.trustpilot.com/review/genspark.ai?page=9)
- Gemini Deep Research community complaints (older, consumer tier): forum users complain it explores only about 10 sources and sometimes pulls from a Reddit thread. — [DEV: What users say about Gemini Deep Research](https://dev.to/aigurux/what-users-say-about-gemini-deep-research-3io7); [Nesyona](https://nesyona.com/articles/perplexity-vs-claude-vs-chatgpt-deep-research-2026)
- Kimi pricing note: Deep Research costs about 5-10% of monthly credits on the Moderato plan (about $19/month per an aggregator). — [Kimi help](https://www.kimi.com/en/help/deep-research/deep-research-overview)
- Industry piece (KrASIA, 2025/26): traffic for both Manus and Genspark has declined since launch, suggesting neither has stable product-market fit. Search summary only, date unclear. — [KrASIA](https://kr-asia.com/chinese-ai-agents-made-a-splash-in-2025-but-can-they-go-the-distance)

### Inferences
- Consistent praise: speed and citations (Perplexity), structure and depth (ChatGPT), narrative synthesis (Claude), integration (Gemini). Consistent complaints: opaque credit and quota accounting, refunds for failed runs, thin support, and a need to verify claims.
- G2 vs Trustpilot divergence likely reflects selection effects (G2 invites reviews from verified business users; Trustpilot attracts disputes).

### Gaps
- No Reddit, Hacker News or X content retrieved. No App Store or Product Hunt scores for the main products (only a Manus App Store quote, second-hand).
- No G2/Trustpilot data for OpenAI Deep Research, Claude Research or Grok DeepSearch as distinct products.

## 3. Documented failures: hallucinated citations, audits, lawsuits, refunds, rate limits, controversies

### Takeaway
There is solid academic and journalistic evidence that AI search and deep research tools produce unsupported statements and fabricated or misattributed citations at meaningful rates. Perplexity is both the best performer in the Tow Center audit and the most sued. Manus has refund and credit complaints and a major regulatory controversy over its Meta sale.

### Cited Findings
- Tow Center / CJR (March 2025): 1,600 queries (20 publishers x 10 articles x 8 chatbots); more than 60% answered incorrectly overall. Perplexity lowest error at 37%, Grok-3 Search highest at 94%. Premium tiers gave more confidently wrong answers than free tiers. Tools fabricated links and cited syndicated copies, and licensing deals did not guarantee accurate citation. The test was identifying articles from excerpts, so it measures news-source attribution, not full deep research. — [CJR](https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php); [Nieman Lab](https://www.niemanlab.org/2025/03/ai-search-engines-fail-to-produce-accurate-citations-in-over-60-of-tests/); [Fortune](https://fortune.com/2025/03/18/ai-search-engines-confidently-wrong-citing-sources-columbia-study/); [eWeek, 13 Mar 2025](https://www.eweek.com/news/ai-chatbot-citation-problem/)
- OpenAI called the Tow study an "atypical test of our product" (as reported by search summary). — [Digital Trends](https://digitaltrends.com/computing/chatgpt-search-struggles-with-accuracy-research-shows)
- DeepTRACE (Microsoft Research and Salesforce authors; arXiv Sept 2025; ICLR 2026 poster): citation accuracy 40-80% across systems. Unsupported-statement rates: PPLX Deep Research 97.5%, YouChat Deep Research 74.6%. An alphaXiv third-party listing shows GPT-5 deep research at 12.5% unsupported (unverified against the paper). Lead author: "More sources and longer answers do not translate into reliability." Deep research modes reduced overconfidence but stayed one-sided on debate queries. — [arXiv 2509.04499](https://arxiv.org/abs/2509.04499); [Microsoft Research](https://microsoft.com/en-us/research/publication/deeptrace-auditing-deep-research-ai-systems-for-tracking-reliability-across-citations-and-evidence); [alphaXiv](https://www.alphaxiv.org/benchmarks/microsoft/deeptrace)
- arXiv 2604.03173 (April 2026): hallucinated URL rates 3-13% (5-18% non-resolving) across commercial LLMs and deep research agents. Deep research agents had the highest hallucination rates despite more citations. — [arXiv 2604.03173](https://arxiv.org/abs/2604.03173)
- arXiv 2605.06635 (May 2026): benchmarked 14 LLMs on citation quality. Strongest models keep link validity above 94% and relevance above 80%, but factual accuracy of cited content is 39-77%. A secondary summary attributes 39-59% to OpenAI, 45-49% to Gemini and the best scores to Claude. I did not verify that per-vendor split. — [arXiv 2605.06635](https://arxiv.org/html/2605.06635)
- EBU/BBC multi-assistant study: about 3,000+ responses in 14 languages, about 20% with major factual inaccuracies (per Tom's Guide coverage, which reports 45% with at least one significant issue in the headline). — [Tom's Guide](https://www.tomsguide.com/ai/45-percent-of-ai-generated-news-is-wrong-new-study-warns-heres-what-happened-when-i-tested-it-myself)
- Deakin University study (older, ChatGPT of 2023-24, not deep research): about 56% of ChatGPT citations in literature reviews fabricated or erroneous. — [Tech.co](https://tech.co/?p=364401)
- OpenAI community forum posts report hallucinated URLs, fake article titles and fabricated expert quotes (mostly web-mode, not Deep Research). Anecdotal. — [OpenAI Community](https://community.openai.com/t/critical-false-citation-of-nonexistent-article-fabricated-expert-quote-hallucinations/1252568)
- Perplexity litigation: Dow Jones/NY Post (S.D.N.Y. 1:24-cv-07984, 2024); NYT (filed Dec 2025, 1:25-cv-10106, includes Lanham Act claims over hallucinated content attributed to the paper); also Britannica/Merriam-Webster, Nikkei, Asahi, Reddit. Bloomberg Law (9 Feb 2026) described the cases as pending, and I found no ruling. — [TechCrunch on NYT suit](https://techcrunch.com/2025/12/05/the-new-york-times-is-suing-perplexity-for-copyright-infringement); [Bloomberg Law](https://news.bloomberglaw.com/ip-law/news-outlets-perplexity-ai-suits-strike-at-existential-threat)
- Manus controversy: Meta agreed to buy Manus (Butterfly Effect) on 29 Dec 2025 for reportedly over $2B; Chinese regulators opened a review in Jan 2026; on 27 Apr 2026 China ordered the deal unwound. Unconfirmed claim in a Binance Square post that founders were barred from leaving China, not corroborated. — [TechCrunch](https://techcrunch.com/2025/12/29/meta-just-bought-manus-an-ai-startup-everyone-has-been-talking-about); [SiliconANGLE](https://siliconangle.com/2026/04/27/china-blocks-metas-acquisition-ai-agent-developer-manus/); [TechNode](https://technode.com/2026/04/27/manus-related-foreign-investment-deal-ordered-unwound-in-china/); [Caixin](https://www.caixinglobal.com/2026-01-23/in-depth-chinese-startup-manus-swept-up-in-global-ma-frenzy-for-ai-102407173.html). I did not confirm what happened after April 2026.
- A botcrawl post describes Manus deleting website files and breaking WordPress media, a first-person unverified account. A "manusexpose" site compiles allegations and is an advocacy source. — [botcrawl](https://botcrawl.com/?p=171692)

### Inferences
- Tow Center results (Perplexity best, Grok worst) conflict with DeepTRACE (Perplexity Deep Research 97.5% unsupported). The tests measure different things (news-article identification vs claim-level support) and ran different Perplexity modes, so neither is a verdict on "Perplexity Deep Research" quality overall.
- A working link is not evidence the page supports the claim (2605.06635), so link-click verification is not enough.

### Gaps
- No lawsuit against OpenAI, Google, Anthropic, xAI, Manus or Genspark that is specifically about deep research outputs surfaced (NYT v. OpenAI is a general copyright case and was not researched here).
- No refund complaint data for OpenAI, Claude or Gemini deep research found.
- Could not open the CJR or arXiv pages to confirm figures.

## 4. Head-to-head comparison tests by independent people

### Takeaway
Many head-to-heads exist, but most are blogs with weak methodology, affiliate links or competitor interests. They disagree, so no stable ranking emerges. Perplexity wins on speed and cost, OpenAI on structure and length, Claude on writing and synthesis.

### Cited Findings
- Tom's Guide, "I just tested AI deep research on Grok-3 vs Perplexity vs Gemini" (early 2025). Winner not visible in the snippet I obtained. — [Tom's Guide](https://www.tomsguide.com/ai/i-just-tested-ai-deep-research-on-grok-3-vs-perplexity-vs-gemini-heres-the-winner)
- Tom's Guide, "I just tested ChatGPT vs Perplexity for research and there's a very clear winner". The title implies a winner but I did not see which. — [Tom's Guide](https://www.tomsguide.com/ai/i-tested-chatgpt-vs-perplexity-for-research-and-this-is-the-one-i-recommend)
- AIMultiple (research firm; one benchmark of coding-agent research, "DR-20"): Claude Code 0.775 requirements met versus Gemini CLI 0.565; Codex CLI 0.79 but about 42 minutes per task. Author has an Exa-related relationship per the search summary. — [AIMultiple](https://aimultiple.com/ai-deep-research)
- DRACO benchmark figure cited by a blog: Perplexity 70.5% vs Gemini 59.0%. Secondary and unverified. — [via Nesyona](https://nesyona.com/articles/best-ai-for-research)
- A site composite scorecard ranks Perplexity 77, ChatGPT 73, Gemini 72.5, Claude 67. It is the site's own invented index, so weak evidence. — [Superkind](https://superkind.ai/blog/ai-deep-research-tools)
- Others that exist but I could not open: [Presenc.ai](https://presenc.ai/research/deep-research-mode-comparison-2026), [Learn Prompting newsletter](https://newsletter.learnprompting.org/p/deep-research-chatgpt-vs-gemini-who-wins), [TWiT/Hands-On AI](https://twit.tv/posts/tech/chatgpt-vs-gemini-vs-claude-vs-perplexity-which-ai-does-deep-research-best-2026) (concludes deep research tools are "not a silver bullet"), [Position Is Everything](https://www.positioniseverything.net/i-tested-chatgpts-deep-research-against-gemini-perplexity-and-grok-ai-to-see-which-is-best/).
- Manus vs Genspark: see Section 1 (Techpoint, N=1).
- Open benchmark: Deep Research Bench II, see Section 1.

### Inferences
- Rankings flip by test design, so the report should present results as task-dependent and avoid one number.

### Gaps
- Dates, prompts and sample sizes are unknown for most head-to-heads. Several pages cite model versions I cannot verify.

## 5. Consensus "best for X" picks

### Takeaway
Blogs converge on a loose division of labour, but these are opinion pieces with commercial incentives, not measured results.

### Cited Findings
- Fast cited answers and shopping/quick fact lookups: Perplexity. Long structured reports, tables, executive summaries: ChatGPT. Nuanced synthesis, contradictory sources, analysis of documents you supply: Claude. Google Workspace users and academic/Google Scholar sources: Gemini. Common workflow advice: Perplexity to find sources, then Claude or ChatGPT to synthesise. — [Presenc/Superkind/Nesyona/ClickUp roundups via search summaries](https://superkind.ai/blog/ai-deep-research-tools); [ClickUp](https://clickup.com/blog/deep-research-tools/); [Nesyona](https://nesyona.com/articles/perplexity-vs-claude-vs-chatgpt-deep-research-2026)
- Coding research: the only measured item is the AIMultiple DR-20 result in Section 4 (Claude Code and Codex CLI ahead of Gemini CLI), with the vendor-relationship caveat.
- Open-source self-hosting: GPT-Researcher (MIT) and Tongyi DeepResearch (open weights) are the commonly named options, with no independent quality evidence found.

### Inferences
- "Best for" picks for news, due diligence, market research and academic use are not supported by independent evidence I found. Given the audit results, anything for due diligence or journalism needs manual source checking.

### Gaps
- Nothing found specific to due diligence or market research quality. Academic-use evidence is limited to the citation audits above.

## 6. Agent Reach reception

### Takeaway
Agent Reach (Panniantong/Agent-Reach) is a popular MIT-licensed CLI giving agents read-only access to platforms like Twitter/X, Reddit, YouTube, GitHub and Bilibili. Reception appears positive in how-to and review blogs, but I found no critical or independent evaluation, and metrics conflict.

### Cited Findings
- GitHub README (fetched): the tool is read-only; Bilibili, V2EX, GitHub, YouTube and web search/reading work by default; Reddit, LinkedIn and others need login or setup; Twitter/X, Facebook and Instagram are labelled experimental and "may stop working at any time". It recommends a secondary account. The fetch showed about 114k stars, about 10.3k forks, 66 open issues, 94 open PRs, 535 commits. The README warns that the PyPI package named agent-reach is not this project. — [GitHub](https://github.com/Panniantong/Agent-Reach)
- Other pages cite conflicting star counts (about 22.8k vs about 52.9k vs the 114k above), so star figures should be treated as time-dependent and unverified. — [DEV review](https://dev.to/andrew-ooo/agent-reach-review-free-internet-access-for-ai-agents-1nem); [SitePoint](https://www.sitepoint.com/agent-reach-giving-your-ai-eyes-on-the-web/); [Apidog](https://apidog.com/blog/agent-reach-internet-access/); [Linux Today how-to](https://www.linuxtoday.com/blog/how-to-let-claude-code-read-reddit-youtube-and-x-with-agent-reach/)
- Caveats raised in review snippets: platform terms of service may still prohibit automated access; scripted logins risk bans. — [DEV "pragmatic review"](https://dev.to/alya_mahalini_f05d9953cfa/agent-reach-a-pragmatic-review-of-internet-access-for-ai-agents-58kn)
- It has a Product Hunt listing (content not retrievable). — [Product Hunt](https://www.producthunt.com/products/agent-reach)

### Inferences
- Coverage is mostly promotional or how-to content, so sentiment is skewed positive. The experimental status of Twitter/X and the cookie-based access are the practical risks.

### Gaps
- No Hacker News or Reddit reaction, Product Hunt ratings, security audit or independent reliability test found.
- Star count and date of last commit not verified.
