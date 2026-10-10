# T8b C2: pull real resolution per 5-min market from gamma-api (public, no key). Output data/poly_resolution.parquet
import glob, time, json, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
H = {"User-Agent": "curl/8.0", "Accept": "application/json"}
S = requests.Session()
def get(slugs):
    err = None
    for w in [0, 2, 4, 8, 16]:
        time.sleep(w)
        try:
            r = S.get("https://gamma-api.polymarket.com/events", params=[("slug", s) for s in slugs] + [("limit", 100)], headers=H, timeout=60)
            if r.status_code == 429: time.sleep(10); continue
            r.raise_for_status(); return r.json()
        except Exception as e: err = e
    return None
slugs = []
for f in sorted(glob.glob("data/poly/*_markets.parquet")):
    slugs += list(pd.read_parquet(f, columns=["slug"]).slug)
batches = [slugs[i:i+24] for i in range(0, len(slugs), 24)]
def one(b):
    time.sleep(0.15)
    d = get(b)
    if d is None: return [dict(slug=s, fetch="FAIL") for s in b]
    out = {}
    for e in d:
        for m in e["markets"]:
            out[m["slug"]] = dict(slug=m["slug"], fetch="ok", outcomes=m.get("outcomes"), prices=m.get("outcomePrices"), closed=m.get("closed"), uma=m.get("umaResolutionStatus"))
    return [out.get(s, dict(slug=s, fetch="MISSING")) for s in b]
with ThreadPoolExecutor(6) as ex:
    rows = [r for b in ex.map(one, batches) for r in b]
df = pd.DataFrame(rows); df.to_parquet("data/poly_resolution.parquet")
print(len(df), df.fetch.value_counts().to_dict(), df.uma.value_counts(dropna=False).to_dict())
