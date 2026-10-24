#!/usr/bin/env python3 -I
"""T12: CRSI(2,2,75)<=20 -> next 15m candle UP robot, measured on public Binance.vision data.
Produces results/T12_tables.md (auto tables) and results/T12_numbers.json."""
import os, json, numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = f"{HERE}/../data/cache"; RES = f"{HERE}/../results"
SYMS = ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]
FEES = [10, 2, 0]; NBOOT = 2000; RNG = np.random.default_rng(12345)
LOOKBACK = 80  # bars of contiguous history required before a signal (percentrank window 75 + rsi warmup)

def rma(x, n):  # Pine ta.rma: alpha=1/n, SMA seed
    x = pd.Series(x); out = x.ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    return out.values
def rsi(x, n):
    ch = np.diff(x, prepend=np.nan); u = np.where(ch > 0, ch, 0.0); d = np.where(ch < 0, -ch, 0.0)
    u[0] = d[0] = np.nan
    ru, rd = rma(u, n), rma(d, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + ru / rd)
    r = np.where(rd == 0, 100.0, r); r = np.where((ru == 0) & (rd == 0), 50.0, r)  # Pine convention for 0/0 -> rsi 50? (ta.rsi returns 100 when d==0; 50 when both 0 is not reached in practice)
    return r
def streak(c):
    s = np.zeros(len(c))
    for i in range(1, len(c)):
        if c[i] == c[i-1]: s[i] = 0
        elif c[i] > c[i-1]: s[i] = 1 if s[i-1] <= 0 else s[i-1] + 1
        else: s[i] = -1 if s[i-1] >= 0 else s[i-1] - 1
    return s
def percentrank(x, n):  # % of previous n values <= current
    out = np.full(len(x), np.nan)
    if len(x) <= n: return out
    w = sliding_window_view(x, n + 1)  # w[i] = x[i..i+n]; current = w[:, -1], previous = w[:, :-1]
    out[n:] = (w[:, :-1] <= w[:, -1:]).sum(1) / n * 100
    return out
def crsi(close, a=2, b=2, c=75):
    roc = np.diff(close, prepend=np.nan) / np.roll(close, 1) * 100; roc[0] = np.nan
    return (rsi(close, a) + rsi(streak(close), b) + percentrank(roc, c)) / 3

def load15(market, sym):
    k5 = pd.read_pickle(f"{CACHE}/{market}_{sym}_5m.pkl")
    g = k5.resample("15min", label="left", closed="left")
    k = g.agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last"), volume=("volume","sum"), n5=("open","count"))
    k = k[k.n5 > 0].copy()
    k["complete"] = k.n5 == 3
    # first 5m bar of the 15m candle (for maker-fill test) and the +5min bar open (entry B)
    k["low5_1"] = k5["low"].reindex(k.index).values; k["high5_1"] = k5["high"].reindex(k.index).values
    k["open5_2"] = k5["open"].reindex(k.index + pd.Timedelta(minutes=5)).values
    return k

def signals(k):
    """Return DataFrame of trades: one row per signal bar t with entry on bar t+1."""
    k = k.copy()
    k["crsi"] = crsi(k.close.values)
    ts = k.index.asi8 // 60_000  # minutes
    contiguous = np.r_[False, np.diff(ts) == 15]  # bar i directly follows bar i-1
    ok_hist = pd.Series(contiguous & k.complete.values).rolling(LOOKBACK, min_periods=LOOKBACK).min().fillna(0).values.astype(bool)
    sig = (k.crsi.values <= 20) & ok_hist
    idx = np.where(sig)[0]
    idx = idx[idx + 4 < len(k)]
    # entry bar t+1 must be contiguous & complete; hold-longer exits need t+2, t+4 contiguous
    nxt_ok = contiguous[idx + 1] & k.complete.values[idx + 1]
    idx = idx[nxt_ok]
    e = idx + 1
    df = pd.DataFrame({"sig_time": k.index[idx], "entry_time": k.index[e], "entryA": k.open.values[e], "entryB": k.open5_2.values[e],
                       "exit1": k.close.values[e], "open_e": k.open.values[e], "low5": k.low5_1.values[e], "high5": k.high5_1.values[e],
                       "c2ok": contiguous[e+1] & k.complete.values[e+1], "exit2": k.close.values[e+1],
                       "c4ok": contiguous[e+1] & contiguous[e+2] & contiguous[e+3] & k.complete.values[e+1] & k.complete.values[e+2] & k.complete.values[e+3], "exit4": k.close.values[e+3],
                       "crsi": k.crsi.values[idx]})
    df["dir"] = 1
    df["day"] = df.entry_time.dt.floor("D")
    df["up"] = df.exit1 > df.open_e
    df["tie"] = df.exit1 == df.open_e
    df["bpA"] = 1e4 * (df.exit1 - df.entryA) / df.entryA * df.dir
    df["bpB"] = 1e4 * (df.exit1 - df.entryB) / df.entryB * df.dir
    df["bp2"] = np.where(df.c2ok, 1e4 * (df.exit2 - df.entryA) / df.entryA * df.dir, np.nan)
    df["bp4"] = np.where(df.c4ok, 1e4 * (df.exit4 - df.entryA) / df.entryA * df.dir, np.nan)
    df["fill_strict"] = df.low5 < df.open_e   # a resting buy limit at the open price is traded through
    df["fill_touch"] = df.low5 <= df.open_e   # literal "touches" (always true: the bar opens there)
    return df

