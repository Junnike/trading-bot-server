#!/usr/bin/env python3 -I
"""Symbol-wide download: fundingRate + perp 1h klines + spot 1h klines, monthly zips 2022-01..2026-09, all USDT perps with a spot pair. Re-runnable."""
import os, json, time, subprocess, concurrent.futures as cf
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"); BASE = "https://data.binance.vision/data"
SY = json.load(open(f"{ROOT}/symbols.json"))["both"]
def months():
    for y in range(2022, 2027):
        for m in range(1, 13):
            if (y, m) > (2026, 9): return
            yield f"{y}-{m:02d}"
def jobs():
    for s in SY:
        for ym in months():
            yield (f"{BASE}/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{ym}.zip", f"{ROOT}/all/funding/{s}/{ym}.zip")
            yield (f"{BASE}/futures/um/monthly/klines/{s}/1h/{s}-1h-{ym}.zip", f"{ROOT}/all/perp1h/{s}/{ym}.zip")
            yield (f"{BASE}/spot/monthly/klines/{s}/1h/{s}-1h-{ym}.zip", f"{ROOT}/all/spot1h/{s}/{ym}.zip")
def fetch(job):
    url, dst = job
    if os.path.exists(dst) or os.path.exists(dst + ".missing"): return "skip"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for back in [2, 4, 8, 16, None]:
        r = subprocess.run(["curl", "-sS", "-o", dst + ".part", "-w", "%{http_code}", "--max-time", "120", url], capture_output=True, text=True); c = r.stdout.strip()
        if c == "200": os.replace(dst + ".part", dst); return "200"
        if c == "404":
            open(dst + ".missing", "w").write("404\n")
            if os.path.exists(dst + ".part"): os.remove(dst + ".part")
            return "404"
        if back is None:
            if os.path.exists(dst + ".part"): os.remove(dst + ".part")
            return "BLOCKED " + c
        time.sleep(back)
if __name__ == "__main__":
    from collections import Counter
    J = list(jobs()); print(len(J), flush=True); res = Counter()
    with cf.ThreadPoolExecutor(24) as ex:
        for i, r in enumerate(ex.map(fetch, J)):
            res[r.split()[0]] += 1
            if i % 5000 == 0: print(i, dict(res), flush=True)
    print(dict(res))
