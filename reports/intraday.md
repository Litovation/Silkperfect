# Day-trading strategies on NSE 5-minute bars

- Period: 17 Aug 2026 to 11 Nov 2026 (Yahoo's 5-minute history goes back about 60 trading days)
- Shares: the 200 most traded NSE shares
- Trades fill at the close of a 5-minute bar; nothing new after 15:00; everything closed at 15:20
- Costs: intraday brokerage, taxes and 5 basis points of slippage per side, about 0.25% for a round trip on Rs 10,000
- Settings are each method's textbook defaults; none was tuned on this data

**Strategies that made money after costs: 0 of 15.**
**Strategies with a reliable edge before costs (strength 2 or more, positive in both halves): 1 of 15.**

| Strategy | Trades | Wins (%) | Avg before costs (%) | Avg after costs (%) | Strength before costs (t) | First half, before costs (%) | Second half, before costs (%) | Days in profit after costs (%) | Held (min) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gap fade (bet a 1% gap closes) | 1,682 | 41 | +0.102 | -0.152 | +0.56 | +0.073 | +0.120 | 31 | 131 |
| Morning laggards, short | 1,175 | 52 | +0.084 | -0.169 | +0.80 | +0.087 | +0.081 | 39 | 305 |
| Opening-range breakout, short | 7,027 | 53 | +0.042 | -0.211 | -0.54 | +0.000 | +0.090 | 10 | 120 |
| Previous-day high/low breakout | 9,031 | 27 | +0.036 | -0.217 | +0.65 | -0.032 | +0.102 | 15 | 138 |
| Moving-average crossover (9/21) | 34,035 | 34 | +0.031 | -0.222 | +2.35 | +0.021 | +0.041 | 7 | 88 |
| Opening-range breakout, buy | 6,441 | 49 | +0.027 | -0.226 | -0.85 | +0.004 | +0.048 | 10 | 117 |
| VWAP trend (with price vs VWAP) | 71,300 | 21 | +0.010 | -0.243 | +1.67 | +0.007 | +0.013 | 3 | 54 |
| Supertrend (10, 3) | 27,142 | 42 | +0.003 | -0.251 | +0.58 | +0.003 | +0.003 | 5 | 136 |
| Morning leaders, buy | 1,175 | 48 | -0.001 | -0.255 | -0.02 | -0.014 | +0.011 | 37 | 305 |
| First half-hour momentum | 11,707 | 49 | -0.010 | -0.263 | -0.76 | -0.026 | +0.006 | 2 | 30 |
| Bollinger reversion (20, 2) | 21,448 | 62 | -0.023 | -0.276 | -1.44 | -0.013 | -0.032 | 3 | 66 |
| VWAP reversion (fade 2 sd) | 16,662 | 62 | -0.056 | -0.309 | -2.23 | -0.052 | -0.060 | 3 | 123 |
| Gap and go (follow a 1% gap) | 1,682 | 32 | -0.059 | -0.312 | -0.43 | -0.065 | -0.056 | 27 | 197 |
| RSI reversion (30/70) | 10,084 | 57 | -0.072 | -0.326 | -2.22 | -0.044 | -0.100 | 2 | 112 |
| ML classifier (LightGBM) | 3,256 | 45 | -0.083 | -0.336 | -1.85 | n/a | -0.083 | 4 | 30 |

Percentages are of the money in one trade. Strength counts each day once; 2 or more means
the result is unlikely to be luck. With this many strategies, one or two will clear that bar
by chance, which is why both halves of the period must agree.

The ML classifier was trained on days before 07 Oct 2026 (378,000 examples) and traded only on the 23 days from 08 Oct 2026, so its row covers a shorter period than the others.

## Not tested, and why

- **Options strategies** (straddles, strangles, spreads, premium decay): there is no free history of option prices, and they cannot be judged without it.
- **Reinforcement learning:** sixty days of data is far too little; an agent would memorise it.
- **Index arbitrage and pairs trading:** need futures prices and speed that a home setup lacks.
