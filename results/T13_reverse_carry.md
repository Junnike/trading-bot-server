# T13b — reverse funding carry with REAL borrow costs (02.11.2026)

Strategy: at each 8h settlement, long perp / short spot on the 10 eligible coins with the most NEGATIVE trailing-1-day funding (longs are paid). Eligibility: perp 24h volume >= 10M USD, |perp/spot-1| < 2 %, listing/delisting buffers, and Binance cross-margin borrow available for the coin. Equal weight, hysteresis-free (rebalance every 8h), maker 2 bp per leg-side on turnover.

Borrow data: Binance public margin spec (data/binance_margin_spec.json, pulled 02.11.2026, VIP0 daily rate and borrow limit per coin). Rates are TODAY's, applied to 2025-26 history: that understates cost, because borrow rates rise exactly when shorts crowd in (which is when funding is most negative).

| component, 2025-01..2026-09, borrowable coins only (87.6 % of basket slots) | %/yr on one-leg notional |
|---|---|
| funding received by long perp | +120 |
| basis drift (perp vs spot) | −17 |
| borrow interest (VIP0, today's rates, time-weighted 51.6 % APR) | −51 |
| maker fees on turnover | −22 |
| **net** | **+29** (2025 +25, 2026 +27), daily Sharpe 4.2 |

Basket composition 2025-26: rotates over 379 symbols, top names MOVE, BERA, BIO, KAITO, AXS, 0G, REZ, SKL, OM, NMR (each 1-2 % of slots). Funding paid to longs on these: 75-195 %/yr. VIP0 borrow APR: 19-73 %/yr.

Capacity: VIP0 borrow limits are tiny: median 4,074 USD per coin; 285 of 311 borrowable basket coins have a limit below 20k USD. With 10 positions the whole strategy caps at roughly 20-40k USD notional at VIP0 (more at higher VIP tiers, 2x per tier). This is a small-account strategy by construction, which is also why it has not been arbitraged away.

Risks not in the numbers: (1) historical borrow rates unknown, likely higher than today's in the worst slots; (2) "borrow limit" is not "borrow available": Binance often shows insufficient pool balance on newly listed coins; (3) two illiquid legs: slippage on 30-70M-volume perps and thinner spot books; (4) a basket coin can be delisted from margin mid-trade (forced repayment); (5) perp side needs margin, spot short needs collateral: real capital ~2x one-leg notional, so ~+15 %/yr on capital, before leverage; (6) 2022-24 not tested with borrow (funding regime differed).

Venue: needs alt perps AND alt margin borrow on the same exchange: Binance (tested), OKX (public lending rate for MOVE 20 %/yr, API reachable), Bybit (API geo-blocked from this sandbox, unmeasured). Kraken does not list these coins.

Cheapest real-money test: 1 coin from the current basket, ~1,000 USD per leg, 7 days, on Binance or OKX margin: record realised borrow APR, fill slippage on both legs, and funding received. Pass if realised net > +10 %/yr annualised over the week. That is the only test in T12-T13 worth running.

## OKX borrow check (02.11.2026, data/okx_loan_quota.json, results/T13_okx_borrow.csv)

OKX public loan-quota endpoint gives a DAILY basic-tier borrow rate and quota per coin (rate ≈ its Simple-Earn lending rate). OKX lists margin for 262 USDT pairs vs ~318 basket coins borrowable on Binance; only 9 of the top-25 Binance basket names (MOVE, BERA, BIO, KAITO, AXS, AGLD, API3, SEI, AVNT) have OKX margin.

| venue, 2025-01..2026-09, 10 names, maker 2 bp | distinct coins | funding | basis | borrow | fees | net %/yr | 2025 / 2026 | Sharpe |
|---|---|---|---|---|---|---|---|---|
| Binance VIP0 only | 318 | +111 | −17 | −50 | −21 | **+24** | +19 / +24 | 3.7 |
| OKX basic tier only | 149 | +51 | −3 | −14 | −19 | **+15** | +14 / +13 | 3.8 |
| cheapest venue per coin (both accounts) | 318 | +111 | −17 | −40 | −21 | **+35** | +30 / +30 | 5.3 |

OKX is 2-3x cheaper to borrow (MOVE 20 %, BERA 20 %, KAITO 19 %, AXS 11 %, SEI 16 % APR vs Binance 41-66 %) but its margin universe misses the freshest listings where funding is most negative, so the OKX-only basket earns half the funding. OKX quotas are larger: median 16k USD per coin (Binance 4k), 82 of 149 below 20k. Same caveat as above: today's rates applied to history, and quota ≠ availability.

Practical reading: Binance for coverage, OKX for cost; two accounts and routing each coin to the cheaper venue gives the best number, +35 %/yr on one-leg notional, ≈ +17 % on capital unlevered. Capacity realistic for 10-50k USD.
