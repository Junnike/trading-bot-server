# T12c — three signal families on public Binance.vision data (spot/perp 5m, funding)

net = gross − fee; fee 10 bp taker RT unless stated; z = UTC-day cluster bootstrap of gross; trades non-overlapping.


## 1. Funding-extreme carry (perp): enter at settlement when funding is in the tail of its trailing 90-day distribution, hold N settlements, collect funding
| test | full 2020-26: net bp/trade (z, WR, n, max DD bp) | 2025-26 |
|---|---|---|
| BTC short when funding>p95, hold 8h | +8.0 (z 1.7, WR 54%, n 309, mdd -2226) | +12.0 (z 1.6, WR 47%, n 57, mdd -540) |
| BTC short when funding>p95, hold 24h | -1.7 (z 0.3, WR 54%, n 162, mdd -4074) | +18.5 (z 1.0, WR 59%, n 34, mdd -728) |
| BTC long when funding<p05, hold 8h | +13.9 (z 2.2, WR 54%, n 512, mdd -3265) | -10.9 (z -0.1, WR 51%, n 156, mdd -2516) |
| BTC long when funding<p05, hold 24h | +44.4 (z 2.7, WR 51%, n 301, mdd -6428) | -51.0 (z -1.6, WR 40%, n 95, mdd -6428) |
| ETH short when funding>p95, hold 8h | -13.1 (z -0.2, WR 51%, n 291, mdd -5530) | -46.5 (z -1.0, WR 44%, n 48, mdd -2775) |
| ETH short when funding>p95, hold 24h | -30.1 (z -0.5, WR 50%, n 153, mdd -6405) | -109.9 (z -1.0, WR 54%, n 28, mdd -3473) |
| ETH long when funding<p05, hold 8h | -3.2 (z 0.5, WR 54%, n 459, mdd -6646) | -40.9 (z -1.5, WR 46%, n 136, mdd -6646) |
| ETH long when funding<p05, hold 24h | +23.4 (z 1.2, WR 55%, n 284, mdd -5957) | -41.4 (z -0.8, WR 49%, n 88, mdd -5957) |
| SOL short when funding>p95, hold 8h | -76.6 (z -2.3, WR 50%, n 233, mdd -21623) | n/a |
| SOL short when funding>p95, hold 24h | -135.7 (z -1.7, WR 53%, n 120, mdd -18405) | n/a |
| SOL long when funding<p05, hold 8h | -6.4 (z 0.1, WR 54%, n 429, mdd -11337) | -5.3 (z 0.2, WR 54%, n 117, mdd -3774) |
| SOL long when funding<p05, hold 24h | +12.6 (z 0.5, WR 53%, n 256, mdd -10305) | -39.8 (z -0.6, WR 51%, n 79, mdd -5218) |
| XRP short when funding>p95, hold 8h | -52.2 (z -1.8, WR 51%, n 335, mdd -19225) | +26.0 (z 1.7, WR 58%, n 38, mdd -327) |
| XRP short when funding>p95, hold 24h | -136.2 (z -2.3, WR 52%, n 179, mdd -28074) | +112.4 (z 2.6, WR 70%, n 30, mdd -465) |
| XRP long when funding<p05, hold 8h | +9.7 (z 1.0, WR 54%, n 444, mdd -6044) | +13.8 (z 1.0, WR 52%, n 147, mdd -3344) |
| XRP long when funding<p05, hold 24h | +42.8 (z 1.5, WR 60%, n 296, mdd -5302) | +31.0 (z 1.0, WR 58%, n 98, mdd -2285) |
| DOGE short when funding>p95, hold 8h | -89.7 (z -2.5, WR 49%, n 270, mdd -25052) | n/a |
| DOGE short when funding>p95, hold 24h | -246.6 (z -2.3, WR 53%, n 135, mdd -34253) | n/a |
| DOGE long when funding<p05, hold 8h | +19.8 (z 1.1, WR 55%, n 371, mdd -5258) | -5.2 (z 0.2, WR 58%, n 101, mdd -1857) |
| DOGE long when funding<p05, hold 24h | +40.2 (z 1.0, WR 55%, n 239, mdd -7679) | -1.2 (z 0.2, WR 48%, n 66, mdd -2101) |

