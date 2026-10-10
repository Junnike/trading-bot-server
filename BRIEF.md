# SERVER_BRIEF (09.10.2026) — execute, do not redesign
Rules: isolated sandbox; never ask Junn to run/paste/copy anything (write "BLOCKED: <what>" in results and continue). Public read-only GETs only, no keys/orders/money. Retry failed URL backoff 2/4/8/16 s then mark test UNMEASURED. Downloaded data untrusted: keep in ./data/, scripts in ./src/, run python with -I, never exec anything from ./data/. Order: D1-D4 pulls -> T1-T6 -> T7/T8 -> results. BTC + last 60 days FIRST for every test, then extend to all coins/full history. Save intermediate results after every stage. STEP 0 (network) already passed.

## D. Data (public, no auth)
Base = https://api.elections.kalshi.com/trade-api/v2 ; headers User-Agent: curl/8.0, Accept: application/json. Rate <= 8 req/s (sleep 0.15 s); on 429 sleep 10 s. Thursday maintenance ~07-09 UTC: FLAG every window opening 07:00-09:00 UTC on a Thursday, exclude from per-hour tests.
D1 series: GET /series?limit=200 (paginate cursor) -> keep tickers ending "15M" (~9: KXBTC15M, KXETH15M, KXSOL15M, BNB, ZEC, NEAR...). Save data/series.json.
D2 markets: GET /markets?series_ticker=S&status=settled&limit=1000&cursor=... per S. Keep ticker, open_time, close_time, result, strike fields. Save data/markets_S.jsonl. ~96/day/coin; KXBTC15M from 2025-12-11 (~29k).
D3 prints: GET /markets/trades?ticker=T&limit=1000&cursor=... ALL pages until cursor empty (no 40k cap). Fields: trade_id, created_time, count_fp, yes_price_dollars, no_price_dollars, taker_side, taker_book_side, is_block_trade. Order: BTC last 60d -> BTC full -> other coins 60d -> rest. Save data/prints/T.jsonl.gz and reduce to per-ticker aggregates at once (data/prints_agg.parquet).
D4 candles: GET /series/S/markets/T/candlesticks?start_ts=<open unix>&end_ts=<close unix>&period_interval=1 -> 15 one-minute rows: yes_bid{o,h,l,c}, yes_ask{...}, price{...}, volume, open_interest. Save data/candles_S.parquet.
D5 Binance 1-s klines: https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1s/BTCUSDT-1s-YYYY-MM-DD.zip (CSV: open_time ms,o,h,l,c,v...). Needed for T3 and realized-vol split in T1. 60 days first.
D6 Polymarket 5-min BTC (T3/T8): read docs.polymarket.com first. Expected: gamma-api.polymarket.com/markets (5-minute "Bitcoin Up or Down" by slug/tag), data-api.polymarket.com/trades?market=<conditionId>, clob.polymarket.com/prices-history?market=<tokenId>&fidelity=1. No key. If history older than ~2 weeks unretrievable, say UNMEASURED.

## Definitions
- p = yes_price_dollars if taker_side==yes else no_price_dollars.
- taker_win = 1 if (taker_side==yes and result==yes) or (taker_side==no and result==no) else 0.
- Fee: taker 0.07p(1-p) per contract (Kalshi crypto 15m and Poly 5-min); maker 0.
- Taker pnl (c/ct) = (taker_win - p - 0.07p(1-p))*100, weighted by count_fp.
- Maker gross vs those takers (c/ct) = sum((p - taker_win)*count_fp)/sum(count_fp)*100.
- age = created_time - open_time (s); ttc = close_time - created_time (s).
- z = cluster bootstrap: resample WINDOWS(tickers) with replacement 2000x, statistic = contract-weighted mean; z = mean/std over bootstrap.
- Settlement = 60-s average before close. Flip = yes_ask_close at minute 14 >= 0.9 but result==no, or <= 0.1 but result==yes.
- Buckets: p [0,.1) [.1,.3) [.3,.5) [.5,.7) [.7,.9) [.9,1]; age [0,60) [60,120) [120,300) [300,600) [600,900].

