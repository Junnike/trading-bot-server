# T11 calibration scan (10.10.2026): Kalshi + Polymarket

## Kalshi
Files: data/t11_kalshi/{series_cat.json, sample.jsonl, entries.jsonl, cells.csv, cells_tested.csv, analysis.txt}; scripts src/t11_kalshi_{sample,candles,analyze}.py (src/t11_kalshi_index.py / data/t11_kalshi/index.jsonl = time-window pilot, NOT used: 95% hourly commodity/weather series).

## Confounders (before verdict)
- SAMPLE, NOT FULL: 14,934 series (data/t11_kalshi/series_cat.json; category = series.category field). Excluded: series ending 15M, multivariate/combo markets (mve_filter=exclude), non-binary, result not yes/no (voided/scalar), lifetime volume < 100 contracts (min-volume filter, mild look-ahead on liquidity). Up to 150 random series per category (2,074 series; 864 had zero eligible markets), 12 random eligible markets per series (sample.jsonl: 8,175 kept of 105,049 eligible; per series only the live page + up to 2 /historical pages = newest <=3,000 settled), then <=450 per category -> 5,675 markets with candles (entries.jsonl; ~5.4% of eligible). Uniform over series within category, so hourly/daily series are heavily under-weighted vs their market count.
- Entry price: candlestick QUOTES, not trades. Time points = 10/50/90% of life elapsed (open_time..actual close_time). Quote = last candle close with end_ts <= time point (carry-forward, no look-ahead; candle period 1 min if life<=6h, 60 min if <=150d, else 1 day; quotes older than 6h dropped; median age 0.9 h). BUY YES at yes_ask; BUY NO at 1-yes_bid. Each market gives up to 6 observations (3 times x 2 sides) pooled per cell; observations not independent, bootstrap clusters by close date (2000 reps), not by market.
- Fee: ceil(0.07*p*(1-p)*100)/100 per contract (quadratic, cents rounded up). Per-series fee_multiplier NOT applied.
- Period: closes 2021-07-20..2026-10-10, but 76% of 21,488 obs are 2025-12..2026-10 (month counts in analysis.txt). Holdout = close >= 2026-08-10 (6,007 obs); cells measured on train only, holdout shown separately.
- Categories: 20 raw collapsed to 13 (Other = Culture, Education, Exotics, Social, Transportation, Companies, Health).
- Cells: 9 buckets (0-5,5-10,10-20,20-30,30-50,50-70,70-90,90-95,95-100c) x category (+ALL), plus coarse zones L0-20/M20-70/F70-100 per category because n/cell is small: 168 cells formed, 31 have >=200 markets and were TESTED (137 DEAD by n<200). Bonferroni z threshold (two-sided 5%, 31 cells) = 3.15. Fraction and side pooled, not separate cells.
- Survivorship: voided/scalar and zero-volume markets excluded; series absent from /series absent here.

## Table: top 19 of 31 tested cells by train z (least negative); n = train markets; data/t11_kalshi/cells_tested.csv
| category | venue | bucket | n mkts | win | mean px | EV c/ct | z | months+ | holdout EV |
|---|---|---|---|---|---|---|---|---|---|
| Politics | Kalshi | F70-100 | 203 | 0.858 | 0.890 | -4.4 | -1.5 | 7/18 | -5.3 |
| Commodities | Kalshi | 95-100 | 248 | 0.885 | 0.976 | -10.0 | -1.8 | 1/5 | -13.4 |
| Other | Kalshi | F70-100 | 329 | 0.851 | 0.899 | -6.1 | -2.3 | 12/24 | -5.9 |
| Climate and Weather | Kalshi | L0-20 | 254 | 0.037 | 0.055 | -2.8 | -2.6 | 3/13 | -3.5 |
| Crypto | Kalshi | F70-100 | 238 | 0.799 | 0.905 | -11.8 | -2.6 | 4/17 | -8.4 |
| Commodities | Kalshi | L0-20 | 237 | 0.054 | 0.082 | -3.9 | -2.6 | 1/6 | -2.6 |
| Commodities | Kalshi | F70-100 | 328 | 0.813 | 0.914 | -11.3 | -2.7 | 2/6 | -11.5 |
| Entertainment | Kalshi | F70-100 | 290 | 0.844 | 0.901 | -6.9 | -2.9 | 4/20 | -8.3 |
| Mentions | Kalshi | 70-90 | 230 | 0.742 | 0.805 | -7.9 | -3.0 | 4/17 | -7.1 |
| Sports | Kalshi | F70-100 | 203 | 0.770 | 0.890 | -13.2 | -3.7 | 4/14 | -28.5 |
| Climate and Weather | Kalshi | F70-100 | 248 | 0.833 | 0.898 | -7.7 | -3.7 | 2/13 | -17.9 |
| Commodities | Kalshi | M20-70 | 272 | 0.305 | 0.423 | -13.8 | -3.9 | 1/6 | -5.4 |
| Mentions | Kalshi | F70-100 | 293 | 0.781 | 0.856 | -8.9 | -4.3 | 3/19 | -11.0 |
| Entertainment | Kalshi | L0-20 | 307 | 0.033 | 0.070 | -4.8 | -4.6 | 2/17 | -2.6 |
| Other | Kalshi | M20-70 | 204 | 0.369 | 0.419 | -7.0 | -4.8 | 3/27 | -13.8 |
| ALL | Kalshi | 90-95 | 768 | 0.856 | 0.921 | -7.5 | -4.9 | 10/28 | -19.1 |
| ALL | Kalshi | 30-50 | 1307 | 0.323 | 0.390 | -8.7 | -4.9 | 8/39 | -7.0 |
| Economics | Kalshi | F70-100 | 208 | 0.737 | 0.907 | -18.2 | -5.5 | 2/14 | -21.7 |
| Crypto | Kalshi | L0-20 | 212 | 0.030 | 0.078 | -5.8 | -5.9 | 2/14 | -2.7 |
All 31 tested cells have negative EV (best z -1.5); 0 with z>=2 (~0.7 expected by chance). Pooled ALL zones: z -9.7 to -11.0 (EV L0-20 -4.4c, M20-70 -8.9c, F70-100 -9.3c; analysis.txt).

