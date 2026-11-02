# T16p — last-minute TWAP sniper replay, POLYMARKET BTC 15m Up/Down, Chainlink 60-s TWAP era (markets with tape: 175; data/poly/markets.jsonl; index proxy Binance 1-s closes, fee 0.07·p·(1−p))

Proxy check: Binance 60-s TWAP label agrees with Polymarket resolution in 97.14% of windows; Binance candle colour (close>=open) agrees in 94.29% -> candle-vs-settlement mismatch 5.71%, TWAP-vs-settlement mismatch 2.86% (index difference BRTI vs Binance).
Model certainty: a side reaches prob >= 0.97 at median second 1 of the closing minute (reached at all in 100% of windows).

## Sniper: buy the certain side (prob >= 0.97) at the first tape print <= 0.9 that is >= 2 s after the signal, taker fee ceil(0.07·p·(1−p)), settle 1/0

| fires | per window | hit rate | mean price paid | EV c/contract | z (cluster day) | median signal second | median fill second | by side (YES/NO fires) |
|---|---|---|---|---|---|---|---|---|
| 28 | 16.0% | 85.7% | 0.762 | +8.70 | nan | 12 | 21 | 17/11 |

By month (fires, EV c, hit): 2026-08:28,+8.7,86%
Months with EV > 0: 1/1
Price cap 0.8: fires 10, EV +13.38c, hit 70.0%
Price cap 0.95: fires 28, EV +8.70c, hit 85.7%
Counterparty: in fired windows the last print before 14:00 was 0.516 (YES price); the sniper's fills average 0.764 on the winning side, i.e. the 14:00 holder of the losing side sells out 81% of the time on the side the model already calls.

Calibration of the model on fired trades (claimed prob vs hit): [0.97, 0.99): n 18, claimed 0.973, hit 0.778, EV +5.5c; [0.99, 0.995): n 2, claimed 0.991, hit 1.000, EV +12.1c; [0.995, 0.999): n 4, claimed 0.998, hit 1.000, EV +14.6c; [0.999, 1.0): n 4, claimed 1.000, hit 1.000, EV +15.4c

| variant prob_in / latency s / price cap / fill model | fires | per window | hit % | mean px | median print size (contracts) | EV c | z | months EV>0 |
|---|---|---|---|---|---|---|---|---|
| 0.97 / 2 / 0.9 / any print | 28 | 16.0% | 85.7 | 0.762 | 12 | +8.70 | nan | 1/1 |
| 0.99 / 2 / 0.9 / any print | 23 | 13.1% | 91.3 | 0.789 | 6 | +11.56 | nan | 1/1 |
| 0.999 / 2 / 0.9 / any print | 17 | 9.7% | 88.2 | 0.739 | 9 | +13.44 | nan | 1/1 |
| 0.99 / 2 / 0.8 / any print | 8 | 4.6% | 75.0 | 0.559 | 6 | +17.87 | nan | 1/1 |
| 0.99 / 2 / 0.9 / aggressor-side | 21 | 12.0% | 90.5 | 0.783 | 7 | +11.30 | nan | 1/1 |
| 0.999 / 2 / 0.9 / aggressor-side | 15 | 8.6% | 86.7 | 0.727 | 7 | +13.06 | nan | 1/1 |
| 0.999 / 5 / 0.9 / aggressor-side | 11 | 6.3% | 90.9 | 0.802 | 5 | +9.89 | nan | 1/1 |
| 0.999 / 2 / 0.8 / aggressor-side | 8 | 4.6% | 75.0 | 0.551 | 7 | +18.73 | nan | 1/1 |

Caveats: (1) fill = a print at or below our limit, not a quote: optimistic (same as T12 model A); (2) Binance 1-s close as BRTI proxy, mismatch 2.86% of windows mostly where |closeTWAP-openTWAP| is a few bp; (3) latency 2 s from model to order; (4) one trade per window, no size: the tape shows what printed, not depth.
