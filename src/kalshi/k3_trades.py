#!/usr/bin/env python3 -I
"""Stage 3: trade tape for cell windows (minute-7 bid in [.70,.90)), from open+6:00 to open+8:30 -> data/kalshi/trades.jsonl"""
import sys, os, json, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kget import get
from concurrent.futures import ThreadPoolExecutor
CUT = "2026-08-31T00:00:00Z"
rows = [json.loads(l) for l in open("data/kalshi/candles.jsonl")]
todo = []
for r in rows:
    m7 = [c for c in r["cs"] if c["e"] == r["o"] + 7 * 60]
    if m7 and m7[0]["bid"] is not None and 0.70 <= m7[0]["bid"] < 0.90: todo.append(r)
done = set()
OUT = "data/kalshi/trades.jsonl"
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)["t"])
todo = [r for r in todo if r["t"] not in done]; print("cell windows todo", len(todo), flush=True)
def work(r):
    T = r["t"]; o = r["o"]
    close_iso = pd.Timestamp(r["c"], unit="s", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    ep = "/historical/trades" if close_iso < CUT else "/markets/trades"
    out, cur = [], None
    for _ in range(30):
        p = {"ticker": T, "limit": 1000, "min_ts": o + 6 * 60, "max_ts": o + 8 * 60 + 30}
        if cur: p["cursor"] = cur
        d = get(ep, p)
        if not d or "trades" not in d: return {"t": T, "err": 1, "tr": out}
        out += [{"ts": x["created_time"], "p": float(x["yes_price_dollars"]), "n": float(x["count_fp"]), "ts_side": x.get("taker_side"), "book": x.get("taker_book_side")} for x in d["trades"]]
        cur = d.get("cursor")
        if not cur or not d["trades"]: break
    return {"t": T, "tr": out}
with ThreadPoolExecutor(6) as ex, open(OUT, "a") as f:
    for i, x in enumerate(ex.map(work, todo)):
        f.write(json.dumps(x) + "\n"); f.flush()
        if i % 200 == 0: print(i, flush=True)
print("DONE")
