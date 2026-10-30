# T12d — perp microstructure tests (Binance Vision metrics + bookDepth)

Enter next 5m open, exit close after hold; fee 10 bp taker RT; z = UTC-day cluster bootstrap; non-overlapping trades. Percentiles are trailing 30-day, lagged.


## A. Metrics (5m): open interest, taker buy/sell volume ratio, long/short account ratios


### BTC (metrics rows 566643)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | -10.4 (z -2.0, WR 52%, n 15765) | -10.2 (z -0.8, WR 52%, n 5364) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | -10.9 (z -1.9, WR 52%, n 6932) | -10.1 (z -0.2, WR 52%, n 2265) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | -12.6 (z -1.9, WR 51%, n 3180) | -9.3 (z 0.4, WR 50%, n 991) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | -16.4 (z -2.2, WR 49%, n 2202) | -9.1 (z 0.2, WR 49%, n 691) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | -9.7 (z 1.4, WR 51%, n 12270) | -10.0 (z -0.0, WR 49%, n 3804) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | -9.2 (z 1.6, WR 53%, n 5569) | -10.2 (z -0.2, WR 51%, n 1653) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | -5.5 (z 3.1, WR 54%, n 2759) | -10.5 (z -0.2, WR 52%, n 793) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | +1.3 (z 3.6, WR 55%, n 2031) | -7.9 (z 0.4, WR 53%, n 595) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | -9.5 (z 2.4, WR 52%, n 15107) | -9.5 (z 2.2, WR 52%, n 5425) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | -8.3 (z 2.9, WR 54%, n 6507) | -8.7 (z 1.9, WR 53%, n 2247) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | -4.8 (z 3.2, WR 55%, n 2907) | -6.4 (z 1.6, WR 55%, n 964) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | -4.5 (z 1.8, WR 54%, n 2199) | -10.0 (z -0.0, WR 50%, n 713) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | -10.2 (z -0.7, WR 52%, n 12406) | -10.3 (z -0.8, WR 51%, n 3722) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | -10.8 (z -1.5, WR 52%, n 5508) | -10.1 (z -0.1, WR 52%, n 1648) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | -11.7 (z -1.1, WR 51%, n 2608) | -8.9 (z 0.4, WR 52%, n 772) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | -16.5 (z -2.1, WR 49%, n 2037) | -13.4 (z -0.8, WR 48%, n 608) |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | -10.0 (z 0.4, WR 48%, n 28964) | -10.0 (z -0.2, WR 48%, n 9466) |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | -10.0 (z -0.1, WR 48%, n 25035) | -10.2 (z -1.2, WR 48%, n 8044) |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | -10.1 (z -0.3, WR 49%, n 16642) | -10.9 (z -1.9, WR 48%, n 5356) |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | -9.2 (z 0.6, WR 50%, n 7564) | -12.3 (z -1.4, WR 49%, n 2448) |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | -10.0 (z -0.4, WR 52%, n 28964) | -10.0 (z 0.2, WR 52%, n 9466) |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | -10.0 (z 0.1, WR 52%, n 25035) | -9.8 (z 1.2, WR 52%, n 8044) |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | -9.9 (z 0.3, WR 51%, n 16642) | -9.1 (z 1.8, WR 52%, n 5356) |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | -10.8 (z -0.6, WR 50%, n 7564) | -7.7 (z 1.4, WR 51%, n 2448) |
| taker buy/sell < p05 -> LONG (fade), hold 5m | -9.9 (z 0.7, WR 51%, n 28824) | -10.1 (z -0.5, WR 51%, n 9378) |
| taker buy/sell < p05 -> LONG (fade), hold 15m | -9.7 (z 1.8, WR 52%, n 24865) | -9.8 (z 0.8, WR 51%, n 7947) |
| taker buy/sell < p05 -> LONG (fade), hold 60m | -9.2 (z 1.9, WR 51%, n 16531) | -9.3 (z 1.5, WR 51%, n 5298) |
| taker buy/sell < p05 -> LONG (fade), hold 240m | -7.7 (z 1.9, WR 51%, n 7534) | -8.4 (z 1.0, WR 52%, n 2458) |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | -10.1 (z -0.7, WR 48%, n 28824) | -9.9 (z 0.5, WR 48%, n 9378) |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | -10.3 (z -1.8, WR 48%, n 24865) | -10.2 (z -0.8, WR 49%, n 7947) |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | -10.8 (z -1.9, WR 48%, n 16531) | -10.7 (z -1.4, WR 48%, n 5298) |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | -12.3 (z -1.9, WR 49%, n 7534) | -11.6 (z -1.0, WR 48%, n 2458) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | -10.0 (z -0.2, WR 50%, n 51597) | -10.0 (z 0.5, WR 49%, n 18677) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | -10.1 (z -0.3, WR 49%, n 17533) | -9.9 (z 0.5, WR 50%, n 6312) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | -10.5 (z -0.6, WR 49%, n 4622) | -9.1 (z 0.8, WR 48%, n 1645) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | -12.2 (z -0.6, WR 50%, n 1295) | -6.8 (z 0.7, WR 49%, n 452) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | -10.0 (z 0.3, WR 50%, n 53323) | -10.0 (z 0.2, WR 50%, n 21636) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | -9.9 (z 0.3, WR 50%, n 18240) | -10.0 (z -0.0, WR 49%, n 7342) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | -8.8 (z 1.4, WR 51%, n 4899) | -9.5 (z 0.4, WR 50%, n 1938) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | -5.6 (z 1.3, WR 50%, n 1427) | -11.4 (z -0.3, WR 49%, n 555) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | -9.9 (z 0.4, WR 50%, n 25954) | -9.9 (z 0.5, WR 50%, n 9329) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | -9.8 (z 0.4, WR 51%, n 10411) | -9.5 (z 1.0, WR 51%, n 3639) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | -9.3 (z 0.6, WR 51%, n 4065) | -10.6 (z -0.4, WR 51%, n 1359) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | -8.1 (z 0.7, WR 50%, n 2708) | -12.4 (z -0.6, WR 50%, n 934) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | -10.6 (z -4.2, WR 50%, n 25928) | -10.3 (z -1.6, WR 50%, n 9466) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | -11.4 (z -3.6, WR 49%, n 10434) | -10.8 (z -1.5, WR 50%, n 3704) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | -13.5 (z -3.2, WR 49%, n 4131) | -11.8 (z -1.1, WR 50%, n 1421) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | -14.5 (z -1.8, WR 49%, n 2761) | -12.0 (z -0.6, WR 49%, n 950) |

