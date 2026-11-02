#!/usr/bin/env python3 -I
"""T16p: last-minute TWAP sniper replay on POLYMARKET BTC 15m Up/Down (Chainlink 60-s TWAP era, 2026-08-15..10-31).
Rule (Kalshi): YES iff mean(BRTI over 60 s before close) >= mean(BRTI over 60 s before open).
Proxy index: Binance BTCUSDT 1-second closes (data/binance1s). Tape: data/kalshi/trades_last2.jsonl (minutes 13-15).
Outputs results/T16_poly_twap_sniper.md. Prices converted to UP-token price; taker side = BUY of Up or BUY of Down (= sold Up). Fee 0.07*p*(1-p) (Polymarket crypto taker fee, no rounding)."""
import os, io, json, zipfile, glob, math
import numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data"); RES = os.path.join(ROOT, "..", "results")
PROB_IN = 0.97; PX_MAX = 0.90; LAT = 2  # base case; variants below
VARIANTS = [(0.97, 2, 0.90, False), (0.99, 2, 0.90, False), (0.999, 2, 0.90, False), (0.99, 2, 0.80, False), (0.99, 2, 0.90, True), (0.999, 2, 0.90, True), (0.999, 5, 0.90, True), (0.999, 2, 0.80, True)]

def fee(p): return 0.07 * p * (1 - p)

