# T13 — spot/perp basis (hourly, all USDT perps with spot pair, 24h perp volume >= 10M)

## 1. Basis mean reversion (enter |z|>=2 vs 7-day mean, exit |z|<=0.5 or 24h; PnL = basis convergence in direction of trade + funding carried; fee per leg-side)

| year | n trades | gross bp/trade | +funding bp | net @2bp maker (4 legs = 8 bp) | net @5bp taker (20 bp) | z | median hold h |
|---|---|---|---|---|---|---|---|
| 2022 | 35424 | +1.7 | +0.9 | -5.4 | -17.4 | 28.8 | 2 |
| 2023 | 36726 | +1.6 | +0.9 | -5.5 | -17.5 | 24.7 | 2 |
| 2024 | 49329 | +1.3 | +0.7 | -6.0 | -18.0 | 33.2 | 3 |
| 2025 | 38425 | +2.0 | +2.3 | -3.8 | -15.8 | 31.5 | 3 |
| 2026 | 13805 | +3.0 | +4.0 | -1.0 | -13.0 | 21.7 | 2 |
| ALL | 173709 | +1.7 | +1.4 | -4.9 | -16.9 | 59.6 | 2 |

## 2. Cross-sectional: at each 8h settlement rank by basis; long perp lowest-basis decile, short perp highest-basis decile (perp only, funding included: long pays, short receives). Net of 5 bp per side per rebalance (full turnover assumed).

| year | n periods | long low-basis 8h bp | short high-basis 8h bp | L/S gross bp per 8h | funding bp | net @5bp taker | ann % | z |
|---|---|---|---|---|---|---|---|---|
| 2022 | 1095 | -6.4 | -18.7 | +12.3 | +3.3 | -4.4 | -47.7 | 4.3 |
| 2023 | 1095 | +16.5 | +5.2 | +11.3 | +4.1 | -4.6 | -50.9 | 4.3 |
| 2024 | 1098 | +3.1 | -1.0 | +4.2 | +2.4 | -13.4 | -146.6 | 2.1 |
| 2025 | 1095 | -22.7 | -14.2 | -8.5 | +6.3 | -22.2 | -243.1 | -0.5 |
| 2026 | 819 | -29.6 | -1.3 | -28.3 | +12.3 | -36.0 | -394.6 | -1.6 |
| ALL | 5202 | -6.7 | -6.3 | -0.4 | +5.3 | -15.1 | -165.0 | 2.2 |
