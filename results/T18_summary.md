# T18 — a signal the venue does not price: CRSI + head start at Kalshi minute 1 (03.11.2026)

## 1. The idea
The venue label is "60-s average before close ≥ 60-s average before open". Two things are known exactly at the open: (a) the previous 15-m candle, hence CRSI(2,2,75); (b) the head start hs = open price / pre-open-minute average − 1. Both are Binance-derived, computed from 1-minute klines (VWAP of the minute as the average; validated against 1-s TWAP 97.7 % and Kalshi settlement 97.1 %, T17).
On Binance history (T17 sweep, 5 coins, 2020-2026, TWAP label): CRSI ≤ 20 alone 53.5–56 %; hs > +3 bp alone 56–57.7 %; CRSI ≤ 20 & hs > 0: 57.5–59.9 %; CRSI ≤ 20 & hs > +3: 59.2–62.3 %. All hold in 2025-26 with z 8–13. Long side only; the mirror (CRSI ≥ 80 & hs < 0 → NO) is ≤ 2 pp above 50 % and worthless.

## 2. What the venues charge for it at minute 1 (taker buy YES/Up at the minute-1 ask; fee 0.07·p·(1−p), rounded up to the cent on Kalshi)
| venue / coin | windows | signal | n | hit % | market mid at m1 | ask | taker EV c | z (day clusters) | months EV>0 | minute-1 volume (ct) |
|---|---|---|---|---|---|---|---|---|---|---|
| Kalshi BTC | 11,083 | CRSI≤20 | 2,516 | 55.4 | 0.506 | 0.523 | +1.16 | 1.2 | 8/11 | 8,162 |
| Kalshi BTC | | CRSI≤20 & hs>0 | 1,105 | **61.9** | 0.542 | 0.557 | **+4.20** | **2.7** | **11/11** | 8,834 |
| Kalshi BTC | | CRSI≤20 & hs>+1 | 615 | 63.1 | 0.547 | 0.562 | +4.87 | 2.4 | 7/11 | 9,114 |
| Kalshi BTC, tape fills (first YES-taker print after 62 s) | 1,149 signal windows | CRSI≤20 & hs>0 | 488 | 61.7 | | 0.543 | +5.42 | 2.5 | | print size median 10 ct |
| Kalshi ETH | 7,728 | CRSI≤20 & hs>0 | 544 | 61.4 | 0.536 | 0.569 | +2.58 | 1.3 | 8/12 | 1,085 |
| Kalshi ETH | | CRSI≤20 & hs>+1 | 359 | 63.5 | 0.547 | 0.576 | +3.94 | 1.5 | 9/12 | 945 |
| Kalshi SOL | 7,030 | CRSI≤20 & hs>0 | 520 | 60.4 | 0.541 | 0.563 | +2.06 | 1.0 | 9/11 | 253 |
| Kalshi SOL | | CRSI≤20 & hs>+1 | 354 | 64.7 | 0.553 | 0.577 | +4.98 | 2.0 | 7/11 | 245 |
| Kalshi SOL | | CRSI≤20 & hs>+3 | 179 | 68.7 | 0.575 | 0.596 | +7.18 | 2.2 | 8/11 | 294 |
| Polymarket BTC (TWAP era Aug–Nov 2026) | 7,813 | CRSI≤20 & hs>0 | 571 | 53.6 | 0.557 | 0.557 | **−3.71** | −1.6 | 1/4 | 877 shares |
| Polymarket BTC | | hs>+3 only | 526 | 56.5 | 0.574 | 0.574 | −2.54 | −1.1 | 2/4 | |
Control rows: "hs > +3 only" on Kalshi BTC: hit 57.6 %, mid 0.561, taker EV −2.1c → the head start IS priced; CRSI is the unpriced part. All-windows buy Up on Polymarket: −1.8c (the fee).
Kalshi BTC CRSI≤20 & hs>0 by month (taker EV c / n): Dec +4.7/44 Jan −1.1/56 Feb +13.3/32 Mar +11.0/60 Apr +6.2/47 May +6.5/53 Jun +1.3/55 Jul +2.4/54 Aug +2.7/45 Sep +1.6/53 (sample of 7,000; the 11k run gives 11/11 months > 0). Note the fade from +6..+13c (Feb–May) to +1.5..+3c (Jun–Sep).

