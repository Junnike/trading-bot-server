#!/usr/bin/env python3 -I
"""Stage 4: maker fill replay for the T1b cell (minute 7, yes_bid_close in [.70,.90)).
Order: resting BUY YES at bid_7 (= yes_bid close of the candle ending at open+7:00), live from 7:02 (2 s latency), cancelled at 8:00.
Fill models: A any trade at price <= bid in (7:02, 8:00]; B trade strictly below bid (trade-through); C queue -> UNMEASURED (no book history).
Payout: YES settles 1/0; maker fee 0. Cluster bootstrap by close date. -> results/T12_kalshi_fill.md"""
import json, numpy as np, pandas as pd
cand = {}
for l in open("data/kalshi/candles.jsonl"):
    r = json.loads(l); cand[r["t"]] = r
rows = []
for l in open("data/kalshi/trades.jsonl"):
    x = json.loads(l); r = cand[x["t"]]; o = r["o"]
    m7 = [c for c in r["cs"] if c["e"] == o + 7 * 60][0]; bid = m7["bid"]; ask = m7["ask"]
    tr = pd.DataFrame(x["tr"])
    if len(tr):
        tr["s"] = (pd.to_datetime(tr.ts, utc=True) - pd.Timestamp(o, unit="s", tz="UTC")).dt.total_seconds()
        w = tr[(tr.s > 7 * 60 + 2) & (tr.s <= 8 * 60)]
    else: w = tr
    fillA = bool(len(w) and (w.p <= bid + 1e-9).any()); fillB = bool(len(w) and (w.p < bid - 1e-9).any())
    volA = float(w.n[w.p <= bid + 1e-9].sum()) if len(w) else 0.0; volB = float(w.n[w.p < bid - 1e-9].sum()) if len(w) else 0.0
    yes = 1 if r["res"] == "yes" else 0
    rows.append(dict(t=x["t"], day=pd.Timestamp(r["c"], unit="s", tz="UTC").strftime("%Y-%m-%d"), month=pd.Timestamp(o, unit="s", tz="UTC").strftime("%Y-%m"),
                     bid=bid, ask=ask, yes=yes, pnl=(yes - bid) * 100, fillA=fillA, fillB=fillB, volA=volA, volB=volB, ntr=len(w), err=x.get("err", 0)))
D = pd.DataFrame(rows); D = D[D.err == 0]
def bz(x, days, B=2000, seed=1):
    g = pd.DataFrame({"x": x, "d": days}).groupby("d").x.agg(["sum", "count"]); s, c = g["sum"].values, g["count"].values
    rng = np.random.default_rng(seed); ix = rng.integers(0, len(s), (B, len(s))); m = s[ix].sum(1) / c[ix].sum(1)
    return x.mean() / m.std(ddof=1) if m.std(ddof=1) > 0 else np.nan
L = []
L.append(f"n signals (cell windows with tape) = {len(D)}; sampled windows = {len(cand)}; months = {D.month.nunique()}; hit-bid EV all signals (T1b replica) = {D.pnl.mean():+.2f}c, z {bz(D.pnl.values, D.day.values):.1f}, win {D.yes.mean()*100:.1f}%")
L.append("| model | fill rate | EV/filled c | EV/signal c | n fills | z (cluster day) | win% filled | win% unfilled |\n|---|---|---|---|---|---|---|---|")
res = {}
for mname, col in [("A optimistic (trade <= bid)", "fillA"), ("B trade-through (trade < bid)", "fillB")]:
    f = D[D[col]]; u = D[~D[col]]; fr = D[col].mean()
    evf = f.pnl.mean() if len(f) else np.nan; z = bz(f.pnl.values, f.day.values) if len(f) > 10 else np.nan
    res[col] = dict(fr=fr, evf=evf, evs=fr * evf, n=len(f), z=z, wf=f.yes.mean() * 100 if len(f) else np.nan, wu=u.yes.mean() * 100 if len(u) else np.nan)
    L.append(f"| {mname} | {fr*100:.1f}% | {evf:+.2f} | {fr*evf:+.2f} | {len(f)} | {z:.1f} | {res[col]['wf']:.1f} | {res[col]['wu']:.1f} |")
L.append("| C queue (depth ahead) | unmeasured | unmeasured | unmeasured | unmeasured | unmeasured | unmeasured | unmeasured |")
# monthly, model B
mo = D.groupby("month").apply(lambda g: pd.Series(dict(n=len(g), fillB=g.fillB.mean() * 100, ev_signal=(g.pnl * g.fillB).mean(), ev_filled=g.pnl[g.fillB].mean() if g.fillB.any() else np.nan, hitbid=g.pnl.mean())), include_groups=False)
L.append("\nModel B by month (EV/signal c, fill %, n): " + " ".join(f"{m}:{r.ev_signal:+.2f}({r.fillB:.0f}%,{int(r.n)})" for m, r in mo.iterrows()))
pos = int((mo.ev_signal > 0).sum()); L.append(f"Months positive (model B EV/signal): {pos}/{len(mo)}")
last2 = D[D.month.isin(sorted(D.month.unique())[-2:])]; fB = last2[last2.fillB]
L.append(f"Last-2-months holdout ({', '.join(sorted(D.month.unique())[-2:])}): model B fill {last2.fillB.mean()*100:.1f}%, EV/filled {fB.pnl.mean():+.2f}c, EV/signal {(last2.pnl*last2.fillB).mean():+.2f}c, n fills {len(fB)}, z {bz(fB.pnl.values, fB.day.values) if len(fB)>10 else np.nan:.1f}")
# adverse selection detail & confounders
L.append(f"Adverse selection: filled(B) win {res['fillB']['wf']:.1f}% vs unfilled {res['fillB']['wu']:.1f}% (bid mean filled {D.bid[D.fillB].mean():.3f} vs unfilled {D.bid[~D.fillB].mean():.3f}); median contracts traded below bid when filled = {D.volB[D.fillB].median():.0f}")
spread = (D.ask - D.bid); L.append(f"Spread at 7:00: median {spread.median()*100:.1f}c; bid on sub-cent tick (not multiple of 1c): {((D.bid*100).round(3) % 1 != 0).mean()*100:.1f}% of signals; windows with zero trades in (7:02,8:00]: {(D.ntr==0).mean()*100:.1f}%")
dead = res["fillB"]["evs"] <= 0.5 or pos < 8
L.append(f"KILL RULE: model B EV/signal {res['fillB']['evs']:+.2f}c (need > +0.5) and {pos}/{len(mo)} months positive (need >= 8/11) -> {'DEAD' if dead else 'ALIVE'}")
open("results/T12_kalshi_fill.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
D.to_csv("results/T12_kalshi_fill_signals.csv", index=False)
