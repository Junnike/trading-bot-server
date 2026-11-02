#!/usr/bin/env python3 -I
"""Build hourly panel from data/all: perp close, spot close, perp quote volume, funding (8h) -> data/cache/panel_*.pkl. Re-runnable (rebuild with --force)."""
import os, sys, io, glob, zipfile, numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"); C = f"{ROOT}/cache"
def rz(p, cols):
    with zipfile.ZipFile(p) as z: raw = z.read(z.namelist()[0])
    hdr = 0 if raw[:1].isalpha() else None
    d = pd.read_csv(io.BytesIO(raw), header=hdr, usecols=range(len(cols))); d.columns = cols; return d
def norm(t): t = t.astype("int64"); return np.where(t > 10**14, t // 1000, t)
def klines(kind, sym):
    fs = sorted(glob.glob(f"{ROOT}/all/{kind}/{sym}/*.zip"))
    if not fs: return None
    d = pd.concat([rz(f, ["t","o","h","l","c","v","ct","qv"]) for f in fs]); d["t"] = pd.to_datetime(norm(d.t), unit="ms", utc=True)
    d = d.drop_duplicates("t").set_index("t").sort_index(); return d[["c","qv"]].astype(float)
def funding(sym):
    fs = sorted(glob.glob(f"{ROOT}/all/funding/{sym}/*.zip"))
    if not fs: return None
    d = pd.concat([rz(f, ["t","iv","r"]) for f in fs]); d["t"] = pd.to_datetime(((norm(d.t) + 1800_000) // 3600_000) * 3600_000, unit="ms", utc=True)
    return d.drop_duplicates("t").set_index("t").r.astype(float).sort_index()
if __name__ == "__main__":
    force = "--force" in sys.argv
    if os.path.exists(f"{C}/panel_perp.pkl") and not force: sys.exit(0)
    syms = sorted(set(os.path.basename(p) for p in glob.glob(f"{ROOT}/all/perp1h/*")))
    P, S, V, F = {}, {}, {}, {}
    for s in syms:
        kp = klines("perp1h", s); ks = klines("spot1h", s); f = funding(s)
        if kp is None or ks is None or f is None or len(kp) < 24 * 30: continue
        P[s] = kp.c; V[s] = kp.qv; S[s] = ks.c; F[s] = f
    idx = pd.date_range("2022-01-01", "2026-09-30 23:00", freq="1h", tz="UTC")
    P = pd.DataFrame(P).reindex(idx); S = pd.DataFrame(S).reindex(idx); V = pd.DataFrame(V).reindex(idx); F = pd.DataFrame(F).reindex(idx)
    for k, d in [("perp", P), ("spot", S), ("qv", V), ("fund", F)]: d.to_pickle(f"{C}/panel_{k}.pkl")
    print(len(P.columns), "symbols;", P.notna().sum(1).describe()[["min","50%","max"]].to_dict())
