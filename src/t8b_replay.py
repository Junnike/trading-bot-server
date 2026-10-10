# T8b replay engine: Poly 5-min maker ladder with pull rule, FIFO-share fills, delay, size. Per-day -> data/t8b/day_*.npz
# usage: python -I src/t8b_replay.py [lo hi]
import sys, os, glob, json, numpy as np, pandas as pd
from numba import njit
from multiprocessing import Pool
D = "data"
# ---- Binance 1-s close (dense, ffill), as first pass
bd = sorted(glob.glob(f"{D}/binance/BTCUSDT-1s-*.parquet"))
bn = pd.concat([pd.read_parquet(f, columns=["t", "c"]) for f in bd])
T0 = int(bn.t.min()); NPX = int(bn.t.max()) - T0 + 1
px = np.full(NPX, np.nan); px[bn.t.values - T0] = bn.c.values
px = pd.Series(px).ffill().values
del bn
LV = 6  # levels 0.45..0.20
# ---- configs
CFG = []   # (k, share, delay, S, perm, mode)  mode 1 = aggressor-correct, 0 = any-side (first-pass style)
for mode in (1, 0):
    for perm in (0, 1):
        for k in (2, 3):
            for share in (1.0, 0.238, 0.10, 0.05):
                for delay in (0, 2, 6):
                    CFG.append((k, share, delay, 1.0, perm, mode))
for perm in (0, 1):
    for k in (2, 3):
        for share in (0.238, 0.10, 0.05):
            for delay in (2, 6):
                for S in (10.0, 50.0):
                    CFG.append((k, share, delay, S, perm, 1))
OD = "t8b"
if os.environ.get("T8B_CAP"):   # capacity sweep: best cell, S in 1..50
    OD = "t8b_cap"
    CFG = [(2, 0.238, 2, S, 0, 1) for S in (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 50.0)]
CFGA = np.array(CFG, dtype=np.float64)

@njit(cache=True)
def engine(offs, age, oi, buy, pr, size, mv, cfg, out):
    nw = len(offs) - 1
    for w in range(nw):
        a0 = offs[w]; a1 = offs[w + 1]
        if a1 == a0: continue
        mn = np.empty(301); mx = np.empty(301)
        m0 = 0.0; m1 = 0.0
        for a in range(301):
            if mv[w, a] < m0: m0 = mv[w, a]
            if mv[w, a] > m1: m1 = mv[w, a]
            mn[a] = m0; mx[a] = m1
        for c in range(cfg.shape[0]):
            k = cfg[c, 0]; sh = cfg[c, 1]; dl = int(cfg[c, 2]); S = cfg[c, 3]; perm = cfg[c, 4] > 0.5; mode = cfg[c, 5]
            fu = np.zeros(LV); fd = np.zeros(LV)
            for i in range(a0, a1):
                a = age[i]
                if a < dl: continue
                li = a - dl - 1
                if li < 0: li = 0
                if perm:
                    au = mn[li] > -k; ad = mx[li] < k
                else:
                    au = mv[w, li] > -k; ad = mv[w, li] < k
                p = int(pr[i]); sz = size[i] * sh
                hu = False; hd = False; xu = 0; xd = 0
                if mode > 0.5:
                    if oi[i] == 0:
                        if buy[i] == 1: hd = True; xd = 1000 - p
                        else: hu = True; xu = p
                    else:
                        if buy[i] == 1: hu = True; xu = 1000 - p
                        else: hd = True; xd = p
                else:
                    xu = p if oi[i] == 0 else 1000 - p
                    xd = 1000 - xu
                    hu = True; hd = True
                tb = 0 if a < 60 else (1 if a < 180 else 2)
                if hu and au:
                    for j in range(LV):
                        L = 450 - 50 * j
                        if xu <= L and fu[j] < S:
                            q = min(S - fu[j], sz)
                            fu[j] += q
                            out[c, w, 0, j, tb] += q
                if hd and ad:
                    for j in range(LV):
                        L = 450 - 50 * j
                        if xd <= L and fd[j] < S:
                            q = min(S - fd[j], sz)
                            fd[j] += q
                            out[c, w, 1, j, tb] += q

