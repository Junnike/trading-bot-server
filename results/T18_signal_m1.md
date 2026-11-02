# T18 — Binance-derived signals priced at Kalshi minute 1 (CRSI not priced, head start priced)

Signals computed at the window open from Binance 1-minute data; executed at the Kalshi minute-1 ask (taker) or bid (maker, fill assumed). Candle quotes are closes of the 1-minute candle, not the book: see the tape-based fill check in T18_fills.

## KXBTC15M / BTCUSDT — 7085 windows with minute-1 quotes, 2025-12..2026-09, base P(yes) 50.0%, mid1 0.499

| signal | n | per day | hit % | market mid1 | ask1 | taker EV @ask1 c | z (cluster day) | taker EV @ask2 c | maker @bid1 EV c (fill assumed) | months > 0 | median m1 volume (ct) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CRSI<=20 | 1166 | 4.0 | 55.1 | 0.503 | 0.518 | +1.25 | 0.9 | +1.95 | +6.35 | 8/10 | 20940 |
| CRSI<=20 & hs>0 | 499 | 1.7 | 61.7 | 0.538 | 0.552 | +4.56 | 2.1 | +5.22 | +9.31 | 9/10 | 23425 |
| CRSI<=20 & hs>+1 | 272 | 0.9 | 63.6 | 0.541 | 0.554 | +6.20 | 2.3 | +6.20 | +10.86 | 8/10 | 22056 |
| CRSI<=20 & hs>+3 | 105 | 0.4 | 66.7 | 0.556 | 0.570 | +7.70 | 1.8 | +9.49 | +12.60 | 8/10 | 16793 |
| CRSI<=10 & hs>0 | 127 | 0.4 | 63.0 | 0.552 | 0.568 | +4.21 | 1.0 | +5.21 | +9.50 | 7/10 | 21439 |
| hs>+3 only | 622 | 2.1 | 57.6 | 0.561 | 0.578 | -2.14 | -1.2 | -0.84 | +3.07 | 3/10 | 12943 |
| CRSI>=80 & hs<0 (buy NO) | 473 | 1.6 | 54.8 | 0.535 | 0.550 | -2.21 | -1.0 | -1.78 | +2.71 | 4/10 | 20351 |
| CRSI>=80 & hs<-1 (buy NO) | 265 | 0.9 | 57.0 | 0.543 | 0.557 | -0.74 | -0.2 | -0.83 | +4.12 | 6/10 | 14393 |
| hs<-3 only (buy NO) | 620 | 2.1 | 55.8 | 0.566 | 0.583 | -4.40 | -2.1 | -3.89 | +0.93 | 4/10 | 11714 |

CRSI<=20 & hs>0 by month (taker EV c / n): 25-12:+4.7/44 26-01:-1.1/56 26-02:+13.3/32 26-03:+11.0/60 26-04:+6.2/47 26-05:+6.5/53 26-06:+1.3/55 26-07:+2.4/54 26-08:+2.7/45 26-09:+1.6/53
