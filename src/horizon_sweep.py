#!/usr/bin/env python3 -I
"""Hold-horizon sweep: CRSI(2,2,75)<=20 on 15m/1h/4h/1d spot candles, enter next open, hold 1/2/4/8 bars.
Also an inverted test (CRSI>=80 -> short) and a CRSI<=20 on daily with longer holds. Writes results/T12b_horizon.md"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import crsi, boot_z, CACHE, RES, SYMS
TFS = {"15m": 15, "1h": 60, "4h": 240, "1d": 1440}; HOLDS = [1, 2, 4, 8]
WINDOWS = {"full": ("2020-01-01", "2026-09-30 23:59:59"), "2025+": ("2025-01-01", "2026-09-30 23:59:59")}

def candles(sym, tf):
    k5 = pd.read_pickle(f"{CACHE}/spot_{sym}_5m.pkl")
    k = k5.resample(f"{TFS[tf]}min", label="left", closed="left").agg(open=("open","first"), close=("close","last"), n5=("open","count"))
    k = k[k.n5 > 0]; k["complete"] = k.n5 >= TFS[tf] // 5 * 0.9   # allow maintenance gaps inside long candles
    return k

def trades(k, tf, hold, thr=20, side=1):
    c = crsi(k.close.values); ts = k.index.asi8 // 60_000
    contig = np.r_[False, np.diff(ts) == TFS[tf]]
    okh = pd.Series(contig & k.complete.values).rolling(80, min_periods=80).min().fillna(0).values.astype(bool)
    sig = ((c <= thr) if side == 1 else (c >= 100 - thr)) & okh
    idx = np.where(sig)[0]; idx = idx[idx + hold < len(k)]
    # entry bar e=idx+1 .. exit bar idx+hold must be contiguous
    ok = np.ones(len(idx), bool)
    for j in range(1, hold + 1): ok &= contig[idx + j] & k.complete.values[idx + j]
    idx = idx[ok]; e = idx + 1
    # non-overlapping: skip signals that fire while a trade is open
    keep, last_exit = [], -1
    for i in idx:
        if i >= last_exit: keep.append(i); last_exit = i + hold
    idx = np.array(keep, int); e = idx + 1
    entry = k.open.values[e]; exit_ = k.close.values[idx + hold]
    bp = side * 1e4 * (exit_ - entry) / entry
    return pd.DataFrame({"t": k.index[e], "bp": bp, "day": k.index[e].floor("D")})

rows = []
for sym in SYMS:
    for tf in TFS:
        k = candles(sym, tf)
        for side, name in [(1, "long<=20"), (-1, "short>=80")]:
            for hold in HOLDS:
                d = trades(k, tf, hold, side=side)
                for w, (t0, t1) in WINDOWS.items():
                    s = d[(d.t >= t0) & (d.t <= t1)]
                    if len(s) < 30: continue
                    days = (pd.Timestamp(t1, tz="UTC") - pd.Timestamp(t0, tz="UTC")).days
                    g = s.bp.mean(); z = boot_z(s.bp.values, s.day.values)
                    rows.append(dict(coin=sym[:-4], tf=tf, side=name, hold=hold, window=w, n=len(s), wr=(s.bp > 0).mean()*100,
                                     gross=g, net2=g-2, net10=g-10, z=z, evday10=(g-10)*len(s)/days, worst=s.bp.min()))
R = pd.DataFrame(rows); R.to_csv(f"{RES}/T12b_horizon.csv", index=False)
md = ["# T12b — hold-horizon sweep, CRSI(2,2,75) on spot candles (Binance.vision), non-overlapping trades\n",
      "net10 = gross − 10 bp taker round trip; net2 = gross − 2 bp maker; z = cluster(UTC day) bootstrap z of gross; evday10 = net10 × trades/day.\n"]
for w in WINDOWS:
    md.append(f"\n## Window {w}\n")
    for side in ["long<=20", "short>=80"]:
        md.append(f"\n### {side}\n")
        sub = R[(R.window == w) & (R.side == side)]
        piv = sub.pivot_table(index=["tf", "hold"], columns="coin", values="net10", aggfunc="first")[["BTC","ETH","SOL","XRP","DOGE"]]
        pz = sub.pivot_table(index=["tf", "hold"], columns="coin", values="z", aggfunc="first")[["BTC","ETH","SOL","XRP","DOGE"]]
        pn = sub.pivot_table(index=["tf", "hold"], columns="coin", values="n", aggfunc="first")[["BTC","ETH","SOL","XRP","DOGE"]]
        md.append("net @10bp (z) [n]\n")
        md.append("| tf | hold | " + " | ".join(piv.columns) + " |\n|---|---|" + "---|" * 5)
        for (tf, h), r in piv.iterrows():
            cells = [f"{r[c]:+.1f} ({pz.loc[(tf,h),c]:.1f}) [{int(pn.loc[(tf,h),c])}]" if not np.isnan(r[c]) else "n/a" for c in piv.columns]
            md.append(f"| {tf} | {h} | " + " | ".join(cells) + " |")
md.append("\n## Cells with net @10bp > 0 AND z >= 2 in BOTH windows\n")
good = R[(R.net10 > 0) & (R.z >= 2)]
both = good.groupby(["coin","tf","side","hold"]).window.nunique(); both = both[both == 2]
md.append(f"{len(both)} cells: " + (", ".join(f"{c} {tf} {s} hold{h}" for (c,tf,s,h) in both.index) if len(both) else "none"))
md.append("\n## Cells with net @2bp > 0 AND z >= 2 in BOTH windows\n")
good = R[(R.net2 > 0) & (R.z >= 2)]
both = good.groupby(["coin","tf","side","hold"]).window.nunique(); both = both[both == 2]
md.append(f"{len(both)} cells: " + (", ".join(f"{c} {tf} {s} hold{h}" for (c,tf,s,h) in both.index) if len(both) else "none"))
open(f"{RES}/T12b_horizon.md", "w").write("\n".join(md) + "\n")
print("\n".join(md[-4:]))
