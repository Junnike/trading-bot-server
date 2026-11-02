# T18p — Polymarket BTC 15m: CRSI / head-start signals at minute 1 (TWAP era, n markets 7813, 2026-08..2026-11; data/poly/markets_first3.jsonl)

Minute-1 activity: median prints 42, median shares 877. Base P(Up) 49.7%; minute-1 mid (from last ask/bid prints) 0.498.

| signal | n | hit % | mid1 | fill px (first Up-taker print after 62 s) | EV c (fee incl.) | z | months > 0 | fill after 65 s EV | fill after 75 s EV | median print size |
|---|---|---|---|---|---|---|---|---|---|---|
| CRSI<=20 | 1344 | 51.6 | 0.518 | 0.518 | -1.80 | -1.3 | 0/4 | -1.60 | -1.39 | 8 |
| CRSI<=20 & hs>0 | 571 | 53.6 | 0.557 | 0.557 | -3.71 | -1.6 | 1/4 | -3.53 | -3.40 | 6 |
| CRSI<=20 & hs>+1 | 280 | 53.2 | 0.567 | 0.566 | -5.02 | -1.5 | 2/4 | -4.97 | -4.77 | 6 |
| CRSI<=20 & hs>+3 | 102 | 52.9 | 0.590 | 0.587 | -7.36 | -1.4 | 0/3 | -7.16 | -7.24 | 9 |
| hs>+3 only | 526 | 56.5 | 0.574 | 0.574 | -2.54 | -1.1 | 2/4 | -2.41 | -2.11 | 6 |
| all windows (buy Up) | 7753 | 49.7 | 0.498 | 0.499 | -1.78 | -3.3 | 0/4 | -1.72 | -1.66 | 8 |

CRSI<=20 & hs>0 by month (EV c / n): 26-08:-4.3/129 26-09:-3.1/206 26-10:-4.7/230 26-11:+26.9/6

Note: Polymarket's minute-1 'mid' is reconstructed from the last aggressor prints on each side before 62 s, not from a book snapshot.