def boot_z(x, days):
    x = np.asarray(x, float); m = ~np.isnan(x); x, days = x[m], np.asarray(days)[m]
    if len(x) < 10: return np.nan
    d = pd.DataFrame({"x": x, "d": days}).groupby("d").x.agg(["sum", "count"])
    s, c = d["sum"].values, d["count"].values; D = len(s)
    ix = RNG.integers(0, D, size=(NBOOT, D))
    means = s[ix].sum(1) / c[ix].sum(1)
    sd = means.std(ddof=1)
    return x.mean() / sd if sd > 0 else np.nan

def stats(bp, days, fee):
    bp = np.asarray(bp, float); m = ~np.isnan(bp); bp = bp[m]; days = np.asarray(days)[m]
    if len(bp) == 0: return dict(n=0)
    net = bp - fee
    w, l = net[net > 0], net[net < 0]
    return dict(n=int(len(net)), mean=float(net.mean()), median=float(np.median(net)),
                skew=float(w.mean() / -l.mean()) if len(w) and len(l) else np.nan, z=float(boot_z(net, days)))

def quarters(df, col, fee, start, end):
    q = pd.period_range(start, end, freq="Q")
    g = df.set_index("entry_time")[col].dropna()
    out = {}
    for p in q:
        s = g[(g.index >= p.start_time.tz_localize("UTC")) & (g.index <= p.end_time.tz_localize("UTC"))]
        out[str(p)] = (float(s.mean() - fee) if len(s) else np.nan, int(len(s)))
    return out

def fmt(x, d=2): return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"

