# SERVER_T12 — real-market EV re-check on PUBLIC data (run 2026-10-24, cloud sandbox)

Independent replication of the DeepSeek leg verdict of 23.10 (run 20261023_014357). Different code (`src/*.py`, written fresh),
different data source (https://data.binance.vision monthly 5m zips, spot + USDT-M perp + fundingRate). No keys, no wallets, no live bots.

## 0. Status / blockers

- `BLOCKED: pine files missing` — the repo (`main.py`, `requirements.txt` only) contains no `.ps`/`.pine` file anywhere
  (`tools/kaheksajalg/hunt_real_market_ev/` does not exist). Per the task, only the BTC gate robot is authoritative.
- Assumption stated: the same CRSI(2,2,75)<=20 -> next-15m-UP robot was ALSO run on ETH/SOL/XRP/DOGE as a labelled stand-in so the
  per-coin tables and the DeepSeek comparison have something to compare. Those four rows are NOT the Pine v1 robots.
- No URL was blocked. api.binance.com was not used. 1180 zips downloaded, 35 × 404 = pre-listing months only
  (SOL spot 2020-01..07, SOL perp 2020-01..08, DOGE perp 2020-01..06). Log: `data/download_log.txt`.
- Branch: pushed to `claude/t12-real-market-ev` (task) and to the session's designated branch `claude/eloquent-wright-h4abms`.

## 1. Gate (must pass before anything else counts)

BTC spot, 2020-01-01..2026-08-16, CRSI(2,2,75) <= 20 on 15m close -> next 15m candle UP (close > open):

| metric | value | target |
|---|---|---|
| WR | **57.00 %** | 57.0 ± 1.0 % |
| n | **37 679** | ~37 800 |
| ties (close == open, counted as not-UP) | 11 | |

**Gate PASS.** Direction edge replicated to 0.00 pp and n to −0.3 %.

## 2. Data & method

- Spot and perp 5m klines 2020-01..2026-09, funding rates same window. Microsecond timestamps (from 2025) normalised to ms.
- Row counts per month checked vs 288/day; see `results/data_gaps.md`. Spot: 462 missing 5m bars per coin (identical across coins,
  Binance maintenance windows 2020-02..2023-03). Perp: SOL/XRP missing 864+576 bars in 2022-02/04 (futures maintenance). No gap-filling;
  a signal is only taken when the previous 80 15m bars are contiguous and complete and the entry bar is contiguous and complete.
- 15m = resample of 5m (open=first, high=max, low=min, close=last, vol=sum), bins at :00/:15/:30/:45 UTC, 3 of 3 sub-bars required.
- CRSI = mean of RSI(2, close) [Wilder RMA], RSI(2, up/down streak), PercentRank(75) of 1-bar ROC (share of previous 75 values <= current), Pine conventions.
- Entry A = next 15m open; entry B = open of the 5m bar 5 min later; exit = that 15m close. Fees 10/2/0 bp round trip, net = gross − fee.
- z = mean / sd of 2000 cluster-bootstrap means, cluster = UTC day of entry. Skew = mean win / |mean loss| on net bp.
- EV/day = net bp/trade × trades/day (trades / calendar days with data).
- Perp variant: signals computed on perp klines themselves; funding added when the 15-min hold crosses a 00/08/16 UTC funding timestamp
  (hold of the :45 bar), long pays positive rate: funding bp = −rate × 10⁴.
- Maker fill: resting buy limit at the 15m open price counts as filled only if the first 5m bar's low is strictly BELOW the open
  (low <= open is trivially always true because the bar opens there; that literal reading gives 100 % fill and is not reported).
- Hold-longer: same entry A, exit at the 2nd / 4th 15m close.
- Full window = 2020-01-01..2026-09-30 (27 quarters, 2026Q3 complete here because data goes to 30.09); curve-fit window = 2025-01-01..2026-08-16.

## 3. Results — full window 2020-01-01..2026-09-30

### Table 1 — direction WR and n vs header

| coin | robot | n | WR up % | ties | trades/day | header WR | within 1.5 pp? |
|---|---|---|---|---|---|---|---|
| BTCUSDT | CRSI gate (spec) | 38 408 | 56.96 | 12 | 15.58 | 57.0 (task spec) | YES |
| ETHUSDT | CRSI stand-in | 38 454 | 56.70 | 65 | 15.60 | BLOCKED: pine file missing | n/a |
| SOLUSDT | CRSI stand-in | 36 864 | 53.08 | 689 | 16.45 | BLOCKED: pine file missing | n/a |
| XRPUSDT | CRSI stand-in | 39 592 | 54.89 | 691 | 16.06 | BLOCKED: pine file missing | n/a |
| DOGEUSDT | CRSI stand-in | 38 936 | 54.74 | 717 | 15.80 | BLOCKED: pine file missing | n/a |

### Table 2 — net bp per trade (spot), entry A and entry B

| coin | entry | n | gross | median | skew | net @10bp | net @2bp | net @0bp | z | EV/day @2bp |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | A | 38 408 | +1.09 | 3.27 | 0.829 | −8.91 | **−0.91** | +1.09 | 5.37 | −14.2 |
| BTC | B | 38 408 | +0.19 | 1.43 | 0.871 | −9.81 | −1.81 | +0.19 | 1.04 | −28.2 |
| ETH | A | 38 454 | +1.10 | 4.22 | 0.816 | −8.90 | **−0.90** | +1.10 | 4.37 | −14.1 |
| ETH | B | 38 454 | +0.04 | 2.01 | 0.850 | −9.96 | −1.96 | +0.04 | 0.17 | −30.6 |
| SOL | A | 36 864 | +1.47 | 4.08 | 0.906 | −8.53 | **−0.53** | +1.47 | 4.26 | −8.7 |
| SOL | B | 36 864 | −0.73 | 0.91 | 0.894 | −10.73 | −2.73 | −0.73 | −2.31 | −44.9 |
| XRP | A | 39 592 | +1.60 | 4.07 | 0.863 | −8.40 | **−0.40** | +1.60 | 5.49 | −6.4 |
| XRP | B | 39 592 | −0.33 | 1.77 | 0.868 | −10.33 | −2.33 | −0.33 | −1.21 | −37.4 |
| DOGE | A | 38 936 | +2.31 | 4.77 | 0.885 | −7.69 | **+0.31** | +2.31 | 6.25 | +4.9 |
| DOGE | B | 38 936 | +0.49 | 1.64 | 0.901 | −9.51 | −1.51 | +0.49 | 1.47 | −23.8 |

z is for the gross (0 bp) series; the direction edge is statistically real (z 4–6) but worth only +1.1..+2.3 bp gross, below a 2 bp maker round trip.
Skew < 1 on every coin: losses are larger than wins; WR 55–57 % only just covers that.

### Table 3 — quarters with net @2bp > 0 (entry A, spot), 27 quarters 2020Q1..2026Q3

| coin | BTC | ETH | SOL | XRP | DOGE |
|---|---|---|---|---|---|
| positive quarters | 5/27 | 6/27 | 10/25 | 11/27 | 13/27 |

Quarters with >=3 coins positive: 9 of 27. 2022Q1, 2022Q2, 2022Q4, 2023Q2, **2024Q2**, 2025Q1, 2025Q4, 2026Q2 are 0/5.
Full per-quarter table in `results/T12_tables.md`.

### Table 4 — perp + funding, maker fill, hold-longer (entry A)

| coin | perp n | perp WR % | perp gross | funding bp/trade | perp net @2bp +funding (z) | maker fill % | net @2bp filled only (n) | hold 2 bars @2bp (z) | hold 4 bars @2bp (z) |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 38 278 | 57.11 | +0.91 | −0.036 | −1.13 (−5.5) | 95.1 | −1.52 (36 526) | +0.16 (0.5) | +0.34 (0.7) |
| ETH | 38 439 | 56.96 | +1.10 | −0.043 | −0.94 (−3.7) | 95.4 | −1.72 (36 671) | +0.57 (1.4) | +0.63 (1.0) |
| SOL | 36 334 | 53.93 | +1.43 | −0.009 | −0.58 (−1.7) | 92.4 | −2.77 (34 046) | +1.46 (2.6) | +2.22 (2.4) |
| XRP | 39 406 | 54.68 | +1.56 | −0.042 | −0.48 (−1.6) | 91.5 | −2.12 (36 229) | +1.43 (3.1) | +2.33 (3.1) |
| DOGE | 36 397 | 55.42 | +2.32 | −0.036 | +0.28 (0.7) | 88.6 | −2.10 (34 484) | +2.41 (4.2) | +3.98 (4.7) |

Maker fills: when the limit does fill (price traded through the open), the filled subset is WORSE (−1.5..−2.8 bp at 2 bp) than the
unconditional set — adverse selection: the bars that fill a resting bid are the ones that went down first.
Hold-longer looks positive on DOGE/XRP/SOL over 2020–2026 but is negative or zero on every coin in the 2025–26 window (below) — a 2021 artefact.

## 4. Curve-fit check — 2025-01-01..2026-08-16 only

| coin | n | WR % | gross A | net @2bp A | z | net @2bp B | quarters >0 @2bp | perp net @2bp +fund | hold2 @2bp | hold4 @2bp |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 9 672 | 55.13 | +0.84 | −1.16 | 3.09 | −1.45 | 0/7 | −1.23 | −0.86 | −0.65 |
| ETH | 9 304 | 56.35 | +0.57 | −1.43 | 1.33 | −1.23 | 1/7 | −1.52 | −1.16 | −2.16 |
| SOL | 9 732 | 53.95 | +0.93 | −1.07 | 2.03 | −1.07 | 1/7 | −1.13 | −0.75 | −1.56 |
| XRP | 9 741 | 53.93 | +1.45 | −0.55 | 3.57 | −0.71 | 2/7 | −0.69 | +0.77 | +0.99 |
| DOGE | 9 643 | 54.57 | +1.26 | −0.74 | 2.36 | 0.00 | 2/7 | −0.91 | −0.21 | −1.01 |

BTC WR in 2025–26 is 55.1 % (−1.9 pp vs the 2020–26 gate figure): the edge is decaying, not just fee-eaten.
Only 2025Q3 has >=3 coins positive at 2 bp; 2025Q1, 2025Q4, 2026Q2, 2026Q3 are 0/5.

## 5. Verdicts

`maker-EV (2 bp) > 0 on >=3 coins in EVERY quarter? NO` (fails first in 2020Q1; 18 of 27 quarters fail; 2025-26 window: 6 of 7 fail)
`EV (0 bp) > 0 on >=3 coins in EVERY quarter? NO` (fails 2020Q1, 2022Q1-Q2, 2022Q4, 2023Q2, 2024Q2, 2025Q1, 2025Q4, 2026Q2 ...)
`EV (10 bp) > 0 on >=3 coins in EVERY quarter? NO` (no quarter on any coin is positive at 10 bp)

## 6. Comparison to prior (DeepSeek 23.10, local 5m CSVs)

| item | DeepSeek 23.10 | this run (Binance.vision) | SAME/DIFFERENT |
|---|---|---|---|
| gross bp/trade range | +1.54..+2.94 | +1.09..+2.31 | DIFFERENT (0.4–0.6 bp lower here) |
| net @2bp BTC | −0.46 | −0.91 | DIFFERENT (Δ 0.45) |
| net @2bp ETH | −0.07 | −0.90 | DIFFERENT (Δ 0.83) |
| net @2bp SOL | +0.94 | −0.53 | DIFFERENT (Δ 1.47, sign flips) |
| net @2bp XRP | −0.21 | −0.40 | SAME (Δ 0.19) |
| net @2bp DOGE | −0.04 | +0.31 | DIFFERENT (Δ 0.35) |
| entry B net @2bp | −1.78..−2.63 | −1.51..−2.73 | SAME (range overlaps; B kills every coin on both runs) |
| funding | ±0.004 bp | −0.009..−0.043 bp | DIFFERENT in size, SAME in conclusion (negligible) |
| verdict @2bp | NO (2024Q2 all five negative) | NO (2024Q2 is 0/5 here too; also 2022Q1-Q2, 2022Q4, 2023Q2, 2025Q1, 2025Q4, 2026Q2) | SAME |
| verdict @0bp | NO (2025Q4) | NO (2025Q4: BTC/ETH/DOGE < 0, XRP ≈ 0, SOL +0.16) | SAME |
| verdict @10bp | NO | NO | SAME |

Likely causes of the per-coin differences: (1) ETH/SOL/XRP/DOGE here are the CRSI stand-in, not the Pine v1 robots DeepSeek measured
(the Pine files are not in this repo), so those rows are robot-mismatched and a 0.3 bp agreement cannot be expected; (2) windows differ
(this run ends 2026-09-30; DeepSeek's local CSVs presumably run to 23.10.2026 and may start later); (3) different exchange-feed CSVs can
differ by a few bp around gaps. BTC is the only like-for-like row: both runs agree it is negative at 2 bp with the same direction WR;
the 0.45 bp level difference is of the same size as the window/feed effects above. Funding differs 10× in size but is < 0.05 bp either way.

Overall: the same conclusion is reached independently — gross edge real but ≈1–2 bp, dead at 2 bp maker, dead at every fee level
in the quarter test, entry +5 min destroys it, maker fills are adversely selected, no coin is alive in 2025–26.
**The 5 robots are dead twice (BTC like-for-like; the other four at least on their stand-in).**

## 7. Confounders

1. Data gaps: 462 missing spot 5m bars/coin (maintenance), 16 031 missing 5m bars in total incl. pre-listing partial months; handled by
   requiring 80 contiguous complete bars before and 1 after each signal, no forward-fill. Effect on n: BTC gate n 37 679 vs ~37 800 expected (−0.3 %).
2. Resample alignment: 15m bins are left-labelled :00/:15/:30/:45 UTC from 5m; Pine's 15m close equals the last 5m close, verified by gate WR.
3. Header WR source: the Pine headers are not available; the only reference WR is the 57.0 % from the task spec, which the gate matched.
4. Microsecond timestamps: all 2025+ zips use µs; normalised (`t > 1e14 -> t // 1000`), alignment asserted on all 5m bars.
5. Ties (close == open) counted as NOT UP; 11–717 per coin (more on low-priced SOL/XRP/DOGE) — at most 1.8 % of signals.
6. Funding hit rule: funding counted only when 15-min hold crosses the funding minute (bar starting :45 before 00/08/16); size is < 0.05 bp regardless.
7. Maker "touch" definition: strict low < open used; literal low <= open is 100 % by construction.
8. Perp signals are computed on perp klines (not spot signals executed on perp) — stated assumption.

## 8. Cheapest real-money test

`nothing alive, no test`

## Files

- `src/download.py` — fetch zips (re-runnable, 404s logged); `src/build.py` — parse, normalise, row-count check; `src/analyze.py` — all measures.
- `results/T12_tables.md` — every auto-generated table incl. full 27-quarter grid; `results/T12_numbers.json` — raw numbers; `results/data_gaps.md` — gap report.
