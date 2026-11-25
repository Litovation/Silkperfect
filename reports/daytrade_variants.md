# Day-trade rule: every variant

48 variants of the opening-range breakout: buying or shorting, a 15- or 30-minute range,
the stop at the middle or far edge of the range, targets of 1, 2 or 3 times the risk, with
and without a volume filter. Same 200 shares, same costs.

The days are split at 28 Sep 2026. The first half is where a pattern is looked for;
the second half is the check. Trying this many variants guarantees a few look good by luck,
so only a variant that works in both halves counts.

- Variants that made money after costs in both halves: **0 of 48**
- Variants with a reliable edge before costs in both halves: **0 of 48**
- Variants that made money after costs over all days: **0 of 48**
- Best result after costs over all days: -0.123 R a trade

## The five that looked best in the first half, and what they did next

| Variant | Trades | First half, after costs (R) | Second half, after costs (R) | Before costs, all days (R) |
| --- | ---: | ---: | ---: | ---: |
| Short, 30-min range, stop at far edge, target 3R | 6,460 | -0.210 | -0.022 | +0.101 |
| Short, 30-min range, stop at far edge, target 3R, volume 1.5x | 4,319 | -0.214 | -0.036 | +0.081 |
| Short, 30-min range, stop at far edge, target 1R, volume 1.5x | 4,319 | -0.215 | -0.060 | +0.069 |
| Short, 30-min range, stop at far edge, target 2R | 6,460 | -0.216 | -0.018 | +0.099 |
| Short, 30-min range, stop at far edge, target 2R, volume 1.5x | 4,319 | -0.216 | -0.036 | +0.080 |

## All variants

