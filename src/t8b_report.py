# T8b aggregation -> prints tables as JSON-ish text to data/t8b_tables.txt
import glob, json, numpy as np, pandas as pd
D = "data"
CFG = json.load(open(f"{D}/t8b/cfg.json"))
fs = sorted(glob.glob(f"{D}/t8b/day_*.npz"))
Z = [np.load(f) for f in fs]
start = np.concatenate([z["start"] for z in Z]); up_st = np.concatenate([z["up"] for z in Z]); proxy = np.concatenate([z["proxy"] for z in Z])
vol = np.concatenate([z["vol"] for z in Z]); npr = np.concatenate([z["nprint"] for z in Z])
fills = np.concatenate([z["fills"] for z in Z], axis=1)   # cfg, W, 2, 6, 3
san = np.concatenate([z["san"] for z in Z], axis=1)
ND = 239
day = (start // 86400); ud, dinv = np.unique(day, return_inverse=True)
mon = pd.to_datetime(start, unit="s").strftime("%Y-%m").values
# real label from fresh gamma pull
rs = pd.read_parquet(f"{D}/poly_resolution.parquet")
def lab(p):
    try:
        a = json.loads(p)
        return 1 if a[0] == "1" else (0 if a[1] == "1" else -1)
    except Exception: return -1
rs["lab"] = rs.prices.map(lab) if "prices" in rs else -1
slug2lab = dict(zip(rs.slug, rs.lab))
slugs = ["btc-updown-5m-%d" % s for s in start]
up = np.array([slug2lab.get(s, -1) for s in slugs])
meas = up >= 0
out = []
P = lambda *a: out.append(" ".join(str(x) for x in a))
P("windows(total in 239 d, with Binance 1h history)", len(start), "real label measured", int(meas.sum()), "UNMEASURED", int((~meas).sum()), "| stored-vs-fresh label differ", int((meas & (up_st >= 0) & (up != up_st)).sum()), "stored unresolved", int((up_st < 0).sum()))
# sanity (first pass replica, stored label, lag 1)
sv = san[:, :, :].sum(axis=1)
sm = (up_st >= 0)
for r, nm in enumerate(["2bp", "3bp", "none"]):
    P("SANITY first-pass replica", nm, "net USD/day", round((san[r, :, 0].sum() + san[r, :, 1].sum()) / ND, 1), "pnl", round(san[r, :, 0].sum() / ND, 1), "reb", round(san[r, :, 1].sum() / ND, 1), "fills", int(san[r, :, 2].sum()))
lv = 0.45 - 0.05 * np.arange(6)
fee = lambda p: 0.07 * p * (1 - p)
def pnl_cfg(c, mask, upl, reb=False):
    F = fills[c]  # W,2,6,3
    F0 = F[:, 0].sum(-1); F1 = F[:, 1].sum(-1)
    w = (F0 * (upl[:, None] - lv[None])).sum(1) + (F1 * ((1 - upl)[:, None] - lv[None])).sum(1)
    if reb: w = w + 0.2 * ((F0 + F1) * fee(lv)[None]).sum(1)
    return np.where(mask, w, 0.0)
rng = np.random.default_rng(7)
BI = rng.integers(0, ND, (2000, ND))
def stats(w):
    dd = np.bincount(dinv, weights=w, minlength=len(ud))
    dd = np.concatenate([dd, np.zeros(ND - len(dd))])
    bm = dd[BI].mean(1)
    mm = pd.Series(w).groupby(mon).sum()
    return dd.sum() / ND, bm.mean() / bm.std(), (mm > 0).mean() * 100, f"{(mm>0).sum()}/{len(mm)}"
def key(c): return tuple(CFG[c])
idx = {key(c): c for c in range(len(CFG))}
upr = np.where(meas, up, 0).astype(float)
# TABLE 1
P("T1 grid (aggressor-side fills, re-place rule, S=1, real label, rebate 0): k share delay -> USD/day, fills/day, windows, z, months+")
res1 = {}
for k in (2, 3):
    for sh in (1.0, 0.238, 0.10, 0.05):
        for dl in (0, 2, 6):
            c = idx[(k, sh, dl, 1.0, 0, 1)]
            w = pnl_cfg(c, meas, upr); u, z, mp, mt = stats(w)
            nf = fills[c][meas].sum() / ND; nw = int((fills[c][meas].sum((1, 2, 3)) > 0).sum())
            res1[(k, sh, dl)] = (u, z, mp)
            P(f" k{k} sh{sh} d{dl}: {u:.1f} USD/d, {nf:.1f} fills/d, {nw} win, z {z:.1f}, mo+ {mt}")
P("T1b same, permanent pull (first-pass rule), k share delay:")
for k in (2, 3):
    for sh in (1.0, 0.238, 0.10, 0.05):
        r = []
        for dl in (0, 2, 6):
            c = idx[(k, sh, dl, 1.0, 1, 1)]; u, z, mp, mt = stats(pnl_cfg(c, meas, upr)); r.append(f"d{dl} {u:.1f} (z{z:.1f},{mt})")
        P(f" perm k{k} sh{sh}: " + " | ".join(r))
P("T1c any-side fills (first-pass style, re-place), k share delay:")
for k in (2, 3):
    for sh in (1.0, 0.238, 0.05):
        r = []
        for dl in (0, 2, 6):
            c = idx[(k, sh, dl, 1.0, 0, 0)]; u, z, mp, mt = stats(pnl_cfg(c, meas, upr)); r.append(f"d{dl} {u:.1f}")
        P(f" anyside k{k} sh{sh}: " + " | ".join(r))
# TABLE 2 label
both = meas
diff = int((both & (proxy != up)).sum())
P("T2 label: real(gamma) vs Binance-close proxy differ", diff, "of", int(both.sum()), f"= {100*diff/both.sum():.2f}%")
for nm, lab_ in [("real", upr), ("proxy", proxy.astype(float))]:
    for rule, c in [("replace", idx[(2, 1.0, 0, 1.0, 0, 0)]), ("perm", idx[(2, 1.0, 0, 1.0, 1, 0)])]:
        w = pnl_cfg(c, both, lab_) ; wr = pnl_cfg(c, both, lab_, True)
        u, z, mp, mt = stats(w); P(f" any-side k2 sh1.0 d0 {rule} label={nm}: {u:.1f} USD/d (+rebate {stats(wr)[0]:.1f}) z {z:.1f} mo+ {mt}")
# best realistic
cands = [(k, sh, dl) for k in (2, 3) for sh in (0.238, 0.10, 0.05) for dl in (2, 6)]
bst = max(cands, key=lambda t: res1[t][0]); P("BEST realistic (share<=0.238, delay>=2, re-place):", bst, f"{res1[bst][0]:.1f} USD/d z {res1[bst][1]:.1f} mo+ {res1[bst][2]:.0f}%")
k, sh, dl = bst
# TABLE 3 size
P("T3 size (best cell, per-level cap S shares): S -> USD/day, z")
for S in (1.0, 10.0, 50.0):
    c = idx[(k, sh, dl, S, 0, 1)]; u, z, mp, mt = stats(pnl_cfg(c, meas, upr)); P(f" S{int(S)}: {u:.1f} USD/d z {z:.1f} mo+ {mt} fills/d {fills[c][meas].sum()/ND:.1f}")
# TABLE 4 where money
c = idx[(k, sh, dl, 1.0, 0, 1)]
F = fills[c][meas]; U = upr[meas]
P("T4 by level (fill price p, qty/d, win rate, pnl USD/d):")
for j in range(6):
    q = F[:, :, j, :].sum((1, 2)); q0 = F[:, 0, j, :].sum(1); q1 = F[:, 1, j, :].sum(1)
    wins = (q0 * U + q1 * (1 - U)).sum(); qq = q0.sum() + q1.sum()
    P(f" L{lv[j]:.2f}: qty/d {qq/ND:.1f} winrate {wins/qq:.4f} vs p {lv[j]:.2f}  pnl {(wins - lv[j]*qq)/ND:.1f}")
for tb, nm in enumerate(["0-60", "60-180", "180-300"]):
    q0 = F[:, 0, :, tb]; q1 = F[:, 1, :, tb]
    pn = (q0 * (U[:, None] - lv)).sum() + (q1 * ((1 - U)[:, None] - lv)).sum(); qq = q0.sum() + q1.sum()
    wins = (q0.sum(1) * U + q1.sum(1) * (1 - U)).sum()
    avgp = ((q0 + q1) * lv).sum() / qq
    P(f" time {nm}s: qty/d {qq/ND:.1f} avg p {avgp:.3f} winrate {wins/qq:.4f} pnl {pn/ND:.1f} USD/d")
# TABLE 5 monthly + vol
w = pnl_cfg(idx[(k, sh, dl, 1.0, 0, 1)], meas, upr)
mm = pd.Series(w).groupby(mon).sum()
P("T5 monthly USD/day (sum/days in month):", {m: round(v / len(np.unique(day[mon == m])), 1) for m, v in mm.items()}, "months+", f"{(mm>0).sum()}/{len(mm)}")
qs = np.quantile(vol[meas], [0.25, 0.5, 0.75]); vq = np.digitize(vol, qs)
for q in range(4):
    m = meas & (vq == q); ndq = len(np.unique(day[m]))
    P(f" volQ{q+1} (sigma {vol[m].mean():.2e}) windows {int(m.sum())}: {w[m].sum()/ndq:.1f} USD/day over {ndq} d, per window {w[m].mean()*100:.2f} c")
open(f"{D}/t8b_tables.txt", "w").write("\n".join(out)); print("\n".join(out))
