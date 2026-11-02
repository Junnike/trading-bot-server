# T18p — Polymarket BTC 15m: CRSI / head-start signals at minute 1 (TWAP era, n markets 4707, 2026-08..2026-09; data/poly/markets_first3.jsonl)

Minute-1 activity: median prints 50, median shares 937. Base P(Up) 50.0%; minute-1 mid (from last ask/bid prints) 0.499.

| signal | n | hit % | mid1 | fill px (first Up-taker print after 62 s) | EV c (fee incl.) | z | months > 0 | fill after 65 s EV | fill after 75 s EV | median print size |
|---|---|---|---|---|---|---|---|---|---|---|
| CRSI<=20 | 788 | 53.2 | 0.523 | 0.522 | -0.66 | -0.4 | 0/2 | -0.37 | -0.06 | 8 |
| CRSI<=20 & hs>0 | 331 | 54.1 | 0.557 | 0.557 | -3.25 | -1.1 | 0/2 | -2.95 | -2.63 | 8 |
| CRSI<=20 & hs>+1 | 171 | 56.7 | 0.570 | 0.570 | -1.90 | -0.5 | 1/2 | -1.81 | -1.55 | 7 |
| CRSI<=20 & hs>+3 | 61 | 57.4 | 0.600 | 0.597 | -3.94 | -0.6 | 0/2 | -3.86 | -3.42 | 10 |
| hs>+3 only | 348 | 58.6 | 0.574 | 0.575 | -0.47 | -0.2 | 1/2 | -0.56 | -0.13 | 8 |
| all windows (buy Up) | 4649 | 50.1 | 0.499 | 0.500 | -1.57 | -2.3 | 0/2 | -1.52 | -1.44 | 8 |

CRSI<=20 & hs>0 by month (EV c / n): 26-08:-4.3/129 26-09:-2.5/202

Note: Polymarket's minute-1 'mid' is reconstructed from the last aggressor prints on each side before 62 s, not from a book snapshot.
