#!/usr/bin/env python3 -I
"""Binance spot BTCUSDT 1-second klines, daily zips, for every day with a sampled Kalshi window. Re-runnable."""
import os, json, time, subprocess, concurrent.futures as cf, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
days = sorted({pd.Timestamp(json.loads(l)["o"], unit="s", tz="UTC").strftime("%Y-%m-%d") for l in open(f"{ROOT}/kalshi/candles.jsonl")})
def fetch(d):
    dst = f"{ROOT}/binance1s/BTCUSDT-1s-{d}.zip"
    if os.path.exists(dst) or os.path.exists(dst + ".missing"): return "skip"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for back in [2, 4, 8, 16, None]:
        c = subprocess.run(["curl", "-sS", "-o", dst + ".part", "-w", "%{http_code}", "--max-time", "180", f"https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1s/BTCUSDT-1s-{d}.zip"], capture_output=True, text=True).stdout.strip()
        if c == "200": os.replace(dst + ".part", dst); return "200"
        if c == "404": open(dst + ".missing", "w").write("404\n"); return "404"
        if back is None: return "BLOCKED " + c
        time.sleep(back)
from collections import Counter
with cf.ThreadPoolExecutor(12) as ex: print(len(days), dict(Counter(r.split()[0] for r in ex.map(fetch, days))))