_cache = {}
def sec_closes(day):
    if day in _cache: return _cache[day]
    p = f"{ROOT}/binance1s/BTCUSDT-1s-{day}.zip"
    if not os.path.exists(p): _cache[day] = None; return None
    with zipfile.ZipFile(p) as z: raw = z.read(z.namelist()[0])
    hdr = 0 if raw[:1].isalpha() else None
    d = pd.read_csv(io.BytesIO(raw), header=hdr, usecols=[0, 4]); d.columns = ["t", "c"]
    t = d.t.astype("int64").values; t = np.where(t > 10**14, t // 1000, t) // 1000
    s = pd.Series(d.c.values.astype(float), index=t)
    s = s[~s.index.duplicated()]
    _cache[day] = s; return s

def closes(t0, t1):
    """1-s closes for [t0, t1) as array (ffill within day files)."""
    days = sorted({pd.Timestamp(x, unit="s", tz="UTC").strftime("%Y-%m-%d") for x in (t0, t1 - 1)})
    parts = [sec_closes(d) for d in days]
    if any(p is None for p in parts): return None
    s = pd.concat(parts).sort_index()
    idx = np.arange(t0, t1); v = s.reindex(idx).ffill().values
    return v if not np.isnan(v).any() else None

def load_poly():
    for l in open(f"{ROOT}/poly/markets.jsonl"):
        r = json.loads(l)
        if r.get("err") or not r.get("closed"): continue
        try: outs = json.loads(r["outcomes"]); prs = json.loads(r["prices"])
        except Exception: continue
        if sorted(prs) != ["0", "1"]: continue
        up_won = prs[outs.index("Up")] == "1"
        tr = []
        for t in r["tr"]:
            up_px = t["p"] if t["o"] == "Up" else 1 - t["p"]
            taker_bought_up = (t["side"] == "BUY") == (t["o"] == "Up")
            tr.append({"ts": t["ts"], "p": up_px, "n": t["n"], "ts_side": "yes" if taker_bought_up else "no"})
        yield {"t": r["slug"], "o": r["start"], "c": r["start"] + 900, "res": "yes" if up_won else "no", "tr": tr}
rows = []; models = []
for x in load_poly():
    r = x; o, c = r["o"], r["c"]; yes = 1 if r["res"] == "yes" else 0
    pre = closes(o - 60, o); win = closes(o, c)
    if pre is None or win is None: continue
    open_twap = pre.mean(); close_twap = win[-60:].mean()
    cand_label = int(win[-1] >= win[0]); twap_label = int(close_twap >= open_twap)
    rets = np.diff(np.log(win[:13 * 60])); sig = rets.std() if len(rets) > 10 else 1e-4
    tr = pd.DataFrame(x["tr"])
    if len(tr):
        tr["s"] = tr.ts.astype(float) - o; tr = tr.sort_values("s")
    before = tr[tr.s < 14 * 60] if len(tr) else tr
    p14 = before.p.iloc[-1] if len(before) else None
    probs = np.zeros(60)
    for k in range(1, 60):
        partial = win[14 * 60: 14 * 60 + k].mean(); p_now = win[14 * 60 + k - 1]; m = 60 - k
        pred = (partial * k + p_now * m) / 60
        var = (p_now ** 2) * (sig ** 2) * m * (m + 1) * (2 * m + 1) / 6 / 3600
        z = (pred - open_twap) / math.sqrt(var) if var > 0 else (1e9 if pred >= open_twap else -1e9)
        probs[k] = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    models.append(dict(t=x["t"], o=o, c=c, yes=yes, probs=probs, tr=tr, p14=p14))
    rows.append(dict(t=x["t"], yes=yes, cand=cand_label, twap=twap_label, agree_twap=int(twap_label == yes), agree_cand=int(cand_label == yes), ntr=len(tr), p14=p14,
                     first_certain=next((k for k in range(1, 60) if probs[k] >= 0.97 or probs[k] <= 0.03), None)))

def replay(prob_in, lat, px_max, aggr=False):
    out = []
    for mdl in models:
        tr = mdl["tr"]; probs = mdl["probs"]; o = mdl["o"]; yes = mdl["yes"]
        if not len(tr): continue
        for k in range(1, 60):
            prob = probs[k]; side = 1 if prob >= prob_in else (-1 if prob <= 1 - prob_in else 0)
            if not side: continue
            s_now = 14 * 60 + k
            cands = tr[(tr.s >= s_now + lat) & (tr.s < 15 * 60)]
            px_side = cands.p if side == 1 else 1 - cands.p
            ok = cands[px_side <= px_max]
            if aggr:   # realistic: only prints where the TAKER bought our side (so the ask at that price existed)
                ok = ok[ok.ts_side == ("yes" if side == 1 else "no")]
            if len(ok):
                px = ok.p.iloc[0] if side == 1 else 1 - ok.p.iloc[0]; win_ = yes if side == 1 else 1 - yes; sz = float(ok.n.iloc[0])
                out.append(dict(t=mdl["t"], month=pd.Timestamp(o, unit="s", tz="UTC").strftime("%Y-%m"), day=pd.Timestamp(mdl["c"], unit="s", tz="UTC").strftime("%Y-%m-%d"),
                                k=k, side=side, prob=prob if side == 1 else 1 - prob, px=px, win=win_, pnl=(win_ - px - fee(px)) * 100, fill_s=float(ok.s.iloc[0]), p14=mdl["p14"], sz=sz))
            break
    return pd.DataFrame(out)
trades = replay(PROB_IN, LAT, PX_MAX).to_dict("records")
D = pd.DataFrame(rows); T = pd.DataFrame(trades)
def bz(x, days, B=2000, seed=1):
    g = pd.DataFrame({"x": x, "d": days}).groupby("d").x.agg(["sum", "count"]); s, c = g["sum"].values, g["count"].values
    if len(s) < 5: return float("nan")
    rng = np.random.default_rng(seed); ix = rng.integers(0, len(s), (B, len(s))); m = s[ix].sum(1) / c[ix].sum(1); return x.mean() / m.std(ddof=1)
L = [f"# T16p — last-minute TWAP sniper replay, POLYMARKET BTC 15m Up/Down, Chainlink 60-s TWAP era (markets with tape: {len(D)}; data/poly/markets.jsonl; index proxy Binance 1-s closes, fee 0.07·p·(1−p))\n",
     f"Proxy check: Binance 60-s TWAP label agrees with Polymarket resolution in {D.agree_twap.mean()*100:.2f}% of windows; Binance candle colour (close>=open) agrees in {D.agree_cand.mean()*100:.2f}% -> candle-vs-settlement mismatch {100-D.agree_cand.mean()*100:.2f}%, TWAP-vs-settlement mismatch {100-D.agree_twap.mean()*100:.2f}% (index difference BRTI vs Binance).",
     f"Model certainty: a side reaches prob >= {PROB_IN} at median second {D.first_certain.median():.0f} of the closing minute (reached at all in {D.first_certain.notna().mean()*100:.0f}% of windows).\n",
     f"## Sniper: buy the certain side (prob >= {PROB_IN}) at the first tape print <= {PX_MAX} that is >= {LAT} s after the signal, taker fee ceil(0.07·p·(1−p)), settle 1/0\n"]
if len(T):
    L.append(f"| fires | per window | hit rate | mean price paid | EV c/contract | z (cluster day) | median signal second | median fill second | by side (YES/NO fires) |\n|---|---|---|---|---|---|---|---|---|")
    L.append(f"| {len(T)} | {len(T)/len(D)*100:.1f}% | {T.win.mean()*100:.1f}% | {T.px.mean():.3f} | {T.pnl.mean():+.2f} | {bz(T.pnl.values, T.day.values):.1f} | {T.k.median():.0f} | {T.fill_s.median()-14*60:.0f} | {(T.side==1).sum()}/{(T.side==-1).sum()} |")
    mo = T.groupby("month").agg(n=("pnl", "size"), ev=("pnl", "mean"), hit=("win", "mean"))
    L.append("\nBy month (fires, EV c, hit): " + " ".join(f"{m}:{r.n:.0f},{r.ev:+.1f},{r.hit*100:.0f}%" for m, r in mo.iterrows()))
    L.append(f"Months with EV > 0: {(mo.ev>0).sum()}/{len(mo)}")
    for pm in (0.80, 0.95):
        sub = T[(T.px <= pm)] if pm < PX_MAX else T
        L.append(f"Price cap {pm}: fires {len(sub)}, EV {sub.pnl.mean():+.2f}c, hit {sub.win.mean()*100:.1f}%" if len(sub) else f"Price cap {pm}: no fires")
    # who pays: the holder's price at 14:00 in fired windows
    f14 = T.dropna(subset=["p14"])
    if len(f14):
        L.append(f"Counterparty: in fired windows the last print before 14:00 was {f14.p14.mean():.3f} (YES price); the sniper's fills average {f14.px.mean():.3f} on the winning side, i.e. the 14:00 holder of the losing side sells out {((f14.side==1)&(f14.p14>0.5)|(f14.side==-1)&(f14.p14<0.5)).mean()*100:.0f}% of the time on the side the model already calls.")
else:
    L.append("No fires: the tape never printed <= PX_MAX on the certain side after the signal (market already priced it) in any window.")
if len(T):
    T["pb"] = pd.cut(T.prob, [0.97, 0.99, 0.995, 0.999, 1.0001], right=False)
    cal = T.groupby("pb", observed=True).agg(n=("win", "size"), claimed=("prob", "mean"), hit=("win", "mean"), ev=("pnl", "mean"))
    L.append("\nCalibration of the model on fired trades (claimed prob vs hit): " + "; ".join(f"{i}: n {r.n:.0f}, claimed {r.claimed:.3f}, hit {r.hit:.3f}, EV {r.ev:+.1f}c" for i, r in cal.iterrows()))
    L.append("\n| variant prob_in / latency s / price cap / fill model | fires | per window | hit % | mean px | median print size (contracts) | EV c | z | months EV>0 |\n|---|---|---|---|---|---|---|---|---|")
    for pi, la, pm, ag in VARIANTS:
        V = replay(pi, la, pm, ag)
        if not len(V): L.append(f"| {pi} / {la} / {pm} / {'aggressor-side' if ag else 'any print'} | 0 | | | | | | | |"); continue
        mv = V.groupby("month").pnl.mean()
        L.append(f"| {pi} / {la} / {pm} / {'aggressor-side' if ag else 'any print'} | {len(V)} | {len(V)/len(D)*100:.1f}% | {V.win.mean()*100:.1f} | {V.px.mean():.3f} | {V.sz.median():.0f} | {V.pnl.mean():+.2f} | {bz(V.pnl.values, V.day.values):.1f} | {(mv>0).sum()}/{len(mv)} |")
L.append(f"\nCaveats: (1) fill = a print at or below our limit, not a quote: optimistic (same as T12 model A); (2) Binance 1-s close as BRTI proxy, mismatch {100-D.agree_twap.mean()*100:.2f}% of windows mostly where |closeTWAP-openTWAP| is a few bp; (3) latency {LAT} s from model to order; (4) one trade per window, no size: the tape shows what printed, not depth.")
os.makedirs(RES, exist_ok=True); open(f"{RES}/T16_poly_twap_sniper.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
D.to_csv(f"{RES}/T16p_windows.csv", index=False); T.to_csv(f"{RES}/T16p_trades.csv", index=False)
