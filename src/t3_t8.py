import sys, glob, os, json, numpy as np, pandas as pd
from scipy.stats import norm
D = "data"
lo, hi, tag = sys.argv[1], sys.argv[2], sys.argv[3]
LAT = int(sys.argv[4]) if len(sys.argv) > 4 else 1   # date range inclusive (UTC), output tag
days = sorted(os.path.basename(f)[:10] for f in glob.glob(f"{D}/poly/*_trades.parquet"))
days = [d for d in days if lo <= d <= hi and os.path.exists(f"{D}/binance/BTCUSDT-1s-{d}.parquet")]
mk = pd.concat([pd.read_parquet(f"{D}/poly/{d}_markets.parquet") for d in days], ignore_index=True)
def load_day(d):
    t = pd.read_parquet(f"{D}/poly/{d}_trades.parquet", columns=["cid", "oi", "side", "price", "size", "ts"])
    return t
# Binance 1-s close as dense array by second, ffill gaps
bdays = sorted(set(days) | {(pd.Timestamp(d) - pd.Timedelta(days=1)).strftime("%Y-%m-%d") for d in days})
bn = pd.concat([pd.read_parquet(f"{D}/binance/BTCUSDT-1s-{d}.parquet", columns=["t", "c"]) for d in bdays if os.path.exists(f"{D}/binance/BTCUSDT-1s-{d}.parquet")])
t0 = int(bn.t.min()); n = int(bn.t.max()) - t0 + 1
px = np.full(n, np.nan); px[(bn.t.values - t0)] = bn.c.values
px = pd.Series(px).ffill().values
lr = np.diff(np.log(px), prepend=np.nan)
cs = np.nancumsum(np.nan_to_num(lr)); cs2 = np.nancumsum(np.nan_to_num(lr) ** 2)
def sigma(t):  # per-sec std of 1-s log returns over previous 3600 s ending at t (index)
    i = t - t0; a = i - 3600
    k = 3599.0
    m = (cs[i] - cs[a]) / 3600; v = (cs2[i] - cs2[a]) / 3600 - m * m
    return np.sqrt(np.maximum(v, 1e-18))
mk = mk[mk.closed & mk.prices.notna()].copy()
mk["up"] = mk.prices.map(lambda s: 1 if json.loads(s)[0] == "1" else (0 if json.loads(s)[1] == "1" else -1))
mk = mk[mk.up >= 0]; mk = mk[(mk.start - t0 >= 3700) & (mk.start + 300 - t0 < n)]
fee = lambda p: 0.07 * p * (1 - p)
def boot(g_cid, val, w, B=2000, seed=1):
    # cluster bootstrap over windows of weighted mean
    rng = np.random.default_rng(seed)
    u, inv = np.unique(g_cid, return_inverse=True)
    sw = np.bincount(inv, w * val); sn = np.bincount(inv, w)
    k = len(u); idx = rng.integers(0, k, (B, k))
    m = sw[idx].sum(1) / np.maximum(sn[idx].sum(1), 1e-12)
    return m.mean(), m.std()
out = {"days": [days[0], days[-1], len(days)], "markets": int(len(mk))}

def prep(d):
    tr = load_day(d)
    tr = tr.merge(mk[["cid", "start", "up"]], on="cid"); tr["age"] = tr.ts - tr.start
    tr["cid"] = tr.start
    return tr
levels = np.round(np.arange(0.05, 0.951, 0.05), 2)
CFG = [(c, r) for c in (300, 240) for r in (None, 2, 3, 5)]
RES = {k: [] for k in CFG}
def t8day(tr):
    for cut, rule in CFG:
        for cid, g in tr[tr.age <= cut].groupby("start"):
            up = g.up.iat[0]; u = g.u.values; mv = g.mv.values
            ok_up = np.ones(len(g), bool) if rule is None else (np.minimum.accumulate(mv) > -rule)
            ok_dn = np.ones(len(g), bool) if rule is None else (np.maximum.accumulate(mv) < rule)
            pnl = 0.0; r = 0.0; nf = 0
            if ok_up.any():
                mn = np.min(np.where(ok_up, u, 9))
                for L in levels[levels > mn]:
                    pnl += up - L; r += 0.2 * fee(L); nf += 1
            if ok_dn.any():
                mx = np.max(np.where(ok_dn, u, -9))
                for L in levels[levels > 1 - mx]:
                    pnl += (1 - up) - L; r += 0.2 * fee(L); nf += 1
            RES[(cut, rule)].append((cid, pnl, r, nf))
