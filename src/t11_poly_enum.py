# Stage 1: enumerate closed Polymarket events by endDate windows (3 x 2-day windows per month), keep market-level fields.
import requests, json, time, os, datetime as dt, sys
from concurrent.futures import ThreadPoolExecutor
OUT = "data/t11_poly/markets.jsonl"; DONE = "data/t11_poly/enum_done.txt"
H = {"User-Agent": "curl/8.0", "Accept": "application/json"}
def get(url, p):
    for w in [0, 2, 4, 8, 16]:
        time.sleep(w)
        try:
            r = requests.get(url, params=p, headers=H, timeout=60)
            if r.status_code == 429: time.sleep(10); continue
            r.raise_for_status(); return r.json()
        except Exception as e: err = e
    raise RuntimeError(f"UNMEASURED {url} {p} {err}")
wins = []
for y, mo in [(2025, m) for m in range(1, 13)] + [(2026, m) for m in range(1, 10)]:
    for d in (5, 15, 25):
        a = dt.datetime(y, mo, d)
        for k in range(8):  # 6-hour chunks (API caps offset ~2000)
            wins.append(((a + dt.timedelta(hours=6*k)).strftime("%Y-%m-%dT%H:%M:%SZ"), (a + dt.timedelta(hours=6*k+6)).strftime("%Y-%m-%dT%H:%M:%SZ")))
done = set(open(DONE).read().split()) if os.path.exists(DONE) else set()
def run(w):
    if w[0] in done: return
    rows = []; off = 0
    while True:
        try: r = get("https://gamma-api.polymarket.com/events", dict(closed="true", limit=100, offset=off, end_date_min=w[0], end_date_max=w[1]))
        except RuntimeError as ex:
            if "422" in str(ex): open("data/t11_poly/enum_capped.txt","a").write(f"{w[0]} off={off}\n"); break
            raise
        for e in r:
            tags = [t["label"] for t in e.get("tags", [])]
            for m in e.get("markets", []):
                rows.append(dict(win=w[0], evslug=e["slug"], evvol=e.get("volume"), tags=tags, slug=m.get("slug"), q=m.get("question"),
                    cid=m.get("conditionId"), tokens=m.get("clobTokenIds"), prices=m.get("outcomePrices"), outcomes=m.get("outcomes"),
                    start=m.get("startDate"), end=m.get("endDate"), closed_t=m.get("closedTime"), vol=m.get("volumeNum"),
                    uma=m.get("umaResolutionStatus"), fees=m.get("feesEnabled"), fs=m.get("feeSchedule")))
        if len(r) < 100 or off >= 9900: break
        off += 100
    with open(OUT, "a") as f:
        for x in rows: f.write(json.dumps(x) + "\n")
    open(DONE, "a").write(w[0] + "\n"); print(w, len(rows), flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(run, wins))
