# RESULTS_T13 (Kalshi BTC15M minute-7 bid [.70,.90) resting-bid replay). Sources: data/t13/tape.jsonl (trade tape), data/t13/replay.parquet, data/t13/analysis.txt (src/t13_pull.py, src/t13_an.py), candle_parts/KXBTC15M_*, markets_KXBTC15M.jsonl
Confounders: bid = yes_bid_close of candle with end_ts = open+420 s (same as T1b, an_common m=7), tick 1c (0% of cell bids sub-cent; trade prices 4-dp). Order live S+2 s, cancel S+62 s, fill price = our bid, maker fee 0, settle 0/100. One candle per ticker -> 4703 signals = 4703 distinct markets, no same-market overlap; adjacent 15m windows are correlated, so z is clustered on UTC date (2000 reps).
Tape: all 4703/4703 cell windows pulled (3641 /historical/trades, 1062 live); 111 windows have no print in [S,S+62] (data/t13/tape.jsonl). Mapping: our YES bid fills when taker_side=no and yes_price<=bid (no_price>=1-bid); strict (B) = yes_price<bid. Book depth is not in the public API: model C UNMEASURED; rows Q50/Q200/Q1000 only ASSUME depth ahead = 50/200/1000 ct vs cumulative taker-NO volume at <=bid (sensitivity, not measurement).
| model | fill rate | n fills | EV/filled c (z) | EV/signal c (z) | win filled / unfilled |
| A any print <=bid (optimistic) | 0.838 | 3942 | +0.88 (1.5) | +0.74 (1.5) | 0.808 / 0.904 |
| A2 taker-NO <=bid | 0.833 | 3918 | +0.94 (1.6) | +0.78 (1.6) | 0.809 / 0.898 |
| B taker-NO strictly < bid | 0.701 | 3297 | -0.33 (-0.5) | -0.23 (-0.5) | 0.795 / 0.890 |
| C true queue | UNMEASURED | - | - | - | - |
| Q50 / Q200 / Q1000 (assumed depth) | 0.771/0.712/0.596 | 3624/3349/2804 | +0.28/+0.17/-0.75 | +0.22/+0.12/-0.45 | ~0.80 / ~0.88 |
Adverse selection (data/t13/analysis.txt): unconditional cell EV with fill-at-bid for every signal = +2.47c; filled B win 79.5% vs unfilled 89.0%, unfilled counterfactual EV +9.05c, so fills come when price falls through our bid (the winners escape). EV/signal collapses from +2.47 to -0.23 (B).
Model B per month, EV/signal c (data/t13/replay.parquet): 2025-12 -0.64, 2026-01 -2.03, 02 +1.04, 03 -1.58, 04 +1.10, 05 -0.52, 06 +0.16, 07 -0.49, 08 -0.75, 09 +1.90, 10 -3.27 -> 4/11 positive. Holdout 2026-09..10: n=839, 617 fills, EV/signal +0.69 (z 0.7), EV/filled +0.94 (z 0.7) (noisy, Sep +1.9 / Oct -3.3).
KILL RULE: B EV/signal -0.23c <= +0.5c AND 4/11 < 8/11 months positive -> both triggers hit.
VERDICT: KILLED as executable maker strategy. Even optimistic model A is only +0.74c/signal (z 1.5, not significant); the T1b +2.5c does not survive fills/adverse selection. True queue position UNMEASURED (no historical book).