## Pooled view, train (data/t11_kalshi/analysis.txt)
bucket win/mean px/EV c: 0-5 .008/.021/-2.3; 5-10 .032/.067/-4.5; 10-20 .083/.142/-7.1; 20-30 .175/.244/-8.9; 30-50 .323/.390/-8.7; 50-70 .526/.597/-9.1; 70-90 .744/.803/-7.4; 90-95 .856/.921/-7.5; 95-100 .869/.977/-11.7.
Cause is mostly spread: median ask-bid 5c. By spread (diagnostic, not counted as cells): <3c EV -2.0c, 3-10c -4.6c, >=10c -22.2c; win minus mid: -0.05c, -0.16c, -1.57c, so mid quotes are about calibrated, longshots slightly overpriced (tight 0-5c: win-mid -0.3c, EV -1.95c). Tight (<3c) zones: L0-20 -2.1c, M20-70 -2.9c, F70-100 -1.3c (holdout -0.4c); tight 90-95 +0.6c (n=236, z 0.4, not significant). By time point EV -8.5/-7.4/-7.1c (10/50/90%); YES -7.4c, NO -8.0c.

## Verdict
KILLED for Kalshi: no category x price cell has positive EV after fee at the ask. 0 ALIVE cells, so USD/day ceiling is not applicable. Miscalibration exists only inside the spread. Maker (inside-spread) edge NOT tested (no fill/queue model).

## UNMEASURED
Full population (~5.4% of eligible markets sampled; hourly/daily series under-weighted); trade-based entry prices; per-series fee_multiplier and maker fees/rebates; maker-side edge; contracts/day per cell (only lifetime volume_fp stored in entries.jsonl); pre-2025 years thin (many months <=5 markets, so months+ there is weak); 137 of 168 cells below n=200 untested; Sports/Elections thin (few series with eligible settled markets in pulled pages); Polymarket is the other helper's file.


## Polymarket
All numbers: data/t11_poly/ (cells_all.csv, obs.parquet, summary.json, select_counts.json, table.md). Scripts src/t11_poly_*.py.

## Confounders (before verdict)
- Sample, not census: gamma-api /events closed=true, 504 six-hour endDate windows (3 x 2-day blocks/month, 2025-01..2026-09) -> 828,489 market rows (data/t11_poly/markets.jsonl). 3 windows hit the API offset cap (~2100) and are truncated (enum_capped.txt: 2026-08-15, 2026-09-05, 2026-09-06). Then random sample up to 2,500 markets per category (select_counts.json): 15,477 sampled, 14,307 with usable entries. Per category: Sports 2485, Finance 2466, Crypto 2409 (non-5m/15m), Culture 2303, Politics 2223, Weather 1959, EconData 401 (all eligible), Other 61. "EconData" = Fed/CPI/jobs tags only; true data-release brackets mostly UNMEASURED.
- Entry price = NOT an ask. It is the first point of the public CLOB prices-history (clob.polymarket.com, YES token) at or after 10/50/90% of life (life = gamma startDate -> closedTime). Spread, depth and fill probability are NOT modelled; real buy cost is >= this price, so every EV below is an UPPER bound. Point must be within 10% of life (+10 min) of the time point. NO side priced as 1-p from the YES history.
- Close = closedTime (actual resolution), not endDate (sports/event markets close days before endDate). Using closedTime to define life leaks timing of resolution; 90% point is therefore often near-decided. 23,218 of 92,660 side-observations dropped as price outside [0.01,0.99] (untradeable/decided) - this removes the most extreme near-certainties, a survivorship-like filter (summary.json drop).
- Fee: flat 0.07*p*(1-p) per contract, no rounding (spec formula; feeSchedule rate in gamma is 0.07 for sampled fee-enabled markets, many older/sports markets actually have lower or 0 fees, so fee is conservative there).
- Category: first match from gamma event tags (src/t11_poly_common.py), fixed order Weather, Sports, Politics, EconData, Finance, Crypto, Culture, else Other. Min volume 1,000 USD (volumeNum). Excluded: 5m/15m up-or-down crypto, unresolved or 50/50 voided markets (10,361, so voids/delists are NOT in sample = survivorship), non-binary markets. Non-Yes/No binaries (team names, o/u) use outcome-0 token.
- Both sides of every market are observations (mirror cells, not independent). Markets within one event are correlated; bootstrap clusters by close DATE only (2000 reps), so z is somewhat overstated.
- Holdout = markets closing 2026-08 and 2026-09 (12,352 obs), excluded from cell statistics; rule frozen = (category, tf, bucket). Months+ counts months with >=10 obs, by close month (2024-11..2026-09; early months are thin: median 407 markets/month).
- Cells: 8 cat x 3 tf x 9 buckets = 216 possible; 188 had >=30 obs, 112 had n>=200. Bonferroni z threshold (216 cells, two-sided 5%) = 3.68.

