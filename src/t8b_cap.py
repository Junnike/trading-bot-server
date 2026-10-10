# T8b capacity sweep for best cell (k2, share 0.238, delay 2, re-place) from data/t8b_cap/day_*.npz
import glob, json, numpy as np, pandas as pd
D = "data"; ND = 239
Z = [np.load(f) for f in sorted(glob.glob(f"{D}/t8b_cap/day_*.npz"))]
start = np.concatenate([z["start"] for z in Z]); F = np.concatenate([z["fills"] for z in Z], axis=1)
rs = pd.read_parquet(f"{D}/poly_resolution.parquet"); sl = dict(zip(rs.slug, rs.prices))
def lab(p):
    try: a = json.loads(p); return 1 if a[0] == "1" else (0 if a[1] == "1" else -1)
    except Exception: return -1
up = np.array([lab(sl.get("btc-updown-5m-%d" % s)) for s in start]); meas = up >= 0; upr = np.where(meas, up, 0.0)
lv = 0.45 - 0.05 * np.arange(6)
day = start // 86400; ud, dinv = np.unique(day, return_inverse=True); mon = pd.to_datetime(start, unit="s").strftime("%Y-%m").values
BI = np.random.default_rng(7).integers(0, ND, (2000, ND))
cfg = json.load(open(f"{D}/t8b_cap/cfg.json"))
for c, cf in enumerate(cfg):
    f0 = F[c, :, 0].sum(-1); f1 = F[c, :, 1].sum(-1)
    w = np.where(meas, (f0 * (upr[:, None] - lv)).sum(1) + (f1 * ((1 - upr)[:, None] - lv)).sum(1), 0)
    dd = np.concatenate([np.bincount(dinv, weights=w, minlength=len(ud)), np.zeros(ND - len(ud))]); bm = dd[BI].mean(1)
    mm = pd.Series(w).groupby(mon).sum(); last = w[start >= pd.Timestamp("2026-08-01").timestamp()].sum() / 69
    print(f"S{int(cf[3])}: {dd.sum()/ND:.1f} USD/d z {bm.mean()/bm.std():.1f} mo+ {(mm>0).sum()}/{len(mm)} fills/d {F[c][meas].sum()/ND:.0f} Aug-Oct {last:.1f} USD/d")
