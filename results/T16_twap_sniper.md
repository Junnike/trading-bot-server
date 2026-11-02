# T16 — last-minute TWAP sniper replay, Kalshi BTC 15m (windows with tape: 1352; sample data/kalshi/candles.jsonl + trades_last2.jsonl; index proxy Binance 1-s closes)

Proxy check: Binance 60-s TWAP label agrees with Kalshi settlement in 98.96% of windows; Binance candle colour (close>=open) agrees in 94.30% -> candle-vs-settlement mismatch 5.70%, TWAP-vs-settlement mismatch 1.04% (index difference BRTI vs Binance).
Model certainty: a side reaches prob >= 0.97 at median second 1 of the closing minute (reached at all in 100% of windows).

## Sniper: buy the certain side (prob >= 0.97) at the first tape print <= 0.9 that is >= 2 s after the signal, taker fee ceil(0.07·p·(1−p)), settle 1/0

| fires | per window | hit rate | mean price paid | EV c/contract | z (cluster day) | median signal second | median fill second | by side (YES/NO fires) |
|---|---|---|---|---|---|---|---|---|
| 206 | 15.2% | 91.3% | 0.697 | +20.03 | 9.6 | 1 | 25 | 100/106 |

By month (fires, EV c, hit): 2025-12:85,+24.1,94% 2026-01:121,+17.2,89%
Months with EV > 0: 2/2
Price cap 0.8: fires 113, EV +31.51c, hit 88.5%
Price cap 0.95: fires 206, EV +20.03c, hit 91.3%
Counterparty: in fired windows the last print before 14:00 was 0.501 (YES price); the sniper's fills average 0.693 on the winning side, i.e. the 14:00 holder of the losing side sells out 84% of the time on the side the model already calls.

Calibration of the model on fired trades (claimed prob vs hit): [0.97, 0.99): n 109, claimed 0.976, hit 0.890, EV +21.4c; [0.99, 0.995): n 14, claimed 0.992, hit 0.857, EV +13.5c; [0.995, 0.999): n 19, claimed 0.997, hit 0.947, EV +15.7c; [0.999, 1.0): n 64, claimed 1.000, hit 0.953, EV +20.5c

| variant prob_in / latency s / price cap / fill model | fires | per window | hit % | mean px | median print size (contracts) | EV c | z | months EV>0 |
|---|---|---|---|---|---|---|---|---|
| 0.97 / 2 / 0.9 / any print | 206 | 15.2% | 91.3 | 0.697 | 5 | +20.03 | 9.6 | 2/2 |
| 0.99 / 2 / 0.9 / any print | 190 | 14.1% | 92.1 | 0.690 | 5 | +21.65 | 9.6 | 2/2 |
| 0.999 / 2 / 0.9 / any print | 167 | 12.4% | 91.6 | 0.671 | 5 | +23.01 | 9.8 | 2/2 |
| 0.99 / 2 / 0.8 / any print | 122 | 9.0% | 89.3 | 0.555 | 5 | +31.99 | 11.6 | 2/2 |
| 0.99 / 2 / 0.9 / aggressor-side | 82 | 6.1% | 86.6 | 0.658 | 5 | +19.40 | 5.5 | 2/2 |
| 0.999 / 2 / 0.9 / aggressor-side | 71 | 5.3% | 85.9 | 0.644 | 9 | +20.11 | 5.4 | 2/2 |
| 0.999 / 5 / 0.9 / aggressor-side | 59 | 4.4% | 84.7 | 0.652 | 7 | +18.17 | 5.0 | 2/2 |
| 0.999 / 2 / 0.8 / aggressor-side | 41 | 3.0% | 80.5 | 0.470 | 8 | +31.73 | 6.5 | 2/2 |

Caveats: (1) fill = a print at or below our limit, not a quote: optimistic (same as T12 model A); (2) Binance 1-s close as BRTI proxy, mismatch 1.04% of windows mostly where |closeTWAP-openTWAP| is a few bp; (3) latency 2 s from model to order; (4) one trade per window, no size: the tape shows what printed, not depth.
