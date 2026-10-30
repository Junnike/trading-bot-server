#!/usr/bin/env python3 -I
"""Bullish/bearish 'flip' (SMC change-of-character + market-structure-shift) detector with 1:1 bracket.
Legs (bullish): 1) a bar's low takes out the last swing low (sweep); 2) a close above the last lower swing high (flip);
3) pullback whose low stays above the sweep low (strict) ; 4) breakout bar closes above the flip-leg high with strong body.
Entry: next open after leg-4 bar (or on retrace to leg-3 low + 50% of the leg, limit, variant). Stop below leg-3 low, target = entry + (entry-stop).
Resolution on 5m bars (first touch wins; both touched in same 5m bar -> loss). Writes results/T12e_flip.md"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import boot_z, CACHE, RES, SYMS
WINDOWS = {"full": ("2020-01-01", "2026-09-30 23:59:59"), "2025+": ("2025-01-01", "2026-09-30 23:59:59")}
TFS = {"15m": 15, "1h": 60, "4h": 240}

def candles(k5, tf):
    k = k5.resample(f"{tf}min", label="left", closed="left").agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last"), volume=("volume","sum")).dropna()
    return k

def swings(h, l, n):
    """fractal swing highs/lows confirmed n bars later; returns arrays of (confirm_index, price, pivot_index)"""
    N = len(h); sh, sl = [], []
    for i in range(n, N - n):
        if h[i] == h[i-n:i+n+1].max() and (h[i-n:i] < h[i]).all(): sh.append((i + n, h[i], i))
        if l[i] == l[i-n:i+n+1].min() and (l[i-n:i] > l[i]).all(): sl.append((i + n, l[i], i))
    return sh, sl

def detect(k, n, body_min, vol_min, side=1):
    """Return list of setups: (bar index of leg-4 bar, stop, flip_high, leg3_low). side=1 bullish; side=-1 run on inverted prices."""
    o, h, l, c, v = k.open.values, k.high.values, k.low.values, k.close.values, k.volume.values
    if side == -1: o, h, l, c = -o, -l, -h, -c
    body = np.abs(c - o); rng = h - l; avg_body = pd.Series(body).rolling(20).mean().shift(1).values; avg_vol = pd.Series(v).rolling(20).mean().shift(1).values
    sh, sl = swings(h, l, n)
    sh_conf = np.array([s[0] for s in sh]); sl_conf = np.array([s[0] for s in sl])
    setups = []; N = len(k); i = 2 * n + 25
    while i < N - 2:
        # last confirmed swing low / high as of bar i
        a = np.searchsorted(sl_conf, i, side="right") - 1; b = np.searchsorted(sh_conf, i, side="right") - 1
        if a < 1 or b < 0: i += 1; continue
        last_low = sl[a][1]
        # leg 1: sweep — bar i low < last confirmed swing low, close back above it (liquidity grab)
        if not (l[i] < last_low and c[i] > last_low): i += 1; continue
        sweep_low = l[i]
        # find the lower high to flip: most recent swing high whose pivot is before bar i
        hh = [s for s in sh if s[2] < i and s[0] <= i]
        if not hh: i += 1; continue
        flip_level = hh[-1][1]
        # leg 2: within 3n bars a close above flip_level
        j = i + 1; flipped = None
        while j < min(i + 3 * n, N - 1):
            if l[j] < sweep_low: break           # new low -> setup void
            if c[j] > flip_level: flipped = j; break
            j += 1
        if flipped is None: i += 1; continue
        leg_high = h[i:flipped + 1].max()
        # leg 3: pullback — bars after flip; pullback low must stay above sweep_low; ends when a bar closes above leg_high (leg 4)
        q = flipped + 1; pb_low = np.inf; done = None
        while q < min(flipped + 3 * n, N - 1):
            if l[q] < sweep_low: break
            pb_low = min(pb_low, l[q])
            if c[q] > leg_high and q > flipped + 1:
                done = q; break
            q += 1
        if done is None or not np.isfinite(pb_low): i += 1; continue
        # leg 4 strength filters
        if body[done] < body_min * avg_body[done] or (c[done] - l[done]) / max(rng[done], 1e-12) < 0.6 or v[done] < vol_min * avg_vol[done]: i = done + 1; continue
        setups.append((done, pb_low, leg_high, sweep_low))
        i = done + 1
    return setups

def bracket(k5, k, setups, side, fee, slip_bp=0):
    """resolve each setup on 5m bars; entry = next tf bar open; stop = pb_low; target = entry + (entry - stop)."""
    o5, h5, l5 = k5.open.values, k5.high.values, k5.low.values
    if side == -1: o5, h5, l5 = -o5, -l5, -h5
    t5 = k5.index.asi8; rows = []
    for (d, stop, _, _) in setups:
        if d + 1 >= len(k): continue
        et = k.index[d + 1]; s = np.searchsorted(t5, et.value)
        if s >= len(k5) or k5.index[s] != et: continue
        entry = o5[s]; risk = entry - stop
        if risk <= 0 or risk / abs(entry) > 0.05: continue     # need stop below entry; skip absurd (>5%) stops
        target = entry + risk; res = None
        for q in range(s, min(s + 2000, len(k5))):
            hit_t, hit_s = h5[q] >= target, l5[q] <= stop
            if hit_s: res = -1; break          # same bar both -> loss (conservative)
            if hit_t: res = 1; break
        if res is None: continue
        bp = res * 1e4 * risk / abs(entry) - fee - slip_bp
        rows.append((et, bp, res, 1e4 * risk / abs(entry)))
    return pd.DataFrame(rows, columns=["t", "bp", "res", "risk_bp"])

def st(d):
    out = {}
    for w, (t0, t1) in WINDOWS.items():
        s = d[(d.t >= t0) & (d.t <= t1)]
        if len(s) < 20: out[w] = None; continue
        yrs = (pd.Timestamp(t1, tz="UTC") - pd.Timestamp(t0, tz="UTC")).days / 365.25
        out[w] = dict(n=len(s), wr=(s.res > 0).mean() * 100, net=s.bp.mean(), z=boot_z(s.bp.values, s.t.dt.floor("D").values), tpy=len(s) / yrs, risk=s.risk_bp.median(), ret=s.bp.sum() / 1e2)
    return out

md = ["# T12e — bullish / bearish flip (sweep → flip of lower high → pullback holds → strong breakout close), 1:1 bracket\n",
      "Entry next candle open after the breakout bar; stop = pullback low; target = same distance. Resolved on 5m bars, same-bar touch counts as loss. Fee 10 bp RT included in net; break-even WR at 1:1 = 50% + fee/(2·risk).\n",
      "| coin | tf | side | filter | full: WR% (n, net bp/trade, z, trades/yr, median risk bp, cum %) | 2025-26 |\n|---|---|---|---|---|---|"]
hits = []
FILTERS = {"loose": (2, 0.8, 0.8), "medium": (3, 1.2, 1.2), "strict": (3, 1.8, 1.8)}   # swing n, body x avg, volume x avg
for sym in SYMS:
    k5 = pd.read_pickle(f"{CACHE}/spot_{sym}_5m.pkl")
    for tf, mins in TFS.items():
        k = candles(k5, mins)
        for side, sname in [(1, "bull"), (-1, "bear")]:
            for fname, (n, bm, vm) in FILTERS.items():
                d = bracket(k5, k, detect(k, n, bm, vm, side), side, 10)
                r = st(d)
                cells = ["n/a" if r[w] is None else f"{r[w]['wr']:.1f}% (n {r[w]['n']}, {r[w]['net']:+.1f} bp, z {r[w]['z']:.1f}, {r[w]['tpy']:.0f}/yr, risk {r[w]['risk']:.0f}, cum {r[w]['ret']:+.0f}%)" for w in WINDOWS]
                md.append(f"| {sym[:-4]} | {tf} | {sname} | {fname} | " + " | ".join(cells) + " |")
                if all(r[w] and r[w]["net"] > 0 and r[w]["z"] >= 2 for w in WINDOWS): hits.append(f"{sym[:-4]} {tf} {sname} {fname}")
md.append("\n## Cells with net > 0 and z >= 2 in BOTH windows\n" + ("\n".join("- " + h for h in hits) if hits else "none"))
open(f"{RES}/T12e_flip.md", "w").write("\n".join(md) + "\n"); print(md[-1])
