# T16 — last-minute TWAP sniper replay, Kalshi BTC 15m (windows with tape: 7365; sample data/kalshi/candles.jsonl + trades_last2.jsonl; index proxy Binance 1-s closes)

Proxy check: Binance 60-s TWAP label agrees with Kalshi settlement in 98.66% of windows; Binance candle colour (close>=open) agrees in 93.46% -> candle-vs-settlement mismatch 6.54%, TWAP-vs-settlement mismatch 1.34% (index difference BRTI vs Binance).
Model certainty: a side reaches prob >= 0.97 at median second 1 of the closing minute (reached at all in 100% of windows).

## Sniper: buy the certain side (prob >= 0.97) at the first tape print <= 0.9 that is >= 2 s after the signal, taker fee ceil(0.07·p·(1−p)), settle 1/0

| fires | per window | hit rate | mean price paid | EV c/contract | z (cluster day) | median signal second | median fill second | by side (YES/NO fires) |
|---|---|---|---|---|---|---|---|---|
| 765 | 10.4% | 82.0% | 0.740 | +6.63 | 4.7 | 6 | 20 | 350/415 |

By month (fires, EV c, hit): 2025-12:85,+24.1,94% 2026-01:124,+16.0,88% 2026-02:90,+8.0,91% 2026-03:53,+7.5,91% 2026-04:67,+11.2,87% 2026-05:73,-8.4,67% 2026-06:45,+2.3,78% 2026-07:51,-5.6,69% 2026-08:77,+3.1,73% 2026-09:63,-5.5,71% 2026-10:37,+2.2,81%
Months with EV > 0: 8/11
Price cap 0.8: fires 282, EV +15.97c, hit 68.1%
Price cap 0.95: fires 765, EV +6.63c, hit 82.0%
Counterparty: in fired windows the last print before 14:00 was 0.487 (YES price); the sniper's fills average 0.739 on the winning side, i.e. the 14:00 holder of the losing side sells out 78% of the time on the side the model already calls.

Calibration of the model on fired trades (claimed prob vs hit): [0.97, 0.99): n 485, claimed 0.976, hit 0.790, EV +6.0c; [0.99, 0.995): n 60, claimed 0.992, hit 0.817, EV +1.9c; [0.995, 0.999): n 63, claimed 0.997, hit 0.889, EV +9.2c; [0.999, 1.0): n 157, claimed 1.000, hit 0.885, EV +9.5c

| variant prob_in / latency s / price cap / fill model | fires | per window | hit % | mean px | median print size (contracts) | EV c | z | months EV>0 |
|---|---|---|---|---|---|---|---|---|
| 0.97 / 2 / 0.9 / any print | 765 | 10.4% | 82.0 | 0.740 | 11 | +6.63 | 4.7 | 8/11 |
| 0.99 / 2 / 0.9 / any print | 662 | 9.0% | 81.4 | 0.715 | 11 | +8.64 | 6.0 | 8/11 |
| 0.999 / 2 / 0.9 / any print | 520 | 7.1% | 79.2 | 0.680 | 11 | +9.92 | 6.0 | 8/11 |
| 0.99 / 2 / 0.8 / any print | 444 | 6.0% | 72.7 | 0.583 | 10 | +12.63 | 6.1 | 8/11 |
| 0.99 / 2 / 0.9 / aggressor-side | 436 | 5.9% | 72.7 | 0.668 | 10 | +4.57 | 2.6 | 8/11 |
| 0.999 / 2 / 0.9 / aggressor-side | 319 | 4.3% | 67.4 | 0.617 | 11 | +4.34 | 2.0 | 7/11 |
| 0.999 / 5 / 0.9 / aggressor-side | 264 | 3.6% | 66.3 | 0.621 | 16 | +2.87 | 1.3 | 7/11 |
| 0.999 / 2 / 0.8 / aggressor-side | 215 | 2.9% | 52.6 | 0.454 | 11 | +5.46 | 1.9 | 7/11 |

Caveats: (1) fill = a print at or below our limit, not a quote: optimistic (same as T12 model A); (2) Binance 1-s close as BRTI proxy, mismatch 1.34% of windows mostly where |closeTWAP-openTWAP| is a few bp; (3) latency 2 s from model to order; (4) one trade per window, no size: the tape shows what printed, not depth.