| Variant | Trades | Before costs (R) | After costs (R) | Strength after costs (t) |
| --- | ---: | ---: | ---: | ---: |
| Short, 30-min range, stop at far edge, target 3R | 6,460 | +0.101 | -0.123 | -4.53 |
| Short, 30-min range, stop at far edge, target 2R | 6,460 | +0.099 | -0.124 | -4.63 |
| Short, 30-min range, stop at far edge, target 3R, volume 1.5x | 4,319 | +0.081 | -0.128 | -5.58 |
| Short, 30-min range, stop at far edge, target 2R, volume 1.5x | 4,319 | +0.080 | -0.129 | -5.67 |
| Short, 30-min range, stop at far edge, target 1R, volume 1.5x | 4,319 | +0.069 | -0.140 | -6.55 |
| Short, 30-min range, stop at far edge, target 1R | 6,460 | +0.082 | -0.141 | -5.68 |
| Short, 15-min range, stop at far edge, target 3R | 7,169 | +0.099 | -0.151 | -4.43 |
| Short, 15-min range, stop at far edge, target 3R, volume 1.5x | 4,919 | +0.083 | -0.151 | -5.45 |
| Short, 15-min range, stop at far edge, target 2R, volume 1.5x | 4,919 | +0.081 | -0.153 | -5.63 |
| Short, 15-min range, stop at far edge, target 2R | 7,169 | +0.093 | -0.156 | -4.67 |
| Buy, 30-min range, stop at far edge, target 3R, volume 1.5x | 4,473 | +0.026 | -0.176 | -6.39 |
| Short, 15-min range, stop at far edge, target 1R, volume 1.5x | 4,919 | +0.054 | -0.180 | -7.05 |
| Buy, 30-min range, stop at far edge, target 3R | 5,865 | +0.032 | -0.182 | -6.28 |
| Buy, 15-min range, stop at far edge, target 3R, volume 1.5x | 5,021 | +0.041 | -0.186 | -6.19 |
| Buy, 30-min range, stop at far edge, target 2R, volume 1.5x | 4,473 | +0.016 | -0.186 | -6.90 |
| Short, 15-min range, stop at far edge, target 1R | 7,169 | +0.061 | -0.188 | -6.31 |
| Buy, 30-min range, stop at far edge, target 2R | 5,865 | +0.025 | -0.189 | -6.73 |
| Buy, 15-min range, stop at far edge, target 2R, volume 1.5x | 5,021 | +0.034 | -0.193 | -6.69 |
| Buy, 30-min range, stop at far edge, target 1R, volume 1.5x | 4,473 | +0.000 | -0.201 | -8.37 |
| Buy, 15-min range, stop at far edge, target 3R | 6,529 | +0.039 | -0.203 | -6.12 |
| Buy, 30-min range, stop at far edge, target 1R | 5,865 | +0.010 | -0.204 | -8.12 |
| Buy, 15-min range, stop at far edge, target 2R | 6,529 | +0.035 | -0.208 | -6.54 |
| Buy, 15-min range, stop at far edge, target 1R, volume 1.5x | 5,021 | +0.013 | -0.213 | -8.47 |
| Buy, 15-min range, stop at far edge, target 1R | 6,529 | +0.016 | -0.226 | -8.09 |
| Short, 30-min range, stop at middle, target 3R, volume 1.5x | 4,319 | +0.127 | -0.231 | -6.64 |
| Short, 30-min range, stop at middle, target 2R, volume 1.5x | 4,319 | +0.116 | -0.242 | -7.29 |
| Short, 30-min range, stop at middle, target 3R | 6,460 | +0.168 | -0.243 | -5.48 |
| Short, 30-min range, stop at middle, target 2R | 6,460 | +0.143 | -0.269 | -6.50 |
| Short, 15-min range, stop at middle, target 3R, volume 1.5x | 4,919 | +0.124 | -0.271 | -6.68 |
| Short, 30-min range, stop at middle, target 1R, volume 1.5x | 4,319 | +0.075 | -0.283 | -9.82 |
| Short, 15-min range, stop at middle, target 3R | 7,169 | +0.155 | -0.297 | -5.66 |
| Short, 15-min range, stop at middle, target 2R, volume 1.5x | 4,919 | +0.096 | -0.299 | -7.69 |
| Buy, 30-min range, stop at middle, target 3R, volume 1.5x | 4,473 | +0.029 | -0.316 | -8.69 |
| Short, 30-min range, stop at middle, target 1R | 6,460 | +0.080 | -0.331 | -10.09 |
| Buy, 30-min range, stop at middle, target 2R, volume 1.5x | 4,473 | +0.013 | -0.331 | -9.53 |
| Short, 15-min range, stop at middle, target 2R | 7,169 | +0.116 | -0.336 | -7.03 |
| Short, 15-min range, stop at middle, target 1R, volume 1.5x | 4,919 | +0.053 | -0.343 | -10.64 |
| Buy, 15-min range, stop at middle, target 3R, volume 1.5x | 5,021 | +0.038 | -0.344 | -9.32 |
| Buy, 30-min range, stop at middle, target 1R, volume 1.5x | 4,473 | -0.011 | -0.355 | -12.79 |
| Buy, 30-min range, stop at middle, target 3R | 5,865 | +0.029 | -0.358 | -9.39 |
| Buy, 15-min range, stop at middle, target 2R, volume 1.5x | 5,021 | +0.022 | -0.360 | -10.49 |
| Buy, 30-min range, stop at middle, target 2R | 5,865 | +0.021 | -0.367 | -10.37 |
| Buy, 15-min range, stop at middle, target 1R, volume 1.5x | 5,021 | -0.004 | -0.386 | -13.73 |
| Buy, 15-min range, stop at middle, target 3R | 6,529 | +0.046 | -0.386 | -9.28 |
| Buy, 30-min range, stop at middle, target 1R | 5,865 | -0.008 | -0.395 | -14.24 |
| Buy, 15-min range, stop at middle, target 2R | 6,529 | +0.031 | -0.401 | -10.48 |
| Short, 15-min range, stop at middle, target 1R | 7,169 | +0.044 | -0.408 | -11.51 |
| Buy, 15-min range, stop at middle, target 1R | 6,529 | -0.001 | -0.433 | -13.89 |