@njit(cache=True)
def sanity(offs, age, u, mvl, up, rules, res):
    # first-pass replica: file order, all prints age 0..300, ladder 0.05..0.95 both sides, 1 share/level, fills if any ok print strictly through
    nw = len(offs) - 1
    for w in range(nw):
        a0 = offs[w]; a1 = offs[w + 1]
        if a1 == a0: continue
        for r in range(len(rules)):
            rule = rules[r]
            mnv = 1e9; mxv = -1e9
            umin = 9.0; umax = -9.0; anyu = False; anyd = False
            for i in range(a0, a1):
                if mvl[i] < mnv: mnv = mvl[i]
                if mvl[i] > mxv: mxv = mvl[i]
                oku = True if rule < 0 else (mnv > -rule)
                okd = True if rule < 0 else (mxv < rule)
                if oku:
                    anyu = True
                    if u[i] < umin: umin = u[i]
                if okd:
                    anyd = True
                    if u[i] > umax: umax = u[i]
            pnl = 0.0; reb = 0.0; nf = 0
            for j in range(1, 20):
                L = round(0.05 * j * 100) / 100.0
                if anyu and L > umin:
                    pnl += up[w] - L; reb += 0.2 * 0.07 * L * (1 - L); nf += 1
                if anyd and L > 1 - umax:
                    pnl += (1 - up[w]) - L; reb += 0.2 * 0.07 * L * (1 - L); nf += 1
            res[r, w, 0] = pnl; res[r, w, 1] = reb; res[r, w, 2] = nf

def do_day(d):
    fo = f"{D}/{OD}/day_{d}.npz"
    if os.path.exists(fo): return d
    mk = pd.read_parquet(f"{D}/poly/{d}_markets.parquet")
    mk = mk[(mk.start - T0 >= 3700) & (mk.start + 300 - T0 < NPX)].reset_index(drop=True)
    pj = mk.prices.map(lambda s: 1 if json.loads(s)[0] == "1" else (0 if json.loads(s)[1] == "1" else -1)) if mk.prices.notna().all() else mk.prices.map(lambda s: -1 if s is None else (1 if json.loads(s)[0] == "1" else (0 if json.loads(s)[1] == "1" else -1)))
    mk["up"] = pj.values
    st = mk.start.values.astype(np.int64)
    ar = np.arange(301)
    mv = ((px[(st[:, None] + ar[None, :]) - T0] / px[st - T0][:, None] - 1) * 1e4).astype(np.float32)
    proxy = (px[st + 300 - T0] >= px[st - T0]).astype(np.int8)
    # vol: std of 1-s log returns over 3600 s before open
    lp = np.log(px[(st[:, None] + np.arange(-3600, 1)[None, :]) - T0])
    vol = np.diff(lp, axis=1).std(axis=1)
    tr = pd.read_parquet(f"{D}/poly/{d}_trades.parquet", columns=["cid", "oi", "side", "price", "size", "ts"])
    widx = pd.Series(np.arange(len(mk)), index=mk.cid)
    tr["w"] = tr.cid.map(widx); tr = tr[tr.w.notna()].copy(); tr["w"] = tr.w.astype(np.int64)
    tr["age"] = tr.ts - st[tr.w.values]
    tr = tr[(tr.age >= 0) & (tr.age <= 300)]
    ft = {}
    # file-order (sanity)
    o = np.argsort(tr.w.values, kind="stable"); t1 = tr.iloc[o]
    offs = np.searchsorted(t1.w.values, np.arange(len(mk) + 1)).astype(np.int64)
    u = np.where(t1.oi.values == 0, t1.price.values, 1 - t1.price.values)
    mvl = (px[t1.ts.values - 1 - T0] / px[st[t1.w.values] - T0] - 1) * 1e4
    upf = mk.up.values.astype(np.float64)
    res = np.zeros((3, len(mk), 3))
    sanity(offs, t1.age.values.astype(np.int64), u, mvl, upf, np.array([2.0, 3.0, -1.0]), res)
    # ts-order (engine)
    o = np.lexsort((tr.ts.values, tr.w.values)); t2 = tr.iloc[o]
    offs = np.searchsorted(t2.w.values, np.arange(len(mk) + 1)).astype(np.int64)
    out = np.zeros((len(CFG), len(mk), 2, LV, 3), dtype=np.float32)
    engine(offs, t2.age.values.astype(np.int64), t2.oi.values.astype(np.int8), (t2.side.values == "BUY").astype(np.int8),
           np.round(t2.price.values * 1000).astype(np.int64), t2["size"].values.astype(np.float64), mv, CFGA, out)
    np.savez_compressed(fo, start=st, up=mk.up.values, proxy=proxy, vol=vol, nprint=np.diff(offs), fills=out, san=res)
    return d

if __name__ == "__main__":
    lo = sys.argv[1] if len(sys.argv) > 1 else "0000"; hi = sys.argv[2] if len(sys.argv) > 2 else "9999"
    days = sorted(os.path.basename(f)[:10] for f in glob.glob(f"{D}/poly/*_trades.parquet"))
    days = [d for d in days if lo <= d <= hi and d <= "2026-10-08"]
    with Pool(4) as p:
        for d in p.imap_unordered(do_day, days): print(d, flush=True)
    json.dump([list(c) for c in CFG], open(f"{D}/{OD}/cfg.json", "w"))
