#!/usr/bin/env python3 -I
"""Download Binance Vision daily perp 'metrics' (5 coins, 2021-01..2026-09) and 'bookDepth' (BTC, ETH, 2023-01..2026-09).
Re-runnable; 404s recorded as .missing."""
import os, sys, time, subprocess, concurrent.futures as cf, datetime as dt
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
BASE = "https://data.binance.vision/data/futures/um/daily"
def days(a, b):
    d = dt.date.fromisoformat(a)
    while d <= dt.date.fromisoformat(b): yield d.isoformat(); d += dt.timedelta(1)
def jobs():
    for s in ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]:
        for d in days("2021-01-01", "2026-09-30"): yield (f"{BASE}/metrics/{s}/{s}-metrics-{d}.zip", f"{ROOT}/metrics/{s}/{s}-metrics-{d}.zip")
    for s in ["BTCUSDT","ETHUSDT"]:
        for d in days("2023-01-01", "2026-09-30"): yield (f"{BASE}/bookDepth/{s}/{s}-bookDepth-{d}.zip", f"{ROOT}/bookDepth/{s}/{s}-bookDepth-{d}.zip")
def fetch(job):
    url, dst = job
    if os.path.exists(dst) or os.path.exists(dst + ".missing"): return "skip"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for back in [2, 4, 8, 16, None]:
        r = subprocess.run(["curl", "-sS", "-o", dst + ".part", "-w", "%{http_code}", "--max-time", "120", url], capture_output=True, text=True)
        c = r.stdout.strip()
        if c == "200": os.replace(dst + ".part", dst); return "200"
        if c == "404":
            open(dst + ".missing", "w").write("404\n")
            if os.path.exists(dst + ".part"): os.remove(dst + ".part")
            return "404"
        if back is None: return f"BLOCKED {c}"
        time.sleep(back)
if __name__ == "__main__":
    from collections import Counter
    with cf.ThreadPoolExecutor(16) as ex: res = list(ex.map(fetch, list(jobs())))
    print(Counter(r.split()[0] for r in res))
