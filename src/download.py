#!/usr/bin/env python3 -I
"""Download public Binance.vision monthly 5m klines (spot + USDT-M perp) and funding rates.
Re-runnable: skips files that already exist. Writes data/download_log.txt with BLOCKED/404 entries."""
import os, sys, time, subprocess, concurrent.futures as cf
SYMS = ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]
BASE = "https://data.binance.vision/data"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
def months():
    for y in range(2020, 2027):
        for m in range(1, 13):
            if (y, m) > (2026, 9): return
            yield f"{y}-{m:02d}"
def jobs():
    for s in SYMS:
        for ym in months():
            yield (f"{BASE}/spot/monthly/klines/{s}/5m/{s}-5m-{ym}.zip", f"{ROOT}/spot/{s}/{s}-5m-{ym}.zip")
            yield (f"{BASE}/futures/um/monthly/klines/{s}/5m/{s}-5m-{ym}.zip", f"{ROOT}/perp/{s}/{s}-5m-{ym}.zip")
            yield (f"{BASE}/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{ym}.zip", f"{ROOT}/funding/{s}/{s}-fundingRate-{ym}.zip")
def fetch(job):
    url, dst = job
    if os.path.exists(dst) or os.path.exists(dst + ".missing"): return (url, "skip")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for i, back in enumerate([2, 4, 8, 16, None]):
        r = subprocess.run(["curl", "-sS", "-o", dst + ".part", "-w", "%{http_code}", "--max-time", "120", url], capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200":
            os.replace(dst + ".part", dst); return (url, "200")
        if code == "404":
            open(dst + ".missing", "w").write("404\n"); 
            if os.path.exists(dst + ".part"): os.remove(dst + ".part")
            return (url, "404")
        if back is None: 
            if os.path.exists(dst + ".part"): os.remove(dst + ".part")
            return (url, f"BLOCKED {code or 'net'}")
        time.sleep(back)
if __name__ == "__main__":
    res = []
    with cf.ThreadPoolExecutor(8) as ex:
        for r in ex.map(fetch, list(jobs())): res.append(r)
    with open(f"{ROOT}/download_log.txt", "w") as f:
        for url, st in res:
            if st != "skip": f.write(f"{st} {url}\n")
    from collections import Counter
    print(Counter(st.split()[0] for _, st in res))
