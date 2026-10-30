"""First available data date for TradFi symbols on Binance (data.binance.vision 1m klines) and Bybit (public.bybit.com trades). Writes data/tradfi/history_binance_bybit.json"""
import re, json, sys, pathlib, subprocess
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from tradfi_classify import norm, category
D = pathlib.Path(__file__).resolve().parent.parent / "data" / "tradfi"
u = set(json.load(open(D / "stock_universe_matched.json"))) - {"DASH", "STX", "CVX", "EQT", "MAR", "ROK", "HUT", "COP", "RUM"}
get = lambda x: subprocess.run(["curl", "-s", "-m", "40", x], capture_output=True, text=True).stdout
def cls(s):
    b = norm(s); b = re.sub(r"^1000(?=[A-Z]{3,})", "", b); c = category(b, False)
    if c is None and b in u: c = "stocks"
    return b, c
def tf(f): return {s: cls(s) for s in json.load(open(D / f)) if s.endswith(("USDT", "USDC")) and cls(s)[1] not in (None, "crypto", "token_gold")}
BN, BY = tf("raw_binance_symbols.json"), tf("raw_bybit_symbols.json")
def bn(s):
    x = get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/monthly/klines/%s/1m/&max-keys=1000" % s)
    m = sorted(re.findall(r"1m-(\d{4}-\d{2})\.zip<", x))
    d = get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/daily/klines/%s/1m/&max-keys=1000" % s)
    dd = sorted(re.findall(r"1m-(\d{4}-\d{2}-\d{2})\.zip<", d))
    return s, (dd[0] if dd and (not m or dd[0][:7] <= m[0]) else (m[0] if m else None)), (dd[-1] if dd else (m[-1] if m else None))
def by(s):
    x = get("https://public.bybit.com/trading/%s/" % s)
    f = sorted(re.findall(r'href="[^"]*?(\d{4}-\d{2}-\d{2})\.csv\.gz"', x))
    return s, (f[0] if f else None), (f[-1] if f else None)
with ThreadPoolExecutor(12) as ex:
    rb = list(ex.map(bn, BN)); ry = list(ex.map(by, BY))
json.dump({"binance": {s: dict(base=BN[s][0], cat=BN[s][1], first=a, last=b) for s, a, b in rb},
           "bybit": {s: dict(base=BY[s][0], cat=BY[s][1], first=a, last=b) for s, a, b in ry}}, open(D / "history_binance_bybit.json", "w"), indent=0)
for nm, r in (("binance", rb), ("bybit", ry)):
    f = sorted(a for s, a, b in r if a); print(nm, len(r), "first", f[:3], "last-first", f[-3:])
