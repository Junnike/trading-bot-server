#!/usr/bin/env python3 -I
"""T18: signal-at-minute-1 scorer on Kalshi 15m markets. Signal known at the open from Binance data:
 CRSI(2,2,75) of the previous 15m close (<=20 -> UP) and head start hs = open price / VWAP of the pre-open minute - 1 (bp).
Price = Kalshi 1-min candle yes_bid/yes_ask close at minute 1 (and 2). Taker fee ceil(0.07 p (1-p)). Settle 1/0.
Usage: python3 -I src/kalshi/k8_signal_m1.py KXBTC15M BTCUSDT   -> appends a section to results/T18_signal_m1.md"""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from analyze import crsi
S = sys.argv[1] if len(sys.argv) > 1 else "KXBTC15M"; SYM = sys.argv[2] if len(sys.argv) > 2 else "BTCUSDT"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data"); RES = os.path.join(ROOT, "..", "results")
cf = f"{ROOT}/kalshi/candles_{S}.jsonl" if S != "KXBTC15M" else f"{ROOT}/kalshi/candles.jsonl"
m1 = pd.read_pickle(f"{ROOT}/cache/spot1m_{SYM}.pkl"); vw = m1.vwap
k = m1.resample("15min", label="left", closed="left").agg(o=("o", "first"), c=("c", "last"), n=("o", "count")); k = k[k.n == 15]
k["crsi_prev"] = pd.Series(crsi(k.c.values), index=k.index).shift(1)
k["hs"] = (k.o / vw.reindex(k.index - pd.Timedelta(minutes=1)).values - 1) * 1e4
rows = []
for l in open(cf):
    r = json.loads(l); o = r["o"]; T = pd.Timestamp(o, unit="s", tz="UTC")
    if T not in k.index or np.isnan(k.crsi_prev[T]) or np.isnan(k.hs[T]): continue
    d = {c["e"] - o: c for c in r["cs"]}; c1 = d.get(60, {}); c2 = d.get(120, {})
    rows.append({"yes": 1 if r["res"] == "yes" else 0, "crsi": k.crsi_prev[T], "hs": k.hs[T], "day": pd.Timestamp(r["c"], unit="s", tz="UTC").strftime("%Y-%m-%d"),
                 "month": T.strftime("%Y-%m"), "bid1": c1.get("bid"), "ask1": c1.get("ask"), "bid2": c2.get("bid"), "ask2": c2.get("ask"), "vol1": c1.get("vol")})
D = pd.DataFrame(rows).dropna(subset=["ask1", "bid1"]); fee = lambda p: np.ceil(0.07 * p * (1 - p) * 100) / 100
def bz(x, days, B=2000, seed=1):
    g = pd.DataFrame({"x": x, "d": days}).groupby("d").x.agg(["sum", "count"]); s, c = g["sum"].values, g["count"].values
    if len(s) < 5: return float("nan")
    rng = np.random.default_rng(seed); ix = rng.integers(0, len(s), (B, len(s))); m = s[ix].sum(1) / c[ix].sum(1); return x.mean() / m.std(ddof=1)
L = [f"\n## {S} / {SYM} — {len(D)} windows with minute-1 quotes, {D.month.min()}..{D.month.max()}, base P(yes) {D.yes.mean()*100:.1f}%, mid1 {((D.ask1+D.bid1)/2).mean():.3f}\n",
     "| signal | n | per day | hit % | market mid1 | ask1 | taker EV @ask1 c | z (cluster day) | taker EV @ask2 c | maker @bid1 EV c (fill assumed) | months > 0 | median m1 volume (ct) |\n|---|---|---|---|---|---|---|---|---|---|---|---|"]
SIG = [("CRSI<=20", lambda D: D.crsi <= 20, 1), ("CRSI<=20 & hs>0", lambda D: (D.crsi <= 20) & (D.hs > 0), 1), ("CRSI<=20 & hs>+1", lambda D: (D.crsi <= 20) & (D.hs > 1), 1),
       ("CRSI<=20 & hs>+3", lambda D: (D.crsi <= 20) & (D.hs > 3), 1), ("CRSI<=10 & hs>0", lambda D: (D.crsi <= 10) & (D.hs > 0), 1), ("hs>+3 only", lambda D: D.hs > 3, 1),
       ("CRSI>=80 & hs<0 (buy NO)", lambda D: (D.crsi >= 80) & (D.hs < 0), -1), ("CRSI>=80 & hs<-1 (buy NO)", lambda D: (D.crsi >= 80) & (D.hs < -1), -1), ("hs<-3 only (buy NO)", lambda D: D.hs < -3, -1)]
days_total = D.day.nunique()
for name, f, side in SIG:
    s = D[f(D)]
    if len(s) < 30: L.append(f"| {name} | {len(s)} | | | | | | | | | | |"); continue
    if side == 1: win, px1, px2, pxm, mid = s.yes, s.ask1, s.ask2, s.bid1, (s.ask1 + s.bid1) / 2
    else: win, px1, px2, pxm, mid = 1 - s.yes, 1 - s.bid1, 1 - s.bid2, 1 - s.ask1, 1 - (s.ask1 + s.bid1) / 2
    ev1 = (win - px1 - fee(px1)) * 100; ev2 = (win - px2.fillna(px1) - fee(px2.fillna(px1))) * 100; evm = (win - pxm) * 100; mo = ev1.groupby(s.month).mean()
    L.append(f"| {name} | {len(s)} | {len(s)/days_total:.1f} | {win.mean()*100:.1f} | {mid.mean():.3f} | {px1.mean():.3f} | {ev1.mean():+.2f} | {bz(ev1.values, s.day.values):.1f} | {ev2.mean():+.2f} | {evm.mean():+.2f} | {(mo>0).sum()}/{len(mo)} | {s.vol1.median():.0f} |")
s = D[(D.crsi <= 20) & (D.hs > 0)]; ev1 = (s.yes - s.ask1 - fee(s.ask1)) * 100
L.append("\nCRSI<=20 & hs>0 by month (taker EV c / n): " + " ".join(f"{m[2:]}:{v:+.1f}/{n}" for (m, v), n in zip(ev1.groupby(s.month).mean().items(), ev1.groupby(s.month).size())))
os.makedirs(RES, exist_ok=True)
p = f"{RES}/T18_signal_m1.md"
if not os.path.exists(p): open(p, "w").write("# T18 — Binance-derived signals priced at Kalshi minute 1 (CRSI not priced, head start priced)\n\nSignals computed at the window open from Binance 1-minute data; executed at the Kalshi minute-1 ask (taker) or bid (maker, fill assumed). Candle quotes are closes of the 1-minute candle, not the book: see the tape-based fill check in T18_fills.\n")
open(p, "a").write("\n".join(L) + "\n"); print("\n".join(L))
