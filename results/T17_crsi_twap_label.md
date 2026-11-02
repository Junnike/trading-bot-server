# T17 — CRSI robot scored on the venue TWAP label (03.11.2026)

Validation on 7000 Kalshi windows: 1-min VWAP label = 1-s TWAP label 97.83%; VWAP label = Kalshi settlement 97.20%; 1-s TWAP = settlement 98.54%; candle label = settlement 93.33%. VWAP-of-minute is an acceptable long-history proxy for the venue label.

| coin | window | n signals | WR candle label % | WR TWAP label % | drop pp | agreement of labels on signal bars % | EV at p=0.55 taker on TWAP label (c) |
|---|---|---|---|---|---|---|---|
| BTC | 2020-26 | 38408 | 56.99 | 56.11 | +0.88 | 94.6 | -0.62 |
| BTC | 2025-26 | 10408 | 55.20 | 54.54 | +0.65 | 95.0 | -2.19 |
| ETH | 2020-26 | 38454 | 56.87 | 56.00 | +0.87 | 94.4 | -0.73 |
| ETH | 2025-26 | 10001 | 56.59 | 55.77 | +0.82 | 95.0 | -0.96 |
| SOL | 2020-26 | 36857 | 54.98 | 53.48 | +1.50 | 94.1 | -3.25 |
| SOL | 2025-26 | 10448 | 55.47 | 53.79 | +1.67 | 94.8 | -2.94 |
| XRP | 2020-26 | 39592 | 56.63 | 54.70 | +1.94 | 94.3 | -2.04 |
| XRP | 2025-26 | 10486 | 54.86 | 53.15 | +1.72 | 94.7 | -3.59 |
| DOGE | 2020-26 | 38935 | 56.93 | 56.09 | +0.84 | 93.9 | -0.64 |
| DOGE | 2025-26 | 10354 | 55.68 | 54.58 | +1.10 | 94.8 | -2.15 |

EV column: binary payout buying UP at 0.55 with taker fee 0.07·p·(1−p); break-even WR at 0.55 is 56.7 %, at 0.50 it is 51.75 %.
Caveats: label proxy = 1-min VWAP (volume-weighted, not time-weighted) of Binance, validated above; venue indices (BRTI, Chainlink) add ~1-2 % further disagreement; the robot here is the CRSI gate, not the Pine v1 robots (files missing).