## 2. BTC→alt lead-lag (spot 5m): BTC 5m return beyond ±thr → trade alt in same direction at next 5m open, hold H bars
| test | full 2020-26: net bp/trade (z, WR, n, max DD bp) | 2025-26 |
|---|---|---|
| ETH BTC > +0.5% → long, hold 5m | -9.9 (z 0.1, WR 46%, n 8637, mdd -85798) | -9.1 (z 0.5, WR 46%, n 947, mdd -8663) |
| ETH BTC < -0.5% → short, hold 5m | -12.7 (z -3.9, WR 44%, n 8543, mdd -108775) | -8.7 (z 0.6, WR 46%, n 861, mdd -7461) |
| ETH BTC > +0.5% → long, hold 15m | -7.0 (z 2.8, WR 49%, n 7206, mdd -50931) | -9.4 (z 0.2, WR 45%, n 824, mdd -8195) |
| ETH BTC < -0.5% → short, hold 15m | -11.8 (z -1.8, WR 46%, n 7106, mdd -84752) | -8.2 (z 0.6, WR 45%, n 730, mdd -6270) |
| ETH BTC > +1.0% → long, hold 5m | -10.1 (z -0.0, WR 46%, n 1399, mdd -15708) | -3.9 (z 1.0, WR 45%, n 102, mdd -988) |
| ETH BTC < -1.0% → short, hold 5m | -16.5 (z -2.3, WR 45%, n 1354, mdd -23861) | -10.6 (z -0.1, WR 39%, n 84, mdd -1242) |
| ETH BTC > +1.0% → long, hold 15m | -2.2 (z 2.2, WR 49%, n 1241, mdd -6875) | -3.4 (z 0.5, WR 48%, n 95, mdd -1432) |
| ETH BTC < -1.0% → short, hold 15m | -21.0 (z -2.8, WR 43%, n 1183, mdd -25857) | -17.3 (z -0.5, WR 44%, n 77, mdd -1290) |
| SOL BTC > +0.5% → long, hold 5m | -8.4 (z 1.6, WR 48%, n 7593, mdd -66814) | -9.1 (z 0.5, WR 46%, n 947, mdd -8842) |
| SOL BTC < -0.5% → short, hold 5m | -15.0 (z -4.5, WR 45%, n 7465, mdd -115004) | -8.3 (z 0.5, WR 46%, n 861, mdd -7274) |
| SOL BTC > +0.5% → long, hold 15m | -2.4 (z 4.8, WR 50%, n 6371, mdd -31347) | -8.2 (z 0.5, WR 46%, n 824, mdd -7957) |
| SOL BTC < -0.5% → short, hold 15m | -19.2 (z -5.5, WR 46%, n 6236, mdd -120332) | -11.4 (z -0.3, WR 46%, n 730, mdd -8232) |
| SOL BTC > +1.0% → long, hold 5m | -8.7 (z 0.4, WR 48%, n 1154, mdd -11355) | -1.0 (z 1.2, WR 48%, n 102, mdd -1208) |
| SOL BTC < -1.0% → short, hold 5m | -24.1 (z -3.3, WR 43%, n 1064, mdd -27888) | +5.9 (z 0.8, WR 45%, n 84, mdd -1509) |
| SOL BTC > +1.0% → long, hold 15m | +4.2 (z 3.0, WR 50%, n 1041, mdd -7653) | -1.2 (z 0.6, WR 48%, n 95, mdd -1632) |
| SOL BTC < -1.0% → short, hold 15m | -42.7 (z -4.6, WR 42%, n 940, mdd -40954) | -18.2 (z -0.3, WR 44%, n 77, mdd -2242) |
| XRP BTC > +0.5% → long, hold 5m | -10.1 (z -0.1, WR 46%, n 8637, mdd -87088) | -6.7 (z 1.5, WR 48%, n 947, mdd -6756) |
| XRP BTC < -0.5% → short, hold 5m | -14.2 (z -4.1, WR 44%, n 8543, mdd -122019) | -8.3 (z 0.4, WR 47%, n 861, mdd -7364) |
| XRP BTC > +0.5% → long, hold 15m | -8.1 (z 1.5, WR 49%, n 7206, mdd -58666) | -9.6 (z 0.1, WR 47%, n 824, mdd -8943) |
| XRP BTC < -0.5% → short, hold 15m | -15.2 (z -3.7, WR 45%, n 7106, mdd -109142) | -11.5 (z -0.3, WR 46%, n 730, mdd -8592) |
| XRP BTC > +1.0% → long, hold 5m | -8.1 (z 0.7, WR 47%, n 1399, mdd -14477) | +7.9 (z 2.0, WR 54%, n 102, mdd -970) |
| XRP BTC < -1.0% → short, hold 5m | -16.8 (z -1.5, WR 44%, n 1354, mdd -28157) | +7.5 (z 0.6, WR 43%, n 84, mdd -1872) |
| XRP BTC > +1.0% → long, hold 15m | -0.6 (z 2.3, WR 50%, n 1241, mdd -5603) | +7.8 (z 0.9, WR 53%, n 95, mdd -1815) |
| XRP BTC < -1.0% → short, hold 15m | -25.5 (z -2.9, WR 42%, n 1183, mdd -33829) | -21.0 (z -0.3, WR 42%, n 77, mdd -2722) |
| DOGE BTC > +0.5% → long, hold 5m | -9.0 (z 0.9, WR 47%, n 8637, mdd -84191) | -5.0 (z 1.7, WR 48%, n 947, mdd -4826) |
| DOGE BTC < -0.5% → short, hold 5m | -12.5 (z -1.9, WR 46%, n 8543, mdd -110379) | -7.2 (z 0.6, WR 46%, n 861, mdd -7027) |
| DOGE BTC > +0.5% → long, hold 15m | -5.4 (z 2.9, WR 50%, n 7206, mdd -45869) | -9.9 (z 0.0, WR 48%, n 824, mdd -8911) |
| DOGE BTC < -0.5% → short, hold 15m | -12.5 (z -1.4, WR 46%, n 7106, mdd -92652) | -7.9 (z 0.3, WR 46%, n 730, mdd -7024) |
| DOGE BTC > +1.0% → long, hold 5m | -3.2 (z 1.4, WR 47%, n 1399, mdd -13951) | +22.6 (z 1.6, WR 47%, n 102, mdd -653) |
| DOGE BTC < -1.0% → short, hold 5m | -14.9 (z -0.9, WR 46%, n 1354, mdd -27288) | +13.5 (z 0.8, WR 42%, n 84, mdd -2558) |
| DOGE BTC > +1.0% → long, hold 15m | +8.1 (z 3.4, WR 52%, n 1241, mdd -3888) | +13.2 (z 1.1, WR 51%, n 95, mdd -1207) |
| DOGE BTC < -1.0% → short, hold 15m | -23.1 (z -2.0, WR 45%, n 1183, mdd -32384) | -11.5 (z -0.0, WR 43%, n 77, mdd -1624) |