### ETH (metrics rows 470933)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | -10.4 (z -1.9, WR 52%, n 14350) | -10.2 (z -0.6, WR 53%, n 5823) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | -11.0 (z -1.7, WR 53%, n 6204) | -10.6 (z -0.6, WR 53%, n 2453) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | -12.4 (z -1.3, WR 52%, n 2824) | -10.0 (z 0.0, WR 53%, n 1063) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | -15.5 (z -1.4, WR 49%, n 1983) | -14.7 (z -0.7, WR 48%, n 756) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | -10.2 (z -0.7, WR 52%, n 9017) | -10.0 (z -0.0, WR 52%, n 3346) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | -10.2 (z -0.2, WR 53%, n 4245) | -10.4 (z -0.2, WR 53%, n 1497) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | -9.9 (z 0.1, WR 52%, n 2166) | -15.5 (z -1.4, WR 51%, n 717) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | -10.3 (z -0.1, WR 53%, n 1633) | -15.3 (z -0.7, WR 53%, n 557) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | -10.0 (z 0.1, WR 52%, n 14670) | -10.3 (z -0.9, WR 52%, n 5863) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | -9.7 (z 0.4, WR 53%, n 6181) | -10.8 (z -0.8, WR 51%, n 2401) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | -8.6 (z 0.7, WR 54%, n 2620) | -11.9 (z -0.6, WR 51%, n 981) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | -10.7 (z -0.2, WR 53%, n 1948) | -11.7 (z -0.3, WR 51%, n 734) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | -10.3 (z -0.9, WR 52%, n 8610) | -10.6 (z -0.8, WR 52%, n 3218) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | -11.1 (z -1.2, WR 52%, n 3938) | -10.5 (z -0.3, WR 53%, n 1432) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | -12.0 (z -0.8, WR 52%, n 1947) | -16.2 (z -1.4, WR 51%, n 689) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | -13.1 (z -0.6, WR 50%, n 1518) | -6.1 (z 0.4, WR 53%, n 540) |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | -9.9 (z 0.8, WR 48%, n 23805) | -9.8 (z 1.2, WR 48%, n 9233) |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | -9.7 (z 1.6, WR 48%, n 20619) | -9.6 (z 1.2, WR 49%, n 8003) |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | -9.1 (z 1.7, WR 50%, n 13715) | -9.0 (z 1.3, WR 50%, n 5370) |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | -9.0 (z 0.6, WR 51%, n 6307) | -10.3 (z -0.1, WR 50%, n 2508) |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | -10.1 (z -0.8, WR 51%, n 23805) | -10.2 (z -1.2, WR 51%, n 9233) |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | -10.3 (z -1.6, WR 51%, n 20619) | -10.4 (z -1.2, WR 51%, n 8003) |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | -10.9 (z -1.7, WR 50%, n 13715) | -11.0 (z -1.2, WR 50%, n 5370) |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | -11.0 (z -0.6, WR 49%, n 6307) | -9.7 (z 0.1, WR 50%, n 2508) |
| taker buy/sell < p05 -> LONG (fade), hold 5m | -10.0 (z -0.0, WR 52%, n 23786) | -9.9 (z 0.5, WR 52%, n 9293) |
| taker buy/sell < p05 -> LONG (fade), hold 15m | -9.8 (z 1.3, WR 52%, n 20401) | -9.9 (z 0.4, WR 52%, n 7987) |
| taker buy/sell < p05 -> LONG (fade), hold 60m | -9.1 (z 1.9, WR 52%, n 13685) | -9.0 (z 1.4, WR 52%, n 5407) |
| taker buy/sell < p05 -> LONG (fade), hold 240m | -10.1 (z -0.1, WR 50%, n 6293) | -10.7 (z -0.3, WR 51%, n 2501) |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | -10.0 (z 0.0, WR 48%, n 23786) | -10.1 (z -0.5, WR 48%, n 9293) |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | -10.2 (z -1.3, WR 48%, n 20401) | -10.1 (z -0.4, WR 48%, n 7987) |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | -10.9 (z -1.9, WR 48%, n 13685) | -11.0 (z -1.3, WR 48%, n 5407) |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | -9.9 (z 0.1, WR 50%, n 6293) | -9.3 (z 0.3, WR 49%, n 2501) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | -9.9 (z 0.8, WR 50%, n 54167) | -9.9 (z 0.8, WR 50%, n 16039) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | -9.8 (z 0.8, WR 50%, n 18458) | -9.8 (z 0.3, WR 50%, n 5498) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | -9.6 (z 0.4, WR 50%, n 4918) | -10.6 (z -0.4, WR 49%, n 1493) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | -7.5 (z 0.7, WR 52%, n 1403) | -6.6 (z 0.6, WR 52%, n 441) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | -9.8 (z 2.0, WR 50%, n 40055) | -9.8 (z 1.0, WR 50%, n 25633) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | -9.4 (z 1.7, WR 50%, n 13693) | -9.7 (z 0.7, WR 50%, n 8741) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | -8.5 (z 1.0, WR 50%, n 3658) | -9.8 (z 0.1, WR 50%, n 2330) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | -6.7 (z 0.6, WR 52%, n 1048) | -15.9 (z -0.8, WR 50%, n 667) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | -10.0 (z -0.1, WR 51%, n 21591) | -10.2 (z -0.5, WR 50%, n 9022) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | -10.1 (z -0.2, WR 50%, n 8705) | -10.9 (z -1.1, WR 50%, n 3605) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | -9.5 (z 0.3, WR 50%, n 3462) | -10.6 (z -0.2, WR 50%, n 1406) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | -8.2 (z 0.5, WR 51%, n 2355) | -8.2 (z 0.3, WR 51%, n 988) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | -10.2 (z -1.5, WR 50%, n 21479) | -10.2 (z -0.6, WR 50%, n 8929) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | -10.6 (z -1.3, WR 49%, n 8718) | -10.5 (z -0.7, WR 50%, n 3582) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | -12.5 (z -1.7, WR 48%, n 3543) | -13.1 (z -1.2, WR 49%, n 1445) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | -18.4 (z -2.5, WR 48%, n 2370) | -16.8 (z -1.2, WR 47%, n 1001) |

