# T15 — "exit before the last minute" test on Kalshi BTC 15m (02.11.2026)

Data: 7,633 random settled KXBTC15M windows 2025-12..2026-10 with 1-minute yes_bid/yes_ask (data/kalshi/candles.jsonl, same sample as T12 bid fill replay).
Question: is the last minute rigged against the holder (so that selling at minute 13-14 beats holding to settlement)?

## 1. Minute-14 calibration (mid price vs share that settles YES)
| mid at m14 | n | mid | settles YES | YES − mid (c) |
|---|---|---|---|---|
| [0,.1) | 3207 | .012 | .008 | −0.4 |
| [.1,.3) | 380 | .180 | .129 | −5.1 |
| [.3,.5) | 211 | .395 | .346 | −4.9 |
| [.5,.7) | 238 | .585 | .588 | +0.3 |
| [.7,.9) | 338 | .815 | .867 | +5.2 |
| [.9,.95) | 221 | .926 | .982 | +5.6 |
| [.95,.99) | 594 | .975 | .971 | −0.3 |
| [.99,1] | 2444 | .997 | .999 | +0.2 |

Flip rate: priced ≥ .90 at minute 14 and settles NO: **0.71 %** (n 3,259); priced ≤ .10 and settles YES: 0.78 % (n 3,218). At minute 13: 1.9 %. Median spread at m14 0.3c, at m13 1.0c.
The last minute is NOT a 13 % bleed on Kalshi. A contract that is "won" at minute 14 loses 0.7 % of the time, which is what one minute of BTC volatility produces. If anything the m14 price is slightly too cheap for the favourite (.7-.95 buckets settle 5c above price): holders are paid for the last minute, not robbed.

## 2. Hold vs exit, T1b cell (buy YES at bid_7 in [.70,.90), maker fee 0; exit = sell at bid_m, taker fee ceil(0.07·p·(1−p)))
| | hold to settle | exit m12 | exit m13 | exit m14 |
|---|---|---|---|---|
| EV c/contract (n 1,646) | **+2.67** | −0.36 (no fee +0.87) | +0.43 (no fee +1.59) | +0.09 (no fee +1.16) |
| months positive of 11 | 8 | | | 5 |
Exiting early loses 1.1-2.3c even BEFORE the exit fee: the price at m14 is below the settlement expectation (see §1), and the taker fee and spread take the rest.

## 3. Generic taker entry (buy YES at ask_7, all 7,633 windows)
hold −2.64c vs exit at m14 −4.58c. Mean move from bid_14 to settlement is +1.05c in the holder's favour.

## Verdict
Exit-before-the-last-minute is DEAD on Kalshi: it costs 1-2.5c per contract versus holding, in every variant, and the premise (a rigged last minute) does not appear in the data: the flip rate is 0.7 %, not 13 %. The 13 % figure from the earlier session was the share of 15-minute candles whose colour on the venue's resolution source differs from Binance's candle; that is a resolution-source mismatch that the market price already incorporates by minute 14, not a last-minute manipulation, and the robots' 61 % Binance win rate never applied to it. Polymarket: not testable here (no quote history), but the same logic holds: whatever the resolution rule, the minute-14 price is the market's own estimate of it, and selling into it pays spread plus fee for nothing.
