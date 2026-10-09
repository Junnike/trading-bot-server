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
