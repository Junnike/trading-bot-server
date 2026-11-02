#!/usr/bin/env python3 -I
"""Polymarket BTC 15m Up/Down: gamma market meta + trade tape from minute 12 to close, TWAP era 2026-08-15..2026-10-31.
Public endpoints only. Output data/poly/markets.jsonl (one line per market: meta + trades). Re-runnable."""
import os, sys, json, time, threading, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
OUT = "data/poly/markets_first3.jsonl"; T0 = 1786492800; T1 = 1793577600   # 2026-08-15 00:00Z .. 2026-10-31 24:00Z
_lock = threading.Lock(); _next = [0.0]; SLOT = 0.12
def get(url):
    for wait in (0, 2, 4, 8, 16):
        if wait: time.sleep(wait)
        with _lock:
            t = max(time.time(), _next[0]); _next[0] = t + SLOT
        d = t - time.time()
        if d > 0: time.sleep(d)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            if e.code == 429:
                with _lock: _next[0] = time.time() + 5
        except Exception:
            pass
    return "ERR"
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)["start"])
starts = [t for t in range(T0, T1, 900) if t not in done]; print("todo", len(starts), flush=True)
def work(st):
    slug = f"btc-updown-15m-{st}"
    ev = get(f"https://gamma-api.polymarket.com/events?slug={slug}")
    if ev == "ERR": return {"start": st, "err": "gamma"}
    if not ev: return {"start": st, "err": "nomarket"}
    m = ev[0]["markets"][0]
    rec = {"start": st, "slug": slug, "cid": m["conditionId"], "outcomes": m.get("outcomes"), "prices": m.get("outcomePrices"), "closed": m.get("closed"), "desc": ev[0].get("description", "")[:160], "tr": []}
    off = 0
    while off < 12000:
        tr = get(f"https://data-api.polymarket.com/trades?market={m['conditionId']}&limit=1000&offset={off}")
        if tr == "ERR": rec["err"] = "trades"; break
        if not tr: break
        rec["tr"] += [{"ts": x["timestamp"], "side": x["side"], "o": x["outcome"], "p": float(x["price"]), "n": float(x["size"])} for x in tr if x["timestamp"] < st + 3 * 60]
        if min(x["timestamp"] for x in tr) < st - 60 or len(tr) < 1000: break
        off += 1000
    return rec
with ThreadPoolExecutor(6) as ex, open(OUT, "a") as f:
    for i, r in enumerate(ex.map(work, starts)):
        f.write(json.dumps(r) + "\n"); f.flush()
        if i % 500 == 0: print(i, flush=True)
print("DONE")
