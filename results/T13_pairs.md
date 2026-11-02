# T13 Pairs trading (hourly Binance USDT perps)

## (a) By year, entry 2, exit 0.5, stop 4, max hold 72h

| Period | Trades | Win% (gross>0) | Gross bp | Net bp taker (20) | Net bp maker (8) | Boot z (gross) | Median hold h | Trades/day | Ann. net maker |
|---|---|---|---|---|---|---|---|---|---|
| 2022 | 644 | 56.7% | -17.58 | -37.58 | -25.58 | -0.66 | 27 | 2.34 | -10.9% |
| 2023 | 1448 | 59.0% | 10.97 | -9.03 | 2.97 | 0.73 | 22 | 3.97 | 2.2% |
| 2024 | 1395 | 57.5% | -33.08 | -53.08 | -41.08 | -1.32 | 28 | 3.81 | -28.6% |
| 2025 | 1627 | 61.1% | 24.73 | 4.73 | 16.73 | 1.72 | 23 | 4.46 | 13.6% |
| 2026 | 1144 | 55.0% | -35.73 | -55.73 | -43.73 | -2.12 | 22 | 4.19 | -33.5% |
| ALL | 6258 | 58.2% | -6.75 | -26.75 | -14.75 | -0.82 | 24 | 3.81 | -10.2% |

## (b) 2025-01-01..2026-09-30

| Period | Trades | Win% (gross>0) | Gross bp | Net bp taker (20) | Net bp maker (8) | Boot z (gross) | Median hold h | Trades/day | Ann. net maker |
|---|---|---|---|---|---|---|---|---|---|
| 2025 | 1627 | 61.1% | 24.73 | 4.73 | 16.73 | 1.74 | 23 | 4.46 | 13.6% |
| 2026 | 1144 | 55.0% | -35.73 | -55.73 | -43.73 | -2.17 | 22 | 4.19 | -33.5% |
| ALL | 2771 | 58.6% | -0.23 | -20.23 | -8.23 | -0.01 | 23 | 4.34 | -6.5% |

## (c) Sensitivity (ALL period)

| Variant | Trades | Net bp maker (ALL) | Boot z (gross) |
|---|---|---|---|
| entry 1.5 | 8716 | -10.21 | -0.31 |
| entry 2.5 | 4682 | -5.95 | 0.21 |
| max hold 24h | 8382 | -11.47 | -0.64 |
| max hold 168h | 5878 | -17.33 | -0.92 |
| universe 30 | 3537 | -16.45 | -0.96 |
| universe 100 | 9648 | -4.42 | 0.55 |

## (d)

**Verdict: DEAD** - full period net maker -14.75 bp/trade, gross z -0.82; 2025-26 net maker -8.23 bp/trade, gross z -0.01 (taker net -26.75 / -20.23).

Notes: universe = top-50 by whole-sample mean quote volume after dropping symbols with >5% NaN in 2024-01..2026-09 (selection uses full-sample volume, a mild look-ahead per spec). Pairs: 90d trailing (2160 bars before rebalance), rebalance every 30d from 2022-04-01; pairs with any NaN in window skipped; chosen greedily by half-life with NO shared symbols (avg 13.0 pairs/period, may be <20; capital still 20 units). z uses spread and 168h rolling stats through bar t-1; entry/exit at bar t close; forced exit at rebalance bar close. Sizing 1 unit each leg, beta ignored (only used for spread/signal). Trades assigned to period by entry time; win = gross>0; bootstrap clusters by UTC entry day (2000 resamples, z = mean/sd of resampled means). Annualised = sum(net maker bp)/1e4/20 scaled by 365/days covered (2022 starts at first rebalance, 2026 ends 09-30). Trades discarded if exit price NaN.
