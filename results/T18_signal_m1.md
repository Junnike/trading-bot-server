# T18 — Binance-derived signals priced at Kalshi minute 1 (CRSI not priced, head start priced)

Signals computed at the window open from Binance 1-minute data; executed at the Kalshi minute-1 ask (taker) or bid (maker, fill assumed). Candle quotes are closes of the 1-minute candle, not the book: see the tape-based fill check in T18_fills.

## KXBTC15M / BTCUSDT — 15103 windows with minute-1 quotes, 2025-12..2026-10, base P(yes) 50.3%, mid1 0.499

| signal | n | per day | hit % | market mid1 | ask1 | taker EV @ask1 c | z (cluster day) | taker EV @ask2 c | maker @bid1 EV c (fill assumed) | months > 0 | median m1 volume (ct) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CRSI<=20 | 2516 | 7.8 | 55.4 | 0.506 | 0.523 | +1.16 | 1.2 | +2.12 | +6.50 | 8/11 | 8162 |
| CRSI<=20 & hs>0 | 1105 | 3.4 | 61.9 | 0.542 | 0.557 | +4.20 | 2.7 | +4.97 | +9.27 | 11/11 | 8834 |
| CRSI<=20 & hs>+1 | 615 | 1.9 | 63.1 | 0.547 | 0.562 | +4.87 | 2.4 | +5.30 | +9.87 | 7/11 | 9114 |
| CRSI<=20 & hs>+3 | 243 | 0.8 | 66.3 | 0.561 | 0.575 | +6.75 | 2.2 | +8.38 | +11.67 | 9/11 | 7993 |
| CRSI<=10 & hs>0 | 259 | 0.8 | 62.9 | 0.547 | 0.562 | +4.74 | 1.6 | +5.78 | +9.67 | 7/11 | 10423 |
| hs>+3 only | 1510 | 4.7 | 57.2 | 0.559 | 0.575 | -2.26 | -1.9 | -1.55 | +2.84 | 3/11 | 5428 |
| CRSI>=80 & hs<0 (buy NO) | 1004 | 3.1 | 58.4 | 0.533 | 0.549 | +1.45 | 0.9 | +1.67 | +6.76 | 5/11 | 7248 |
| CRSI>=80 & hs<-1 (buy NO) | 581 | 1.8 | 60.1 | 0.541 | 0.558 | +2.29 | 1.1 | +2.10 | +7.67 | 5/11 | 5721 |
| hs<-3 only (buy NO) | 1442 | 4.5 | 56.2 | 0.564 | 0.582 | -3.94 | -2.9 | -3.87 | +1.50 | 1/11 | 4640 |

CRSI<=20 & hs>0 by month (taker EV c / n): 25-12:+4.7/98 26-01:+1.3/211 26-02:+8.0/166 26-03:+6.4/234 26-04:+4.2/78 26-05:+6.5/53 26-06:+1.3/55 26-07:+2.4/54 26-08:+2.7/45 26-09:+1.6/53 26-10:+0.0/58
