#!/usr/bin/env python3 -I
"""Microstructure tests on Binance Vision perp data:
 A. metrics (5m): open-interest change, taker buy/sell ratio, long/short ratios -> squeeze / crowd signals
 B. bookDepth (~30s, bands +-1..5%): bid/ask depth imbalance -> direction signal (BTC, ETH)
Writes results/T12d_micro.md"""
import os, sys, io, glob, zipfile, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import boot_z, CACHE, RES, SYMS
ROOT = f"{CACHE}/.."; WINDOWS = {"full": ("2021-01-01", "2026-09-30 23:59:59"), "2025+": ("2025-01-01", "2026-09-30 23:59:59")}
HOLDS = [1, 3, 12, 48]  # 5m bars: 5m, 15m, 1h, 4h

def read_many(pattern, parse):
    out = []
    for p in sorted(glob.glob(pattern)):
        with zipfile.ZipFile(p) as z: raw = z.read(z.namelist()[0])
        out.append(parse(raw))
    return pd.concat(out)

def load_metrics(sym):
    c = f"{CACHE}/metrics_{sym}.pkl"
    if os.path.exists(c): return pd.read_pickle(c)
    def parse(raw):
        d = pd.read_csv(io.BytesIO(raw)); d["t"] = pd.to_datetime(d.create_time, utc=True); return d.set_index("t")[["sum_open_interest","sum_open_interest_value","count_toptrader_long_short_ratio","sum_toptrader_long_short_ratio","count_long_short_ratio","sum_taker_long_short_vol_ratio"]]
    m = read_many(f"{ROOT}/metrics/{sym}/*.zip", parse); m = m[~m.index.duplicated()].sort_index()
    m.columns = ["oi","oiv","top_cnt","top_pos","glob_cnt","taker"]; m.to_pickle(c); return m

def load_depth(sym):
    c = f"{CACHE}/depth_{sym}.pkl"
    if os.path.exists(c): return pd.read_pickle(c)
    def parse(raw):
        d = pd.read_csv(io.BytesIO(raw)); d["t"] = pd.to_datetime(d.timestamp, utc=True)
        p = d.pivot_table(index="t", columns="percentage", values="notional", aggfunc="first")
        return p
    p = read_many(f"{ROOT}/bookDepth/{sym}/*.zip", parse); p = p[~p.index.duplicated()].sort_index()
    p.columns = [f"b{int(c)}" for c in p.columns]; p.to_pickle(c); return p

def st(bp, t, fee=10):
    out = {}
    for w, (t0, t1) in WINDOWS.items():
        m = (t >= t0) & (t <= t1); x = bp[m]
        if len(x) < 30: out[w] = None; continue
        days = (pd.Timestamp(t1, tz="UTC") - pd.Timestamp(t0, tz="UTC")).days
        out[w] = dict(n=len(x), wr=(x > 0).mean()*100, net=x.mean()-fee, z=boot_z(x, t[m].floor("D").values), evday=(x.mean()-fee)*len(x)/days)
    return out
def nonoverlap(idx, hold):
    keep, last = [], -1
    for i in idx:
        if i >= last: keep.append(i); last = i + hold
    return np.array(keep, int)
def run(px, cond, side, hold):
    """px: DataFrame with open, close on 5m grid (contiguity checked); cond: bool array aligned to px; enter next open, exit close after hold bars"""
    ts = px.index.asi8 // 60_000; contig = np.r_[False, np.diff(ts) == 5]
    idx = np.where(cond)[0]; idx = idx[idx + hold < len(px)]
    ok = np.ones(len(idx), bool)
    for k in range(1, hold + 1): ok &= contig[idx + k]
    idx = nonoverlap(idx[ok], hold); e = idx + 1
    bp = side * 1e4 * (px.close.values[idx + hold] - px.open.values[e]) / px.open.values[e]
    return bp, px.index[e]
def fmt(name, r):
    cells = ["n/a" if r[w] is None else f"{r[w]['net']:+.1f} (z {r[w]['z']:.1f}, WR {r[w]['wr']:.0f}%, n {r[w]['n']})" for w in WINDOWS]
    return f"| {name} | " + " | ".join(cells) + " |"
