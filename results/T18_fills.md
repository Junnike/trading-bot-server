# T18 fills — CRSI<=20 signal windows with first-3-minute tape (BTC, n 764; data/kalshi/trades_first3.jsonl)

Minute-1 activity: median prints 274, median contracts 8685; YES-taker prints exist after 62 s in 98% of windows (that is where a taker buy can be priced from the tape).

| signal | fill model | n | hit % | mean fill px | candle ask1 | EV c (fee incl.) | z | median fill delay s | median print size ct |
|---|---|---|---|---|---|---|---|---|---|
| CRSI<=20 | taker, first YES-taker print after 62s | 752 | 54.8 | 0.501 | 0.512 | +2.72 | 1.5 | 0 | 9 |
| CRSI<=20 | taker, first any print after 62s | 761 | 54.9 | 0.495 | 0.514 | +3.49 | 2.0 | nan | nan |
| CRSI<=20 | taker, first YES-taker print after 65s | 752 | 54.8 | 0.501 | 0.512 | +2.71 | 1.5 | 1 | 9 |
| CRSI<=20 | taker, first any print after 65s | 761 | 54.9 | 0.494 | 0.514 | +3.54 | 2.0 | nan | nan |
| CRSI<=20 | taker, first YES-taker print after 75s | 751 | 54.9 | 0.498 | 0.512 | +3.05 | 1.7 | 1 | 9 |
| CRSI<=20 | taker, first any print after 75s | 761 | 54.9 | 0.492 | 0.514 | +3.70 | 2.1 | nan | nan |
| CRSI<=20 | candle ask1 close (T18 table) | 764 | 54.8 | 0.514 | 0.514 | +1.48 | 0.8 | | |
| CRSI<=20 & hs>0 | taker, first YES-taker print after 62s | 315 | 62.5 | 0.532 | 0.544 | +7.35 | 2.7 | 1 | 9 |
| CRSI<=20 & hs>0 | taker, first any print after 62s | 319 | 62.4 | 0.526 | 0.545 | +7.77 | 3.1 | nan | nan |
| CRSI<=20 & hs>0 | taker, first YES-taker print after 65s | 315 | 62.5 | 0.532 | 0.544 | +7.36 | 2.8 | 1 | 8 |
| CRSI<=20 & hs>0 | taker, first any print after 65s | 319 | 62.4 | 0.525 | 0.545 | +7.94 | 3.2 | nan | nan |
| CRSI<=20 & hs>0 | taker, first YES-taker print after 75s | 315 | 62.5 | 0.530 | 0.544 | +7.57 | 2.8 | 1 | 8 |
| CRSI<=20 & hs>0 | taker, first any print after 75s | 319 | 62.4 | 0.524 | 0.545 | +8.03 | 3.2 | nan | nan |
| CRSI<=20 & hs>0 | candle ask1 close (T18 table) | 321 | 62.3 | 0.545 | 0.545 | +5.83 | 2.3 | | |
| CRSI<=20 & hs>+1 | taker, first YES-taker print after 62s | 171 | 65.5 | 0.543 | 0.552 | +9.24 | 2.8 | 1 | 9 |
| CRSI<=20 & hs>+1 | taker, first any print after 62s | 174 | 65.5 | 0.539 | 0.554 | +9.68 | 3.0 | nan | nan |
| CRSI<=20 & hs>+1 | taker, first YES-taker print after 65s | 171 | 65.5 | 0.546 | 0.552 | +8.90 | 2.7 | 1 | 9 |
| CRSI<=20 & hs>+1 | taker, first any print after 65s | 174 | 65.5 | 0.540 | 0.554 | +9.57 | 3.0 | nan | nan |
| CRSI<=20 & hs>+1 | taker, first YES-taker print after 75s | 171 | 65.5 | 0.545 | 0.552 | +9.04 | 2.8 | 1 | 8 |
| CRSI<=20 & hs>+1 | taker, first any print after 75s | 174 | 65.5 | 0.539 | 0.554 | +9.61 | 3.1 | nan | nan |
| CRSI<=20 & hs>+1 | candle ask1 close (T18 table) | 176 | 65.3 | 0.554 | 0.554 | +7.96 | 2.5 | | |

Reading: the YES-taker-print fill is what a taker order would have paid (someone lifted that ask); if it is close to the candle ask and EV stays positive, the candle-based T18 numbers are executable at the printed sizes.