## 3. Daily breakout (spot): close > prior N-day high → long next open; exit next open after close < prior M-day low. Fee 10 bp RT. Per-trade bp; also total return and trades/yr

| test | full: net bp/trade (z, WR, n, mdd) | 2025-26 | full total net % | trades/yr | buy&hold full % |
|---|---|---|---|---|---|
| BTC 50d high / 20d low | +1422.6 (z 1.2, WR 45%, n 20, mdd -3416) | n/a | +349% | 3.0 | +772% |
| BTC 20d high / 10d low | +1309.9 (z 1.2, WR 43%, n 35, mdd -6038) | n/a | +723% | 5.2 | +868% |
| BTC 100d high / 50d low | n/a | n/a | +618% | 1.2 | +1048% |
| ETH 50d high / 20d low | +3749.4 (z 1.4, WR 56%, n 16, mdd -4977) | n/a | +1588% | 2.4 | +939% |
| ETH 20d high / 10d low | +1257.4 (z 1.4, WR 51%, n 37, mdd -6271) | n/a | +867% | 5.5 | +1510% |
| ETH 100d high / 50d low | n/a | n/a | +1682% | 0.9 | +1484% |
| SOL 50d high / 20d low | +9913.6 (z 1.5, WR 47%, n 15, mdd -7481) | n/a | +5986% | 2.4 | +3911% |
| SOL 20d high / 10d low | +3566.8 (z 1.6, WR 41%, n 32, mdd -7299) | n/a | +5584% | 5.2 | +2577% |
| SOL 100d high / 50d low | n/a | n/a | +15798% | 0.8 | +5492% |
| XRP 50d high / 20d low | +416.1 (z 0.4, WR 37%, n 19, mdd -9795) | n/a | -19% | 2.8 | +442% |
| XRP 20d high / 10d low | +1584.2 (z 1.3, WR 39%, n 31, mdd -8974) | n/a | +585% | 4.6 | +539% |
| XRP 100d high / 50d low | n/a | n/a | +211% | 0.9 | +652% |
| DOGE 50d high / 20d low | +28115.9 (z 1.1, WR 33%, n 18, mdd -15176) | n/a | +2506% | 2.7 | +3533% |
| DOGE 20d high / 10d low | +2426.5 (z 1.7, WR 48%, n 29, mdd -5992) | n/a | +2390% | 4.3 | +3880% |
| DOGE 100d high / 50d low | n/a | n/a | +2184% | 0.9 | +4575% |
