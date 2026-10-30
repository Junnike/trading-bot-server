#!/usr/bin/env python3 -I
"""Index all settled KXBTC15M markets: paginate /historical/markets and live /markets (status=settled). -> data/kalshi/markets.jsonl"""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kget import get
OUT = "data/kalshi/markets.jsonl"; seen = {}
KEEP = ["ticker", "open_time", "close_time", "result", "volume_fp", "floor_strike", "status"]
for ep, p in [("/historical/markets", {"series_ticker": "KXBTC15M", "limit": 1000}), ("/markets", {"series_ticker": "KXBTC15M", "status": "settled", "limit": 1000})]:
    cur = None; pages = 0
    while True:
        q = dict(p); 
        if cur: q["cursor"] = cur
        r = get(ep, q)
        if not r or "markets" not in r: print("stop", ep, r and str(r)[:100]); break
        for m in r["markets"]:
            if m.get("result") in ("yes", "no"): seen[m["ticker"]] = {k: m.get(k) for k in KEEP}
        pages += 1; cur = r.get("cursor")
        if pages % 10 == 0: print(ep, pages, len(seen), r["markets"][-1]["close_time"], flush=True)
        if not cur or not r["markets"]: break
with open(OUT, "w") as f:
    for m in sorted(seen.values(), key=lambda m: m["open_time"]): f.write(json.dumps(m) + "\n")
import collections
print(len(seen), min(m["open_time"] for m in seen.values()), max(m["open_time"] for m in seen.values()))
print(sorted(collections.Counter(m["open_time"][:7] for m in seen.values()).items()))
