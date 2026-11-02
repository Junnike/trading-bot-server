# T13 summary (02.11.2026) — market-neutral and structure strategies on public Binance data, all USDT perps with spot pair (470 symbols, hourly, 2022-01..2026-09)

| test | file | best realistic cell | 2025-26 | verdict |
|---|---|---|---|---|
| Cross-sectional funding carry (long spot / short perp, top-N trailing funding, hysteresis exit, maker 2 bp/leg) | T13_carry.md | hyst4 K21 N20: +3.9 %/yr unlevered, Sharpe 3.7, z 7.8; funding +8.3 %/yr, costs 5.4 %/yr | 2025 −1.0 %, 2026 −2.5 % | DEAD for 2025-26 (funding premium arbitraged away; 2024 +13 %) |
| Reverse carry (long perp / short spot, most negative funding) | T13_carry.md | +58 %/yr, funding +76 %/yr | 2025 +120 %, 2026 +89 % | UNEXECUTABLE: needs spot borrow on the most-shorted alts (unavailable or >100 % APR); flagged as a lead only |
| Spot/perp basis mean reversion (|z|≥2 vs 7-day, 24h max) | T13_basis.md | gross +1.7 bp + funding +1.4 bp per trade, z 60, n 174k | 2026 gross +3.0 + 4.0 | DEAD: 3 bp edge vs 8 bp maker / 20 bp taker round trip |
| Cross-sectional basis → next-8h perp return (decile L/S) | T13_basis.md | +12 bp/8h gross in 2022-23 | −8.5 / −28 bp per 8h | DEAD (sign flipped in 2025-26) |
| Statistical pairs (top-50, 90-day cointegration, |z|≥2, 72h) | T13_pairs.md | 2025: +16.7 bp/trade net maker, z 1.7 | 2026: −43.7 bp, z −2.1; 2025-26 net −8.2 bp, z 0.0 | DEAD |
| Bullish/bearish flip, 1:1 bracket (T12e) | T12e_flip.md | mean WR 51.5 % over 49 cells, no cell z ≥ 2 | same | DEAD |
| Perp microstructure: depth imbalance, OI, taker ratio (T12d) | T12d_micro.md | 384 cells, all negative at 10 bp | all negative | DEAD |

Data notes: 32,533 of 81,054 monthly files 404 (pre-listing months); 470 symbols in panel; broken symbols (delisted perps pinned, relisted tokens: SC, RAY, FTT, LUNA, STRAX, DGB …) removed by |basis| < 2 % and ±7/14-day listing/delisting filters, without which carry showed a fake −49 %/yr drift and reverse carry +250 %/yr.

Bottom line across T12-T13: every price-only, structure, order-book and market-neutral strategy tested on free data is either below fees or dead in 2025-26. The only positive 2025-26 numbers are the unexecutable reverse carry (borrow) and single-year pairs 2025 (reversed in 2026). Nothing here justifies a live test.