HDR = "| signal | full: net bp/trade @10bp (z, WR, n) | 2025-26 |\n|---|---|---|"
md = ["# T12d — perp microstructure tests (Binance Vision metrics + bookDepth)\n", "Enter next 5m open, exit close after hold; fee 10 bp taker RT; z = UTC-day cluster bootstrap; non-overlapping trades. Percentiles are trailing 30-day, lagged.\n"]
hits = []
def rq(s, q, win=8640): return s.rolling(win, min_periods=win//2).quantile(q).shift(1)

# ---------- A. metrics ----------
md.append("\n## A. Metrics (5m): open interest, taker buy/sell volume ratio, long/short account ratios\n")
for sym in SYMS:
    m = load_metrics(sym); p = pd.read_pickle(f"{CACHE}/perp_{sym}_5m.pkl")
    j = p[["open","close"]].join(m, how="inner").dropna(subset=["open","oi","taker"])
    j["doi1h"] = j.oi.pct_change(12) * 100; j["ret1h"] = j.close.pct_change(12) * 100
    j["dtop"] = j.top_pos.diff(12)
    sigs = {
        "OI 1h chg > p95 & price 1h up (crowded longs) -> SHORT": (-1, (j.doi1h > rq(j.doi1h, .95)) & (j.ret1h > 0)),
        "OI 1h chg > p95 & price 1h down (crowded shorts) -> LONG": (1, (j.doi1h > rq(j.doi1h, .95)) & (j.ret1h < 0)),
        "OI 1h chg < p05 & price 1h down (long liquidation) -> LONG": (1, (j.doi1h < rq(j.doi1h, .05)) & (j.ret1h < 0)),
        "OI 1h chg < p05 & price 1h up (short squeeze done) -> SHORT": (-1, (j.doi1h < rq(j.doi1h, .05)) & (j.ret1h > 0)),
        "taker buy/sell > p95 -> LONG (momentum)": (1, j.taker > rq(j.taker, .95)),
        "taker buy/sell > p95 -> SHORT (fade)": (-1, j.taker > rq(j.taker, .95)),
        "taker buy/sell < p05 -> LONG (fade)": (1, j.taker < rq(j.taker, .05)),
        "taker buy/sell < p05 -> SHORT (momentum)": (-1, j.taker < rq(j.taker, .05)),
        "top-trader L/S ratio > p95 -> SHORT (fade crowd)": (-1, j.top_pos > rq(j.top_pos, .95)),
        "top-trader L/S ratio < p05 -> LONG (fade crowd)": (1, j.top_pos < rq(j.top_pos, .05)),
        "top-trader L/S 1h rise > p95 -> LONG (follow smart money)": (1, j.dtop > rq(j.dtop, .95)),
        "top-trader L/S 1h fall < p05 -> SHORT (follow smart money)": (-1, j.dtop < rq(j.dtop, .05)),
    }
    md.append(f"\n### {sym[:-4]} (metrics rows {len(j)})\n" + HDR)
    for name, (side, cond) in sigs.items():
        for hold in HOLDS:
            bp, t = run(j, cond.fillna(False).values, side, hold); r = st(bp, t)
            md.append(fmt(f"{name}, hold {hold*5}m", r))
            if all(r[w] and r[w]["net"] > 0 and r[w]["z"] >= 2 for w in WINDOWS): hits.append(f"{sym[:-4]} {name} hold {hold*5}m: " + " / ".join(f"{r[w]['net']:+.1f} z{r[w]['z']:.1f}" for w in WINDOWS))

# ---------- B. bookDepth ----------
md.append("\n## B. Order-book depth imbalance (bookDepth ~30 s snapshots, notional in bands); imb_k = (bid_k - ask_k)/(bid_k + ask_k), sampled at the 5m bar close\n")
for sym in ["BTCUSDT", "ETHUSDT"]:
    d = load_depth(sym)
    for k in [1, 2, 5]:
        d[f"imb{k}"] = (d[f"b-{k}"] - d[f"b{k}"]) / (d[f"b-{k}"] + d[f"b{k}"])
    d["imb1_5"] = ((d["b-1"]) - d["b1"]) / (d["b-5"] + d["b5"])   # near-touch imbalance relative to total depth
    d5 = d[[c for c in d.columns if c.startswith("imb")]].resample("5min", label="left", closed="left").last()
    d5["dimb1"] = d5.imb1.diff(3)  # 15-min change in imbalance
    p = pd.read_pickle(f"{CACHE}/perp_{sym}_5m.pkl"); m = load_metrics(sym)
    j = p[["open","close"]].join(d5, how="inner").join(m[["oi","taker"]], how="left").dropna(subset=["imb1"])
    j["doi1h"] = j.oi.pct_change(12) * 100
    md.append(f"\n### {sym[:-4]} (depth rows {len(d)}, 5m rows {len(j)}; first {j.index[0].date()})\n" + HDR)
    sigs = {}
    for k in [1, 2, 5]:
        s = j[f"imb{k}"]
        sigs[f"imb±{k}% > p90 -> LONG"] = (1, s > rq(s, .9)); sigs[f"imb±{k}% < p10 -> SHORT"] = (-1, s < rq(s, .1))
        sigs[f"imb±{k}% > p90 -> SHORT (fade)"] = (-1, s > rq(s, .9)); sigs[f"imb±{k}% < p10 -> LONG (fade)"] = (1, s < rq(s, .1))
    sigs["imb1 15m rise > p95 -> LONG"] = (1, j.dimb1 > rq(j.dimb1, .95)); sigs["imb1 15m fall < p05 -> SHORT"] = (-1, j.dimb1 < rq(j.dimb1, .05))
    sigs["imb±1% > p90 & taker > p80 -> LONG (book+flow agree)"] = (1, (j.imb1 > rq(j.imb1, .9)) & (j.taker > rq(j.taker, .8)))
    sigs["imb±1% < p10 & taker < p20 -> SHORT (book+flow agree)"] = (-1, (j.imb1 < rq(j.imb1, .1)) & (j.taker < rq(j.taker, .2)))
    sigs["imb±1% > p90 & OI 1h chg > p90 -> LONG"] = (1, (j.imb1 > rq(j.imb1, .9)) & (j.doi1h > rq(j.doi1h, .9)))
    sigs["imb±1% < p10 & OI 1h chg > p90 -> SHORT"] = (-1, (j.imb1 < rq(j.imb1, .1)) & (j.doi1h > rq(j.doi1h, .9)))
    for name, (side, cond) in sigs.items():
        for hold in HOLDS:
            bp, t = run(j, cond.fillna(False).values, side, hold); r = st(bp, t)
            md.append(fmt(f"{name}, hold {hold*5}m", r))
            if all(r[w] and r[w]["net"] > 0 and r[w]["z"] >= 2 for w in WINDOWS): hits.append(f"{sym[:-4]} {name} hold {hold*5}m: " + " / ".join(f"{r[w]['net']:+.1f} z{r[w]['z']:.1f}" for w in WINDOWS))
md.append("\n## Cells with net @10bp > 0 and z >= 2 in BOTH windows\n")
md.append("\n".join("- " + h for h in hits) if hits else "none")
open(f"{RES}/T12d_micro.md", "w").write("\n".join(md) + "\n"); print("\n".join(md[-3:]))
