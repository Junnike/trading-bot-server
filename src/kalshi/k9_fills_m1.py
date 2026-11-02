#!/usr/bin/env python3 -I
"""T18 fill check: for CRSI<=20 signal windows (BTC), replace the minute-1 candle ask with the tape.
Order: taker buy YES at t = 60 s + LAT. Fill price = price of the first print after t where the TAKER bought YES (that print IS the ask being lifted).
Also: fill at the first print of any side after t (optimistic), and size of that print. Settle 1/0, fee ceil(0.07 p (1-p)). -> results/T18_fills.md"""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from analyze import crsi
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data"); RES = os.path.join(ROOT, "..", "results")
m1 = pd.read_pickle(f"{ROOT}/cache/spot1m_BTCUSDT.pkl"); vw = m1.vwap
k = m1.resample("15min", label="left", closed="left").agg(o=("o", "first"), c=("c", "last"), n=("o", "count")); k = k[k.n == 15]
k["crsi_prev"] = pd.Series(crsi(k.c.values), index=k.index).shift(1); k["hs"] = (k.o / vw.reindex(k.index - pd.Timedelta(minutes=1)).values - 1) * 1e4
cand = {json.loads(l)["t"]: json.loads(l) for l in open(f"{ROOT}/kalshi/candles.jsonl")}
fee = lambda p: np.ceil(0.07 * p * (1 - p) * 100) / 100
def bz(x, days, B=2000, seed=1):
    g = pd.DataFrame({"x": x, "d": days}).groupby("d").x.agg(["sum", "count"]); s, c = g["sum"].values, g["count"].values
    if len(s) < 5: return float("nan")
    rng = np.random.default_rng(seed); ix = rng.integers(0, len(s), (B, len(s))); m = s[ix].sum(1) / c[ix].sum(1); return x.mean() / m.std(ddof=1)
rows = []
for l in open(f"{ROOT}/kalshi/trades_first3.jsonl"):
    x = json.loads(l)
    if x.get("err"): continue
    r = cand[x["t"]]; o = r["o"]; T = pd.Timestamp(o, unit="s", tz="UTC")
    if T not in k.index: continue
    tr = pd.DataFrame(x["tr"])
    if not len(tr): continue
    tr["s"] = (pd.to_datetime(tr.ts, utc=True, format="ISO8601") - T).dt.total_seconds(); tr = tr.sort_values("s")
    d = {c["e"] - o: c for c in r["cs"]}; ask1 = d.get(60, {}).get("ask")
    rec = dict(t=x["t"], yes=1 if r["res"] == "yes" else 0, crsi=k.crsi_prev[T], hs=k.hs[T], day=pd.Timestamp(r["c"], unit="s", tz="UTC").strftime("%Y-%m-%d"), month=T.strftime("%Y-%m"), ask1=ask1,
               n_prints_m1=int(((tr.s >= 60) & (tr.s < 120)).sum()), vol_m1=float(tr.n[(tr.s >= 60) & (tr.s < 120)].sum()))
    for lat in (2, 5, 15):
        t0 = 60 + lat; w = tr[(tr.s >= t0) & (tr.s < 180)]
        y = w[w.ts_side == "yes"]            # taker bought YES -> that price was the ask
        rec[f"fill_yes_{lat}"] = float(y.p.iloc[0]) if len(y) else np.nan; rec[f"size_yes_{lat}"] = float(y.n.iloc[0]) if len(y) else np.nan; rec[f"fill_s_{lat}"] = float(y.s.iloc[0]) if len(y) else np.nan
        rec[f"fill_any_{lat}"] = float(w.p.iloc[0]) if len(w) else np.nan
    # also the opposite: what price did YES-takers pay in the whole minute 1 (the ask path)
    y1 = tr[(tr.s >= 60) & (tr.s < 120) & (tr.ts_side == "yes")]; rec["ask_path_min"] = float(y1.p.min()) if len(y1) else np.nan; rec["ask_path_max"] = float(y1.p.max()) if len(y1) else np.nan
    rows.append(rec)
D = pd.DataFrame(rows)
L = [f"# T18 fills — CRSI<=20 signal windows with first-3-minute tape (BTC, n {len(D)}; data/kalshi/trades_first3.jsonl)\n",
     f"Minute-1 activity: median prints {D.n_prints_m1.median():.0f}, median contracts {D.vol_m1.median():.0f}; YES-taker prints exist after 62 s in {D.fill_yes_2.notna().mean()*100:.0f}% of windows (that is where a taker buy can be priced from the tape).",
     "\n| signal | fill model | n | hit % | mean fill px | candle ask1 | EV c (fee incl.) | z | median fill delay s | median print size ct |\n|---|---|---|---|---|---|---|---|---|---|"]
for name, msk in [("CRSI<=20", D.crsi <= 20), ("CRSI<=20 & hs>0", (D.crsi <= 20) & (D.hs > 0)), ("CRSI<=20 & hs>+1", (D.crsi <= 20) & (D.hs > 1))]:
    s = D[msk]
    for lat in (2, 5, 15):
        for fm in ("yes", "any"):
            px = s[f"fill_{fm}_{lat}"]; ok = px.notna(); q = s[ok]; p = px[ok]
            if len(q) < 20: continue
            ev = (q.yes - p - fee(p)) * 100
            L.append(f"| {name} | taker, first {'YES-taker' if fm=='yes' else 'any'} print after {60+lat}s | {len(q)} | {q.yes.mean()*100:.1f} | {p.mean():.3f} | {q.ask1.mean():.3f} | {ev.mean():+.2f} | {bz(ev.values, q.day.values):.1f} | {(q[f'fill_s_{lat}'] - 60 - lat).median() if fm=='yes' else float('nan'):.0f} | {q[f'size_yes_{lat}'].median() if fm=='yes' else float('nan'):.0f} |")
    c = s[s.ask1.notna()]; ev = (c.yes - c.ask1 - fee(c.ask1)) * 100
    L.append(f"| {name} | candle ask1 close (T18 table) | {len(c)} | {c.yes.mean()*100:.1f} | {c.ask1.mean():.3f} | {c.ask1.mean():.3f} | {ev.mean():+.2f} | {bz(ev.values, c.day.values):.1f} | | |")
L.append("\nReading: the YES-taker-print fill is what a taker order would have paid (someone lifted that ask); if it is close to the candle ask and EV stays positive, the candle-based T18 numbers are executable at the printed sizes.")
open(f"{RES}/T18_fills.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
