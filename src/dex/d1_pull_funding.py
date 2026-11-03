#!/usr/bin/env python3 -I
"""Pull funding history: Hyperliquid (hourly, all perps, since 2025-01-01) and Aster (8h, all USDT perps). Public APIs. Re-runnable (per-coin files)."""
import os, json, time, subprocess, concurrent.futures as cf
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "dex"); os.makedirs(f"{ROOT}/hl", exist_ok=True); os.makedirs(f"{ROOT}/aster", exist_ok=True)
def post(body):
    for i in range(4):
        r = subprocess.run(["curl", "-sS", "--max-time", "30", "-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(body), "https://api.hyperliquid.xyz/info"], capture_output=True, text=True).stdout
        try: return json.loads(r)
        except Exception: time.sleep(2 * (i + 1))
    return None
def get(u):
    for i in range(4):
        r = subprocess.run(["curl", "-sS", "--max-time", "30", u], capture_output=True, text=True).stdout
        try: return json.loads(r)
        except Exception: time.sleep(2 * (i + 1))
    return None
coins = [x["name"] for x in post({"type": "meta"})["universe"]]
def hl(coin):
    p = f"{ROOT}/hl/{coin}.json"
    if os.path.exists(p): return "skip"
    out, start = [], 1735689600000
    for _ in range(40):
        d = post({"type": "fundingHistory", "coin": coin, "startTime": start})
        if not d: break
        out += d
        if len(d) < 500: break
        start = d[-1]["time"] + 1; time.sleep(0.2)
    json.dump(out, open(p, "w")); return "ok"
syms = [s["symbol"] for s in get("https://fapi.asterdex.com/fapi/v1/exchangeInfo")["symbols"] if s["symbol"].endswith("USDT")]
def aster(sym):
    p = f"{ROOT}/aster/{sym}.json"
    if os.path.exists(p): return "skip"
    out, start = [], 1735689600000
    for _ in range(10):
        d = get(f"https://fapi.asterdex.com/fapi/v1/fundingRate?symbol={sym}&startTime={start}&limit=1000")
        if not isinstance(d, list) or not d: break
        out += d
        if len(d) < 1000: break
        start = d[-1]["fundingTime"] + 1; time.sleep(0.2)
    json.dump(out, open(p, "w")); return "ok"
with cf.ThreadPoolExecutor(4) as ex:
    r1 = list(ex.map(hl, coins)); print("hl", len(coins), r1.count("ok"), flush=True)
with cf.ThreadPoolExecutor(4) as ex:
    r2 = list(ex.map(aster, syms)); print("aster", len(syms), r2.count("ok"), flush=True)
print("DONE")
