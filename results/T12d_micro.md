# T12d — perp microstructure tests (Binance Vision metrics + bookDepth)

Enter next 5m open, exit close after hold; fee 10 bp taker RT; z = UTC-day cluster bootstrap; non-overlapping trades. Percentiles are trailing 30-day, lagged.


## A. Metrics (5m): open interest, taker buy/sell volume ratio, long/short account ratios


### BTC (metrics rows 566643)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | n/a | n/a |

### ETH (metrics rows 470933)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | n/a | n/a |

### SOL (metrics rows 470913)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | n/a | n/a |

### XRP (metrics rows 471214)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | n/a | n/a |

### DOGE (metrics rows 470926)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT, hold 240m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h down (long liquidation) -> LONG, hold 240m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 5m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 15m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 60m | n/a | n/a |
| OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT, hold 240m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> LONG (momentum), hold 240m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 5m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 15m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 60m | n/a | n/a |
| taker buy/sell > p95 -> SHORT (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> LONG (fade), hold 240m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 5m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 15m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 60m | n/a | n/a |
| taker buy/sell < p05 -> SHORT (momentum), hold 240m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio > p95 -> SHORT (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 5m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 15m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 60m | n/a | n/a |
| top-trader L/S ratio < p05 -> LONG (fade crowd), hold 240m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h rise > p95 -> LONG (follow smart money), hold 240m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 5m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 15m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 60m | n/a | n/a |
| top-trader L/S 1h fall < p05 -> SHORT (follow smart money), hold 240m | n/a | n/a |

## B. Order-book depth imbalance (bookDepth ~30 s snapshots, notional in bands); imb_k = (bid_k - ask_k)/(bid_k + ask_k), sampled at the 5m bar close


### BTC (depth rows 3854903, 5m rows 390766; first 2023-01-01)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| imb±1% > p90 -> LONG, hold 5m | n/a | n/a |
| imb±1% > p90 -> LONG, hold 15m | n/a | n/a |
| imb±1% > p90 -> LONG, hold 60m | n/a | n/a |
| imb±1% > p90 -> LONG, hold 240m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 5m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 15m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 60m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 240m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 5m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 15m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 60m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 240m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 5m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 15m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 60m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 240m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 5m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 15m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 60m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 240m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 5m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 15m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 60m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 240m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 5m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 15m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 60m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 240m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 5m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 15m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 60m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 240m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 5m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 15m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 60m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 240m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 5m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 15m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 60m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 240m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 5m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 15m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 60m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 240m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 5m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 15m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 60m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 240m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 5m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 15m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 60m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 240m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 5m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 15m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 60m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 240m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 5m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 15m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 60m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 240m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 5m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 15m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 60m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 240m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 5m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 15m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 60m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 240m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 5m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 15m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 60m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 240m | n/a | n/a |

### ETH (depth rows 3857784, 5m rows 391054; first 2023-01-01)
| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |
|---|---|---|
| imb±1% > p90 -> LONG, hold 5m | n/a | n/a |
| imb±1% > p90 -> LONG, hold 15m | n/a | n/a |
| imb±1% > p90 -> LONG, hold 60m | n/a | n/a |
| imb±1% > p90 -> LONG, hold 240m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 5m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 15m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 60m | n/a | n/a |
| imb±1% < p10 -> SHORT, hold 240m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 5m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 15m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 60m | n/a | n/a |
| imb±1% > p90 -> SHORT (fade), hold 240m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 5m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 15m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 60m | n/a | n/a |
| imb±1% < p10 -> LONG (fade), hold 240m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 5m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 15m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 60m | n/a | n/a |
| imb±2% > p90 -> LONG, hold 240m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 5m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 15m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 60m | n/a | n/a |
| imb±2% < p10 -> SHORT, hold 240m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 5m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 15m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 60m | n/a | n/a |
| imb±2% > p90 -> SHORT (fade), hold 240m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 5m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 15m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 60m | n/a | n/a |
| imb±2% < p10 -> LONG (fade), hold 240m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 5m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 15m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 60m | n/a | n/a |
| imb±5% > p90 -> LONG, hold 240m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 5m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 15m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 60m | n/a | n/a |
| imb±5% < p10 -> SHORT, hold 240m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 5m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 15m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 60m | n/a | n/a |
| imb±5% > p90 -> SHORT (fade), hold 240m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 5m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 15m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 60m | n/a | n/a |
| imb±5% < p10 -> LONG (fade), hold 240m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 5m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 15m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 60m | n/a | n/a |
| imb1 15m rise > p95 -> LONG, hold 240m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 5m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 15m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 60m | n/a | n/a |
| imb1 15m fall < p05 -> SHORT, hold 240m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 5m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 15m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 60m | n/a | n/a |
| imb±1% > p90 & taker > p80 -> LONG (book+flow agree), hold 240m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 5m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 15m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 60m | n/a | n/a |
| imb±1% < p10 & taker < p20 -> SHORT (book+flow agree), hold 240m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 5m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 15m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 60m | n/a | n/a |
| imb±1% > p90 & OI 1h chg > p90 -> LONG, hold 240m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 5m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 15m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 60m | n/a | n/a |
| imb±1% < p10 & OI 1h chg > p90 -> SHORT, hold 240m | n/a | n/a |

## Cells with net @10bp > 0 and z >= 2 in BOTH windows

none
