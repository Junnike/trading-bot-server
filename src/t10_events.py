# T10: event windows vs others. Inputs data/binance/*.parquet (1-s), data/poly/*_markets|trades.parquet (D6), data/poly_resolution.parquet (real label)
import glob, json, os, numpy as np, pandas as pd
D = "data"; ND = 239
# Event dates (US data days, 08:30 ET). From public BLS/Fed calendars as recalled; NOT verified online (bls.gov page only lists future dates). Completeness uncertain.
CPI = ["2026-02-13","2026-03-11","2026-04-10","2026-05-12","2026-06-10","2026-07-14","2026-08-12","2026-09-11","2026-10-14"]
NFP = ["2026-02-11","2026-03-06","2026-04-03","2026-05-08","2026-06-05","2026-07-02","2026-08-07","2026-09-04","2026-10-02"]
FOMC = ["2026-03-18","2026-04-29","2026-06-17","2026-07-29","2026-09-16"]
EVD = set(CPI + NFP + FOMC)
bn = pd.concat([pd.read_parquet(f, columns=["t", "c"]) for f in sorted(glob.glob(f"{D}/binance/BTCUSDT-1s-*.parquet"))])
T0 = int(bn.t.min()); N = int(bn.t.max()) - T0 + 1
px = np.full(N, np.nan); px[bn.t.values - T0] = bn.c.values; px = pd.Series(px).ffill().values
rs = pd.read_parquet(f"{D}/poly_resolution.parquet"); sl = dict(zip(rs.slug, rs.prices))
def lab(p):
    try: a = json.loads(p); return 1 if a[0] == "1" else (0 if a[1] == "1" else -1)
    except Exception: return -1
rows = []
for f in sorted(glob.glob(f"{D}/poly/*_trades.parquet")):
    d = os.path.basename(f)[:10]
    if d > "2026-10-08": continue
    mk = pd.read_parquet(f"{D}/poly/{d}_markets.parquet", columns=["cid", "start", "slug"])
    mk = mk[(mk.start - T0 >= 0) & (mk.start + 300 - T0 < N)]
    mk["up"] = mk.slug.map(lambda s: lab(sl.get(s)))
    st = mk.start.values
    mk["mv"] = px[st + 120 - T0] / px[st - T0] - 1
    tr = pd.read_parquet(f, columns=["cid", "oi", "side", "price", "ts"])
    tr = tr[tr.side == "BUY"].merge(mk[["cid", "start", "mv"]], on="cid")
    tr["age"] = tr.ts - tr.start
    tr = tr[(tr.age >= 120) & (tr.age <= 150)]
    tr["pointed"] = (tr.mv > 0).astype(int)
    tr = tr[tr.oi == np.where(tr.mv > 0, 0, 1)].sort_values(["start", "ts"])
    ask = tr.groupby("start").price.first()   # first taker BUY print of the pointed token at/after +120 s = ask proxy
    mk["ask"] = mk.start.map(ask)
    rows.append(mk[["start", "up", "mv", "ask"]])
W = pd.concat(rows).drop_duplicates("start").reset_index(drop=True)
W = W[(W.up >= 0) & (W.mv != 0)].reset_index(drop=True)
W["hit"] = ((W.mv > 0).astype(int) == W.up).astype(int)
W["ev"] = (W.hit - W.ask - 0.07 * W.ask * (1 - W.ask)) * 100
dt_ny = pd.to_datetime(W.start, unit="s", utc=True).dt.tz_convert("America/New_York")
dt_u = pd.to_datetime(W.start, unit="s", utc=True)
mn = lambda dt, h, m: ((dt.dt.hour * 60 + dt.dt.minute) - (h * 60 + m))
nyday = dt_ny.dt.strftime("%Y-%m-%d"); dow = dt_ny.dt.dayofweek  # Mon=0..Sun=6
inw = lambda x: (x >= -10) & (x <= 10)
T = {
 "0830NY_dataday": inw(mn(dt_ny, 8, 30)) & nyday.isin(EVD),
 "0930NY_weekday": inw(mn(dt_ny, 9, 30)) & (dow <= 4),
 "CME1800NY_SunFri": inw(mn(dt_ny, 18, 0)) & (dow != 5),
 "0000UTC": inw(((dt_u.dt.hour * 60 + dt_u.dt.minute + 10) % 1440) - 10),
}
anyev = np.zeros(len(W), bool)
for v in T.values(): anyev |= v.values
T["OTHER(no event)"] = pd.Series(~anyev)
T["ALL"] = pd.Series(np.ones(len(W), bool))
day = (W.start // 86400).values; ud, di = np.unique(day, return_inverse=True)
mon = pd.to_datetime(W.start, unit="s").dt.strftime("%Y-%m").values
BI = np.random.default_rng(11).integers(0, len(ud), (2000, len(ud)))
def cl(mask, col):
    # day-cluster bootstrap of mean over windows in mask with valid col
    v = W[col].values; m = mask & ~np.isnan(v)
    s = np.bincount(di, weights=np.where(m, v, 0), minlength=len(ud)); c = np.bincount(di, weights=m.astype(float), minlength=len(ud))
    ss = s[BI].sum(1); cc = c[BI].sum(1); bm = ss / np.maximum(cc, 1)
    return v[m].mean(), bm.std(), int(m.sum()), bm
out = []; P = lambda s: out.append(s)
P(f"windows with label+move+ask proxy: {W.ask.notna().sum()} of {len(W)} (hit-rate base all {W.hit.mean():.4f})")
res = {}
for k, v in T.items():
    m = v.values
    h, hs, nh, hb = cl(m, "hit"); e, es, ne, eb = cl(m, "ev")
    ev_m = pd.Series(W.ev.values[m & W.ask.notna().values]).groupby(mon[m & W.ask.notna().values]).mean()
    res[k] = (e, eb, nh)
    P(f"{k}: n_hit={nh} hit={h:.4f} (z vs 0.5 {(h-.5)/hs:.1f}) | n_ev={ne} EV={e:.2f} c/sh z {e/es:.1f} | months+ {(ev_m>0).sum()}/{len(ev_m)} ({(ev_m>0).mean()*100:.0f}%)")
o = res["OTHER(no event)"]
for k in list(T)[:4]:
    d = res[k][1] - o[1]; P(f"  diff EV {k} minus OTHER: {res[k][0]-o[0]:+.2f} c/sh (bootstrap z, independent-resample approx) {(res[k][0]-o[0])/np.sqrt(res[k][1].var()+o[1].var()):.1f}")
# FOMC 14:00 variant
m14 = (inw(mn(dt_ny, 14, 0)) & nyday.isin(FOMC)).values
e, es, ne, _ = cl(m14, "ev"); h, hs, nh, _ = cl(m14, "hit")
P(f"variant FOMC 14:00NY: n_hit={nh} hit={h:.4f} n_ev={ne} EV={e:.2f} z {e/es:.1f}")
open(f"{D}/t10_tables.txt", "w").write("\n".join(out)); print("\n".join(out))