fs = []
for d in days:
    tr = prep(d)
    f = tr[(tr.side == "BUY") & (tr.age >= 0) & (tr.age <= 30)].copy()
    f["pw"] = np.where(f.oi == 0, 1, 0)
    st = f.start.values; ts = f.ts.values
    S0 = px[st - t0]; St = px[ts - t0]; sg = np.array([sigma(s) for s in ts])
    tau = np.maximum(st + 300 - 60 - ts, 0)
    z = (np.log(St / S0)) / (sg * np.sqrt(tau + 20))
    pup = norm.cdf(z)
    f["fair"] = np.where(f.oi == 0, pup, 1 - pup)
    f["win"] = (f.oi == (1 - f.up)).astype(float)   # outcome 0 = Up
    f["fee"] = fee(f.price); f["edge"] = f.fair - f.price - f.fee; f["pnl"] = f.win - f.price - f.fee
    f = f[(f.price > 0.01) & (f.price < 0.99)]
    f = f.drop(columns=['side','pw']).astype({'oi':'int8','up':'int8','price':'float32','size':'float32','fair':'float32','win':'float32','fee':'float32','edge':'float32','pnl':'float32','age':'int16'})
    fs.append(f)
    tr = tr[(tr.age >= 0) & (tr.age <= 300)].copy()
    tr['u'] = np.where(tr.oi == 0, tr.price, 1 - tr.price)
    ts_ = tr.ts.values; st_ = tr.start.values
    tr['mv'] = (px[ts_ - LAT - t0] / px[st_ - t0] - 1) * 1e4
    t8day(tr[['age','up','u','mv','start']]); del tr
f = pd.concat(fs, ignore_index=True)
rows = []
def row(name, g):
    if len(g) == 0: return
    m, s = boot(g.cid.values, g.pnl.values, g["size"].values)
    rows.append(dict(bucket=name, n=len(g), windows=g.cid.nunique(), shares=round(g["size"].sum()), avg_fill=round(np.average(g.price, weights=g["size"]), 3),
                     model_edge_c=round(np.average(g.edge, weights=g["size"]) * 100, 2), realized_ev_c=round(np.average(g.pnl, weights=g["size"]) * 100, 2), z=round(m / s, 2)))
for nm, a, b in [("0-5", 0, 5), ("5-10", 5, 10), ("10-22", 10, 22), ("22-30", 22, 31)]:
    row(nm, f[(f.age >= a) & (f.age < b)])
row("all 0-30", f)
for th in [0.0, 0.02, 0.05]:
    row(f"model edge>{th} (0-30)", f[f.edge > th])
    row(f"model edge>{th} (9-22)", f[(f.edge > th) & (f.age >= 9) & (f.age < 22)])
out["T3"] = rows
mrows = []
f["month"] = pd.to_datetime(f.ts, unit="s").dt.strftime("%Y-%m")
for nm, g in [("all 0-30", f), ("edge>0.05 0-30", f[f.edge > 0.05]), ("edge>0.05 9-22", f[(f.edge > 0.05) & (f.age >= 9) & (f.age < 22)]), ("edge>0 0-30", f[f.edge > 0])]:
    for mo, h in g.groupby("month"):
        mrows.append(dict(cell=nm, month=mo, n=len(h), windows=h.cid.nunique(), ev_c=round(np.average(h.pnl, weights=h["size"]) * 100, 2)))
pd.DataFrame(mrows).to_csv(f"{D}/T3_monthly_{tag}.csv", index=False)
pd.DataFrame(rows).to_csv(f"{D}/T3_{tag}.csv", index=False)
res = []
nd = len(days)
for (cut, rule), lst in RES.items():
    A = np.array(lst); per = A[:, 1:3]; nf = int(A[:, 3].sum())
    dd = pd.Series(per.sum(1)).groupby(A[:, 0] // 86400).sum()
    a = per
    res.append(dict(cutoff_s=cut, rule="none" if rule is None else f"{rule}bp", days_pos=f"{(dd>0).sum()}/{len(dd)}", fills=nf, markets=len(a), pnl_usd_day=round(a[:, 0].sum() / nd, 2), rebate_usd_day=round(a[:, 1].sum() / nd, 2), net_usd_day=round(a.sum() / nd, 2), z=round(a.sum(1).mean() / (a.sum(1).std() / np.sqrt(len(a))), 2)))
    mo = pd.Series(per.sum(1)).groupby(pd.to_datetime(A[:, 0], unit="s").strftime("%Y-%m")).sum()
    res[-1]["months_pos"] = f"{(mo>0).sum()}/{len(mo)}"
out["T8"] = res
pd.DataFrame(res).to_csv(f"{D}/T8_{tag}.csv", index=False)
json.dump(out, open(f"{D}/T3T8_{tag}.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
