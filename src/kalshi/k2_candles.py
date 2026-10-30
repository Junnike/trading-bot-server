#!/usr/bin/env python3 -I
"""Stage 2: stratified random sample (PER_MONTH per month, seed 7), 1-min candles per market -> data/kalshi/candles.jsonl (one line per market, 15 candles)."""
import sys, os, json, random, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kget import get
from concurrent.futures import ThreadPoolExecutor
PER_MONTH = int(sys.argv[1]) if len(sys.argv) > 1 else 700
CUT = "2026-08-31T00:00:00Z"
ms = [json.loads(l) for l in open("data/kalshi/markets.jsonl")]
def thu(m):
    t = pd.Timestamp(m["open_time"]); return t.weekday() == 3 and 7 <= t.hour < 9
ms = [m for m in ms if not thu(m)]
rng = random.Random(7); bym = {}
for m in ms: bym.setdefault(m["open_time"][:7], []).append(m)
todo = []
for k in sorted(bym):
    l = sorted(bym[k], key=lambda m: m["ticker"]); rng.shuffle(l); todo += l[:PER_MONTH]
done = set()
OUT = "data/kalshi/candles.jsonl"
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)["t"])
todo = [m for m in todo if m["ticker"] not in done]; print("todo", len(todo), flush=True)
def v(x, k):
    if not x: return None
    y = x.get(k + "_dollars") if (k + "_dollars") in x else x.get(k)
    return float(y) if y not in (None, "") else None
def work(m):
    T = m["ticker"]; o = int(pd.Timestamp(m["open_time"]).timestamp()); c = int(pd.Timestamp(m["close_time"]).timestamp())
    eps = [f"/series/KXBTC15M/markets/{T}/candlesticks", f"/historical/markets/{T}/candlesticks"]
    if m["close_time"] < CUT: eps.reverse()
    for ep in eps:
        r = get(ep, {"start_ts": o, "end_ts": c, "period_interval": 1})
        if r and r.get("candlesticks"):
            cs = [{"e": x["end_period_ts"], "bid": v(x.get("yes_bid"), "close"), "ask": v(x.get("yes_ask"), "close"), "bid_o": v(x.get("yes_bid"), "open"), "ask_o": v(x.get("yes_ask"), "open"),
                   "px": v(x.get("price"), "close"), "vol": float(x.get("volume_fp", x.get("volume", 0)) or 0), "oi": float(x.get("open_interest_fp", x.get("open_interest", 0)) or 0)} for x in r["candlesticks"]]
            return {"t": T, "o": o, "c": c, "res": m["result"], "cs": cs}
    return {"t": T, "o": o, "c": c, "res": m["result"], "cs": []}
with ThreadPoolExecutor(6) as ex, open(OUT, "a") as f:
    for i, x in enumerate(ex.map(work, todo)):
        f.write(json.dumps(x) + "\n"); f.flush()
        if i % 500 == 0: print(i, flush=True)
print("DONE")
