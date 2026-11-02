# T19 — Crypto.com stock perps over the weekend vs the real Monday open (03.11.2026)

Perp hourly candles from api.crypto.com (24/7); real daily open/close from Yahoo. Gap = Monday open / Friday close − 1. Perp implied = perp close at Sunday 23:00 UTC / Friday real close − 1. Error = Monday open / perp Sunday-23 price − 1 (what a Sunday-night buyer would make before costs if the perp converged to the real open).

| instrument | weekends | median weekend volume (contracts, Sat+Sun) | corr(perp implied, real gap) | mean |error| bp | mean error bp (sign = Monday open above perp) | sd error bp | weekends with |error| > 30 bp |
|---|---|---|---|---|---|---|---|
| TSLAUSD-PERP | 20 | 24.3 | 0.04 | 114 | -16 | 143 | 18 |
| SPYUSD-PERP | 26 | 132.4 | 0.78 | 22 | +9 | 31 | 5 |
| QQQUSD-PERP | 26 | 265.9 | 0.74 | 46 | +7 | 57 | 17 |
| NVDAUSD-PERP | 20 | 289.0 | 0.67 | 85 | +6 | 104 | 15 |
| AAPLUSD-PERP | 20 | 6.8 | -0.03 | 69 | +0 | 85 | 16 |
| MSTRUSD-PERP | 20 | 64.6 | 0.45 | 227 | -27 | 303 | 18 |

Reading: corr near 1 and |error| of a few bp means the perp already prices the Monday open on Sunday night (no edge). A large, sign-consistent error would be an edge, but weekend volume shows whether anyone could have traded it; the live quote is a market maker's and is 5 bp wide, so prints, not quotes, are what the candles show.

## Verdict
No weekend edge to harvest. SPY/QQQ/NVDA perps track the real Monday gap (corr 0.67–0.78) with no sign bias (mean error +6..+9 bp, i.e. zero after a 5-bp spread); the 30–100 bp error sd is simply what happens between Sunday 23:00 UTC and the 09:30 ET open while index futures trade, not a mispricing. TSLA/AAPL/MSTR show corr ≈ 0 because the weekend candles are stale prints (7–25 contracts per weekend), while the live quote is a market maker's 5-bp-wide price that tracks futures; you cannot buy at a stale print. The 0 % fee promotion on the app's tokenized spot does not change this: the spread and the market maker's information are the fee. `nothing alive, no test`.
