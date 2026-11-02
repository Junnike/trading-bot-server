# T16 — the "last 60 seconds": what the TWAP rule does and whether it can be traded (03.11.2026)

## 1. The rule (verified from the venues' own text)
- Kalshi KXBTC15M rules_primary (API): YES iff the simple average of the 60 seconds of CF Benchmarks BRTI before the close ≥ the simple average of the 60 seconds of BRTI before the open.
- Polymarket BTC Up/Down 15m description (gamma API): Up iff the Chainlink BTC/USD 60-second TWAP stream at the end of the range ≥ its value at the start. In force since 14 Aug 2026 (30-second window 7–14 Aug, point price before).
Both venues therefore settle on "last-minute average vs pre-open-minute average" on an index that is not Binance. Junn was right about the mechanism.

## 2. What it does to a candle-direction robot (data: 7,365 Kalshi windows Dec 2025–Oct 2026, 7,776 Polymarket markets Aug–Oct 2026, Binance 1-s klines as index proxy)
| | Kalshi | Polymarket |
|---|---|---|
| Binance candle colour (close ≥ open) agrees with settlement | 93.5 % | 93.9 % |
| Binance 60-s TWAP label agrees with settlement | 98.7 % | 98.3 % |
| in contested windows (two averages within 5 bp, ~35 % of all) | — | 94.4 % |
So 6–7 % of candles settle the other way from the Binance candle: the "13 %" from the earlier session is not reproduced here, but the direction is the same. A 61 % Binance-candle robot is ≈ 55–56 % on the venue's outcome, below the ~63 % break-even. That is the bleed, and it is in the rule, not in the last minute.

## 3. Does exiting before the last minute help? (T15, Kalshi 7,633 windows)
No. Contracts priced ≥ .90 at minute 14 lose 0.7 %; the minute-14 price already reflects the TWAP rule. For the minute-7 bid entry: hold +2.67c vs exit at m14 +0.09c (+1.16c before the exit fee). Selling into the last minute pays spread and fee for nothing.

## 4. Can the rule be traded the other way — the last-minute sniper? (src/kalshi/k6_twap_sniper.py, src/poly/p2_sniper.py)
At second k of the closing minute, k/60 of the closing average is known. Model: P(close avg ≥ open avg) from the partial average + current price + a random-walk forecast of the remaining seconds (1-s vol from the window). Fire when P ≥ threshold and the tape still prints the certain side at ≤ 0.90 at least 2 s later; taker fee 0.07·p·(1−p); one trade per window.

| venue, variant | fires / window | hit % (claimed ≥ 97–99.9) | EV c/contract | z | months > 0 |
|---|---|---|---|---|---|
| Kalshi, any print, P ≥ .99 | 9.0 % | 81 | +8.6 | 6.0 | 8/11 |
| Kalshi, aggressor-side fills, P ≥ .99, 2 s | 5.9 % | 73 | +4.6 | 2.6 | 8/11 |
| Kalshi, aggressor-side, P ≥ .999, 5 s | 3.6 % | 66 | +2.9 | 1.3 | 7/11 |
| Polymarket, any print, P ≥ .99 | 10.1 % | 80 | +3.5 | 2.6 | 3/3 |
| Polymarket, aggressor-side, P ≥ .99, 2 s | 9.4 % | 78 | +3.0 | 2.1 | 2/3 |
| Polymarket, aggressor-side, P ≥ .999, 5 s | 5.0 % | 70 | −0.5 | −0.3 | 1/3 |

Kalshi by month, aggressor-side P ≥ .99 / 2 s (EV c, fires): Dec +28/33, Jan +15/51, Feb +2/30, Mar +2/21, Apr +8/32, **May −6/52, Jun +2/34, Jul −4/36, Aug +8/63, Sep −5/53, Oct +5/31**. Last six months: 269 fires, EV −0.23c, hit 68 %, median print 18 contracts (≈ 12 USD), ≈ 6 fires/day across all windows → ≈ 0 USD/day.
Calibration: claimed 97–100 % hits only 79–89 % on Kalshi and 80–85 % on Polymarket. The misses are index-proxy error (Binance ≠ BRTI/Chainlink) concentrated in exactly the contested windows where the sniper fires.

## 5. Verdict
- The last minute is not a scam on the holder; it is a different outcome definition. The 6–7 % candle mismatch is the whole cost, and no exit timing recovers it.
- The sniper edge that the rule creates was real on Kalshi Dec 2025–Apr 2026 (+15 to +28c per contract) and is gone since May 2026: with realistic fills it is 0 ± 1c, print sizes of 10–20 contracts, and the counterparties who used to sell out at 0.65 at second 20 are no longer there. On Polymarket it is +3c with optimistic fills and ≤ 0 at 5 s latency, with a worse proxy.
- To revive it you would need the actual index feed (BRTI or the Chainlink stream, both paid), sub-second execution, and even then the capacity is a few dollars per fire. `nothing alive, no test`.

## 6. What this means for the robots
A direction robot for these venues must be trained and scored on the venue's own label: 60-s average before close vs 60-s average before open, built from 1-s index data, not on Binance candles. That re-labelling is one line in the pipeline (`src/kalshi/k6_twap_sniper.py::closes`) and costs nothing; if the robots' 61 % on candles drops to 55 % on the TWAP label, they were never 61 % for this purpose. Files: results/T16_twap_sniper.md (Kalshi), results/T16_poly_twap_sniper.md (Polymarket), results/T15_last_minute_exit.md, data pulls src/kalshi/k5_trades_last2.py, src/poly/p1_pull.py, src/download_1s.py.
