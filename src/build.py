#!/usr/bin/env python3 -I
"""Parse Binance.vision monthly zips -> per-symbol 5m pickles (spot, perp) + funding.
Normalises microsecond timestamps, checks row counts per month, writes data/gaps.md.
Re-runnable: skips symbols whose cache exists (delete data/cache to rebuild)."""
import os, io, zipfile, calendar, glob
import numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CACHE = f"{ROOT}/cache"; os.makedirs(CACHE, exist_ok=True)
SYMS = ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]
COLS = ["open_time","open","high","low","close","volume","close_time","qv","n","tbv","tbqv","ig"]

def read_zip(path, cols):
    with zipfile.ZipFile(path) as z:
        name = z.namelist()[0]
        raw = z.read(name)
    first = raw.split(b"\n", 1)[0]
    header = 0 if first[:1].isalpha() else None
    df = pd.read_csv(io.BytesIO(raw), header=header)
    df.columns = cols[:len(df.columns)]
    return df

def norm_ms(t):
    t = t.astype("int64")
    return np.where(t > 10**14, t // 1000, t)  # microseconds -> ms

def build_klines(market, sym):
    rows, log = [], []
    for p in sorted(glob.glob(f"{ROOT}/{market}/{sym}/{sym}-5m-*.zip")):
        ym = p[-11:-4]; y, m = int(ym[:4]), int(ym[5:])
        df = read_zip(p, COLS)
        df["open_time"] = norm_ms(df["open_time"])
        df = df[["open_time","open","high","low","close","volume"]].astype({"open":float,"high":float,"low":float,"close":float,"volume":float})
        exp = calendar.monthrange(y, m)[1] * 288
        log.append((market, sym, ym, len(df), exp))
        rows.append(df)
    k = pd.concat(rows, ignore_index=True).drop_duplicates("open_time").sort_values("open_time")
    k["ts"] = pd.to_datetime(k["open_time"], unit="ms", utc=True)
    k = k.set_index("ts").drop(columns="open_time")
    k.index = k.index.as_unit("ms"); bad = k.index.asi8 % 300000 != 0
    assert bad.sum() == 0, f"{market} {sym} misaligned 5m bars: {bad.sum()}"
    return k, log

def build_funding(sym):
    rows = []
    for p in sorted(glob.glob(f"{ROOT}/funding/{sym}/{sym}-fundingRate-*.zip")):
        df = read_zip(p, ["calc_time","interval_h","rate"])
        rows.append(df)
    f = pd.concat(rows, ignore_index=True)
    f["calc_time"] = norm_ms(f["calc_time"])
    # funding timestamps are 00/08/16 UTC +- few ms -> round to nearest hour
    f["ts"] = pd.to_datetime(((f["calc_time"] + 1800_000) // 3600_000) * 3600_000, unit="ms", utc=True)
    f = f.drop_duplicates("ts").set_index("ts")["rate"].astype(float).sort_index()
    return f

if __name__ == "__main__":
    logs = []
    for sym in SYMS:
        for market in ["spot", "perp"]:
            out = f"{CACHE}/{market}_{sym}_5m.pkl"
            if os.path.exists(out): 
                logs += pd.read_pickle(f"{CACHE}/{market}_{sym}_log.pkl"); continue
            k, log = build_klines(market, sym)
            k.to_pickle(out); pd.to_pickle(log, f"{CACHE}/{market}_{sym}_log.pkl"); logs += log
            print(market, sym, len(k), k.index[0], k.index[-1])
        fo = f"{CACHE}/funding_{sym}.pkl"
        if not os.path.exists(fo): build_funding(sym).to_pickle(fo)
    L = pd.DataFrame(logs, columns=["market","sym","month","rows","expected"])
    L["missing"] = L["expected"] - L["rows"]
    L.to_csv(f"{CACHE}/rowcounts.csv", index=False)
    gaps = L[L["missing"] != 0]
    with open(f"{ROOT}/../results/data_gaps.md", "w") as f:
        f.write("# 5m row counts vs expected (288/day)\n\n")
        f.write(f"Months checked: {len(L)}; months with missing bars: {(L.missing>0).sum()}; total missing 5m bars: {int(L.missing.clip(lower=0).sum())}\n\n")
        f.write("First-month partial listings (symbol listed mid-month) are included below.\n\n")
        f.write(gaps.to_markdown(index=False) + "\n")
    print(gaps.groupby(["market","sym"]).missing.sum())
