#!/usr/bin/env python3 -I
"""Cross-sectional funding carry: at each 8h settlement rank symbols by trailing funding, long spot / short perp top-N.
PnL per 8h per position = spot_ret - perp_ret + funding received. Costs: fee per leg-side on turnover (taker 5+5 bp, maker 2+2 bp).
Liquidity filter: perp quote volume last 24h >= MINVOL USD. Writes results/T13_carry.md"""
import numpy as np, pandas as pd, os
C = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cache"); RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
P = pd.read_pickle(f"{C}/panel_perp.pkl"); S = pd.read_pickle(f"{C}/panel_spot.pkl"); V = pd.read_pickle(f"{C}/panel_qv.pkl"); F = pd.read_pickle(f"{C}/panel_fund.pkl")
sett = P.index[P.index.hour.isin([0, 8, 16])]
# 8h returns from settlement to settlement
Pp, Ss = P.loc[sett], S.loc[sett]
rp = Pp.pct_change().shift(-1); rs = Ss.pct_change().shift(-1)          # return over the NEXT 8h
fund_next = F.loc[sett].shift(-1)                                        # funding paid at the END of the next 8h (received by short if >0)
vol24 = V.rolling(24).sum().loc[sett]
def boot_z(x, B=2000, seed=1):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(1); return x.mean() / m.std(ddof=1)
def run(K, N, minvol, fee_leg, start="2022-02-01", end="2026-09-30", side="long_fund"):
    sig = F.loc[sett].rolling(K).mean()                                   # trailing K settlements avg funding (known at t)
    elig = (vol24 >= minvol) & sig.notna() & Pp.notna() & Ss.notna()
    s = sig.where(elig)
    if side == "long_fund": rank = s.rank(axis=1, ascending=False)
    else: rank = (-s).rank(axis=1, ascending=False)
    W = (rank <= N).astype(float); W = W.div(W.sum(1).replace(0, np.nan), axis=0).fillna(0)
    sgn = 1 if side == "long_fund" else -1
    # position PnL: long spot short perp (sgn=1): rs - rp + fund ; reversed for sgn=-1 (needs borrow; flagged)
    pos = sgn * (rs - rp) + sgn * fund_next
    gross = (W * pos).sum(1)
    turnover = (W - W.shift(1).fillna(0)).abs().sum(1)                    # fraction of book traded (both legs each)
    cost = turnover * 2 * fee_leg                                          # 2 legs
    net = gross - cost
    m = (net.index >= start) & (net.index <= end)
    g, n, to = gross[m], net[m], turnover[m]
    fy = (W * sgn * fund_next).sum(1)[m]; bas = (W * sgn * (rs - rp)).sum(1)[m]
    daily = n.groupby(n.index.floor("D")).sum()
    cum = (1 + n).cumprod(); dd = (cum / cum.cummax() - 1).min()
    yrs = (n.index[-1] - n.index[0]).days / 365.25
    return dict(K=K, N=N, minvol=minvol, fee=fee_leg, side=side, ann=float(cum.iloc[-1] ** (1 / yrs) - 1) * 100, sharpe=float(daily.mean() / daily.std() * np.sqrt(365)), z=float(boot_z(daily.values)),
                fund_ann=float(fy.mean() * 3 * 365) * 100, basis_ann=float(bas.mean() * 3 * 365) * 100, cost_ann=float((g - n).mean() * 3 * 365) * 100, turnover_day=float(to.mean() * 3), mdd=float(dd) * 100,
                by_year={str(y): float(((1 + n[n.index.year == y]).prod() - 1) * 100) for y in sorted(set(n.index.year))}, n_avg=float((W[m] > 0).sum(1).mean()))
rows = []
for K in [1, 3, 21]:
    for N in [5, 10, 20, 40]:
        for minvol in [2e6, 10e6]:
            for fee in [0.0005, 0.0002]:
                rows.append(run(K, N, minvol, fee))
R = pd.DataFrame(rows)
md = ["# T13 — cross-sectional funding carry (long spot / short perp, top-N by trailing funding), all Binance USDT perps with spot pair, 2022-02..2026-09\n",
      "K = settlements in trailing funding average (1 = last, 3 = 1 day, 21 = 1 week); N = positions; minvol = perp 24h quote volume filter; fee per leg-side (0.05% taker / 0.02% maker), charged on turnover × 2 legs. ann = annualised net return on gross notional of ONE leg (unlevered, cash fully deployed). z = daily bootstrap.\n",
      "| K | N | minvol | fee | ann net % | Sharpe | z | funding ann % | basis drift ann % | cost ann % | turnover/day | maxDD % | 2022 | 2023 | 2024 | 2025 | 2026 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in R.itertuples():
    by = r.by_year; md.append(f"| {r.K} | {r.N} | {r.minvol/1e6:.0f}M | {r.fee*1e4:.0f}bp | {r.ann:+.1f} | {r.sharpe:.2f} | {r.z:.1f} | {r.fund_ann:+.1f} | {r.basis_ann:+.1f} | {r.cost_ann:.1f} | {r.turnover_day:.2f} | {r.mdd:.1f} | " + " | ".join(f"{by.get(str(y), float('nan')):+.1f}" for y in range(2022, 2027)) + " |")
# benchmark: all eligible positive-funding, and reverse side (short spot needs borrow)
b = run(3, 1000, 2e6, 0.0002); md.append(f"\nBenchmark all-eligible positive-funding equal weight (K3, maker): ann {b['ann']:+.1f}%, Sharpe {b['sharpe']:.2f}, funding {b['fund_ann']:+.1f}%, basis drift {b['basis_ann']:+.1f}%, avg positions {b['n_avg']:.0f}")
rv = run(3, 10, 2e6, 0.0002, side="short_fund"); md.append(f"Reverse side (long perp / short spot, most negative funding, K3 N10 maker; ignores spot borrow cost): ann {rv['ann']:+.1f}%, Sharpe {rv['sharpe']:.2f}, by year " + ", ".join(f"{k}:{v:+.0f}" for k, v in rv['by_year'].items()))
best = R[(R.fee == 0.0002)].sort_values("sharpe", ascending=False).iloc[0]
md.append(f"\nBest maker cell: K{best.K} N{best.N} minvol {best.minvol/1e6:.0f}M -> ann {best.ann:+.1f}%, Sharpe {best.sharpe:.2f}, z {best.z:.1f}, 2025 {best.by_year.get('2025', float('nan')):+.1f}%, 2026 {best.by_year.get('2026', float('nan')):+.1f}%")
open(f"{RES}/T13_carry.md", "w").write("\n".join(md) + "\n"); R.to_pickle(f"{RES}/T13_carry.pkl"); print("\n".join(md[-3:]))