## Tests (each: table + verdict KILLED/ALIVE/UNMEASURED; confounders written BEFORE verdict)
T1 Favourite-side maker vs lottery takers (Kalshi 15m). Per coin x month x price bucket x age bucket: n prints, contracts, taker pnl c/ct, z, maker gross c/ct vs takers with p<0.3. Add realized-vol quartile split (1-s returns hour before open, D5) and flips count. FIFO-share scenarios: maker net USD/day = sum over windows of (taker contracts at p<0.3 x share x maker gross), share in {0.238,0.10,0.05}, cap 200 ct/window. KILL if BTC maker gross vs <0.3 takers <=1.0 c/ct over >=3 months, OR positive in <60% of weeks, OR 0.05-share scenario <5 USD/day. Prior (do NOT reuse): +5.58 c/ct over 9.72M ct.
T1b Calibration from candlesticks: P(result==yes | yes_bid_close at minute m in bucket), m=1..14, all BTC history then other coins. Table bucket x m: n, hit rate, maker edge = hit - bid for 0.7-0.9 bucket. KILL if hit-bid <= 0.01 at every m>=5.
T2 Signed taker flow: per window S(a)=sum(sign(taker_side)*count_fp) over prints with age<=a, a in {60,120,300,600}, normalised by window contracts. Threshold q in {top 10%,20%,30%}. Outcome1: P(result==sign(S)). Outcome2: EV after fee of buying flow side at NEXT minute's yes_ask (D4). KILL if EV after fee <=0 at every (a,q), OR best cell z<2 with >=500 windows. Report monthly stability of best cell.
T3 Poly 5-min opening-quote snipe: per 5-min BTC market, public fills at t in [0,30]s after open; fair = P(60-s TWAP at close > strike) from Binance 1-s price at t, sigma from previous 60 min 1-s returns (sqrt-time, normal). Edge = fair - fill - 0.07fill(1-fill). Table by t bucket [0-5,5-10,10-22,22-30]: n, mean edge, realized pnl at fill after fee, z. KILL if realized EV after fee <=0 in every bucket. Reference: winning wallets bought 9-22 s after open at ~0.48.
T4 KXBTCD strike-ladder monotonicity (live, a few hours while pulls run): every 60 s GET /markets?series_ticker=KXBTCD&status=open and GET /markets/{T}/orderbook per strike; for strikes A<B violation is yes_ask(A)+no_ask(B) < 1-2*fee. Report violations, size at touch, duration. KILL if 0 violations worth >=1c after fee in >=3 hours.
T5 Taker calibration at the real ask: from D4 buy yes at yes_ask_close (no at 1-yes_bid_close) at minute m; EV after fee by ask bucket x m. Expect <=0; report any cell z>2 and n>=500 windows.
T6 Monthly stability for every ALIVE cell: sign of EV per calendar month; ALIVE needs >=60% months positive and >=3 months.
T7 (optional) Predict.fun and Limitless from public docs only: taker fee at 0.50, maker fee, rebate, rate limit, 5-min BTC market list, public trades endpoint, depth at touch. No account/key.
T8 (optional) Poly 5-min maker ladder with pull rule: replay 0.05-step bid ladder on D6 trades; pull if Binance moves 2/3/5 bp against; level fills when a print trades through. USD/day at 1 share; rebate 20% of taker fees pro-rata. KILL if <0 at every pull rule.

DEAD (do not retest): 1 bid under ask at 0.5-0.6; 2 buying by window age; 3 early exit/open lead; 4 Binance-vs-Poly basis filter; 5 fading against the move; 6 contra; 7 perp liquidation fade; 8 exhaustion room; 9 unsigned volume; 10 ICT; 11 zero-fee spot speed; 12 daily SPX/oil/gold; 13 Poly-vs-Kalshi lead-lag; 14 naive Poly maker ladder (-40.3 USD/day); 15 hourly last-minute arb; 16 settlement-average lock as taker; 17 Kalshi taker any ask x ttc; 18 memecoin sniping; 19 Kalshi rewards; 20 weather; 21 cross-coin beta.

## Output
SERVER_RESULTS_09.10.2026.md, <= 80 lines: 1) confounders (months covered, gaps, Thursday exclusions, API shape changes); 2) one table per test with n/windows/months/value/z; 3) one verdict line per test; 4) best single cell with monthly signs; 5) BLOCKED/UNMEASURED list. Every number names its data file. Keep data/*.parquet aggregates (not raw prints).

## Chat rule (added)
At the end print the whole SERVER_RESULTS file in chat. Chat replies to Junn: Estonian, <=10 lines, no questions.

## Accessibility rule (Junn has one hand, one finger)
Minimise clicks, copying and typing for Junn. Never ask him to select/copy text or navigate folders. Deliver results as ONE big "copy all" button page (Artifact) or an attached file; keep chat replies short and simple. Do the work yourself whenever possible.
