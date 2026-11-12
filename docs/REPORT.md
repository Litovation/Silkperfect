# Silkperfect: what was tested, what was found, what to do

Written 12 Nov 2026 in plain language. All numbers come from this project's
own tests on real NSE prices unless a source is named. Past results do not
promise future returns, and this is not financial advice.

## The short answer

- **Day trading:** not profitable with an ordinary account. 64 versions tested, all lost after costs.
- **AI prediction models:** none worked. Four tested, all did worse than simply holding every share.
- **Chinese rule-based methods:** none beat holding.
- **Momentum, held for months:** the only method that came out ahead, and the only one worth continuing with. It is not proven, and it has long flat or losing stretches.
- **The reliable way to be profitable** is the dull one: own the market through a low-cost fund for years. Momentum is a possible addition on top, not a replacement.

## What we set out to do

The starting idea was that an AI model (Google's TimesFM) could forecast
share prices well enough to trade on. The plan was to test that honestly
before risking money: against simple baselines, with real Indian trading
costs, then with pretend money, and only then with real money.

## What was built

| Piece | What it does |
| --- | --- |
| Data | Every NSE share's daily prices from 2019, free from NSE, adjusted for splits, bonuses and dividends, checked against NSE's official files with zero differences |
| Costs | Real Indian charges: brokerage, taxes, exchange fees, stamp duty, plus a small allowance for bad fills |
| Test bench | Each method only ever sees past prices; automatic checks prove the future cannot leak in |
| Dashboard | Plain-language page, pretend account, and pages for each test |
| Daily job | One command updates prices and the pretend account |

78 automatic checks pass. Everything is in the repository.

## Everything that was tested

### 1. Forecasting one share's price

*Question: can a model predict where a share will be in a week?*

| Method | Better than assuming "no change"? |
| --- | --- |
| TimesFM (Google AI model) | No. Worse in every year 2021 to 2026, on all 11 shares |
| Simple trend and average methods | No |

Trading on TimesFM's forecasts lost 1.2% a year against 12.9% for just
holding the shares.

### 2. Picking the best shares each month

*Question: from the 200 most traded shares, can a method pick 20 that beat
holding all 200? Rs 1 crore, 10 Feb 2021 to 9 Nov 2026, after costs.*

| Method | Per year | Verdict |
| --- | ---: | --- |
| Momentum, NSE index style | 26.6% | Ahead |
| Momentum, past-year return | 25.8% | Ahead |
| **Hold all 200 shares** | **16.1%** | **The bar to beat** |
| Chronos (Amazon AI) | 15.4% | Behind |
| Qlib recipe (Microsoft, Beijing lab) | 13.3% | Behind |
| TimesFM (Google AI) | 13.0% | Behind |
| Kronos (Tsinghua University AI) | 12.8% | Behind |
| Steadiest shares | 10.4% | Behind |
| Last month's biggest fallers | 7.7% | Behind |

### 3. Trading more often

| Swap shares | Hold all 200 | Momentum | Momentum's costs |
| --- | ---: | ---: | ---: |
| Monthly | 16.1% | 25.8% | Rs 18.7 lakh |
| Weekly | 14.3% | 24.8% | Rs 39.0 lakh |
| Daily | 8.5% | 20.2% | Rs 86.5 lakh |

More trading gave lower returns and deeper falls, every time.

### 4. Day trading

*Bought and sold the same day, on 5-minute prices for 200 shares, about 60 trading days.*

- **The day-trader skill's breakout rule, 48 versions:** none made money. It hit its target 42.5% of the time and its stop 42.3%, a coin toss, and then paid costs.
- **Fifteen other common methods** (gap trades, VWAP, RSI, Bollinger, Supertrend, moving-average crossover, morning leaders, a machine-learning classifier): none made money.
- **Why:** the best method gained 0.10% per trade before costs. A trade costs about 0.25%.

### 5. Chinese rule-based methods

*Each rule decides when to hold a share and when to sit in cash.*

| Rule | Per year | Worst fall |
| --- | ---: | ---: |
| Hold the same shares | 15.7% | -21.4% |
| Chan theory, third-class points (czsc) | 11.7% | -13.8% |
| RSRS timing | 5.7% | -11.4% |
| Chan theory, all points | 4.4% | -13.7% |
| Turtle breakout | 3.9% | -12.6% |

All earned less than holding. They fell less only because they sat in cash about half the time.

### 6. Small money: Rs 10,000

| Plan | Rs 10,000 became | Fees paid |
| --- | ---: | ---: |
| Momentum, 5 shares, swapped monthly | Rs 5,885 | Rs 12,400 |
| Momentum, 5 shares, swapped every 3 months | Rs 28,656 | Rs 6,875 |
| Momentum, 3 shares, swapped every 3 months | Rs 17,591 | Rs 4,525 |
| One Nifty 50 fund, bought once | Rs 17,514 | about Rs 30 |

Results swing wildly because every order costs Rs 20 to Rs 45 however small.
At this size fees and luck decide the outcome, not the method.

## What I concluded

1. **Predicting prices from past prices does not work for an ordinary person.** Every AI model failed, including ones built for share prices. Anything predictable in public price data is traded away by professional firms first.
2. **Costs are the real opponent.** Every method that traded often lost, and the more often it traded, the more it lost.
3. **The professionals win a different game.** Trading firms in India earned about Rs 61,000 crore in a year, mostly in index options, by being the shopkeeper everyone trades with and by being fastest. About 91% of individuals in that market lost money (SEBI, 2024-25). Their methods need computers inside the exchange and costs near zero.
4. **One simple old rule held up: momentum.** Shares that have risen most over the past year tended to keep doing better for the next few months.

## Momentum: the honest picture

**In its favour**
- Ahead of holding everything in all ten combinations of settings tested, by 7 to 11 points a year.
- Still ahead when measured NSE's own way, which I did not design.
- It trades rarely, so costs stay small.
- It is a well-known effect, studied for decades in many countries.

**Against it**
- Its lead came from three strong years. Year by year, NSE-style momentum against holding all 200:

| Year | Hold all 200 | Momentum (NSE style) |
| --- | ---: | ---: |
| 2021 (from Feb) | +30.5% | +86.9% |
| 2022 | -0.5% | +8.7% |
| 2023 | +44.8% | +67.5% |
| 2024 | +20.8% | +32.6% |
| 2025 | +4.9% | -12.3% |
| 2026 (to Nov) | -1.1% | -2.2% |

- It has done worse than holding everything for the last two years.
- Its statistical strength is 1.5 to 1.8, under the usual pass mark of 2, so luck is not ruled out.
- Its worst falls were 26% to 41%, deeper than the market's 24%.
- It is one period of under six years.

## If you continue for months: what to expect

From the test, how momentum did over every possible stretch of a given length:

| If you held for | Chance it made money | Typical result | Worst stretch | Chance it beat holding all 200 |
| --- | ---: | ---: | ---: | ---: |
| 3 months | 67% | +4.7% | -26% | 64% |
| 6 months | 71% | +6.0% | -28% | 66% |
| 12 months | 74% | +11.6% | -23% | 69% |
| 24 months | 81% | +62% | -21% | 68% |

Read this carefully:

- **A few months proves nothing.** One time in three, a three-month stretch lost money, and one time in three momentum trailed plain holding.
- **Patience is the method.** The chance of a gain rises with time, but even two years was a loss about one time in five.
- **These are past numbers from a mostly rising market.** The next six years can be worse.

So "can it be profitable if we continue for months?" Likely over years, uncertain
over months, and never guaranteed.

## How to be profitable: my recommendation in order

1. **Base: a low-cost index fund, held for years.** This is the only approach here that needs no method to keep working. It earned 9% to 16% a year in the test period depending on which index.
2. **Addition: a momentum index fund or ETF, for a part of the money.** It follows the one idea that held up, in a single purchase with tiny fees. Expect it to trail the market for a year or two at a time.
3. **Check it yourself: run the pretend account for six months or more.** It is built and costs nothing.
4. **Picking momentum shares yourself:** only with about Rs 1 lakh or more, swapping every three to six months. Below that, fees decide the result.
5. **Do not day trade, do not buy options, do not pay for trading robots.** The tests and SEBI's own numbers agree.

## Other methods that could be tested next

| Idea | Why it might help | What it needs |
| --- | --- | --- |
| Momentum only while the market is in an uptrend | Could cut the deep falls and the bad years | Nothing new; testable now |
| Momentum mixed with low volatility or quality | Smoother ride | Quality needs company accounts data |
| Value and quality (cheap, profitable companies) | The other well-studied long-term effects | Company accounts data |
| Chinese price-only momentum variants (trend slope) | Flagged by the research as worth a look | Nothing new; testable now |
| A longer history, back to 2010 | Would show how momentum did in bad decades | More NSE downloads |
| Options strategies | Where most Indian trading happens | Paid option price history |

Of these, the first and the fifth are the most useful: one could fix
momentum's main weakness, the other would show whether its lead is real.

## What was not done, and limits

- Real-money trading through Upstox and OpenAlgo was never connected. It is only needed for automatic orders.
- Day trading was tested on about 60 days, all that free 5-minute data offers.
- Options strategies and reinforcement learning were not tested.
- Three rights issues in the first test's shares are not adjusted, and two demergers are estimated.
- Brokerage and depository charges are my defaults, not confirmed against an Upstox contract note.
- Qlib's and Kronos's settings were used as published, not re-tuned for India.

## Where to find things

| File | Contents |
| --- | --- |
| `docs/PLAN.md` | Running notes and every result table |
| `docs/WHO_MAKES_MONEY.md` | How professional firms profit in India |
| `reports/ranking.md` | Share-picking test, all methods |
| `reports/intraday.md` | Fifteen day-trading methods |
| `reports/daytrade_variants.md` | 48 versions of the breakout rule |
| `reports/chinese_methods.md` | Chan theory, RSRS, turtle, reversal |
| `reports/NSE speed trading and czsc.md` | Research on Chinese tools |