### SOL (metrics rows 470913)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | -10.8 (z -2.1, WR 51%, n 13509) | -10.7 (z -1.5, WR 51%, n 5340) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | -12.0 (z -2.0, WR 52%, n 5869) | -11.2 (z -0.8, WR 52%, n 2302) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | -10.7 (z -0.2, WR 52%, n 2673) | -7.8 (z 0.5, WR 51%, n 1046) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | -12.3 (z -0.3, WR 52%, n 1864) | -2.4 (z 0.9, WR 53%, n 745) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | -10.4 (z -0.8, WR 50%, n 10111) | -9.5 (z 0.9, WR 51%, n 4027) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | -9.7 (z 0.3, WR 52%, n 4545) | -8.2 (z 1.4, WR 53%, n 1762) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | -11.2 (z -0.4, WR 51%, n 2218) | -7.5 (z 0.7, WR 52%, n 840) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | -4.3 (z 0.8, WR 52%, n 1614) | -16.1 (z -0.8, WR 50%, n 615) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | -8.7 (z 3.4, WR 51%, n 13526) | -8.5 (z 2.2, WR 51%, n 5367) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | -7.1 (z 3.0, WR 52%, n 5850) | -6.5 (z 2.3, WR 51%, n 2290) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | -2.3 (z 2.7, WR 54%, n 2645) | -6.1 (z 0.9, WR 53%, n 1024) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | +7.6 (z 3.0, WR 55%, n 1978) | -0.7 (z 1.2, WR 55%, n 792) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | -10.6 (z -1.2, WR 51%, n 9789) | -10.3 (z -0.6, WR 50%, n 3912) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | -10.1 (z -0.1, WR 52%, n 4374) | -9.8 (z 0.1, WR 52%, n 1712) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | -12.7 (z -0.8, WR 50%, n 2134) | -6.0 (z 0.9, WR 50%, n 821) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | -21.5 (z -2.0, WR 49%, n 1631) | -14.3 (z -0.5, WR 48%, n 631) |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | -10.1 (z -0.4, WR 48%, n 24182) | -9.9 (z 0.4, WR 47%, n 9369) |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | -10.0 (z -0.1, WR 48%, n 20815) | -10.0 (z 0.1, WR 48%, n 8088) |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | -10.1 (z -0.1, WR 49%, n 13773) | -10.8 (z -0.9, WR 49%, n 5445) |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | -10.0 (z 0.0, WR 49%, n 6307) | -9.8 (z 0.1, WR 49%, n 2503) |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | -9.9 (z 0.4, WR 50%, n 24182) | -10.1 (z -0.4, WR 49%, n 9369) |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | -10.0 (z 0.1, WR 50%, n 20815) | -10.0 (z -0.1, WR 50%, n 8088) |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | -9.9 (z 0.1, WR 50%, n 13773) | -9.2 (z 0.9, WR 50%, n 5445) |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | -10.0 (z -0.0, WR 51%, n 6307) | -10.2 (z -0.1, WR 51%, n 2503) |
| taker buy/sell < p05 -> LONG (fade), hold 5m | -9.8 (z 1.2, WR 50%, n 24140) | -10.2 (z -0.5, WR 50%, n 9415) |
| taker buy/sell < p05 -> LONG (fade), hold 15m | -9.3 (z 2.7, WR 51%, n 20740) | -9.6 (z 1.1, WR 51%, n 8077) |
| taker buy/sell < p05 -> LONG (fade), hold 60m | -8.6 (z 2.1, WR 51%, n 13729) | -8.5 (z 1.6, WR 51%, n 5440) |
| taker buy/sell < p05 -> LONG (fade), hold 240m | -8.6 (z 0.6, WR 51%, n 6288) | -9.1 (z 0.3, WR 50%, n 2504) |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | -10.2 (z -1.2, WR 47%, n 24140) | -9.8 (z 0.5, WR 47%, n 9415) |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | -10.7 (z -2.7, WR 47%, n 20740) | -10.4 (z -1.1, WR 48%, n 8077) |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | -11.4 (z -2.1, WR 49%, n 13729) | -11.5 (z -1.6, WR 49%, n 5440) |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | -11.4 (z -0.6, WR 49%, n 6288) | -10.9 (z -0.3, WR 50%, n 2504) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | -10.3 (z -2.0, WR 49%, n 49708) | -10.2 (z -1.5, WR 48%, n 18154) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | -10.7 (z -2.0, WR 49%, n 16914) | -10.6 (z -1.4, WR 48%, n 6196) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | -13.2 (z -2.1, WR 49%, n 4459) | -11.7 (z -1.1, WR 48%, n 1649) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | -23.1 (z -2.4, WR 47%, n 1267) | -15.4 (z -1.0, WR 46%, n 480) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | -9.9 (z 0.7, WR 49%, n 36188) | -10.0 (z -0.1, WR 49%, n 17757) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | -9.6 (z 0.8, WR 49%, n 12320) | -10.0 (z -0.0, WR 49%, n 6057) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | -9.0 (z 0.5, WR 49%, n 3281) | -11.2 (z -0.4, WR 49%, n 1630) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | -7.2 (z 0.4, WR 49%, n 949) | -17.6 (z -0.6, WR 48%, n 480) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | -9.5 (z 1.6, WR 50%, n 21874) | -9.2 (z 1.7, WR 50%, n 9360) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | -9.0 (z 1.4, WR 51%, n 8808) | -8.7 (z 1.1, WR 51%, n 3750) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | -5.3 (z 2.4, WR 51%, n 3529) | -6.8 (z 1.2, WR 51%, n 1512) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | +0.4 (z 2.4, WR 51%, n 2358) | -3.3 (z 1.1, WR 51%, n 1037) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | -10.2 (z -0.6, WR 50%, n 22091) | -10.2 (z -0.4, WR 50%, n 9599) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | -10.9 (z -1.3, WR 51%, n 8920) | -10.6 (z -0.6, WR 51%, n 3853) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | -13.7 (z -1.8, WR 51%, n 3631) | -13.7 (z -1.3, WR 52%, n 1576) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | -24.4 (z -3.3, WR 49%, n 2354) | -21.8 (z -1.9, WR 49%, n 1030) |

