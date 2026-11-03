# trading-bot-server — research pipeline (T12–T20)

Plain Python 3.10+ scripts. No API keys needed for any backtest; all data is public. Any person or model can run it.
Requires: `pip install pandas numpy tabulate` (plus `cryptography` only for the Kalshi live bot). Run every script with `python3 -I`.
Everything writes to `data/` (git-ignored, rebuildable) and `results/` (committed).

## Install on a droplet (Ubuntu)
```
sudo apt install -y python3-pip curl unzip
git clone https://github.com/Junnike/trading-bot-server /opt/trading-bot-server && cd /opt/trading-bot-server
git checkout claude/t12-real-market-ev
pip3 install pandas numpy tabulate
```

## Rebuild the data (all public, re-runnable, skips what exists)
| step | command | what it fetches | time |
|---|---|---|---|
| 1 | `python3 -I src/download.py` | Binance spot+perp 5m klines and funding, 5 coins, 2020–2026 | 5 min |
| 2 | `python3 -I src/build.py` | parses into `data/cache/*.pkl`, writes `results/data_gaps.md` | 2 min |
| 3 | `python3 -I src/download_1m.py && python3 -I src/download_1m_daily.py 2026-10-01 2026-11-02` | 1-minute klines (venue TWAP label) | 5 min |
| 4 | `python3 -I src/download_all.py && python3 -I src/panel.py` | funding + 1h klines for all 470 USDT perps with spot, hourly panel | 90 min |
| 5 | `python3 -I src/download_micro.py` | Binance perp metrics + order-book depth | 30 min |
| 6 | `python3 -I src/download_1s.py` | Binance 1-second klines for Kalshi sample days | 10 min |
| 7 | `python3 -I src/kalshi/k1_index.py && python3 -I src/kalshi/k2_candles.py 700 && python3 -I src/kalshi/k3_trades.py && python3 -I src/kalshi/k5_trades_last2.py` | Kalshi BTC 15m markets, 1-min candles, trade tapes | 2–4 h (rate-limited) |
| 8 | `python3 -I src/poly/p1_pull.py && python3 -I src/poly/p3_pull_first3.py` | Polymarket BTC 15m trade tapes (TWAP era) | 2 h |
| 9 | `python3 -I src/dex/d1_pull_funding.py` | Hyperliquid + Aster funding history | 30 min |

## Run the tests (each writes one file in `results/`)
| test | command | result file |
|---|---|---|
| T12 CRSI robots, fee grid, quarters, perp+funding, maker fill, hold-longer | `src/analyze.py` | T12_results.md, T12_tables.md |
| T12 Kalshi bid fill replay | `src/kalshi/k4_replay.py` | T12_kalshi_fill.md |
| T12b hold-horizon sweep | `src/horizon_sweep.py` | T12b_horizon.md |
| T12c funding timing, lead-lag, breakout | `src/families.py` | T12c_families.md |
| T12d order-book / OI / taker-ratio | `src/micro.py` | T12d_micro.md |
| T12e bullish-flip pattern | `src/flip.py` | T12e_flip.md |
| T13 funding carry / basis / pairs | `src/carry.py`, `src/basis.py`, `src/pairs.py` | T13_*.md |
| T13b reverse carry with real borrow | `src/okx_select.py` + notebook cells in T13_reverse_carry.md | T13_reverse_carry.md |
| T15 exit before last minute | (inline in T15_last_minute_exit.md) | T15_last_minute_exit.md |
| T16 TWAP sniper Kalshi / Polymarket | `src/kalshi/k6_twap_sniper.py`, `src/poly/p2_sniper.py` | T16_*.md |
| T17 CRSI on venue label | `src/twap_label.py` | T17_crsi_twap_label.md |
| T18 signal at Kalshi minute 1 | `src/kalshi/k8_signal_m1.py KXBTC15M BTCUSDT`, `k9_fills_m1.py`, `src/poly/p4_signal_m1.py` | T18_*.md |
| T19 stock perps weekend | `src/stock_perp_weekend.py` | T19_stock_perp_weekend.md |
| T20 cross-venue funding carry (DEX) | `src/dex/d2_dex_carry.py` | T20_dex_carry.md |

Conventions shared by all tests: cluster bootstrap z by UTC day (`analyze.boot_z`), fee grid 10/2/0 bp or venue fees, two windows (full, 2025-26), non-overlapping trades, no look-ahead (signals from closed bars only). Verdict rule used throughout: a cell is alive only if net > 0 with z ≥ 2 in BOTH windows on the whole population, not a sample.

## Live tooling (measurement, not money)
- `src/kalshi_live/bot.py --paper` + `deploy/kalshi-bot.service`: logs the real Kalshi minute-1 ask on the CRSI + head-start signal.
- `src/okx_logger.py`, `src/okx_report.py`, `src/okx_select.py` + `deploy/okx-logger.*`: T14 reverse-carry logger and report.

## Summaries
`results/FINAL_SUMMARY.md` (T12–T19 verdicts), `results/T20_dex_carry.md` (the one small live candidate), `SERVER_RESULTS_ALL.md` (older T1–T11 plus T12 fill replay).
