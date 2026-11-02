#!/usr/bin/env python3 -I
"""Score CRSI(2,2,75)<=20 -> next-15m UP on (a) Binance candle label (close>=open) and (b) the venue TWAP label:
mean price over the 60 s before close >= mean over the 60 s before open. Long-history proxy: 1-minute VWAP (quote_vol/vol) of the
minute bar ending at close vs the one ending at open. Validated on BTC against 1-s TWAP (Dec 2025-Oct 2026) and Kalshi settlement.
Writes results/T17_crsi_twap_label.md"""
import os, io, glob, zipfile, json, numpy as np, pandas as pd, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import crsi, boot_z, CACHE, RES
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
def rz(p):
    with zipfile.ZipFile(p) as z: raw = z.read(z.namelist()[0])
    d = pd.read_csv(io.BytesIO(raw), header=0 if raw[:1].isalpha() else None, usecols=[0, 1, 2, 3, 4, 5, 7]); d.columns = ["t", "o", "h", "l", "c", "v", "qv"]; return d
def load1m(sym):
    c = f"{CACHE}/spot1m_{sym}.pkl"
    if os.path.exists(c): return pd.read_pickle(c)
    d = pd.concat([rz(p) for p in sorted(glob.glob(f"{ROOT}/spot1m/{sym}/*.zip")) + sorted(glob.glob(f"{ROOT}/spot1m_daily/{sym}/*.zip"))]); t = d.t.astype("int64").values; t = np.where(t > 10**14, t // 1000, t)
    d["t"] = pd.to_datetime(t, unit="ms", utc=True); d = d.drop_duplicates("t").set_index("t").sort_index().astype(float)
    d["vwap"] = (d.qv / d.v).where(d.v > 0, d.c); d.to_pickle(c); return d
md = ["# T17 — CRSI robot scored on the venue TWAP label (03.11.2026)\n"]
# --- validation on BTC: 1-min VWAP label vs 1-s TWAP label vs Kalshi settlement
b = load1m("BTCUSDT")
cand = [json.loads(l) for l in open(f"{ROOT}/kalshi/candles.jsonl")]
src = open(f"{ROOT}/../src/kalshi/k6_twap_sniper.py").read().split("cand = {}")[0]; ns = {"__file__": os.path.abspath("src/kalshi/k6_twap_sniper.py")}; exec(src, ns); closes = ns["closes"]
agree_vw_1s = agree_vw_k = agree_1s_k = agree_c_k = n = 0
for r in cand:
    o, c = r["o"], r["c"]; pre = closes(o - 60, o); win = closes(c - 60, c)
    if pre is None or win is None: continue
    to, tc = pd.Timestamp(o - 60, unit="s", tz="UTC"), pd.Timestamp(c - 60, unit="s", tz="UTC")
    if to not in b.index or tc not in b.index: continue
    l1s = int(win.mean() >= pre.mean()); lvw = int(b.vwap[tc] >= b.vwap[to]); lk = 1 if r["res"] == "yes" else 0
    lc = int(b.c[pd.Timestamp(c - 60, unit="s", tz="UTC")] >= b.o[pd.Timestamp(o, unit="s", tz="UTC")]) if pd.Timestamp(o, unit="s", tz="UTC") in b.index else lk
    n += 1; agree_vw_1s += lvw == l1s; agree_vw_k += lvw == lk; agree_1s_k += l1s == lk; agree_c_k += lc == lk
md.append(f"Validation on {n} Kalshi windows: 1-min VWAP label = 1-s TWAP label {agree_vw_1s/n*100:.2f}%; VWAP label = Kalshi settlement {agree_vw_k/n*100:.2f}%; 1-s TWAP = settlement {agree_1s_k/n*100:.2f}%; candle label = settlement {agree_c_k/n*100:.2f}%. VWAP-of-minute is an acceptable long-history proxy for the venue label.\n")
# --- CRSI robot on both labels
md.append("| coin | window | n signals | WR candle label % | WR TWAP label % | drop pp | agreement of labels on signal bars % | EV at p=0.55 taker on TWAP label (c) |\n|---|---|---|---|---|---|---|---|")
summary = {}
for sym in SYMS:
    m1 = load1m(sym)
    k = m1.resample("15min", label="left", closed="left").agg(o=("o", "first"), c=("c", "last"), n=("o", "count")); k = k[k.n == 15]
    # labels for bar starting at T: candle: c>=o ; twap: vwap[T+14min] >= vwap[T-1min]
    k["lab_c"] = (k.c >= k.o).astype(int)
    vw = m1.vwap
    k["lab_t"] = (vw.reindex(k.index + pd.Timedelta(minutes=14)).values >= vw.reindex(k.index - pd.Timedelta(minutes=1)).values).astype(float)
    k.loc[vw.reindex(k.index + pd.Timedelta(minutes=14)).isna().values | vw.reindex(k.index - pd.Timedelta(minutes=1)).isna().values, "lab_t"] = np.nan
    k["crsi"] = crsi(k.c.values)
    ts = k.index.asi8 // 60_000_000_000 if k.index.dtype.str.endswith("[ns, UTC]") else k.index.as_unit("ms").asi8 // 60_000
    contig = np.r_[False, np.diff(ts) == 15]
    sig = (k.crsi.values <= 20) & pd.Series(contig).rolling(80, min_periods=80).min().fillna(0).values.astype(bool)
    idx = np.where(sig)[0]; idx = idx[idx + 1 < len(k)]; idx = idx[contig[idx + 1]]
    e = idx + 1; lc = k.lab_c.values[e]; lt = k.lab_t.values[e]; ok = ~np.isnan(lt); lc, lt = lc[ok], lt[ok]; tt = k.index[e][ok]
    for w, msk in [("2020-26", np.ones(len(lt), bool)), ("2025-26", tt >= "2025-01-01")]:
        a, b2 = lc[msk], lt[msk]
        if len(a) < 100: continue
        wr_c, wr_t = a.mean() * 100, b2.mean() * 100; ev = (b2.mean() - 0.55 - 0.07 * 0.55 * 0.45) * 100
        md.append(f"| {sym[:-4]} | {w} | {len(a)} | {wr_c:.2f} | {wr_t:.2f} | {wr_c - wr_t:+.2f} | {(a == b2).mean()*100:.1f} | {ev:+.2f} |")
        summary[(sym, w)] = (wr_c, wr_t, len(a))
md.append("\nEV column: binary payout buying UP at 0.55 with taker fee 0.07·p·(1−p); break-even WR at 0.55 is 56.7 %, at 0.50 it is 51.75 %.")
md.append("Caveats: label proxy = 1-min VWAP (volume-weighted, not time-weighted) of Binance, validated above; venue indices (BRTI, Chainlink) add ~1-2 % further disagreement; the robot here is the CRSI gate, not the Pine v1 robots (files missing).")
open(f"{RES}/T17_crsi_twap_label.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
