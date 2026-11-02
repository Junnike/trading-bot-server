# T14 — one-week live test plan: reverse funding carry on OKX (written 02.11.2026)

## 0. Purpose and pass/fail
Purpose: measure the three things the backtest cannot see: realised borrow cost, realised fills on both legs, and whether borrow is actually available. Not to make money.
PASS if, over 7 full days, realised net (funding received − borrow interest − fees − slippage − basis change) annualises above +10 %/yr on one-leg notional AND borrow was available on every attempted entry.
FAIL otherwise. A fail on availability alone kills the strategy as designed (coverage), a fail on cost alone sends the borrow assumption back to the backtest.

## 1. Capital and size
- Total at risk: 3,000 USDT in the OKX account. Position: 1,000 USDT notional per leg, ONE coin at a time (the test is about measurement, not diversification). 1,000 USDT spare as margin buffer on both sides.
- Never more than 40 % of the coin's basic-tier borrow quota (quota column in the screen), so the loan is small relative to the pool.
- Hard loss limit for the week: 150 USDT (5 %). Hit it, close everything, test over.

## 2. Account setup (one-time, before day 1)
- OKX account mode: Multi-currency margin (so one USDT balance collateralises both the spot-margin short and the perp long). Confirm maker fee tier (basic: 0.08 % spot maker, 0.02 % perp maker; check the fee page for your tier, the backtest used 0.02 % per leg-side, so spot maker at 0.08 % is 4x worse than assumed: record it).
- Enable spot margin trading and auto-borrow for the margin pair. Set perp leverage 3x isolated or cross at low utilisation; the hedge means price risk is near zero, but liquidation on either leg must be impossible for a ±30 % move.
- API key read-only for logging; trading can be manual for one coin. Keep keys off the droplet unless the logger needs them (public endpoints cover prices, funding and quotas; only balances, borrow interest and fills need the private key).

## 3. Coin selection (public data, src/okx_select.py)
Run `python3 -I src/okx_select.py 15` right before entry. Pick the first coin that satisfies ALL:
- net carry (funding to longs − borrow APR) ≥ +40 %/yr,
- perp 24h volume ≥ 2 M USD and spot 24h volume ≥ 1 M USD (thin books are the main slippage risk; OKX alt perps trade far less than Binance's),
- borrow quota in USD ≥ 2,500 (so 1,000 USDT is ≤ 40 % of it),
- |basis| ≤ 0.5 %,
- not listed in the last 14 days, no delisting or margin-removal notice on OKX announcements.
Snapshot 02.11.2026 14:00 UTC for reference: ZK +58 % funding / 7 % borrow but only 1.3 M perp volume; ATOM +50 / 22 with 2.7 M volume and 51k quota is the only name meeting every rule today. The screen changes every funding interval (4 h on many OKX perps, 8 h on others: the interval is in the last column).

## 4. Entry (post-only, both legs within 5 minutes)
1. Spot leg: on the margin pair, place a post-only SELL limit at the best ask for 1,000 USDT worth, auto-borrow fills the coin. Record borrowed amount, timestamp, fill price, fee.
2. Perp leg: post-only BUY limit at best bid for the same coin quantity (not the same USDT: match the coin amount so the hedge is exact). Record fill price, fee, contract size rounding.
3. If either leg is not filled within 10 minutes, cancel both, note it as a fill failure, retry next funding interval. Three failures on a coin = switch coin.
4. Enter 10-30 minutes BEFORE a funding timestamp so the first payment is collected quickly; entry must be complete before the timestamp.

## 5. Hold and logging (every funding interval, automated on the droplet)
Log one row per funding timestamp to a CSV: time, coin, perp mark, spot last, basis %, funding rate, funding received (USDT, from the bills endpoint), borrow interest accrued (USDT, from the margin interest endpoint), borrowed amount, unrealised PnL both legs, equity. Also log every fill and every failed order.
Daily manual check (once): announcements for the coin (delisting, margin removal, funding-rate cap change), quota still above the loan, margin ratio on both legs above 300 %.

## 6. Exit rules (whichever first)
- Funding to longs annualised falls below the borrow APR for 2 consecutive intervals (the carry has gone): close both legs post-only, re-run the screen, enter the next coin. Expect 1-3 switches in a week; each switch costs ~4 fees plus slippage and is part of what we measure.
- |basis| > 2 % at any logging point: close (something is wrong with the pair).
- Margin ratio on either leg below 200 %, borrow quota cut below the loan, or any delisting notice: close immediately with market orders and log the cost.
- Day 7 at 00:00 UTC: close everything regardless.

## 7. Metrics to compute at the end
Per interval and total: funding received, borrow interest, fees (spot + perp), slippage (fill price vs mid at order time, both legs, entry and exit), basis PnL (perp vs spot drift). Realised net = sum. Annualise on 1,000 USDT one-leg notional. Also: number of fill failures, number of coin switches, hours with borrow unavailable, maximum margin utilisation.
Compare each line to the backtest assumption: borrow APR used (OKX basic rate), fees 2 bp per leg-side, zero slippage, basis drift −3 %/yr. Write the deltas into results/T14_live_result.md.

## 8. What can go wrong, in order of likelihood
1. Borrow pool empty for the chosen coin (quota shown, nothing lendable). Counts as an availability fail; try the next coin, record it.
2. Spot maker fee 0.08 % instead of 0.02 %: alone this is −6 %/yr at the backtest turnover; measure, do not assume.
3. Thin perp book: a 1,000 USDT post-only order may sit unfilled or fill in pieces across a moving mid. Slippage log catches it.
4. Funding flips positive within hours (these coins are volatile in funding, not just price). That is why the exit rule is two intervals, not one.
5. Coin pumps 50 % in a day: hedge holds, but the short spot loan grows in USDT terms and margin ratio drops. The 1,000 USDT buffer covers ±30 %; beyond that, reduce or close.

## 9. Deliverable
A CSV log, the filled T14_live_result.md with the deltas above, and a one-line verdict: PASS / FAIL (availability) / FAIL (cost). If PASS, the next step is the 10-coin basket with 500 USDT per leg on the cheapest-venue routing (Binance + OKX) from results/T13_reverse_carry.md; if FAIL, the strategy is dead and the project has no live candidate.
