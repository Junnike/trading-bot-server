# T16p — last-minute TWAP sniper replay, POLYMARKET BTC 15m Up/Down, Chainlink 60-s TWAP era (markets with tape: 7776; data/poly/markets.jsonl; index proxy Binance 1-s closes, fee 0.07·p·(1−p))

Proxy check: Binance 60-s TWAP label agrees with Polymarket resolution in 98.32% of windows; Binance candle colour (close>=open) agrees in 93.94% -> candle-vs-settlement mismatch 6.06%, TWAP-vs-settlement mismatch 1.68% (index difference BRTI vs Binance).
Model certainty: a side reaches prob >= 0.97 at median second 1 of the closing minute (reached at all in 100% of windows).

## Sniper: buy the certain side (prob >= 0.97) at the first tape print <= 0.9 that is >= 2 s after the signal, taker fee ceil(0.07·p·(1−p)), settle 1/0

| fires | per window | hit rate | mean price paid | EV c/contract | z (cluster day) | median signal second | median fill second | by side (YES/NO fires) |
|---|---|---|---|---|---|---|---|---|
| 1011 | 13.0% | 82.0% | 0.771 | +3.96 | 3.9 | 4 | 10 | 471/540 |

By month (fires, EV c, hit): 2026-08:236,+3.7,79% 2026-09:424,+2.6,82% 2026-10:351,+5.7,84%
Months with EV > 0: 3/3
Price cap 0.8: fires 338, EV +3.66c, hit 61.5%
Price cap 0.95: fires 1011, EV +3.96c, hit 82.0%
Counterparty: in fired windows the last print before 14:00 was 0.499 (YES price); the sniper's fills average 0.771 on the winning side, i.e. the 14:00 holder of the losing side sells out 73% of the time on the side the model already calls.

Calibration of the model on fired trades (claimed prob vs hit): [0.97, 0.99): n 629, claimed 0.976, hit 0.817, EV +3.6c; [0.99, 0.995): n 83, claimed 0.992, hit 0.843, EV +7.0c; [0.995, 0.999): n 116, claimed 0.997, hit 0.845, EV +4.4c; [0.999, 1.0): n 183, claimed 1.000, hit 0.803, EV +3.6c

| variant prob_in / latency s / price cap / fill model | fires | per window | hit % | mean px | median print size (contracts) | EV c | z | months EV>0 |
|---|---|---|---|---|---|---|---|---|
| 0.97 / 2 / 0.9 / any print | 1011 | 13.0% | 82.0 | 0.771 | 10 | +3.96 | 3.9 | 3/3 |
| 0.99 / 2 / 0.9 / any print | 783 | 10.1% | 79.8 | 0.753 | 10 | +3.54 | 2.6 | 3/3 |
| 0.999 / 2 / 0.9 / any print | 562 | 7.2% | 76.0 | 0.718 | 10 | +3.26 | 2.1 | 3/3 |
| 0.99 / 2 / 0.8 / any print | 471 | 6.1% | 66.5 | 0.609 | 10 | +4.28 | 2.1 | 3/3 |
| 0.99 / 2 / 0.9 / aggressor-side | 729 | 9.4% | 78.3 | 0.743 | 8 | +3.03 | 2.1 | 2/3 |
| 0.999 / 2 / 0.9 / aggressor-side | 510 | 6.6% | 73.7 | 0.708 | 9 | +1.94 | 1.1 | 3/3 |
| 0.999 / 5 / 0.9 / aggressor-side | 390 | 5.0% | 69.5 | 0.691 | 9 | -0.54 | -0.3 | 1/3 |
| 0.999 / 2 / 0.8 / aggressor-side | 330 | 4.2% | 59.4 | 0.553 | 10 | +2.83 | 1.2 | 3/3 |

Caveats: (1) fill = a print at or below our limit, not a quote: optimistic (same as T12 model A); (2) Binance 1-s close as BRTI proxy, mismatch 1.68% of windows mostly where |closeTWAP-openTWAP| is a few bp; (3) latency 2 s from model to order; (4) one trade per window, no size: the tape shows what printed, not depth.