## Table (EV c/contract after fee; train = all but last 2 months; tf = fraction of life; source data/t11_poly/cells_all.csv + table.md)
| category | venue | tf | bucket | n obs | win | price | EV c/ct | z | months+ | holdout EV |
|---|---|---|---|---|---|---|---|---|---|---|
| Politics | Poly | 0.1 | 95-100 | 262 | 0.989 | 0.969 | +1.76 | +2.98 | 8/10 | +0.88 |
| Finance | Poly | 0.1 | 50-70 | 1420 | 0.620 | 0.546 | +5.70 | +2.84 | 8/9 | -1.43 |
| Culture | Poly | 0.9 | 50-70 | 214 | 0.682 | 0.586 | +7.94 | +2.74 | 7/8 | +12.43 |
| Culture | Poly | 0.1 | 95-100 | 537 | 0.989 | 0.975 | +1.25 | +2.65 | 8/11 | -0.76 |
| Culture | Poly | 0.9 | 95-100 | 429 | 0.991 | 0.977 | +1.24 | +2.60 | 9/10 | +0.18 |
| Culture | Poly | 0.5 | 90-95 | 225 | 0.964 | 0.924 | +3.53 | +2.12 | 4/6 | +6.69 |
| Politics | Poly | 0.1 | 70-90 | 596 | 0.841 | 0.799 | +3.07 | +1.96 | 9/13 | +5.50 |
| ALL | Poly | all | 0-5 | 6410 | 0.019 | 0.025 | -0.77 | -3.50 | 6/19 | -0.23 |
| ALL | Poly | all | 5-10 | 3258 | 0.061 | 0.071 | -1.53 | -2.37 | 5/19 | -1.63 |
| ALL | Poly | all | 10-20 | 4265 | 0.139 | 0.147 | -1.63 | -2.27 | 9/19 | -2.11 |
| ALL | Poly | all | 20-30 | 3844 | 0.221 | 0.248 | -4.04 | -4.53 | 4/19 | -2.27 |
| ALL | Poly | all | 30-50 | 9017 | 0.390 | 0.415 | -4.13 | -5.11 | 1/19 | -8.12 |
| ALL | Poly | all | 50-70 | 12383 | 0.578 | 0.560 | +0.13 | +0.19 | 9/19 | +2.97 |
| ALL | Poly | all | 70-90 | 8100 | 0.819 | 0.802 | +0.61 | +0.94 | 9/19 | -0.01 |
| ALL | Poly | all | 90-95 | 3157 | 0.934 | 0.926 | +0.41 | +0.59 | 11/18 | +0.25 |
| ALL | Poly | all | 95-100 | 6656 | 0.980 | 0.974 | +0.42 | +1.78 | 10/19 | +0.01 |

## Verdict
- Cells clearing ALL gates (n>=200, z>=3.68, >=60% months+, holdout>0, EV>=1c): 0 of 112. Best raw z = 2.98 (Politics 95-100c at 10% of life, +1.76c, holdout +0.88c): fails Bonferroni. 6 cells have z>=2 (expected by chance ~4-5 of 112 at that level); two of them are negative in holdout.
- Pooled shape (obs.parquet): longshots 0-30c lose 0.8-4.0c/ct after fee (z -2.3 to -4.5): buying cheap does NOT pay. Mid 30-50c loses 4.1c (1/19 months positive). 50-100c is flat to +0.6c (z<2). No favourite-side edge of >=1c survives.
- ALIVE cells: NONE. VERDICT: KILLED (for entries at prices-history price on this sample); USD/day ceiling not applicable.

## UNMEASURED
- Real ask/bid and book depth (no historical order-book snapshots; EV is upper bound). Fill-by-trade variant via data-api /trades not done (offset cap 10k, bounded time).
- Full census of markets (sample = 15,477 of ~122k eligible markets inside the enumerated windows, and the windows themselves cover ~1/10 of calendar days); windows 2026-08-15, 2026-09-05/06 truncated.
- Voided/50-50 and delisted markets (not in sample). Volume/day available per price (USD/day ceiling) - UNMEASURED; no cell alive anyway.
- Finer categories: true economic-release brackets, finance ranges, weather vs sports subtypes beyond tags; per-market fee rates for sports/other.
- Kalshi half: separate helper (not touched here).
