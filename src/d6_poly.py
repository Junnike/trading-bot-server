import os, time, json, datetime as dt, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
OUT = "data/poly"
H = {"User-Agent": "curl/8.0", "Accept": "application/json"}
S = requests.Session()
def get(url, params):
    for w in [0, 2, 4, 8, 16]:
        time.sleep(w)
        try:
            r = S.get(url, params=params, headers=H, timeout=60)
            if r.status_code == 429: time.sleep(10); continue
            r.raise_for_status(); return r.json()
        except Exception as e:
            err = e
    raise RuntimeError(f"UNMEASURED {url} {err}")
def events(slugs):
    d = get("https://gamma-api.polymarket.com/events", [("slug", s) for s in slugs] + [("limit", 100)])
    out = []
    for e in d:
        for m in e["markets"]:
            out.append(dict(slug=m["slug"], cid=m["conditionId"], start=int(m["slug"].rsplit("-",1)[1]),
                            tokens=m["clobTokenIds"], prices=m.get("outcomePrices"), closed=m.get("closed"),
                            vol=m.get("volumeNum"), fee=json.dumps(m.get("feeSchedule")), feesEnabled=m.get("feesEnabled")))
    return out
def trades(cid):
    rows, off = [], 0
    while True:
        d = get("https://data-api.polymarket.com/trades", dict(market=cid, limit=1000, offset=off))
        rows += d
        if len(d) < 1000: break
        off += 1000
    return [(cid, r["outcomeIndex"], r["side"], r["price"], r["size"], r["timestamp"], r["transactionHash"], r["proxyWallet"]) for r in rows]
import sys
day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 10, 9)
while day >= dt.date(2026, 2, 1):
    fn = f"{OUT}/{day}"
    if os.path.exists(fn + "_trades.parquet") or os.path.exists(fn + ".empty"):
        day -= dt.timedelta(days=1); continue
    t0 = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp())
    slugs = [f"btc-updown-5m-{t0+300*i}" for i in range(288)]
    batches = [slugs[i:i+24] for i in range(0, 288, 24)]
    with ThreadPoolExecutor(10) as ex:
        ms = [m for b in ex.map(events, batches) for m in b]
        if not ms:
            open(fn + ".empty", "w").close(); print(day, "empty", flush=True); day -= dt.timedelta(days=1); continue
        tr = [t for b in ex.map(lambda m: trades(m["cid"]), ms) for t in b]
    tdf = pd.DataFrame(tr, columns=["cid","oi","side","price","size","ts","tx","wallet"]).drop_duplicates(["tx","cid","oi","side","price","size","ts","wallet"])
    pd.DataFrame(ms).to_parquet(fn + "_markets.parquet")
    tdf.to_parquet(fn + "_trades.parquet.tmp"); os.rename(fn + "_trades.parquet.tmp", fn + "_trades.parquet")
    print(day, len(ms), len(tdf), flush=True)
    day -= dt.timedelta(days=1)
print("DONE", flush=True)
