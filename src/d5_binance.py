import sys, os, time, io, zipfile, datetime as dt
import requests, pandas as pd
OUT = "data/binance"
BASE = "https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1s/BTCUSDT-1s-%s.zip"
today = dt.date(2026, 10, 9)
recent = [today - dt.timedelta(days=i) for i in range(1, 61)]
old = []
d = today - dt.timedelta(days=61)
while d >= dt.date(2025, 12, 11):
    old.append(d); d -= dt.timedelta(days=1)
cols = ["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"]
s = requests.Session()
for day in recent + old:
    ds = day.isoformat()
    fn = f"{OUT}/BTCUSDT-1s-{ds}.parquet"
    if os.path.exists(fn) or os.path.exists(fn + ".missing"):
        continue
    for k, w in enumerate([0, 2, 4, 8, 16]):
        time.sleep(w)
        try:
            r = s.get(BASE % ds, timeout=120)
            if r.status_code == 404:
                open(fn + ".missing", "w").close(); break
            r.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(r.content))
            df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=cols, usecols=range(6))
            t = df["t"].astype("int64")
            if t.max() > 1e14: t = t // 1000  # microsecond timestamps (2025+ spot)
            out = pd.DataFrame({"t": (t // 1000).astype("int64"), "c": df["c"].astype("float32"),
                                "h": df["h"].astype("float32"), "l": df["l"].astype("float32"),
                                "o": df["o"].astype("float32"), "v": df["v"].astype("float32")})
            out.to_parquet(fn + ".tmp", compression="zstd"); os.rename(fn + ".tmp", fn)
            print(ds, len(out), flush=True); break
        except Exception as e:
            print(ds, "err", e, flush=True)
    else:
        print(ds, "UNMEASURED", flush=True)
print("DONE", flush=True)