### XRP (metrics rows 471214)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | -10.8 (z -1.9, WR 51%, n 14672) | -10.8 (z -1.2, WR 52%, n 4950) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | -11.5 (z -1.5, WR 51%, n 6259) | -11.8 (z -1.0, WR 52%, n 2104) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | -15.9 (z -2.0, WR 52%, n 2763) | -12.7 (z -0.6, WR 53%, n 936) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | -19.1 (z -1.5, WR 51%, n 1886) | -12.9 (z -0.3, WR 51%, n 663) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | -10.6 (z -1.6, WR 49%, n 9420) | -10.5 (z -1.0, WR 49%, n 4524) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | -11.2 (z -1.3, WR 50%, n 4333) | -11.4 (z -0.9, WR 50%, n 1943) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | -11.5 (z -0.6, WR 51%, n 2165) | -12.4 (z -0.7, WR 53%, n 873) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | -11.4 (z -0.3, WR 49%, n 1601) | -18.6 (z -1.3, WR 45%, n 621) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | -8.8 (z 3.9, WR 53%, n 14992) | -8.7 (z 2.8, WR 52%, n 5022) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | -7.2 (z 3.4, WR 54%, n 6303) | -6.8 (z 2.4, WR 52%, n 2137) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | -1.0 (z 3.7, WR 56%, n 2707) | -1.1 (z 2.0, WR 54%, n 957) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | +5.0 (z 2.8, WR 53%, n 1952) | +4.6 (z 1.6, WR 51%, n 702) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | -10.4 (z -0.8, WR 49%, n 8766) | -10.5 (z -1.0, WR 51%, n 4234) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | -11.3 (z -1.3, WR 49%, n 4015) | -11.4 (z -1.0, WR 50%, n 1839) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | -15.4 (z -1.6, WR 48%, n 2051) | -10.8 (z -0.2, WR 49%, n 865) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | -24.5 (z -2.4, WR 48%, n 1531) | -22.7 (z -1.4, WR 50%, n 618) |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | -10.0 (z -0.4, WR 47%, n 24342) | -9.7 (z 1.6, WR 49%, n 9561) |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | -10.2 (z -0.8, WR 48%, n 20783) | -9.5 (z 1.3, WR 49%, n 8149) |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | -9.8 (z 0.4, WR 49%, n 13399) | -9.3 (z 0.7, WR 50%, n 5355) |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | -10.5 (z -0.3, WR 49%, n 6120) | -11.4 (z -0.4, WR 48%, n 2478) |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | -10.0 (z 0.4, WR 47%, n 24342) | -10.3 (z -1.6, WR 49%, n 9561) |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | -9.8 (z 0.8, WR 49%, n 20783) | -10.5 (z -1.4, WR 50%, n 8149) |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | -10.2 (z -0.4, WR 49%, n 13399) | -10.7 (z -0.7, WR 50%, n 5355) |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | -9.5 (z 0.3, WR 51%, n 6120) | -8.6 (z 0.4, WR 52%, n 2478) |
| taker buy/sell < p05 -> LONG (fade), hold 5m | -10.0 (z 0.1, WR 48%, n 24186) | -10.4 (z -2.4, WR 48%, n 9487) |
| taker buy/sell < p05 -> LONG (fade), hold 15m | -9.9 (z 0.3, WR 50%, n 20721) | -10.6 (z -1.7, WR 49%, n 8130) |
| taker buy/sell < p05 -> LONG (fade), hold 60m | -10.3 (z -0.7, WR 50%, n 13481) | -10.8 (z -1.0, WR 50%, n 5424) |
| taker buy/sell < p05 -> LONG (fade), hold 240m | -11.3 (z -0.7, WR 49%, n 6112) | -14.0 (z -1.4, WR 49%, n 2493) |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | -10.0 (z -0.1, WR 46%, n 24186) | -9.6 (z 2.3, WR 49%, n 9487) |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | -10.1 (z -0.3, WR 47%, n 20721) | -9.4 (z 1.7, WR 50%, n 8130) |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | -9.7 (z 0.6, WR 48%, n 13481) | -9.2 (z 1.0, WR 50%, n 5424) |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | -8.7 (z 0.7, WR 50%, n 6112) | -6.0 (z 1.4, WR 50%, n 2493) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | -10.4 (z -3.0, WR 47%, n 60093) | -10.2 (z -1.2, WR 49%, n 21005) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | -11.2 (z -3.1, WR 47%, n 20420) | -10.6 (z -1.3, WR 49%, n 7137) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | -14.6 (z -3.0, WR 48%, n 5365) | -12.6 (z -1.5, WR 49%, n 1877) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | -27.5 (z -3.2, WR 49%, n 1505) | -17.3 (z -1.1, WR 52%, n 533) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | -9.7 (z 1.5, WR 49%, n 35021) | -9.8 (z 0.6, WR 49%, n 16245) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | -9.2 (z 1.4, WR 50%, n 11945) | -9.3 (z 0.6, WR 49%, n 5533) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | -6.5 (z 1.5, WR 51%, n 3200) | -6.7 (z 0.7, WR 50%, n 1481) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | +3.7 (z 1.7, WR 52%, n 919) | +4.1 (z 0.9, WR 51%, n 424) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | -9.3 (z 3.2, WR 50%, n 22476) | -9.7 (z 1.0, WR 50%, n 9516) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | -7.9 (z 3.2, WR 51%, n 8889) | -8.9 (z 1.1, WR 50%, n 3755) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | -3.5 (z 3.3, WR 53%, n 3436) | -5.9 (z 1.4, WR 51%, n 1439) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | +1.1 (z 2.4, WR 51%, n 2225) | -5.8 (z 0.6, WR 50%, n 971) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | -10.4 (z -1.3, WR 48%, n 22551) | -10.5 (z -1.0, WR 50%, n 9477) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | -11.5 (z -1.8, WR 48%, n 9021) | -11.5 (z -1.0, WR 49%, n 3778) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | -15.6 (z -2.4, WR 48%, n 3551) | -15.7 (z -1.4, WR 49%, n 1474) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | -23.3 (z -2.8, WR 49%, n 2232) | -14.7 (z -0.6, WR 52%, n 947) |

