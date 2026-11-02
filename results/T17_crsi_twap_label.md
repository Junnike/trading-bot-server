# T17 — CRSI robot scored on the venue TWAP label (03.11.2026)

Validation on 14556 Kalshi windows: 1-min VWAP label = 1-s TWAP label 97.65%; VWAP label = Kalshi settlement 97.08%; 1-s TWAP = settlement 98.65%; candle label = settlement 93.01%. VWAP-of-minute is an acceptable long-history proxy for the venue label.

| coin | window | n signals | WR candle label % | WR TWAP label % | drop pp | agreement of labels on signal bars % | EV at p=0.55 taker on TWAP label (c) |
|---|---|---|---|---|---|---|---|
| BTC | 2020-26 | 38957 | 56.92 | 56.02 | +0.90 | 94.6 | -0.71 |
| BTC | 2025-26 | 10957 | 55.02 | 54.29 | +0.73 | 95.0 | -2.44 |
| ETH | 2020-26 | 39004 | 56.78 | 55.90 | +0.88 | 94.4 | -0.83 |
| ETH | 2025-26 | 10551 | 56.27 | 55.43 | +0.84 | 95.0 | -1.31 |
| SOL | 2020-26 | 37396 | 54.96 | 53.46 | +1.50 | 94.1 | -3.27 |
| SOL | 2025-26 | 10987 | 55.37 | 53.70 | +1.67 | 94.7 | -3.03 |
| XRP | 2020-26 | 40160 | 56.58 | 54.65 | +1.93 | 94.2 | -2.08 |
| XRP | 2025-26 | 11054 | 54.76 | 53.07 | +1.69 | 94.6 | -3.67 |
| DOGE | 2020-26 | 39480 | 56.90 | 56.04 | +0.86 | 93.9 | -0.69 |
| DOGE | 2025-26 | 10899 | 55.65 | 54.48 | +1.17 | 94.7 | -2.25 |

EV column: binary payout buying UP at 0.55 with taker fee 0.07·p·(1−p); break-even WR at 0.55 is 56.7 %, at 0.50 it is 51.75 %.
Caveats: label proxy = 1-min VWAP (volume-weighted, not time-weighted) of Binance, validated above; venue indices (BRTI, Chainlink) add ~1-2 % further disagreement; the robot here is the CRSI gate, not the Pine v1 robots (files missing).
