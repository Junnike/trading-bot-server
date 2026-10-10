# T8c analysis: cell k2/share0.238/delay2/S1/perm0/mode1, real gamma label. Inputs data/t8b/day_*.npz, data/t8b/cfg.json, data/poly_resolution.parquet, data/t8c_crowd.parquet
import glob, json, numpy as np, pandas as pd
D = "data"; ND = 239
CFG = json.load(open(f"{D}/t8b/cfg.json")); c = CFG.index([2, 0.238, 2, 1.0, 0, 1])
Z = [np.load(f) for f in sorted(glob.glob(f"{D}/t8b/day_*.npz"))]
start = np.concatenate([z["start"] for z in Z]); vol = np.concatenate([z["vol"] for z in Z])
F = np.concatenate([z["fills"][c] for z in Z])  # W,2,6,3
rs = pd.read_parquet(f"{D}/poly_resolution.parquet"); sl = dict(zip(rs.slug, rs.prices))
def lab(p):
    try: a = json.loads(p); return 1 if a[0] == "1" else (0 if a[1] == "1" else -1)
    except Exception: return -1
up = np.array([lab(sl.get("btc-updown-5m-%d" % s)) for s in start]); meas = up >= 0; upr = np.where(meas, up, 0.0)
cr = pd.read_parquet(f"{D}/t8c_crowd.parquet").set_index("start")
lo = cr.lo.reindex(start).fillna(0).values
lv = 0.45 - 0.05 * np.arange(6)
f0 = F[:, 0].sum(-1); f1 = F[:, 1].sum(-1)
w = np.where(meas, (f0 * (upr[:, None] - lv)).sum(1) + (f1 * ((1 - upr)[:, None] - lv)).sum(1), 0.0)
q = f0.sum(1) + f1.sum(1); qw = f0 @ np.ones(6) * 0  # placeholder
pq = ((f0 + f1) * lv).sum(1)                      # sum qty*price
wq = f0.sum(1) * upr + f1.sum(1) * (1 - upr)      # winning qty
day = start // 86400; ud, dinv = np.unique(day, return_inverse=True)
mon = pd.to_datetime(start, unit="s").strftime("%Y-%m").values
BI = np.random.default_rng(7).integers(0, ND, (2000, ND))
def dsum(x):
    return np.concatenate([np.bincount(dinv, weights=x, minlength=len(ud)), np.zeros(ND - len(ud))])
def zb(x):
    bm = dsum(x)[BI].mean(1); return bm.mean() / bm.std()
mdays = pd.Series(day).groupby(mon).nunique()
bpvol = vol * 1e4 * np.sqrt(3600)
qs = np.quantile(bpvol[meas], [.25, .5, .75]); vq = np.digitize(bpvol, qs)
out = []; P = lambda s: out.append(s)
P(f"REPRODUCE: cell k2/sh0.238/d2/S1/real label = {w.sum()/ND:.1f} USD/d, z {zb(w):.1f}, fills/d {q[meas].sum()/ND:.0f} (T8b data/t8b_tables.txt: +18.7, z 4.4, 1725-ish fills/d) -> source data/t8b/day_*.npz")
P(f"vol quartile edges bp/h (60 min pre-open, data/binance 1-s via npz vol): {qs.round(1).tolist()}")
months = sorted(set(mon))
P("T1 month | USD/day [fills/day] (windows) by vol Q1..Q4 | all")
tab = {}
for m in months:
    r = []
    for k in range(4):
        s = (mon == m) & (vq == k) & meas
        nd = mdays[m]; r.append(f"{w[s].sum()/nd:6.1f} [{q[s].sum()/nd:4.0f}] ({s.sum()})")
    s = (mon == m) & meas; nd = mdays[m]
    P(f"{m} d={nd} | " + " | ".join(r) + f" | {w[s].sum()/nd:6.1f}")
    tab[m] = (w[s].sum() / nd)
P("T2/T3 month | fills/d | mean fill p | win rate | taker ct/window <=0.45 | median vol bp/h | USD/d")
rowv = {}
for m in months:
    s = (mon == m) & meas; nd = mdays[m]
    p = pq[s].sum() / q[s].sum(); wr = wq[s].sum() / q[s].sum()
    rowv[m] = (q[s].sum() / nd, p, wr, lo[s].mean(), np.median(bpvol[s]))
    P(f"{m} | {rowv[m][0]:.0f} | {p:.4f} | {wr:.4f} | {rowv[m][3]:.0f} | {rowv[m][4]:.1f} | {tab[m]:.1f}")
# revive rule: candidate thresholds
P("REVIVE candidates (windows qualified: vol bp/h >= X, or crowd ct/window <= Y): USD/d total, z, months+, months with >=1 fill")
cand = []
def ev(name, mask):
    mask = mask & meas
    ww = np.where(mask, w, 0.0)
    mm = pd.Series(ww).groupby(mon).sum() / mdays
    mp = (mm > 0).mean()
    cand.append((name, ww.sum() / ND, zb(ww), mp, f"{(mm>0).sum()}/{len(mm)}", int(mask.sum())))
for qq in (0, .25, .5, .75):
    X = np.quantile(bpvol[meas], qq) if qq else -1; ev(f"vol>={X:.1f} bp/h (Q>={int(qq*4)+1})", bpvol >= X)
for qq in (.25, .5, .75, 1.0):
    Y = np.quantile(lo[meas], qq); ev(f"crowd<={Y:.0f} ct/win (pct{int(qq*100)})", lo <= Y)
for n, u, z, mp, mt, nw in cand: P(f"  {n}: {u:.1f} USD/d z {z:.1f} mo+ {mt} windows {nw}")
open(f"{D}/t8c_tables.txt", "w").write("\n".join(out)); print("\n".join(out))
# recent-regime check of revive rule candidates (Aug-Oct 2026 = 69 days)
rec = start >= pd.Timestamp("2026-08-01").timestamp(); nrec = len(np.unique(day[rec]))
BR = np.random.default_rng(9).integers(0, nrec, (2000, nrec)); dr = np.unique(day[rec])
out2 = []
for nm, mk_ in [("vol>=25.9 (Q3+Q4)", bpvol >= qs[1]), ("vol>=38.5 (Q4)", bpvol >= qs[2])]:
    ww = np.where(mk_ & meas & rec, w, 0.0); dd = np.bincount(np.searchsorted(dr, day[rec]), weights=ww[rec], minlength=nrec); bm = dd[BR].mean(1)
    out2.append(f"RECENT Aug-Oct {nm}: {dd.sum()/nrec:.2f} USD/d z {bm.mean()/bm.std():.1f} (data/t8b/day_*.npz)")
open(f"{D}/t8c_tables.txt", "a").write("\n" + "\n".join(out2)); print("\n".join(out2))
