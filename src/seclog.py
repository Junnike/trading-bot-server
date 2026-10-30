"""1-second logger of Hyperliquid mid prices (crypto perps + xyz TradFi perps). Public API, read-only."""
import gzip, json, os, time, urllib.request, sys
from concurrent.futures import ThreadPoolExecutor
EX = ThreadPoolExecutor(2)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "seclog")
os.makedirs(OUT, exist_ok=True)
URL = "https://api.hyperliquid.xyz/info"

def post(body):
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())

def keep(d):
    return {k: float(v) for k, v in d.items() if not k.startswith(("#", "@"))}

f = None; cur = None
while True:
    t0 = time.time()
    try:
        fa = EX.submit(lambda: (post({"type": "allMids"}), time.time()))
        fb = EX.submit(lambda: (post({"type": "allMids", "dex": "xyz"}), time.time()))
        (a, t1), (b, t2) = fa.result(), fb.result()
        row = {"t": int(t0 * 1000), "la": round(t1 - t0, 3), "lb": round(t2 - t0, 3), "p": {**keep(a), **keep(b)}}
        hour = time.strftime("%Y%m%d_%H", time.gmtime(t0))
        if hour != cur:
            if f: f.close()
            f = gzip.open(os.path.join(OUT, f"mids_{hour}.jsonl.gz"), "at"); cur = hour
        f.write(json.dumps(row, separators=(",", ":")) + "\n"); f.flush()
    except Exception as e:
        sys.stderr.write(f"{time.time()} err {e}\n"); time.sleep(2)
    time.sleep(max(0.0, 1.0 - (time.time() - t0)))
