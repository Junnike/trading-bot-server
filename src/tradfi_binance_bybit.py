"""Binance/Bybit REST is geo-blocked here -> use public data dumps (data.binance.vision S3 listing, public.bybit.com) to list USDT-perp symbols + first 1m kline month. Output data/tradfi/raw_binance_symbols.json, raw_bybit_symbols.json"""
import re, json, subprocess, pathlib, urllib.parse
D = pathlib.Path(__file__).resolve().parent.parent / "data" / "tradfi"
def get(u): return subprocess.run(["curl", "-s", "-m", "40", u], capture_output=True, text=True).stdout
def s3list(prefix):
    out, marker = [], ""
    while True:
        u = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&max-keys=1000&prefix=%s" % prefix + ("&marker=" + urllib.parse.quote(marker) if marker else "")
        x = get(u); out += re.findall(r"<Prefix>([^<]+)</Prefix>", x)[1:]
        m = re.search(r"<NextMarker>([^<]+)</NextMarker>", x)
        if "<IsTruncated>true" in x and m: marker = m.group(1)
        else: return out
syms = [p.rstrip("/").split("/")[-1] for p in s3list("data/futures/um/monthly/klines/")]
json.dump(syms, open(D / "raw_binance_symbols.json", "w"))
print(len(syms))
x = get("https://public.bybit.com/trading/")
bb = re.findall(r'href="([^"/]+)/"', x)
json.dump(bb, open(D / "raw_bybit_symbols.json", "w")); print(len(bb))
