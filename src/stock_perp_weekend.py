#!/usr/bin/env python3 -I
"""T19: Crypto.com stock perps (24/7) vs real Monday open. For each weekend: perp price at Sunday 23:00 UTC vs Friday real close (perp's implied gap)
vs Monday real open gap (Yahoo). If the perp already matches the Monday open, there is no weekend edge. Also weekend volume. -> results/T19_stock_perp_weekend.md"""
import os, json, subprocess, datetime as dt, numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cdc"); RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
def get(u): return json.loads(subprocess.run(["curl", "-sS", "--max-time", "25", "-H", "User-Agent: Mozilla/5.0", u], capture_output=True, text=True).stdout)
def perp_hourly(inst):
    p = f"{ROOT}/{inst}_1h.pkl"
    if os.path.exists(p): return pd.read_pickle(p)
    rows = {}; end = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
    for _ in range(30):
        d = get(f"https://api.crypto.com/exchange/v1/public/get-candlestick?instrument_name={inst}&timeframe=1h&count=300&end_ts={end}").get("result", {}).get("data", [])
        if not d: break
        for x in d: rows[int(x["t"])] = (float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"]), float(x["v"]))
        new_end = min(int(x["t"]) for x in d) - 1
        if new_end >= end or len(d) < 300: break
        end = new_end
    df = pd.DataFrame.from_dict(rows, orient="index", columns=["o", "h", "l", "c", "v"]); df.index = pd.to_datetime(df.index, unit="ms", utc=True); df = df.sort_index(); df.to_pickle(p); return df
def yahoo_daily(tk):
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?interval=1d&range=1y")["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    df = pd.DataFrame({"o": q["open"], "c": q["close"]}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York").date); return df.dropna()
md = ["# T19 — Crypto.com stock perps over the weekend vs the real Monday open (03.11.2026)\n", "Perp hourly candles from api.crypto.com (24/7); real daily open/close from Yahoo. Gap = Monday open / Friday close − 1. Perp implied = perp close at Sunday 23:00 UTC / Friday real close − 1. Error = Monday open / perp Sunday-23 price − 1 (what a Sunday-night buyer would make before costs if the perp converged to the real open).\n",
      "| instrument | weekends | median weekend volume (contracts, Sat+Sun) | corr(perp implied, real gap) | mean |error| bp | mean error bp (sign = Monday open above perp) | sd error bp | weekends with |error| > 30 bp |\n|---|---|---|---|---|---|---|---|"]
for inst, tk in [("TSLAUSD-PERP", "TSLA"), ("SPYUSD-PERP", "SPY"), ("QQQUSD-PERP", "QQQ"), ("NVDAUSD-PERP", "NVDA"), ("AAPLUSD-PERP", "AAPL"), ("MSTRUSD-PERP", "MSTR")]:
    try: P = perp_hourly(inst); Y = yahoo_daily(tk)
    except Exception as e: md.append(f"| {inst} | error {e} | | | | | | |"); continue
    rows = []
    for d in Y.index:
        if d.weekday() != 0: continue
        fri = d - dt.timedelta(days=3)
        if fri not in Y.index: continue
        sun23 = pd.Timestamp(dt.datetime.combine(d, dt.time(0)), tz="UTC") - pd.Timedelta(hours=1)   # Sunday 23:00 UTC = 18:00/19:00 ET (CME equity futures open 18:00 ET)
        if sun23 not in P.index: continue
        sat0 = sun23 - pd.Timedelta(hours=47); wvol = P.v[(P.index >= sat0) & (P.index <= sun23)].sum()
        fc, mo = Y.c[fri], Y.o[d]; pp = P.c[sun23]
        rows.append(dict(mon=d, gap=(mo / fc - 1) * 1e4, implied=(pp / fc - 1) * 1e4, err=(mo / pp - 1) * 1e4, wvol=wvol))
    D = pd.DataFrame(rows)
    if len(D) < 4: md.append(f"| {inst} | {len(D)} | | | | | | |"); continue
    md.append(f"| {inst} | {len(D)} | {D.wvol.median():.1f} | {np.corrcoef(D.implied, D.gap)[0,1]:.2f} | {D.err.abs().mean():.0f} | {D.err.mean():+.0f} | {D.err.std():.0f} | {(D.err.abs()>30).sum()} |")
md.append("\nReading: corr near 1 and |error| of a few bp means the perp already prices the Monday open on Sunday night (no edge). A large, sign-consistent error would be an edge, but weekend volume shows whether anyone could have traded it; the live quote is a market maker's and is 5 bp wide, so prints, not quotes, are what the candles show.")
open(f"{RES}/T19_stock_perp_weekend.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
