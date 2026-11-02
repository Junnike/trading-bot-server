#!/usr/bin/env python3 -I
"""T18p: does Polymarket price CRSI / head start at minute 1? BTC Up/Down 15m, TWAP era, tape minutes -1..3 (data/poly/markets_first3.jsonl).
Signal at the open from Binance 1-min data (CRSI(2,2,75) of previous 15m close; hs = open / pre-open-minute VWAP - 1, bp).
Entry: taker buy UP at t = 60 s + LAT: fill = first print after t where the taker BOUGHT Up (that print is the ask). Market mid at minute 1 from
the last Up-taker (ask) and Down-taker (bid = 1 - p) prints before t. Fee 0.07 p (1-p). Settle 1/0. -> results/T18_poly_signal_m1.md"""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from analyze import crsi
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data"); RES = os.path.join(ROOT, "..", "results")
m1 = pd.read_pickle(f"{ROOT}/cache/spot1m_BTCUSDT.pkl"); vw = m1.vwap
k = m1.resample("15min", label="left", closed="left").agg(o=("o", "first"), c=("c", "last"), n=("o", "count")); k = k[k.n == 15]
k["crsi_prev"] = pd.Series(crsi(k.c.values), index=k.index).shift(1); k["hs"] = (k.o / vw.reindex(k.index - pd.Timedelta(minutes=1)).values - 1) * 1e4
fee = lambda p: 0.07 * p * (1 - p)
def bz(x, days, B=2000, seed=1):
    g = pd.DataFrame({"x": x, "d": days}).groupby("d").x.agg(["sum", "count"]); s, c = g["sum"].values, g["count"].values
    if len(s) < 5: return float("nan")
    rng = np.random.default_rng(seed); ix = rng.integers(0, len(s), (B, len(s))); m = s[ix].sum(1) / c[ix].sum(1); return x.mean() / m.std(ddof=1)
rows = []
for l in open(f"{ROOT}/poly/markets_first3.jsonl"):
    r = json.loads(l)
    if r.get("err") or not r.get("closed") or not r.get("tr"): continue
    try: outs = json.loads(r["outcomes"]); prs = json.loads(r["prices"])
    except Exception: continue
    if sorted(prs) != ["0", "1"]: continue
    st = r["start"]; T = pd.Timestamp(st, unit="s", tz="UTC")
    if T not in k.index or np.isnan(k.crsi_prev[T]) or np.isnan(k.hs[T]): continue
    up = 1 if prs[outs.index("Up")] == "1" else 0
    tr = pd.DataFrame(r["tr"]); tr["s"] = tr.ts - st
    tr["up_px"] = np.where(tr.o == "Up", tr.p, 1 - tr.p); tr["taker_up"] = (tr.side == "BUY") == (tr.o == "Up"); tr = tr.sort_values("s")
    rec = dict(t=r["slug"], up=up, crsi=k.crsi_prev[T], hs=k.hs[T], day=pd.Timestamp(st + 900, unit="s", tz="UTC").strftime("%Y-%m-%d"), month=T.strftime("%Y-%m"),
               n_m1=int(((tr.s >= 60) & (tr.s < 120)).sum()), vol_m1=float(tr.n[(tr.s >= 60) & (tr.s < 120)].sum()))
    before = tr[(tr.s < 62) & (tr.s >= 0)]; a = before[before.taker_up]; b = before[~before.taker_up]
    rec["ask1"] = float(a.up_px.iloc[-1]) if len(a) else np.nan; rec["bid1"] = float(b.up_px.iloc[-1]) if len(b) else np.nan
    for lat in (2, 5, 15):
        w = tr[(tr.s >= 60 + lat) & (tr.s < 180) & tr.taker_up]
        rec[f"fill_{lat}"] = float(w.up_px.iloc[0]) if len(w) else np.nan; rec[f"size_{lat}"] = float(w.n.iloc[0]) if len(w) else np.nan
    rows.append(rec)
D = pd.DataFrame(rows)
L = [f"# T18p — Polymarket BTC 15m: CRSI / head-start signals at minute 1 (TWAP era, n markets {len(D)}, {D.month.min()}..{D.month.max()}; data/poly/markets_first3.jsonl)\n",
     f"Minute-1 activity: median prints {D.n_m1.median():.0f}, median shares {D.vol_m1.median():.0f}. Base P(Up) {D.up.mean()*100:.1f}%; minute-1 mid (from last ask/bid prints) {((D.ask1+D.bid1)/2).mean():.3f}.\n",
     "| signal | n | hit % | mid1 | fill px (first Up-taker print after 62 s) | EV c (fee incl.) | z | months > 0 | fill after 65 s EV | fill after 75 s EV | median print size |\n|---|---|---|---|---|---|---|---|---|---|---|"]
for name, msk in [("CRSI<=20", D.crsi <= 20), ("CRSI<=20 & hs>0", (D.crsi <= 20) & (D.hs > 0)), ("CRSI<=20 & hs>+1", (D.crsi <= 20) & (D.hs > 1)), ("CRSI<=20 & hs>+3", (D.crsi <= 20) & (D.hs > 3)), ("hs>+3 only", D.hs > 3), ("all windows (buy Up)", D.crsi > -1)]:
    s = D[msk & D.fill_2.notna()]
    if len(s) < 30: L.append(f"| {name} | {len(s)} | | | | | | | | | |"); continue
    ev = (s.up - s.fill_2 - fee(s.fill_2)) * 100; mo = ev.groupby(s.month).mean()
    e5 = ((s.up - s.fill_5 - fee(s.fill_5)) * 100).mean(); e15 = ((s.up - s.fill_15 - fee(s.fill_15)) * 100).mean()
    L.append(f"| {name} | {len(s)} | {s.up.mean()*100:.1f} | {((s.ask1+s.bid1)/2).mean():.3f} | {s.fill_2.mean():.3f} | {ev.mean():+.2f} | {bz(ev.values, s.day.values):.1f} | {(mo>0).sum()}/{len(mo)} | {e5:+.2f} | {e15:+.2f} | {s.size_2.median():.0f} |")
s = D[(D.crsi <= 20) & (D.hs > 0) & D.fill_2.notna()]; ev = (s.up - s.fill_2 - fee(s.fill_2)) * 100
L.append("\nCRSI<=20 & hs>0 by month (EV c / n): " + " ".join(f"{m[2:]}:{v:+.1f}/{n}" for (m, v), n in zip(ev.groupby(s.month).mean().items(), ev.groupby(s.month).size())))
L.append("\nNote: Polymarket's minute-1 'mid' is reconstructed from the last aggressor prints on each side before 62 s, not from a book snapshot.")
open(f"{RES}/T18_poly_signal_m1.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
