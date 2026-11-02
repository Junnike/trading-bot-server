# T18 fills — CRSI<=20 signal windows with first-3-minute tape (BTC, n 1149; data/kalshi/trades_first3.jsonl)

Minute-1 activity: median prints 451, median contracts 19556; YES-taker prints exist after 62 s in 99% of windows (that is where a taker buy can be priced from the tape).

| signal | fill model | n | hit % | mean fill px | candle ask1 | EV c (fee incl.) | z | median fill delay s | median print size ct |
|---|---|---|---|---|---|---|---|---|---|
| CRSI<=20 | taker, first YES-taker print after 62s | 1137 | 55.1 | 0.509 | 0.517 | +2.22 | 1.5 | 0 | 10 |
| CRSI<=20 | taker, first any print after 62s | 1146 | 55.1 | 0.503 | 0.518 | +2.90 | 2.0 | nan | nan |
| CRSI<=20 | taker, first YES-taker print after 65s | 1137 | 55.1 | 0.508 | 0.517 | +2.25 | 1.5 | 0 | 10 |
| CRSI<=20 | taker, first any print after 65s | 1146 | 55.1 | 0.502 | 0.518 | +2.95 | 2.0 | nan | nan |
| CRSI<=20 | taker, first YES-taker print after 75s | 1136 | 55.1 | 0.507 | 0.517 | +2.48 | 1.7 | 0 | 10 |
| CRSI<=20 | taker, first any print after 75s | 1146 | 55.1 | 0.501 | 0.518 | +3.08 | 2.1 | nan | nan |
| CRSI<=20 | candle ask1 close (T18 table) | 1148 | 55.1 | 0.518 | 0.518 | +1.35 | 0.9 | | |
| CRSI<=20 & hs>0 | taker, first YES-taker print after 62s | 488 | 61.7 | 0.543 | 0.551 | +5.42 | 2.5 | 0 | 10 |
| CRSI<=20 & hs>0 | taker, first any print after 62s | 492 | 61.6 | 0.537 | 0.551 | +5.89 | 2.7 | nan | nan |
| CRSI<=20 & hs>0 | taker, first YES-taker print after 65s | 488 | 61.7 | 0.543 | 0.551 | +5.43 | 2.5 | 0 | 10 |
| CRSI<=20 & hs>0 | taker, first any print after 65s | 492 | 61.6 | 0.536 | 0.551 | +5.97 | 2.8 | nan | nan |
| CRSI<=20 & hs>0 | taker, first YES-taker print after 75s | 488 | 61.7 | 0.542 | 0.551 | +5.50 | 2.5 | 0 | 10 |
| CRSI<=20 & hs>0 | taker, first any print after 75s | 492 | 61.6 | 0.536 | 0.551 | +6.00 | 2.8 | nan | nan |
| CRSI<=20 & hs>0 | candle ask1 close (T18 table) | 493 | 61.7 | 0.552 | 0.552 | +4.53 | 2.1 | | |
| CRSI<=20 & hs>+1 | taker, first YES-taker print after 62s | 263 | 63.1 | 0.546 | 0.553 | +6.54 | 2.4 | 0 | 10 |
| CRSI<=20 & hs>+1 | taker, first any print after 62s | 266 | 63.2 | 0.541 | 0.554 | +7.04 | 2.6 | nan | nan |
| CRSI<=20 & hs>+1 | taker, first YES-taker print after 65s | 263 | 63.1 | 0.547 | 0.553 | +6.41 | 2.4 | 0 | 9 |
| CRSI<=20 & hs>+1 | taker, first any print after 65s | 266 | 63.2 | 0.542 | 0.554 | +7.03 | 2.6 | nan | nan |
| CRSI<=20 & hs>+1 | taker, first YES-taker print after 75s | 263 | 63.1 | 0.550 | 0.553 | +6.13 | 2.3 | 0 | 10 |
| CRSI<=20 & hs>+1 | taker, first any print after 75s | 266 | 63.2 | 0.544 | 0.554 | +6.73 | 2.5 | nan | nan |
| CRSI<=20 & hs>+1 | candle ask1 close (T18 table) | 267 | 63.3 | 0.554 | 0.554 | +5.92 | 2.2 | | |

Reading: the YES-taker-print fill is what a taker order would have paid (someone lifted that ask); if it is close to the candle ask and EV stays positive, the candle-based T18 numbers are executable at the printed sizes.
