#!/usr/bin/env python3 -I
"""Spot-perp basis tests on the hourly panel.
 1. Basis mean reversion: b = perp/spot - 1 (hourly). z = (b - mean_7d)/sd_7d. Enter when |z|>=2 (sell rich leg / buy cheap leg), exit when |z|<=0.5 or after 24h. PnL = convergence of basis + funding accrued; cost 2 legs each way.
 2. Basis as predictor of next-8h perp return (cross-sectional): rank by b at settlement, long low-basis short high-basis perp (needs no spot).
Writes results/T13_basis.md"""
import numpy as np, pandas as pd, os
C = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cache"); RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
P = pd.read_pickle(f"{C}/panel_perp.pkl"); S = pd.read_pickle(f"{C}/panel_spot.pkl"); V = pd.read_pickle(f"{C}/panel_qv.pkl"); F = pd.read_pickle(f"{C}/panel_fund.pkl").fillna(0)
liq = V.rolling(24).sum() >= 10e6
B = (P / S - 1).where(liq)
def boot_z(x, B_=2000, seed=1):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; rng = np.random.default_rng(seed)
    if len(x) < 10: return np.nan
    m = x[rng.integers(0, len(x), (B_, len(x)))].mean(1); return x.mean() / m.std(ddof=1)
md = ["# T13 — spot/perp basis (hourly, all USDT perps with spot pair, 24h perp volume >= 10M)\n"]
# 1. mean reversion
mu = B.rolling(168, min_periods=100).mean(); sd = B.rolling(168, min_periods=100).std(); Z = ((B - mu) / sd).shift(1)   # z known at bar open
bz = B.values; zz = Z.values; fv = F.values; T, Nn = bz.shape
md.append("## 1. Basis mean reversion (enter |z|>=2 vs 7-day mean, exit |z|<=0.5 or 24h; PnL = basis convergence in direction of trade + funding carried; fee per leg-side)\n")
md.append("| year | n trades | gross bp/trade | +funding bp | net @2bp maker (4 legs = 8 bp) | net @5bp taker (20 bp) | z | median hold h |\n|---|---|---|---|---|---|---|---|")
rows = []
for j in range(Nn):
    i = 0
    while i < T - 1:
        z0 = zz[i, j]
        if np.isnan(z0) or abs(z0) < 2 or np.isnan(bz[i, j]): i += 1; continue
        side = -np.sign(z0)   # z>0: perp rich -> short perp long spot (profit when basis falls) => pnl = -(b_exit-b_entry); funding received if rate>0
        k = i + 1; fund = 0.0
        while k < min(i + 24, T - 1) and not (abs(zz[k, j]) <= 0.5 if not np.isnan(zz[k, j]) else False):
            fund += fv[k, j] * side * -1 * -1 if False else 0; k += 1
        # funding: short perp (side=-1) receives +rate at settlements inside (i,k]; long perp pays
        fund = -side * np.nansum(fv[i + 1:k + 1, j]) * -1
        if np.isnan(bz[k, j]): i = k + 1; continue
        gross = side * (bz[k, j] - bz[i, j]) * 1e4
        rows.append((B.index[i], B.index[i].year, gross, (-side) * np.nansum(fv[i + 1:k + 1, j]) * 1e4 * -1 * -1 if False else side * -1 * np.nansum(fv[i + 1:k + 1, j]) * 1e4 * -1, k - i))
        i = k + 1
D = pd.DataFrame(rows, columns=["t", "year", "gross", "fund", "hold"])
D["fund"] = D["fund"]  # sign: side=-1 (short perp) receives positive funding -> computed above as (+rate)
for y, g in list(D.groupby("year")) + [("ALL", D)]:
    tot = g.gross + g.fund
    md.append(f"| {y} | {len(g)} | {g.gross.mean():+.1f} | {g.fund.mean():+.1f} | {(tot - 8).mean():+.1f} | {(tot - 20).mean():+.1f} | {boot_z(tot.values):.1f} | {g.hold.median():.0f} |")
# 2. cross-sectional basis -> next 8h perp return
sett = P.index[P.index.hour.isin([0, 8, 16])]
Bs = B.loc[sett]; rp = P.loc[sett].pct_change().shift(-1); fn = F.loc[sett].shift(-1)
md.append("\n## 2. Cross-sectional: at each 8h settlement rank by basis; long perp lowest-basis decile, short perp highest-basis decile (perp only, funding included: long pays, short receives). Net of 5 bp per side per rebalance (full turnover assumed).\n")
md.append("| year | n periods | long low-basis 8h bp | short high-basis 8h bp | L/S gross bp per 8h | funding bp | net @5bp taker | ann % | z |\n|---|---|---|---|---|---|---|---|---|")
rk = Bs.rank(axis=1, pct=True)
lo = (rk <= 0.1).astype(float); hi = (rk >= 0.9).astype(float)
lo = lo.div(lo.sum(1).replace(0, np.nan), axis=0); hi = hi.div(hi.sum(1).replace(0, np.nan), axis=0)
rl = (lo * rp).sum(1); rh = (hi * rp).sum(1); fl = -(lo * fn).sum(1); fh = (hi * fn).sum(1)
ls = rl - rh; fund = fl + fh
for y in sorted(set(sett.year)) + ["ALL"]:
    m = (sett.year == y) if y != "ALL" else np.ones(len(sett), bool)
    g = ls[m] * 1e4; f_ = fund[m] * 1e4; net = g + f_ - 2 * 2 * 5   # 2 legs each side, full turnover
    md.append(f"| {y} | {m.sum()} | {rl[m].mean()*1e4:+.1f} | {rh[m].mean()*1e4:+.1f} | {g.mean():+.1f} | {f_.mean():+.1f} | {net.mean():+.1f} | {net.mean()*3*365/100:+.1f} | {boot_z((g+f_).values):.1f} |")
open(f"{RES}/T13_basis.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
