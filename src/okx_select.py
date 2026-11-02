#!/usr/bin/env python3 -I
"""OKX reverse-carry candidate screen, PUBLIC endpoints only (no keys).
Lists USDT perps with the most negative funding that also have OKX margin, with borrow APR, quota and 24h volume.
Run: python3 -I src/okx_select.py [N]"""
import sys, json, subprocess
def get(u):
    return json.loads(subprocess.run(["curl","-sS","--max-time","25","-H","User-Agent: Mozilla/5.0",u],capture_output=True,text=True).stdout)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 15
fr = {x["instId"]: x for x in get("https://www.okx.com/api/v5/public/funding-rate?instId=ANY")["data"] if x["instId"].endswith("-USDT-SWAP")}
margin = {i["instId"] for i in get("https://www.okx.com/api/v5/public/instruments?instType=MARGIN")["data"]}
quota = {x["ccy"]: (float(x["rate"]) * 365 * 100, float(x["quota"])) for x in get("https://www.okx.com/api/v5/public/interest-rate-loan-quota")["data"][0]["basic"]}
tick = {t["instId"]: t for t in get("https://www.okx.com/api/v5/market/tickers?instType=SWAP")["data"]}
spot = {t["instId"]: t for t in get("https://www.okx.com/api/v5/market/tickers?instType=SPOT")["data"]}
rows = []
for inst, x in fr.items():
    c = inst.split("-")[0]; mp = f"{c}-USDT"
    if mp not in margin or c not in quota: continue
    r = float(x["fundingRate"]); nxt = float(x["nextFundingRate"] or 0); hrs = (int(x["nextFundingTime"]) - int(x["fundingTime"])) / 3.6e6
    ann_fund = -r * (24 / hrs) * 365 * 100           # % per year PAID TO LONGS (positive = longs receive)
    t = tick.get(inst, {}); s = spot.get(mp, {})
    vol = float(t.get("volCcy24h", 0)) * float(t.get("last", 0) or 0)
    px = float(t.get("last", 0) or 0); spx = float(s.get("last", 0) or 0)
    basis = (px / spx - 1) * 100 if spx else float("nan")
    rows.append((c, ann_fund, quota[c][0], ann_fund - quota[c][0], vol / 1e6, quota[c][1] * spx, basis, hrs))
rows.sort(key=lambda z: -z[3])
print(f"{'coin':8s} {'fund->long %/yr':>16s} {'borrow %/yr':>12s} {'net carry %/yr':>15s} {'perp 24h $M':>12s} {'quota $':>10s} {'basis %':>8s} {'fund int h':>10s}")
for c, f, b, n, v, q, bs, h in rows[:N]:
    print(f"{c:8s} {f:16.0f} {b:12.0f} {n:15.0f} {v:12.1f} {q:10,.0f} {bs:8.2f} {h:10.0f}")
print(f"\n{len(rows)} OKX coins with both perp and margin; net carry = funding to longs - basic borrow APR (basis drift and fees not included).")