### DOGE (metrics rows 470926)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | -9.2 (z 2.1, WR 53%, n 15577) | -9.5 (z 1.1, WR 52%, n 5177) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | -7.7 (z 2.6, WR 54%, n 6559) | -7.6 (z 1.8, WR 54%, n 2209) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | -6.5 (z 1.3, WR 54%, n 2791) | -6.0 (z 1.0, WR 53%, n 973) |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | -11.0 (z -0.2, WR 51%, n 1887) | -10.6 (z -0.1, WR 51%, n 695) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | -9.6 (z 0.9, WR 50%, n 8437) | -10.4 (z -0.7, WR 49%, n 4152) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | -9.3 (z 0.6, WR 49%, n 3973) | -11.6 (z -0.9, WR 47%, n 1831) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | -5.5 (z 1.5, WR 51%, n 2069) | -14.5 (z -1.0, WR 47%, n 862) |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | -0.5 (z 1.6, WR 51%, n 1549) | -11.3 (z -0.2, WR 49%, n 637) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | -8.7 (z 4.0, WR 52%, n 15674) | -9.3 (z 1.3, WR 51%, n 5419) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | -6.4 (z 3.8, WR 54%, n 6596) | -8.9 (z 0.8, WR 52%, n 2285) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | -1.6 (z 3.4, WR 54%, n 2839) | -7.2 (z 0.8, WR 51%, n 1012) |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | +5.7 (z 3.2, WR 56%, n 2050) | -7.2 (z 0.4, WR 52%, n 756) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | -10.3 (z -0.7, WR 50%, n 8220) | -10.0 (z -0.1, WR 51%, n 3786) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | -11.3 (z -1.2, WR 51%, n 3840) | -10.6 (z -0.4, WR 53%, n 1677) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | -14.2 (z -1.5, WR 48%, n 1985) | -12.0 (z -0.5, WR 51%, n 794) |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | -20.2 (z -1.7, WR 46%, n 1506) | -14.1 (z -0.5, WR 49%, n 612) |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | -10.0 (z 0.3, WR 48%, n 24418) | -9.9 (z 0.5, WR 48%, n 9434) |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | -10.3 (z -1.1, WR 48%, n 21029) | -10.0 (z 0.0, WR 47%, n 8190) |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | -10.6 (z -0.8, WR 49%, n 13753) | -10.3 (z -0.3, WR 49%, n 5472) |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | -11.4 (z -0.7, WR 49%, n 6256) | -13.6 (z -1.1, WR 48%, n 2507) |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | -10.0 (z -0.4, WR 49%, n 24418) | -10.1 (z -0.6, WR 49%, n 9434) |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | -9.7 (z 1.2, WR 50%, n 21029) | -10.0 (z -0.0, WR 51%, n 8190) |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | -9.4 (z 0.8, WR 50%, n 13753) | -9.7 (z 0.3, WR 50%, n 5472) |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | -8.6 (z 0.7, WR 50%, n 6256) | -6.4 (z 1.1, WR 51%, n 2507) |
| taker buy/sell < p05 -> LONG (fade), hold 5m | -10.0 (z -0.3, WR 50%, n 24300) | -10.5 (z -2.2, WR 49%, n 9394) |
| taker buy/sell < p05 -> LONG (fade), hold 15m | -9.8 (z 0.6, WR 51%, n 20936) | -10.4 (z -1.0, WR 50%, n 8132) |
| taker buy/sell < p05 -> LONG (fade), hold 60m | -9.8 (z 0.4, WR 51%, n 13778) | -8.7 (z 1.5, WR 51%, n 5491) |
| taker buy/sell < p05 -> LONG (fade), hold 240m | -9.0 (z 0.5, WR 50%, n 6260) | -7.4 (z 0.9, WR 50%, n 2535) |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | -10.0 (z 0.3, WR 47%, n 24300) | -9.5 (z 2.2, WR 48%, n 9394) |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | -10.2 (z -0.5, WR 47%, n 20936) | -9.6 (z 1.0, WR 48%, n 8132) |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | -10.2 (z -0.4, WR 48%, n 13778) | -11.3 (z -1.4, WR 48%, n 5491) |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | -11.0 (z -0.5, WR 49%, n 6260) | -12.6 (z -0.9, WR 49%, n 2535) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | -10.2 (z -1.5, WR 47%, n 57895) | -9.9 (z 0.1, WR 48%, n 17953) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | -10.6 (z -1.5, WR 48%, n 19646) | -9.9 (z 0.2, WR 49%, n 6099) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | -12.1 (z -1.3, WR 47%, n 5170) | -11.4 (z -0.6, WR 49%, n 1621) |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | -16.2 (z -1.0, WR 48%, n 1450) | -16.0 (z -0.6, WR 49%, n 464) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | -9.7 (z 1.5, WR 49%, n 34211) | -9.3 (z 1.7, WR 50%, n 13897) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | -8.8 (z 1.6, WR 50%, n 11679) | -7.5 (z 1.6, WR 49%, n 4768) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | -6.0 (z 1.5, WR 50%, n 3114) | -1.5 (z 1.5, WR 51%, n 1295) |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | +0.3 (z 1.0, WR 50%, n 899) | +11.9 (z 1.1, WR 51%, n 393) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | -9.9 (z 0.2, WR 50%, n 22842) | -10.6 (z -0.9, WR 50%, n 9491) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | -9.2 (z 1.1, WR 51%, n 9007) | -10.4 (z -0.3, WR 51%, n 3726) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | -8.8 (z 0.6, WR 50%, n 3444) | -11.6 (z -0.5, WR 50%, n 1433) |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | -7.9 (z 0.5, WR 50%, n 2282) | -13.0 (z -0.5, WR 48%, n 975) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | -10.1 (z -0.2, WR 49%, n 22388) | -10.4 (z -0.6, WR 49%, n 9399) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | -10.1 (z -0.1, WR 50%, n 8932) | -11.4 (z -0.8, WR 50%, n 3732) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | -8.9 (z 0.6, WR 50%, n 3540) | -8.7 (z 0.5, WR 50%, n 1471) |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | -13.1 (z -0.6, WR 48%, n 2258) | -11.1 (z -0.2, WR 50%, n 959) |

## B. Order-book depth imbalance (bookDepth ~30 s snapshots, notional in bands); imb_k = (bid_k - ask_k)/(bid_k + ask_k), sampled at the 5m bar close


