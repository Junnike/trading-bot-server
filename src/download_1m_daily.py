#!/usr/bin/env python3 -I
"""Daily 1m spot klines for days not covered by monthly zips (current/previous month). Re-runnable."""
import os, sys, time, subprocess, datetime as dt, concurrent.futures as cf
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
a, b = sys.argv[1], sys.argv[2]  # inclusive dates
def days():
    d = dt.date.fromisoformat(a)
    while d <= dt.date.fromisoformat(b): yield d.isoformat(); d += dt.timedelta(1)
def fetch(j):
    s, d = j; dst = f"{ROOT}/spot1m_daily/{s}/{s}-1m-{d}.zip"
    if os.path.exists(dst) or os.path.exists(dst + ".missing"): return "skip"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for back in [2, 4, 8, None]:
        c = subprocess.run(["curl", "-sS", "-o", dst + ".part", "-w", "%{http_code}", "--max-time", "120", f"https://data.binance.vision/data/spot/daily/klines/{s}/1m/{s}-1m-{d}.zip"], capture_output=True, text=True).stdout.strip()
        if c == "200": os.replace(dst + ".part", dst); return "200"
        if c == "404": open(dst + ".missing", "w").write("404\n"); return "404"
        if back is None: return "BLOCKED " + c
        time.sleep(back)
from collections import Counter
J = [(s, d) for s in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"] for d in days()]
with cf.ThreadPoolExecutor(12) as ex: print(dict(Counter(r.split()[0] for r in ex.map(fetch, J))))
