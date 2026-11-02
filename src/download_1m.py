#!/usr/bin/env python3 -I
"""Spot 1m klines monthly zips 2020-01..2026-10 for the 5 robot coins (for the TWAP/VWAP label). Re-runnable."""
import os, time, subprocess, concurrent.futures as cf
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
def jobs():
    for s in ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]:
        for y in range(2020, 2027):
            for m in range(1, 13):
                if (y, m) > (2026, 10): break
                yield s, f"{y}-{m:02d}"
def fetch(j):
    s, ym = j; dst = f"{ROOT}/spot1m/{s}/{s}-1m-{ym}.zip"
    if os.path.exists(dst) or os.path.exists(dst + ".missing"): return "skip"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for back in [2, 4, 8, 16, None]:
        c = subprocess.run(["curl", "-sS", "-o", dst + ".part", "-w", "%{http_code}", "--max-time", "300", f"https://data.binance.vision/data/spot/monthly/klines/{s}/1m/{s}-1m-{ym}.zip"], capture_output=True, text=True).stdout.strip()
        if c == "200": os.replace(dst + ".part", dst); return "200"
        if c == "404": open(dst + ".missing", "w").write("404\n"); return "404"
        if back is None: return "BLOCKED " + c
        time.sleep(back)
from collections import Counter
with cf.ThreadPoolExecutor(12) as ex: print(dict(Counter(r.split()[0] for r in ex.map(fetch, list(jobs())))))
