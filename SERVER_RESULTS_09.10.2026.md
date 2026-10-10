# SERVER_RESULTS 09.10.2026 (T1-T9). Detail: data/RESULTS_KALSHI.md, RESULTS_POLY.md, RESULTS_T9.md
## 1) Confounders
- Kalshi API: live endpoints reach only ~2026-08-02; older via /historical/* (cutoff 2026-08-10); historical candles drop "_dollars"/"_fp" suffixes (parser fixed). 25-45% of calls got 429 (1.5-5 ok req/s).
- Coverage: BTC markets 28,242 windows 2025-12-10..2026-10-09 (data/markets_KXBTC15M.jsonl); BTC candles 21,807 random windows, 11 months (data/candle_parts/); ETH/SOL candles 60d only; BTC prints = RANDOM 1,663 of 5,730 windows, last 60d (data/prints_cells.parquet). Prints for ETH/SOL/others and BTC full history NOT pulled.
- Thursday 07-09 UTC: 80 BTC windows (~340 expected, exchange closed), excluded everywhere.
- Binance 1-s: 302 days 2025-12-11..2026-10-08, 0 gaps (data/binance/). Poly 5-min BTC: 2026-02-12..2026-10-08, 68.3k windows, prints only (no quotes/depth); strike proxy = Binance close at open second, not Chainlink TWAP.
## 2) Tables
T1 BTC maker vs p<0.3 takers (data/prints_cells.parquet; 1663 win, 3 mo Aug-Oct): maker gross -0.05 c/ct z -0.1; by month +0.4/+0.2/-1.3; weeks>0 56% (9 wk); vol Q1..Q4 -1.4/-0.2/+0.7/+0.3; 17 flip windows -57.1c. FIFO 88 USD/day at share .238/.10/.05 (200ct cap binds). Prior +5.58 not reproduced.
T1b BTC bucket [.7,.9) hit-bid c (data/candle_parts/KXBTC15M_*; n windows; z; % months+): m5 +1.9 (4462;3.2;91%) m6 +1.8 (4615;3.2;82%) m7 +2.5 (4703;4.4;100%) m8 +2.5 (4511;4.5;91%) m9 +2.1 (4164;3.6;91%) m10 +1.9 (3614;3.0;73%) m11 +1.1 (3056;1.6;55%) m12 -0.6 m13 -0.2 m14 +5.7 (989;5.2). ETH m7 +4.6 (z4.4, 3 mo only); SOL ~0.
T2 BTC signed flow (data/prints_win.parquet; 167-499 win/cell): every (a,q) EV after fee negative, -2.8 to -15.2c; best a=60 q=.2 n=333 EV -2.8c z -1.1, months -0.3/-6.1/-0.2. Top-flow windows contrarian (hit 8-42%).
T3 Poly 5-min snipe (data/T3_full.csv, 68.3k win, 239d): EV c/sh after fee, 0-5s -1.72 z-10.9; 5-10s -1.19 z-9.9; 10-22s -1.68 z-21.1; 22-30s -1.87 z-19.7. Model-filtered (fair-fill-fee>5c): +2.81c z10.0 overall; monthly Feb 6.35, Mar 3.91, Apr 3.71, May 2.01, Jun 4.61, Jul 2.36, Aug 0.47, Sep 0.03, Oct 0.70; last 59d +0.36c z0.7 (data/T3_monthly_full.csv, T3_d60.csv).
T4 KXBTCD ladder (data/t4_poll.jsonl): 407 snapshots / 6.8 h; 0 violations after fee; best net edge -0.0014.
T5 taker at real ask BTC (data/candle_parts/KXBTC15M_*): EV by ask bucket -1.13/-2.95/-3.16/-2.15/-1.20/-0.12 c; cells z>2 with n>=500: 0 of 79 (best [.9,1] m11 +0.22c z1.3). ETH 0/71, SOL 1/52.
T6 monthly: T1b m7 positive 11/11 months; T1 p<.3 +0.4/+0.2/-1.3; T2 best Aug/Sep/Oct all <=0; T3 filtered fades to ~0 in Aug-Oct; T8 2bp 9/9 months.
T7 (docs 2026-10-09): taker fee at 0.50: Predict 1.00c (2%*min(p,1-p)), Limitless 1.50c (3% buy, p<=.5), Poly 1.75c. Maker fee 0 on all. Rebate: Predict 25% of taker fee (UP/DOWN, trial to late Oct); Poly 20%; Limitless 5-min rebate UNMEASURED. Rate limit: Predict 240 req/min/key; Limitless unpublished. Limitless 5-min BTC depth snapshot: bid .17 x10, ask .279 x20.
T8 Poly maker ladder with pull (data/T8_full.csv, 239d, 1 share/level, 100% fill when print trades through, rebate 20%): no pull -1338 USD/day; 2bp +509.8 (226/239 days+, 9/9 mo, z110.8); 3bp +327.6 (203/239, 9/9); 5bp -6.7 (136/239, 4/9). Last 59d (T8_d60.csv): 2bp +331.6, 3bp +165, 5bp -176. 6 s pull delay 2bp +218. Quote stop 240 s: 2bp +243.7.
T9 oil->BTC (data/t9/t1.csv t2.csv t3.csv; CL 15m 59d, 1h 729d; excluded 32%/39%): lag0 corr 15m -0.13, 1h -0.045 (co-move); lags 1..4 within |0.035|. Hit of -sign(oil lag1): 15m 0.498 (n4218, z-0.25); 1h 0.506 (n12555, z+1.35). Best n>=300 cell 15m |z|1-2 BTC-prev- n373 hit .550 z1.85. EV real minute-1 ask 15m: -1.52c z-1.75 (2977 win, 3 mo); best cell +0.74c z0.37 (2/3 mo+). 1h ASSUMED p=.52: best hit .529 -> -0.85c. Brent: 2 of 54 cells z>2 (chance).
## 3) Verdicts
T1 KILLED (maker gross <=1.0, 56% weeks, sample 1,663 windows only) | T1b ALIVE (hit-bid >1c at m5-11) but NOT shown executable (no fill/queue model; print-level [.7,.9) maker gross only +0.7 c/ct)
T2 KILLED | T3 KILLED (literal buckets all <0; filtered variant decayed to ~0 Aug-Oct) | T4 KILLED | T5 KILLED
T6 only T1b m7 and T8 pass the monthly rule | T7 UNMEASURED beyond fees | T8 ALIVE at 2bp/3bp pull only (KILLED no pull, 5bp); needs live fill-rate check | T9 KILLED
## 4) Best single cell
T1b BTC bid in [.7,.9) at minute 7: hit-bid +2.5c, z4.4, n=4,703 windows, 11/11 months positive (data/candle_parts/KXBTC15M_*). Assumes fill at bid_close, no queue/adverse selection. Runner-up T8 2bp pull +509.8 USD/day (9/9 months), unrealistic 100% fills.
## 5) BLOCKED / UNMEASURED
Kalshi prints for ETH/SOL/other coins and BTC full history (rate limit); T1/T2 all-coin; Kalshi cent rounding of fees not modelled. Predict.fun markets/trades/depth (API 401, needs key); Limitless 5-min rebate and rate limit; Poly quote/depth history and Chainlink strike. Poly prices-history empty for markets older than ~2 weeks.

# T8b 10.10.2026 Poly 5-min maker ladder, second pass. Scripts src/t8b_label.py t8b_replay.py t8b_report.py t8b_cap.py; tables data/t8b_tables.txt, data/t8b_cap_tables.txt
Setup: ladder 0.45..0.20 both tokens, re-place when back inside k bp (first pass kept permanent pull; shown as T1b), info lag = delay+1 s (first pass lag 1), rebate 0, 239 d, 68810 windows (data/poly_resolution.parquet).
Sanity (data/t8b_tables.txt): first-pass replica (ladder 0.05-0.95, perm pull, share 1, lag 1) = +509.7 USD/d at 2bp, +327.6 at 3bp (first pass 509.8/327.6) OK.
C1 fills = FIFO share x aggressor-side contracts at/through level (sell-Up/buy-Down hit Up bids), partial fills, level cap S. Any-side variant (first-pass style) within 2 USD/d (T1c). C3 queue/depth unmeasured, share is the only proxy.
C2 label: data/poly_resolution.parquet (gamma, 69100 slugs) = labels already stored in data/poly/*_markets.parquet (0 differ; first-pass label was already gamma, only strike/move was Binance). 1 window unresolved = UNMEASURED. Binance-close proxy differs from real in 4819/68810 = 7.00%.
C4 delay 0/2/6 s; C5 rebate +5.5 USD/d on top at share 1 (verdict uses 0); C6 period 2026-02-12..10-08, monthly/vol below.
Result 1 grid (data/t8b_tables.txt) USD/day at S=1, rebate 0, real label [z, months+/9], delay 0 / 2 / 6:
- k2 share1.0: +50.4 [11.9, 8/9] / +20.0 [4.7, 6/9] / -32.1 [-8.8, 0/9]; share0.238: +49.3 / +18.7 [4.4, 6/9] / -33.0; share0.10: +47.5 / +16.3 [3.9, 5/9] / -34.5; share0.05: +44.9 / +13.5 [3.2, 5/9] / -36.5
- k3 share1.0: +28.2 / +5.6 [1.4] / -33.3; share0.238: +27.1 / +4.3 [1.1] / -34.2; share0.05: +23.0 / -0.4 [-0.1] / -37.7. Fills/day ~1700-2200 (1 share/level). Permanent pull (T1b): -5.5 .. -37.7 in all cells.
Result 2 label: first-pass cell on spec ladder (any-side, share 1, d0) = +51.0 re-place / -4.5 perm with real label vs +105.3 / +38.1 with proxy label: proxy inflates by ~54-43 USD/d. The +509.8 came from bids above 0.45 (0.50-0.95 removed by spec ladder).
Result 3 size, best realistic cell k2 share0.238 delay2 (data/t8b_cap_tables.txt): S1 +18.7 [4.4]; S2 +33.8; S5 +66.0 [3.1]; S10 +92.0 [2.2]; S15 +92.8 [1.4]; S20 +74.8; S30 -7.7; S50 -326.9. Growth stops at S~10-15.
Result 4 where money sits (same cell, S1): level fill p -> win rate: .45->.4393 (-4.9 USD/d), .40->.4041 (+1.6), .35->.3653 (+4.6), .30->.3240 (+5.7), .25->.2823 (+6.0), .20->.2386 (+5.7). Time 0-60 s -1.8, 60-180 s +11.1, 180-300 s +9.3 USD/d. Win rate > p at 5 of 6 levels, only 0.45 is the bad fill.
Result 5 monthly USD/day (data/t8b_tables.txt): Feb 53.5, Mar 67.1, Apr 54.7, May 44.9, Jun 18.3, Jul 0.8, Aug -31.8, Sep -25.4, Oct(8 d) -48.5 => 6/9 = 67% months+, but Aug-Oct -30.9 USD/d at S1 (data/t8b_cap_tables.txt), worse with size (S10 -401/d). Vol quartile Q1..Q4 USD/d: -10.1, +3.5, +8.2, +17.2 (only upper 3 positive).
KILL rule check (best realistic cell k2/0.238/d2/rebate0/real): USD/d +18.7 >0, z 4.4 >=2, 67% months >=60%, win rate > p at 5/6 levels => not killed by the literal rule.
VERDICT T8b: ALIVE on the literal rule but FRAGILE: 509.8 ceiling collapses to +18.7 USD/day (S=1); delay 6 s = -33; edge decayed to negative since Aug 2026; low-vol quartile negative. Capacity over whole period +92 USD/day at S~10 per level (z 2.2), but recent 3 months negative at every S, so not deployable without a fresh forward check.

# T8c + T10 (10.10.2026). Scripts src/t8c_crowd.py t8c_an.py t10_events.py; tables data/t8c_tables.txt, data/t10_tables.txt

## Confounders (before verdicts)
- Proxy-vs-real label gap 7.00% in T8b (data/poly_resolution.parquet vs Binance close); both T8c and T10 use the real gamma label.
- Queue position 100% unmeasured: share 0.238 is a scenario only (data/t8b/day_*.npz); competing makers are not observable from D6 trades (data/poly/*_trades.parquet).
- 239-day period (2026-02-12..10-08, data/poly/), Oct = 8 days only; 4 quartile/threshold rules tried = in-sample selection.
- T10 ask proxy = first taker BUY print of the pointed token in +120..+150 s (data/poly/*_trades.parquet), not a quoted ask; 597 of 67946 windows have no such print (excluded from EV only).
- Event dates recalled from public BLS/Fed calendars, NOT verified online (bls.gov pages only show future dates); list may be incomplete/off by a day. 08:30 sample = 21 days.

## T8c
- Reproduction: k2/share0.238/delay2/S1/real label = +18.7 USD/day, z 4.4, 1720 fills/day (data/t8b/day_*.npz) = matches T8b +18.7 (data/t8b_tables.txt). MATCH.
- Table month x vol quartile (USD/day [fills/day]; quartile edges 17.7/25.9/38.5 bp/h, data/t8c_tables.txt; windows per cell listed there):
  Feb Q1..Q4 -0.9/2.9/16.3/35.2 | Mar 0.5/5.3/19.8/41.6 | Apr 1.3/12.6/15.7/25.1 | May 5.0/13.7/13.1/13.1 | Jun -2.9/2.4/3.3/15.4
  Jul -7.7/0.5/2.2/5.9 | Aug -27.2/-2.1/-0.1/-2.3 | Sep -16.8/-8.7/0.1/0.1 | Oct(8d) -43.1/-2.3/-7.0/3.9. Month totals 53.5, 67.1, 54.7, 44.9, 18.3, 0.8, -31.8, -25.4, -48.5.
- Per month fills/day | mean p | win rate | taker ct/window at p<=0.45 (data/t8c_crowd.parquet) | median vol bp/h:
  Feb 1521|.365|.401|36366|38.2; Mar 1473|.369|.414|50287|38.2; Apr 1693|.361|.393|34027|27.0; May 1912|.354|.378|28888|19.5; Jun 1508|.367|.380|31931|32.6
  Jul 1801|.358|.359|29305|21.9; Aug 1905|.348|.332|20159|18.3; Sep 1800|.349|.335|18373|22.4; Oct 1927|.346|.321|17303|18.7. Win rate - p: +3.5 pts Feb, -1.5 pts Aug, -2.5 pts Oct (adverse selection grew).
- Attribution: median vol fell 38 -> 18-22 bp/h and fills/day rose 1500 -> 1900 (fewer pulls/more fills at low vol), but crowding proxy (taker ct/window <=0.45) FELL 36-50k -> 17-20k, so no crowding signal. Yet within Q3/Q4 vol the edge also decayed (Q4: +35 Feb -> -2 Aug, +0.1 Sep) so vol alone does not explain it. Verdict: VOL-DRIVEN IN PART (Q1 collapse), residual decay UNMEASURED (queue/competing makers invisible in trades); crowding by taker volume not supported.
- REVIVE RULE (assumption: in-sample, share 0.238, fixed ladder): "trade only when 60-min pre-open vol >= 25.9 bp/h" = +23.2 USD/day, z 9.6, 7/9 months positive (78%, data/t8c_tables.txt); crowd<=Y rules fail (best -2.6 USD/d). But same rule in Aug-Oct = -1.39 USD/d, z -0.8 (Q4 only -0.54, z -0.5), and high-vol windows are only 25-50% of windows. Formal rule passes, practical status: DEAD for the current regime (zero edge Aug-Oct even in high vol); needs a forward check.

## T10 (data/t10_tables.txt; 5-min BTC windows, +2 min Binance move direction (data/binance/) vs real label (data/poly_resolution.parquet), EV at D6 ask proxy, fee 0.07p(1-p), day-cluster bootstrap 2000)
- Dates used 08:30 NY: CPI 02-13,03-11,04-10,05-12,06-10,07-14,08-12,09-11,10-14(future, no data); NFP 02-11,03-06,04-03,05-08,06-05,07-02,08-07,09-04,10-02; FOMC 03-18,04-29,06-17,07-29,09-16.
- Type: n | hit | EV c/share (z) | months+ : 08:30 data days 105 | .724 | -4.05 (-1.1) | 4/9; 09:30 weekdays 854 | .739 | -0.48 (-0.3) | 3/9
- CME 18:00 Sun-Fri 1018 | .707 | -3.26 (-2.4) | 3/9; 00:00 UTC 1176 | .697 | -3.72 (-2.8) | 1/9; OTHER 64793 | .714 | -0.91 (-4.2) | 0/9; ALL 67946 | .714 | -1.00 | 0/9.
- Hit rate is 70-74% everywhere (event windows not different from others); the Poly ask already prices it in, EV negative in all types. Side check FOMC 14:00 NY n=25 EV +3.3 z 0.9 (not significant).
- VERDICT T10: KILLED (z<2, <60% months positive in all four event types; 08:30 n=105 borderline).
