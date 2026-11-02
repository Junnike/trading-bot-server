# FINAL SUMMARY — T12..T19, 24.10–03.11.2026 (cloud session, public data only, no keys, no live orders)

Everything below is reproducible from `src/` on free data (Binance Vision, Kalshi public API, Polymarket public API, Crypto.com public API, Yahoo). Results files in `results/`. Branches `claude/t12-real-market-ev` and `claude/eloquent-wright-h4abms` are identical.

## 1. One-line verdicts
| # | question | answer | file |
|---|---|---|---|
| T12 | Are the 5 CRSI 15-m direction robots alive as 2-bp maker trades? | **NO.** Gross +1.1..+2.3 bp/trade is real (z 4–6) but below 2 bp; all five negative in 2025-26; entry +5 min kills it; maker fills adversely selected. Replicates DeepSeek 23.10 on independent data. | T12_results.md |
| T12 | Kalshi minute-7 bid cell (T1b, +2.5c) executable as a maker? | **DEAD.** Fills only when the market turns against the bid: filled win 79 % vs unfilled 91 %; model B EV −0.70c/signal, 5/11 months. | SERVER_RESULTS_ALL.md §T12, T12_kalshi_fill.md |
| T12b | CRSI on 1h/4h/1d, longer holds? | DEAD. No cell clears 10 bp with z ≥ 2 in both windows. | T12b_horizon.md |
| T12c | Funding-extreme timing, BTC→alt lead-lag, daily breakout? | DEAD (lead-lag: one marginal cell DOGE +8 bp; breakout = buy-and-hold with smaller drawdown). | T12c_families.md |
| T12d | Order-book depth imbalance, OI, taker ratio (384 cells)? | DEAD. All negative at 10 bp. | T12d_micro.md |
| T12e | "Bullish flip" market-structure pattern, 1:1 bracket? | DEAD. Mean WR 51.5 % over 49 cells, no cell z ≥ 2. | T12e_flip.md |
| T13 | Cross-sectional funding carry, 470 perps? | Dead for 2025-26 (+3.9 %/yr unlevered best cell; 2025 −1 %, 2026 −2.5 %). | T13_carry.md |
| T13b | Reverse carry (long perp / short spot on most-shorted alts) with real borrow? | **The only backtest > 0 with a mechanism:** +24 %/yr Binance, +15 % OKX, +35 % routing both, Sharpe 4–5, 2025 and 2026 both positive. Capacity 10–50k USD. Borrow availability and historical rates unmeasured. | T13_reverse_carry.md, T14_okx_live_test_plan.md |
| T13 | Spot/perp basis mean reversion; cross-sectional basis; statistical pairs? | DEAD (3 bp edge vs 8 bp cost; pairs +17 bp 2025, −44 bp 2026). | T13_basis.md, T13_pairs.md |
| T15 | Exit at minute 13–14 to avoid the "rigged last minute"? | DEAD. Holding beats every exit by 1–2.5c; minute-14 contracts ≥ .90 flip 0.7 %. | T15_last_minute_exit.md |
| T16 | What the TWAP rule does; can the last minute be sniped? | Rule verified on both venues (60-s average vs 60-s average). Candle-vs-settlement mismatch 6–7 %. Sniper was +15..+28c/contract Dec–Apr, **0 ± 1c since May 2026**; Polymarket ≤ 0 at 5 s latency. | T16_summary.md |
| T17 | CRSI robots scored on the venue label? | 53–56 % in 2025-26, 1–2 pp below the candle label, below break-even at 0.55. | T17_crsi_twap_label.md |
| T18 | CRSI + head start at Kalshi minute 1 (crowd ignores the previous candle)? | Real 4-pp mispricing (58.4 % vs 54.3 % priced) but **+1.0c taker after costs, z 0.9** on all 30k windows; the 11k-sample +4.2c was a lucky draw. Polymarket prices it fully. MARGINAL. | T18_summary.md §5 |
| T19 | Crypto.com 24/7 stock perps / tokenized stocks over the weekend? | No mispricing: liquid names already price Monday's open; thin names are stale prints you cannot hit. | T19_stock_perp_weekend.md |

## 2. What the data says, in order of importance
1. **Fees, not signals, are the wall.** Every price/structure/order-book signal on 5-min to 4-h crypto is worth 1–4 bp or 1–4c, and every realistic cost is 2–10 bp or 2–3c. No venue change fixes that; a maker rebate or zero-fee tier changes it only if the counterparty is not an informed market maker (T19 shows it is).
2. **The binary venues settle on 60-s averages of a non-Binance index.** 6–7 % of candles flip colour versus Binance. A robot must be trained on that label (`src/kalshi/k6_twap_sniper.py::closes`, `src/twap_label.py`). Exiting early does not recover the loss; the market price already knows the rule by minute 14.
3. **Edges decay within months.** Kalshi sniper (+25c → 0 after May), Kalshi minute-1 CRSI (+6..+13c Feb–May → +1..+3c Jun–Sep), funding carry (2024 +13 % → 2025-26 negative). Anything found must be re-measured on the latest 2 months before money moves.
4. **Sample selection bit twice.** T18 looked alive on 11k windows and died on 30k; T12 maker fills looked fine on candles and died on the tape. Rule: pull the whole population and the trade tape before believing a z of 2–3.
5. **The one live candidate is market-neutral and capacity-limited:** reverse funding carry with real borrow (T13b/T14). It survives because it is too small for funds. Its unknowns are operational (borrow pool availability, historical borrow rates, two illiquid legs), which only a 7-day, ~1,000 USD/leg test on OKX can answer. Plan and read-only logger are written (`results/T14_okx_live_test_plan.md`, `src/okx_logger.py`, `deploy/`).

## 3. Tools left behind
- Data pipeline: `src/download*.py`, `src/build.py`, `src/panel.py` (470-symbol hourly panel), 1-s/1-m/5-m/1-h Binance caches; Kalshi index/candles/tape pullers (`src/kalshi/k1..k7`), Polymarket tape pullers (`src/poly/p1, p3`).
- Backtests: `src/analyze.py` (CRSI, bootstrap), `carry.py`, `basis.py`, `pairs.py`, `micro.py`, `flip.py`, `horizon_sweep.py`, `families.py`, `twap_label.py`, `stock_perp_weekend.py`, `kalshi/k4, k6, k8, k9`, `poly/p2, p4`.
- Live tooling (not to be armed on current numbers): `src/kalshi_live/bot.py` (paper mode = free measurement of real minute-1 asks), `src/okx_logger.py` + `src/okx_report.py` + `src/okx_select.py` (T14), systemd units in `deploy/`.

## 4. Recommendation
Stop building direction robots for 15-minute binaries. If anything goes live, it is the OKX reverse-carry 7-day test, sized at 1,000 USD per leg, judged by realised borrow rate and fills, with the pass rule in T14. Otherwise the honest state of this project is `nothing alive, no test`, established three times on independent data.