def run_window(label, t0, t1, md, J):
    md.append(f"\n## Window {label}: {t0} .. {t1}\n")
    all_spot, all_perp = {}, {}
    for sym in SYMS:
        ks = load15("spot", sym); ks = ks[(ks.index >= t0) & (ks.index <= t1)]
        all_spot[sym] = signals(ks)
        kp = load15("perp", sym); kp = kp[(kp.index >= t0) & (kp.index <= t1)]
        dp = signals(kp)
        f = pd.read_pickle(f"{CACHE}/funding_{sym}.pkl")
        # funding events F with entry_time < F <= entry_time+15min
        fr = f.reindex(dp.entry_time.dt.floor("h") + pd.Timedelta(hours=1)).values  # candidate: next hour boundary
        hits = ((dp.entry_time + pd.Timedelta(minutes=15)) >= (dp.entry_time.dt.floor("h") + pd.Timedelta(hours=1))).values
        fund_bp = np.where(hits & ~np.isnan(fr), -dp.dir.values * fr * 1e4, 0.0)
        dp["fund_bp"] = fund_bp; dp["bpA_f"] = dp.bpA + dp.fund_bp
        all_perp[sym] = dp
    # Table 1
    md.append("### Table 1 - robot direction WR and n (CRSI(2,2,75)<=20 -> next 15m UP, spot)\n")
    md.append("| coin | n | WR up % | ties | trades/day | Pine header WR | within 1.5pp? |\n|---|---|---|---|---|---|---|")
    for sym, d in all_spot.items():
        days = (pd.Timestamp(t1, tz="UTC") - max(pd.Timestamp(t0, tz="UTC"), d.entry_time.min())).days + 1 if len(d) else 1
        wr = d.up.mean() * 100
        J[label][sym] = dict(n=int(len(d)), wr=float(wr), ties=int(d.tie.sum()), tpd=float(len(d) / days))
        hdr = "57.0 (gate)" if sym == "BTCUSDT" else "BLOCKED: pine file missing"
        ok = ("YES" if abs(wr - 57.0) <= 1.0 else "NO") if sym == "BTCUSDT" else "n/a"
        md.append(f"| {sym} | {len(d)} | {wr:.2f} | {int(d.tie.sum())} | {len(d)/days:.2f} | {hdr} | {ok} |")
    # Table 2
    md.append("\n### Table 2 - net bp per trade, spot, entry A (next 15m open -> 15m close) and entry B (+5 min open -> 15m close)\n")
    md.append("| coin | entry | n | gross mean | median | skew (mean win/mean loss) | net @10bp | net @2bp | net @0bp | z (cluster=day, 2000 boot) | EV/day @2bp (bp) |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for sym, d in all_spot.items():
        for ent, col in [("A", "bpA"), ("B", "bpB")]:
            s = {fee: stats(d[col], d.day, fee) for fee in FEES}
            s0 = s[0]
            if s0["n"] == 0: continue
            tpd = J[label][sym]["tpd"]
            J[label][sym][f"entry{ent}"] = dict(gross=s0["mean"], median=s0["median"], skew=s0["skew"], z=s0["z"], net10=s[10]["mean"], net2=s[2]["mean"], evday2=s[2]["mean"] * tpd, n=s0["n"])
            md.append(f"| {sym} | {ent} | {s0['n']} | {fmt(s0['mean'])} | {fmt(s0['median'])} | {fmt(s0['skew'],3)} | {fmt(s[10]['mean'])} | {fmt(s[2]['mean'])} | {fmt(s[0]['mean'])} | {fmt(s0['z'])} | {fmt(s[2]['mean']*tpd)} |")
    # Table 3 quarters
    qs = pd.period_range(t0, t1, freq="Q")
    md.append(f"\n### Table 3 - quarterly net bp/trade at 2 bp (entry A, spot); {len(qs)} quarters\n")
    md.append("| quarter | " + " | ".join(s.replace("USDT","") for s in SYMS) + " | coins > 0 (of with data) |\n|---|" + "---|" * (len(SYMS) + 1))
    qd = {sym: quarters(all_spot[sym], "bpA", 2, t0, t1) for sym in SYMS}
    pos = {sym: 0 for sym in SYMS}; every3 = True; worst = None
    for q in qs:
        q = str(q); cells = []; npos = 0; nwith = 0
        for sym in SYMS:
            m, n = qd[sym][q]
            if n > 0:
                nwith += 1
                if m > 0: npos += 1; pos[sym] += 1
            cells.append(f"{fmt(m)} (n={n})")
        if nwith > 0 and npos < 3: every3 = False; worst = worst or q
        md.append(f"| {q} | " + " | ".join(cells) + f" | {npos}/{nwith} |")
    md.append("| **positive quarters** | " + " | ".join(f"{pos[s]}/{sum(1 for q in qs if qd[s][str(q)][1]>0)}" for s in SYMS) + " | |")
    J[label]["quarters_pos_2bp"] = pos; J[label]["every_quarter_ge3_at2bp"] = every3; J[label]["first_fail_quarter_2bp"] = worst
    # verdict at 0 and 10 bp
    for fee in [0, 10]:
        qd2 = {sym: quarters(all_spot[sym], "bpA", fee, t0, t1) for sym in SYMS}
        ev = True; first = None
        for q in qs:
            q = str(q); npos = sum(1 for s in SYMS if qd2[s][q][1] > 0 and qd2[s][q][0] > 0); nwith = sum(1 for s in SYMS if qd2[s][q][1] > 0)
            if nwith and npos < 3: ev = False; first = first or q
        J[label][f"every_quarter_ge3_at{fee}bp"] = ev; J[label][f"first_fail_quarter_{fee}bp"] = first
    # Table 4
    md.append("\n### Table 4 - perp + funding, maker fill, hold-longer exits (entry A)\n")
    md.append("| coin | perp n | perp WR % | perp gross | funding bp/trade | perp net @2bp incl. funding | perp z | maker fill % (low<open) | net @2bp filled only | n filled | hold 2 bars net @2bp (z) | hold 4 bars net @2bp (z) |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for sym in SYMS:
        d, p = all_spot[sym], all_perp[sym]
        sp = stats(p.bpA_f, p.day, 2); sg = stats(p.bpA, p.day, 0)
        fl = d[d.fill_strict]; sf = stats(fl.bpA, fl.day, 2)
        h2 = stats(d.bp2, d.day, 2); h4 = stats(d.bp4, d.day, 2)
        J[label][sym].update(perp=dict(n=sp.get("n",0), wr=float(p.up.mean()*100) if len(p) else np.nan, gross=sg.get("mean"), fund=float(p.fund_bp.mean()) if len(p) else np.nan, net2f=sp.get("mean"), z=sp.get("z")),
                             maker=dict(fill_pct=float(d.fill_strict.mean()*100), fill_touch_pct=float(d.fill_touch.mean()*100), net2=sf.get("mean"), n=sf.get("n",0), z=sf.get("z")),
                             hold2=dict(net2=h2.get("mean"), z=h2.get("z"), n=h2.get("n")), hold4=dict(net2=h4.get("mean"), z=h4.get("z"), n=h4.get("n")))
        md.append(f"| {sym} | {sp.get('n',0)} | {fmt(p.up.mean()*100 if len(p) else np.nan)} | {fmt(sg.get('mean'))} | {fmt(p.fund_bp.mean() if len(p) else np.nan,4)} | {fmt(sp.get('mean'))} | {fmt(sp.get('z'))} | {fmt(d.fill_strict.mean()*100,1)} | {fmt(sf.get('mean'))} | {sf.get('n',0)} | {fmt(h2.get('mean'))} ({fmt(h2.get('z'))}) | {fmt(h4.get('mean'))} ({fmt(h4.get('z'))}) |")
    md.append(f"\nVerdict ({label}): `maker-EV (2 bp) > 0 on >=3 coins in EVERY quarter? {'YES' if every3 else 'NO'}`" + (f" (first failing quarter {worst})" if worst else ""))
    md.append(f"At 0 bp: {'YES' if J[label]['every_quarter_ge3_at0bp'] else 'NO'}" + (f" (first fail {J[label]['first_fail_quarter_0bp']})" if J[label]['first_fail_quarter_0bp'] else "") +
              f"; at 10 bp: {'YES' if J[label]['every_quarter_ge3_at10bp'] else 'NO'}" + (f" (first fail {J[label]['first_fail_quarter_10bp']})" if J[label]['first_fail_quarter_10bp'] else ""))
    return all_spot

if __name__ == "__main__":
    md = ["# T12 auto-generated tables (src/analyze.py)\n"]; J = {}
    # gate check exactly as specified
    J["gate"] = {}; kb = load15("spot", "BTCUSDT"); kb = kb[(kb.index >= "2020-01-01") & (kb.index < "2026-08-17")]
    g = signals(kb); J["gate"] = dict(n=int(len(g)), wr=float(g.up.mean()*100), ties=int(g.tie.sum()), wr_excl_ties=float(g.up.sum()/(~g.tie).sum()*100))
    md.append(f"## Gate: BTC 2020-01-01..2026-08-16, CRSI(2,2,75)<=20 -> next 15m UP: WR = {J['gate']['wr']:.2f}% (n={J['gate']['n']}, ties={J['gate']['ties']}, WR excl. ties {J['gate']['wr_excl_ties']:.2f}%). Target 57.0+-1.0%, n~37800. Gate {'PASS' if abs(J['gate']['wr']-57)<=1 and 30000<J['gate']['n']<46000 else 'FAIL'}.\n")
    print(md[-1])
    J["full"] = {s: {} for s in SYMS}; run_window("full", "2020-01-01", "2026-09-30 23:59:59", md, J)
    J["recent"] = {s: {} for s in SYMS}; run_window("recent", "2025-01-01", "2026-08-16 23:59:59", md, J)
    open(f"{RES}/T12_tables.md", "w").write("\n".join(md) + "\n")
    json.dump(J, open(f"{RES}/T12_numbers.json", "w"), indent=1, default=float)
    print("done")
