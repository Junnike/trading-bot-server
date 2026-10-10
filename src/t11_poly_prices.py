# Stage 3: for each sampled market fetch public CLOB prices-history of the YES token in a short window after each of 10/50/90% of life.
import requests, json, time, os, sys
from concurrent.futures import ThreadPoolExecutor
OUT = 'data/t11_poly/entries.jsonl'
H = {"User-Agent": "curl/8.0", "Accept": "application/json"}
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)['cid'])
def get(p):
    for w in [0, 2, 4, 8, 16]:
        time.sleep(w)
        try:
            r = requests.get("https://clob.polymarket.com/prices-history", params=p, headers=H, timeout=60)
            if r.status_code == 429: time.sleep(10); continue
            if r.status_code == 200: return r.json().get('history', [])
            if r.status_code == 400: return None
        except Exception: pass
    return None
def run(m):
    if m['cid'] in done: return
    life = m['close'] - m['start']; res = {}
    for f in (0.1, 0.5, 0.9):
        T = int(m['start'] + f * life); w = int(min(0.1 * life, 5 * 86400))
        w = max(w, 600)
        h = get(dict(market=m['tok'], startTs=T, endTs=min(T + w, m['close']), fidelity=max(1, w // 6000)))
        res[str(f)] = None if h is None else [(x['t'], x['p']) for x in h[:3]]
    with open(OUT, 'a') as fo: fo.write(json.dumps(dict(cid=m['cid'], res=res)) + '\n')
ms = [json.loads(l) for l in open('data/t11_poly/sample.jsonl')]
n = 0
with ThreadPoolExecutor(8) as ex:
    for _ in ex.map(run, ms):
        n += 1
        if n % 500 == 0: print(n, flush=True)
