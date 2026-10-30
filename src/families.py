#!/usr/bin/env python3 -I
"""Three signal-family tests on cached Binance.vision data: funding-extreme carry, BTC->alt lead-lag, daily breakout.
Writes results/T12c_families.md"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import boot_z, CACHE, RES, SYMS
WINDOWS = {"full": ("2020-01-01", "2026-09-30 23:59:59"), "2025+": ("2025-01-01", "2026-09-30 23:59:59")}
def st(df, fee):
    out = {}
    for w, (t0, t1) in WINDOWS.items():
        s = df[(df.t >= t0) & (df.t <= t1)]
        if len(s) < 15: out[w] = None; continue
        days = (pd.Timestamp(t1, tz="UTC") - pd.Timestamp(t0, tz="UTC")).days
        g = s.bp.mean(); out[w] = dict(n=len(s), wr=(s.bp > 0).mean()*100, gross=g, net=g-fee, z=boot_z(s.bp.values, s.day.values), evday=(g-fee)*len(s)/days, mdd=mdd(s.bp.values-fee))
    return out
def mdd(x):
    c = np.cumsum(x); return float((c - np.maximum.accumulate(c)).min())
def nonoverlap(idx, hold):
    keep, last = [], -1
    for i in idx:
        if i >= last: keep.append(i); last = i + hold
    return np.array(keep, int)
def row(name, r):
    cells = []
    for w in WINDOWS:
        x = r[w]
        cells.append("n/a" if x is None else f"{x['net']:+.1f} (z {x['z']:.1f}, WR {x['wr']:.0f}%, n {x['n']}, mdd {x['mdd']:.0f})")
    return f"| {name} | " + " | ".join(cells) + " |"
hdr = "| test | full 2020-26: net bp/trade (z, WR, n, max DD bp) | 2025-26 |\n|---|---|---|"
md = ["# T12c — three signal families on public Binance.vision data (spot/perp 5m, funding)\n", "net = gross − fee; fee 10 bp taker RT unless stated; z = UTC-day cluster bootstrap of gross; trades non-overlapping.\n"]

# ---------- 1. funding-extreme carry (perp) ----------
md.append("\n## 1. Funding-extreme carry (perp): enter at settlement when funding is in the tail of its trailing 90-day distribution, hold N settlements, collect funding\n" + hdr)
for sym in SYMS:
    f = pd.read_pickle(f"{CACHE}/funding_{sym}.pkl"); p = pd.read_pickle(f"{CACHE}/perp_{sym}_5m.pkl")
    f = f[f.index.hour.isin([0, 8, 16])]
    q95 = f.rolling(270, min_periods=180).quantile(0.95).shift(1); q05 = f.rolling(270, min_periods=180).quantile(0.05).shift(1)
    px = p.open.reindex(f.index)  # price at settlement
    for side, name, cond in [(-1, "short when funding>p95", f > q95), (1, "long when funding<p05", f < q05)]:
        for hold in [1, 3]:
            idx = np.where(cond.values & ~px.isna().values)[0]; idx = idx[idx + hold < len(f)]
            idx = nonoverlap(idx, hold)
            ent, ex = px.values[idx], px.values[idx + hold]
            ok = ~np.isnan(ex)
            fund = sum(f.values[idx + j] for j in range(1, hold + 1))  # settlements received/paid during hold
            bp = side * 1e4 * (ex - ent) / ent - side * fund * 1e4   # short receives positive funding
            d = pd.DataFrame({"t": f.index[idx][ok], "bp": bp[ok]}); d["day"] = d.t.dt.floor("D")
            md.append(row(f"{sym[:-4]} {name}, hold {hold*8}h", st(d, 10)))

# ---------- 2. BTC -> alt lead-lag (spot 5m) ----------
md.append("\n## 2. BTC→alt lead-lag (spot 5m): BTC 5m return beyond ±thr → trade alt in same direction at next 5m open, hold H bars\n" + hdr)
btc = pd.read_pickle(f"{CACHE}/spot_BTCUSDT_5m.pkl"); rb = btc.close.pct_change() * 100
for sym in SYMS[1:]:
    a = pd.read_pickle(f"{CACHE}/spot_{sym}_5m.pkl")
    j = pd.DataFrame({"rb": rb}).join(a[["open", "close"]], how="inner").dropna()
    ts = j.index.asi8 // 60_000; contig = np.r_[False, np.diff(ts) == 5]
    for thr in [0.5, 1.0]:
        for hold in [1, 3]:
            for side, cond in [(1, j.rb.values > thr), (-1, j.rb.values < -thr)]:
                idx = np.where(cond)[0]; idx = idx[idx + hold < len(j)]
                ok = np.ones(len(idx), bool)
                for k in range(1, hold + 1): ok &= contig[idx + k]
                idx = nonoverlap(idx[ok], hold)
                e = idx + 1; bp = side * 1e4 * (j.close.values[idx + hold] - j.open.values[e]) / j.open.values[e]
                d = pd.DataFrame({"t": j.index[e], "bp": bp}); d["day"] = d.t.dt.floor("D")
                md.append(row(f"{sym[:-4]} BTC {'>' if side==1 else '<'} {'+' if side==1 else '-'}{thr}% → {'long' if side==1 else 'short'}, hold {hold*5}m", st(d, 10)))

# ---------- 3. daily breakout (spot 1d) ----------
md.append("\n## 3. Daily breakout (spot): close > prior N-day high → long next open; exit next open after close < prior M-day low. Fee 10 bp RT. Per-trade bp; also total return and trades/yr\n")
md.append("| test | full: net bp/trade (z, WR, n, mdd) | 2025-26 | full total net % | trades/yr | buy&hold full % |\n|---|---|---|---|---|---|")
for sym in SYMS:
    k5 = pd.read_pickle(f"{CACHE}/spot_{sym}_5m.pkl")
    d1 = k5.resample("1D").agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last")).dropna()
    for N, M in [(50, 20), (20, 10), (100, 50)]:
        hi = d1.high.rolling(N).max().shift(1); lo = d1.low.rolling(M).min().shift(1)
        c, o = d1.close.values, d1.open.values; trades = []; i = N
        while i < len(d1) - 2:
            if c[i] > hi.values[i]:
                e = i + 1; x = e
                while x < len(d1) - 1 and not (c[x] < lo.values[x]): x += 1
                x = min(x + 1, len(d1) - 1)  # exit next open after the breakdown close
                trades.append((d1.index[e], 1e4 * (o[x] - o[e]) / o[e])); i = x
            else: i += 1
        d = pd.DataFrame(trades, columns=["t", "bp"]); d["day"] = d.t.dt.floor("D")
        r = st(d, 10); tot = (np.prod(1 + (d.bp - 10) / 1e4) - 1) * 100 if len(d) else np.nan
        yrs = (d1.index[-1] - d1.index[0]).days / 365.25; bh = (c[-1] / o[N] - 1) * 100
        md.append(row(f"{sym[:-4]} {N}d high / {M}d low", r)[:-2] + f" | {tot:+.0f}% | {len(d)/yrs:.1f} | {bh:+.0f}% |")
open(f"{RES}/T12c_families.md", "w").write("\n".join(md) + "\n"); print("ok")