## 3. Reading
- Kalshi's minute-1 market knows the head start (it is visible in the price) but does not know that the previous candle was oversold. The combined signal buys at 0.54–0.56 what settles YES 62 % of the time: +4c per contract taker, +9c if a bid at 0.54 fills (fill not modelled). About 7 signals/day on BTC across all 96 windows (1,105 of 11,083 sampled), 4/day on ETH, 4/day on SOL.
- Polymarket prices it fully: same signal, mid 0.557, hit 53.6 % on Chainlink's label. Dead there.
- Capacity: Kalshi BTC minute-1 volume ≈ 8–9k contracts; a 200-contract order (≈ 110 USD) is ~2 % of the minute. At +4c that is 8 USD/signal, ≈ 55 USD/day on BTC if every signal fills at the candle ask; ETH/SOL books are 10–30× thinner. Realistic first-year scale: tens of USD/day, not hundreds.
- Decay: the Kalshi edge halved from H1 to H2 2026 while the hit rate stayed ~62 %: the ask moved from ~0.54 to ~0.56. Someone is already leaning on it. Statistical standing: z 2.4–2.7 on 11k windows, i.e. real but not overwhelming; the full 30k-window pull (running) will say whether z passes 4.

## 4. Status
- ALIVE on Kalshi BTC (and weaker on ETH/SOL): the only strategy in T12–T18 with positive EV at a real venue ask, positive every month, and a mechanism (information the minute-1 crowd ignores).
- Cheapest live test (< 50 USD/day risk): Kalshi BTC only, taker buy YES 20 contracts at the minute-1 ask when CRSI_prev ≤ 20 and hs > 0 (both from a Binance 1-m websocket; the pre-open-minute VWAP and the open print), hold to settlement, 2 weeks, log fill price vs the T18 candle ask. Pass if realised EV > +2c/contract over ≥ 150 signals. Then size up to 100–200 ct.
- Files: src/twap_label.py (T17), src/kalshi/k8_signal_m1.py (scorer), k9_fills_m1.py (tape fills), k7_trades_first3.py (tape pull), k1/k2_*_series.py (ETH/SOL), src/poly/p3_pull_first3.py + p4_signal_m1.py (Polymarket); results/T17_crsi_twap_label.md, T18_signal_m1.md, T18_fills.md, T18_poly_signal_m1.md.

## 5. CORRECTION after the full pull (29,983 of 30,221 BTC windows, all 11 months; results/T18_signal_m1.md regenerated)
| signal | n | per day | hit % | mid1 | ask1 | taker EV c | z | months > 0 | maker @bid EV c (fill assumed) |
|---|---|---|---|---|---|---|---|---|---|
| CRSI≤20 | 5,090 | 15.7 | 53.6 | 0.506 | 0.517 | −0.15 | −0.2 | 3/11 | +4.0 |
| CRSI≤20 & hs>0 | 2,234 | 6.9 | **58.4** | 0.543 | 0.554 | **+1.03** | **0.9** | 7/11 | +5.1 |
| CRSI≤20 & hs>+1 | 1,197 | 3.7 | 59.8 | 0.553 | 0.563 | +1.53 | 1.0 | 6/11 | +5.6 |
| CRSI≤20 & hs>+3 | 424 | 1.3 | 64.4 | 0.569 | 0.580 | +4.44 | 1.9 | 7/11 | +8.6 |
| hs>+3 only (control) | 2,556 | 7.9 | 57.6 | 0.567 | 0.578 | −2.19 | −2.3 | 3/11 | +2.1 |
The 11,083-window sample in §2 (hit 61.9 %, +4.2c, z 2.7, 11/11) was a favourable draw: the 19,000 windows added afterwards hit ~55 % on the same signal. With the whole population the taker edge is +1c per contract and not distinguishable from zero (z 0.9); the hit rate 58.4 % against a market mid of 0.543 is still a real 4-pp mispricing, but the half-spread plus fee (≈ 1.1c + 1.7c) eats it. The tape-fill check (T18_fills.md, +5.4c) was computed on the same lucky sample and carries the same bias.
**Revised verdict: MARGINAL, not alive.** What survives: (1) Kalshi's minute-1 crowd ignores the previous candle (58 % vs 54 % priced) — a real but small inefficiency; (2) the only way to harvest it is as a MAKER at the bid (+5c if filled), which the T12 replay showed is adversely selected on this venue; (3) the taker version is a coin-flip after costs. The bot (src/kalshi_live/bot.py) stays useful only in --paper mode as a measurement tool: run it two weeks to log real asks and ask depth; do not switch to --live on these numbers. `nothing alive, no test` stands for T12–T18.