### BTC (depth rows 3854903, 5m rows 390766; first 2023-01-01)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| imb±1% > p90 -> LONG, hold 5m | -9.7 (z 3.8, WR 53%, n 40741) | -9.9 (z 0.7, WR 51%, n 19746) |
| imb±1% > p90 -> LONG, hold 15m | -9.3 (z 3.3, WR 55%, n 18216) | -9.7 (z 1.1, WR 53%, n 8541) |
| imb±1% > p90 -> LONG, hold 60m | -8.0 (z 2.9, WR 56%, n 7390) | -8.6 (z 1.5, WR 53%, n 3320) |
| imb±1% > p90 -> LONG, hold 240m | -6.1 (z 2.0, WR 54%, n 3213) | -9.2 (z 0.3, WR 52%, n 1412) |
| imb±1% < p10 -> SHORT, hold 5m | -9.8 (z 2.1, WR 53%, n 40300) | -9.8 (z 1.9, WR 53%, n 19816) |
| imb±1% < p10 -> SHORT, hold 15m | -9.5 (z 2.4, WR 54%, n 17763) | -9.5 (z 2.0, WR 54%, n 8333) |
| imb±1% < p10 -> SHORT, hold 60m | -9.2 (z 1.1, WR 55%, n 7114) | -7.8 (z 2.2, WR 54%, n 3132) |
| imb±1% < p10 -> SHORT, hold 240m | -10.7 (z -0.3, WR 54%, n 3079) | -7.1 (z 1.0, WR 55%, n 1306) |
| imb±1% > p90 -> SHORT (fade), hold 5m | -10.3 (z -4.0, WR 47%, n 40741) | -10.1 (z -0.8, WR 48%, n 19746) |
| imb±1% > p90 -> SHORT (fade), hold 15m | -10.7 (z -3.2, WR 45%, n 18216) | -10.3 (z -1.1, WR 47%, n 8541) |
| imb±1% > p90 -> SHORT (fade), hold 60m | -12.0 (z -2.9, WR 44%, n 7390) | -11.4 (z -1.5, WR 47%, n 3320) |
| imb±1% > p90 -> SHORT (fade), hold 240m | -13.9 (z -1.9, WR 46%, n 3213) | -10.8 (z -0.3, WR 48%, n 1412) |
| imb±1% < p10 -> LONG (fade), hold 5m | -10.2 (z -2.1, WR 47%, n 40300) | -10.2 (z -1.9, WR 47%, n 19816) |
| imb±1% < p10 -> LONG (fade), hold 15m | -10.5 (z -2.3, WR 45%, n 17763) | -10.5 (z -1.9, WR 46%, n 8333) |
| imb±1% < p10 -> LONG (fade), hold 60m | -10.8 (z -1.1, WR 45%, n 7114) | -12.2 (z -2.2, WR 46%, n 3132) |
| imb±1% < p10 -> LONG (fade), hold 240m | -9.3 (z 0.3, WR 46%, n 3079) | -12.9 (z -0.9, WR 45%, n 1306) |
| imb±2% > p90 -> LONG, hold 5m | -9.6 (z 4.6, WR 53%, n 41582) | -9.8 (z 2.0, WR 52%, n 19247) |
| imb±2% > p90 -> LONG, hold 15m | -9.1 (z 3.8, WR 54%, n 16989) | -9.4 (z 1.9, WR 53%, n 7703) |
| imb±2% > p90 -> LONG, hold 60m | -8.2 (z 2.4, WR 56%, n 6108) | -8.6 (z 1.3, WR 53%, n 2699) |
| imb±2% > p90 -> LONG, hold 240m | -4.6 (z 2.3, WR 57%, n 2434) | -7.6 (z 0.7, WR 53%, n 1059) |
| imb±2% < p10 -> SHORT, hold 5m | -9.7 (z 3.7, WR 53%, n 41217) | -9.8 (z 2.2, WR 52%, n 19964) |
| imb±2% < p10 -> SHORT, hold 15m | -9.3 (z 2.9, WR 54%, n 16783) | -9.4 (z 2.2, WR 53%, n 7800) |
| imb±2% < p10 -> SHORT, hold 60m | -8.3 (z 2.2, WR 56%, n 6025) | -7.7 (z 2.1, WR 54%, n 2652) |
| imb±2% < p10 -> SHORT, hold 240m | -8.3 (z 0.8, WR 54%, n 2429) | -4.1 (z 1.8, WR 54%, n 1046) |
| imb±2% > p90 -> SHORT (fade), hold 5m | -10.4 (z -4.6, WR 47%, n 41582) | -10.2 (z -1.9, WR 48%, n 19247) |
| imb±2% > p90 -> SHORT (fade), hold 15m | -10.9 (z -3.8, WR 46%, n 16989) | -10.6 (z -2.0, WR 47%, n 7703) |
| imb±2% > p90 -> SHORT (fade), hold 60m | -11.8 (z -2.5, WR 44%, n 6108) | -11.4 (z -1.3, WR 47%, n 2699) |
| imb±2% > p90 -> SHORT (fade), hold 240m | -15.4 (z -2.3, WR 43%, n 2434) | -12.4 (z -0.7, WR 47%, n 1059) |
| imb±2% < p10 -> LONG (fade), hold 5m | -10.3 (z -3.7, WR 47%, n 41217) | -10.2 (z -2.2, WR 47%, n 19964) |
| imb±2% < p10 -> LONG (fade), hold 15m | -10.7 (z -2.9, WR 46%, n 16783) | -10.6 (z -2.2, WR 47%, n 7800) |
| imb±2% < p10 -> LONG (fade), hold 60m | -11.7 (z -2.3, WR 44%, n 6025) | -12.3 (z -2.1, WR 46%, n 2652) |
| imb±2% < p10 -> LONG (fade), hold 240m | -11.7 (z -0.8, WR 46%, n 2429) | -15.9 (z -1.7, WR 46%, n 1046) |
| imb±5% > p90 -> LONG, hold 5m | -9.7 (z 4.0, WR 51%, n 44303) | -9.8 (z 1.7, WR 51%, n 19704) |
| imb±5% > p90 -> LONG, hold 15m | -9.1 (z 3.8, WR 52%, n 16400) | -9.4 (z 1.6, WR 51%, n 7396) |
| imb±5% > p90 -> LONG, hold 60m | -7.9 (z 2.8, WR 53%, n 5042) | -9.0 (z 0.8, WR 52%, n 2333) |
| imb±5% > p90 -> LONG, hold 240m | -1.7 (z 3.1, WR 56%, n 1741) | -5.5 (z 1.2, WR 55%, n 831) |
| imb±5% < p10 -> SHORT, hold 5m | -9.7 (z 3.9, WR 52%, n 44717) | -9.7 (z 2.7, WR 52%, n 23043) |
| imb±5% < p10 -> SHORT, hold 15m | -9.2 (z 3.5, WR 52%, n 16462) | -9.4 (z 2.3, WR 52%, n 8457) |
| imb±5% < p10 -> SHORT, hold 60m | -7.3 (z 3.2, WR 53%, n 5022) | -7.2 (z 2.6, WR 53%, n 2562) |
| imb±5% < p10 -> SHORT, hold 240m | -6.1 (z 1.5, WR 54%, n 1734) | -3.7 (z 1.7, WR 54%, n 874) |
| imb±5% > p90 -> SHORT (fade), hold 5m | -10.3 (z -4.0, WR 48%, n 44303) | -10.2 (z -1.7, WR 49%, n 19704) |
| imb±5% > p90 -> SHORT (fade), hold 15m | -10.9 (z -3.8, WR 48%, n 16400) | -10.6 (z -1.6, WR 49%, n 7396) |
| imb±5% > p90 -> SHORT (fade), hold 60m | -12.1 (z -2.7, WR 47%, n 5042) | -11.0 (z -0.9, WR 48%, n 2333) |
| imb±5% > p90 -> SHORT (fade), hold 240m | -18.3 (z -3.1, WR 44%, n 1741) | -14.5 (z -1.2, WR 45%, n 831) |
| imb±5% < p10 -> LONG (fade), hold 5m | -10.3 (z -3.9, WR 48%, n 44717) | -10.3 (z -2.7, WR 48%, n 23043) |
| imb±5% < p10 -> LONG (fade), hold 15m | -10.8 (z -3.4, WR 48%, n 16462) | -10.6 (z -2.3, WR 47%, n 8457) |
| imb±5% < p10 -> LONG (fade), hold 60m | -12.7 (z -3.3, WR 46%, n 5022) | -12.8 (z -2.6, WR 47%, n 2562) |
| imb±5% < p10 -> LONG (fade), hold 240m | -13.9 (z -1.5, WR 46%, n 1734) | -16.3 (z -1.7, WR 46%, n 874) |
| imb1 15m rise > p95 -> LONG, hold 5m | -9.4 (z 3.5, WR 53%, n 20279) | -9.6 (z 2.4, WR 52%, n 9859) |
| imb1 15m rise > p95 -> LONG, hold 15m | -9.1 (z 3.0, WR 53%, n 12735) | -9.6 (z 1.2, WR 52%, n 6037) |
| imb1 15m rise > p95 -> LONG, hold 60m | -8.5 (z 2.4, WR 52%, n 8676) | -8.8 (z 1.5, WR 52%, n 3987) |
| imb1 15m rise > p95 -> LONG, hold 240m | -6.3 (z 2.1, WR 51%, n 4203) | -7.9 (z 0.9, WR 50%, n 1941) |
| imb1 15m fall < p05 -> SHORT, hold 5m | -9.8 (z 1.6, WR 52%, n 20286) | -10.0 (z -0.3, WR 52%, n 9861) |
| imb1 15m fall < p05 -> SHORT, hold 15m | -9.5 (z 1.7, WR 51%, n 12711) | -9.8 (z 0.6, WR 51%, n 6015) |
| imb1 15m fall < p05 -> SHORT, hold 60m | -10.4 (z -0.7, WR 51%, n 8761) | -11.1 (z -1.2, WR 50%, n 4011) |
| imb1 15m fall < p05 -> SHORT, hold 240m | -11.7 (z -1.0, WR 49%, n 4241) | -10.9 (z -0.4, WR 48%, n 1958) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 5m | -10.3 (z -1.1, WR 51%, n 5918) | -10.3 (z -1.4, WR 49%, n 3271) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 15m | -10.3 (z -0.9, WR 52%, n 4605) | -10.5 (z -1.2, WR 51%, n 2443) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 60m | -9.7 (z 0.3, WR 54%, n 2859) | -11.5 (z -1.3, WR 52%, n 1451) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 240m | -9.6 (z 0.1, WR 54%, n 1624) | -13.6 (z -1.0, WR 51%, n 789) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 5m | -9.8 (z 1.1, WR 52%, n 5951) | -9.7 (z 0.7, WR 51%, n 3252) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 15m | -9.9 (z 0.3, WR 53%, n 4577) | -9.8 (z 0.5, WR 51%, n 2400) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 60m | -10.3 (z -0.4, WR 53%, n 2786) | -9.2 (z 0.8, WR 52%, n 1373) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 240m | -13.3 (z -1.3, WR 52%, n 1549) | -11.6 (z -0.5, WR 51%, n 724) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 5m | -9.8 (z 0.6, WR 52%, n 4817) | -10.5 (z -1.1, WR 49%, n 2222) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 15m | -9.0 (z 1.5, WR 54%, n 2472) | -10.6 (z -0.6, WR 51%, n 1077) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 60m | -6.6 (z 1.8, WR 56%, n 1312) | -11.0 (z -0.3, WR 52%, n 538) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 240m | -3.0 (z 1.8, WR 57%, n 921) | -10.3 (z -0.0, WR 54%, n 379) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 5m | -9.8 (z 1.0, WR 54%, n 6937) | -9.5 (z 1.9, WR 55%, n 3331) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 15m | -9.7 (z 0.6, WR 54%, n 3326) | -9.7 (z 0.5, WR 53%, n 1535) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 60m | -11.6 (z -1.0, WR 54%, n 1610) | -11.8 (z -0.8, WR 53%, n 707) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 240m | -20.3 (z -2.8, WR 52%, n 1027) | -11.0 (z -0.2, WR 52%, n 448) |

