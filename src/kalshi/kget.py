import time, threading, requests, os
BASE = "https://api.elections.kalshi.com/trade-api/v2"; H = {"User-Agent": "curl/8.0", "Accept": "application/json"}
_lock = threading.Lock(); _next = [0.0]; SLOT = float(os.environ.get("KSLOT", "0.18"))
_s = requests.Session()
def get(path, params=None):
    for wait in (0, 2, 4, 8, 16):
        if wait: time.sleep(wait)
        with _lock:
            t = max(time.time(), _next[0]); _next[0] = t + SLOT
        d = t - time.time()
        if d > 0: time.sleep(d)
        try: r = _s.get(BASE + path, params=params, headers=H, timeout=30)
        except Exception: continue
        if r.status_code == 200:
            try: return r.json()
            except Exception: continue
        if r.status_code == 429:
            with _lock: _next[0] = time.time() + 3
            continue
        if r.status_code in (400, 404): return {"_err": r.status_code}
    return None