### ETH (depth rows 3857784, 5m rows 391054; first 2023-01-01)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| imb±1% > p90 -> LONG, hold 5m | -9.7 (z 2.6, WR 54%, n 41444) | -9.9 (z 0.6, WR 53%, n 20386) |
| imb±1% > p90 -> LONG, hold 15m | -9.4 (z 2.3, WR 55%, n 19685) | -9.9 (z 0.2, WR 55%, n 9561) |
| imb±1% > p90 -> LONG, hold 60m | -8.9 (z 1.3, WR 54%, n 8440) | -9.9 (z 0.1, WR 53%, n 4008) |
| imb±1% > p90 -> LONG, hold 240m | -7.3 (z 1.2, WR 54%, n 3642) | -9.7 (z 0.1, WR 54%, n 1695) |
| imb±1% < p10 -> SHORT, hold 5m | -9.8 (z 2.4, WR 53%, n 43520) | -9.7 (z 1.9, WR 52%, n 22507) |
| imb±1% < p10 -> SHORT, hold 15m | -9.7 (z 1.2, WR 54%, n 20160) | -9.5 (z 1.2, WR 53%, n 10130) |
| imb±1% < p10 -> SHORT, hold 60m | -10.2 (z -0.3, WR 53%, n 8424) | -10.4 (z -0.3, WR 51%, n 4022) |
| imb±1% < p10 -> SHORT, hold 240m | -14.4 (z -1.8, WR 50%, n 3624) | -13.6 (z -0.9, WR 51%, n 1689) |
| imb±1% > p90 -> SHORT (fade), hold 5m | -10.3 (z -2.6, WR 46%, n 41444) | -10.1 (z -0.7, WR 47%, n 20386) |
| imb±1% > p90 -> SHORT (fade), hold 15m | -10.6 (z -2.3, WR 45%, n 19685) | -10.1 (z -0.2, WR 45%, n 9561) |
| imb±1% > p90 -> SHORT (fade), hold 60m | -11.1 (z -1.3, WR 45%, n 8440) | -10.1 (z -0.1, WR 47%, n 4008) |
| imb±1% > p90 -> SHORT (fade), hold 240m | -12.7 (z -1.2, WR 46%, n 3642) | -10.3 (z -0.1, WR 46%, n 1695) |
| imb±1% < p10 -> LONG (fade), hold 5m | -10.2 (z -2.5, WR 47%, n 43520) | -10.3 (z -1.8, WR 47%, n 22507) |
| imb±1% < p10 -> LONG (fade), hold 15m | -10.3 (z -1.2, WR 46%, n 20160) | -10.5 (z -1.3, WR 47%, n 10130) |
| imb±1% < p10 -> LONG (fade), hold 60m | -9.8 (z 0.3, WR 47%, n 8424) | -9.6 (z 0.3, WR 49%, n 4022) |
| imb±1% < p10 -> LONG (fade), hold 240m | -5.6 (z 1.9, WR 50%, n 3624) | -6.4 (z 0.9, WR 49%, n 1689) |
| imb±2% > p90 -> LONG, hold 5m | -9.8 (z 2.2, WR 53%, n 41637) | -9.8 (z 0.9, WR 53%, n 19967) |
| imb±2% > p90 -> LONG, hold 15m | -9.4 (z 2.1, WR 55%, n 18202) | -9.5 (z 1.2, WR 54%, n 8502) |
| imb±2% > p90 -> LONG, hold 60m | -7.9 (z 2.3, WR 56%, n 7044) | -7.6 (z 1.7, WR 55%, n 3198) |
| imb±2% > p90 -> LONG, hold 240m | -6.2 (z 1.3, WR 56%, n 2892) | -9.3 (z 0.1, WR 54%, n 1305) |
| imb±2% < p10 -> SHORT, hold 5m | -9.9 (z 1.4, WR 53%, n 42672) | -9.9 (z 0.8, WR 52%, n 21469) |
| imb±2% < p10 -> SHORT, hold 15m | -9.9 (z 0.4, WR 54%, n 18497) | -9.9 (z 0.4, WR 53%, n 9004) |
| imb±2% < p10 -> SHORT, hold 60m | -10.6 (z -0.6, WR 53%, n 6987) | -11.1 (z -0.8, WR 52%, n 3243) |
| imb±2% < p10 -> SHORT, hold 240m | -14.0 (z -1.5, WR 51%, n 2869) | -13.8 (z -0.9, WR 51%, n 1320) |
| imb±2% > p90 -> SHORT (fade), hold 5m | -10.2 (z -2.2, WR 46%, n 41637) | -10.2 (z -1.0, WR 47%, n 19967) |
| imb±2% > p90 -> SHORT (fade), hold 15m | -10.6 (z -2.2, WR 45%, n 18202) | -10.5 (z -1.2, WR 46%, n 8502) |
| imb±2% > p90 -> SHORT (fade), hold 60m | -12.1 (z -2.4, WR 44%, n 7044) | -12.4 (z -1.7, WR 45%, n 3198) |
| imb±2% > p90 -> SHORT (fade), hold 240m | -13.8 (z -1.4, WR 44%, n 2892) | -10.7 (z -0.1, WR 46%, n 1305) |
| imb±2% < p10 -> LONG (fade), hold 5m | -10.1 (z -1.5, WR 47%, n 42672) | -10.1 (z -0.8, WR 48%, n 21469) |
| imb±2% < p10 -> LONG (fade), hold 15m | -10.1 (z -0.4, WR 46%, n 18497) | -10.1 (z -0.4, WR 47%, n 9004) |
| imb±2% < p10 -> LONG (fade), hold 60m | -9.4 (z 0.6, WR 47%, n 6987) | -8.9 (z 0.7, WR 48%, n 3243) |
| imb±2% < p10 -> LONG (fade), hold 240m | -6.0 (z 1.5, WR 49%, n 2869) | -6.2 (z 0.9, WR 49%, n 1320) |
| imb±5% > p90 -> LONG, hold 5m | -9.7 (z 3.3, WR 52%, n 45225) | -9.8 (z 1.5, WR 51%, n 21092) |
| imb±5% > p90 -> LONG, hold 15m | -9.1 (z 3.0, WR 53%, n 17054) | -9.8 (z 0.5, WR 52%, n 7877) |
| imb±5% > p90 -> LONG, hold 60m | -7.9 (z 2.1, WR 55%, n 5460) | -8.8 (z 0.7, WR 53%, n 2509) |
| imb±5% > p90 -> LONG, hold 240m | -6.8 (z 1.0, WR 55%, n 1958) | -11.0 (z -0.2, WR 52%, n 903) |
| imb±5% < p10 -> SHORT, hold 5m | -9.8 (z 1.5, WR 51%, n 41595) | -9.9 (z 0.8, WR 51%, n 19910) |
| imb±5% < p10 -> SHORT, hold 15m | -9.7 (z 1.1, WR 52%, n 15689) | -9.7 (z 0.7, WR 52%, n 7516) |
| imb±5% < p10 -> SHORT, hold 60m | -8.9 (z 1.0, WR 53%, n 5003) | -7.9 (z 1.2, WR 52%, n 2414) |
| imb±5% < p10 -> SHORT, hold 240m | -11.0 (z -0.3, WR 52%, n 1827) | -7.5 (z 0.5, WR 52%, n 896) |
| imb±5% > p90 -> SHORT (fade), hold 5m | -10.3 (z -3.3, WR 48%, n 45225) | -10.2 (z -1.5, WR 49%, n 21092) |
| imb±5% > p90 -> SHORT (fade), hold 15m | -10.9 (z -2.9, WR 47%, n 17054) | -10.2 (z -0.5, WR 48%, n 7877) |
| imb±5% > p90 -> SHORT (fade), hold 60m | -12.1 (z -2.1, WR 45%, n 5460) | -11.2 (z -0.7, WR 47%, n 2509) |
| imb±5% > p90 -> SHORT (fade), hold 240m | -13.2 (z -1.0, WR 45%, n 1958) | -9.0 (z 0.2, WR 48%, n 903) |
| imb±5% < p10 -> LONG (fade), hold 5m | -10.2 (z -1.5, WR 48%, n 41595) | -10.1 (z -0.8, WR 49%, n 19910) |
| imb±5% < p10 -> LONG (fade), hold 15m | -10.3 (z -1.1, WR 48%, n 15689) | -10.3 (z -0.7, WR 48%, n 7516) |
| imb±5% < p10 -> LONG (fade), hold 60m | -11.1 (z -1.0, WR 47%, n 5003) | -12.1 (z -1.2, WR 48%, n 2414) |
| imb±5% < p10 -> LONG (fade), hold 240m | -9.0 (z 0.3, WR 48%, n 1827) | -12.5 (z -0.5, WR 48%, n 896) |
| imb1 15m rise > p95 -> LONG, hold 5m | -9.7 (z 1.5, WR 53%, n 20274) | -9.8 (z 0.6, WR 52%, n 9948) |
| imb1 15m rise > p95 -> LONG, hold 15m | -9.6 (z 1.3, WR 53%, n 13275) | -10.1 (z -0.3, WR 52%, n 6450) |
| imb1 15m rise > p95 -> LONG, hold 60m | -8.7 (z 1.7, WR 52%, n 9149) | -9.1 (z 0.8, WR 52%, n 4341) |
| imb1 15m rise > p95 -> LONG, hold 240m | -6.2 (z 1.8, WR 51%, n 4367) | -7.5 (z 0.7, WR 51%, n 2047) |
| imb1 15m fall < p05 -> SHORT, hold 5m | -9.5 (z 3.2, WR 52%, n 20256) | -9.0 (z 4.3, WR 53%, n 9885) |
| imb1 15m fall < p05 -> SHORT, hold 15m | -9.5 (z 1.5, WR 52%, n 13155) | -8.9 (z 2.0, WR 52%, n 6397) |
| imb1 15m fall < p05 -> SHORT, hold 60m | -10.1 (z -0.2, WR 50%, n 9121) | -9.9 (z 0.1, WR 50%, n 4301) |
| imb1 15m fall < p05 -> SHORT, hold 240m | -12.1 (z -0.9, WR 49%, n 4337) | -9.4 (z 0.2, WR 50%, n 2014) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 5m | -9.9 (z 0.3, WR 51%, n 5795) | -9.5 (z 1.5, WR 51%, n 2875) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 15m | -9.1 (z 2.1, WR 54%, n 4611) | -9.0 (z 1.5, WR 54%, n 2258) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 60m | -8.1 (z 1.8, WR 55%, n 2968) | -8.1 (z 1.1, WR 54%, n 1424) |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 240m | -4.6 (z 1.9, WR 56%, n 1724) | -7.8 (z 0.5, WR 54%, n 815) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 5m | -9.9 (z 0.6, WR 51%, n 6460) | -9.9 (z 0.2, WR 49%, n 3328) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 15m | -9.8 (z 0.5, WR 52%, n 5011) | -10.0 (z -0.1, WR 50%, n 2520) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 60m | -11.2 (z -1.1, WR 52%, n 3097) | -11.8 (z -1.1, WR 50%, n 1504) |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 240m | -13.3 (z -1.1, WR 52%, n 1791) | -11.0 (z -0.2, WR 51%, n 825) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 5m | -10.4 (z -1.1, WR 52%, n 4379) | -10.4 (z -0.7, WR 51%, n 2064) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 15m | -11.0 (z -1.0, WR 54%, n 2392) | -12.3 (z -1.4, WR 52%, n 1100) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 60m | -9.7 (z 0.1, WR 54%, n 1360) | -12.9 (z -0.7, WR 53%, n 605) |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 240m | -11.1 (z -0.2, WR 54%, n 1003) | -22.6 (z -1.5, WR 52%, n 444) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 5m | -9.8 (z 0.5, WR 54%, n 5809) | -9.8 (z 0.3, WR 53%, n 2957) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 15m | -10.3 (z -0.4, WR 55%, n 3006) | -10.1 (z -0.1, WR 54%, n 1491) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 60m | -10.1 (z -0.1, WR 54%, n 1618) | -10.2 (z -0.0, WR 52%, n 760) |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 240m | -18.8 (z -1.9, WR 51%, n 1138) | -22.4 (z -1.6, WR 48%, n 517) |

## Cells with net @10bp > 0 and z >= 2 in BOTH windows

none
