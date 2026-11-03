#!/usr/bin/env python3 -I
"""T20: cross-venue funding arbitrage without borrowing. Long the perp on the venue with the LOWER funding, short the same coin's perp on the venue
with the HIGHER funding; collect the spread every 8h. Venues: Hyperliquid (hourly funding, summed to 8h), Aster (8h), Binance (8h, reference only:
not EU-accessible). Fees per leg-side on turnover (taker 3.5 bp / maker 1.5 bp, 2 legs each side). Hysteresis: enter top-N by trailing spread,
hold while spread >= EXIT_FRAC of the entry threshold and still top-2N. Writes results/T20_dex_carry.md"""
import os, glob, json, numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data"); RES = os.path.join(ROOT, "..", "results")
def load_hl():
    F = {}
    for p in glob.glob(f"{ROOT}/dex/hl/*.json"):
        d = json.load(open(p))
        if not d: continue
        s = pd.Series([float(x["fundingRate"]) for x in d], index=pd.to_datetime([x["time"] for x in d], unit="ms", utc=True).round("h"))
        s = s[~s.index.duplicated()].sort_index()
        F[os.path.basename(p)[:-5]] = s.resample("8h", label="right", closed="right").sum(min_count=6)   # 8h funding = sum of hourly, settlements at 00/08/16
    return pd.DataFrame(F)
def load_aster():
    F = {}
    for p in glob.glob(f"{ROOT}/dex/aster/*.json"):
        d = json.load(open(p))
        if not d: continue
        s = pd.Series([float(x["fundingRate"]) for x in d], index=pd.to_datetime([x["fundingTime"] for x in d], unit="ms", utc=True).round("h"))
        F[os.path.basename(p)[:-9]] = s[~s.index.duplicated()].sort_index()
    return pd.DataFrame(F)
def load_aster_vol():
    V = {}
    for p in glob.glob(f"{ROOT}/dex/aster_vol/*.json"):
        d = json.load(open(p))
        if not d: continue
        V[norm(os.path.basename(p)[:-9])] = pd.Series([float(x[1]) for x in d], index=pd.to_datetime([x[0] for x in d], unit="ms", utc=True))
    return pd.DataFrame(V)
def load_binance():
    P = pd.read_pickle(f"{ROOT}/cache/panel_fund.pkl"); P.columns = [c[:-4] for c in P.columns]; return P[P.index.hour.isin([0, 8, 16])]
def norm(name):  # Hyperliquid uses k-prefixed names for 1000x coins (kPEPE), Binance/Aster use 1000PEPE
    return name[1:] if name.startswith("k") and name[1:].isupper() else name.replace("1000", "")
def boot_z(x, B=2000, seed=1):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(1); return x.mean() / m.std(ddof=1)
def run(FA, FB, K, N, fee, hyst=2, enter_ann=0.0, start="2025-01-01", minvol=0.0, VOL=None):
    """FA, FB: 8h funding frames aligned (same columns, same index). Spread s = |fA - fB| per 8h; long the lower, short the higher."""
    s = (FA - FB); sig = s.rolling(K).mean(); absig = sig.abs()
    elig = absig.notna() & (absig * 3 * 365 * 100 >= enter_ann)
    if minvol > 0 and VOL is not None:
        v = VOL.reindex(columns=s.columns).resample("8h").ffill().reindex(s.index).ffill().shift(1)   # previous day's Aster quote volume, known at decision time
        elig = elig & (v >= minvol)
    rank = absig.where(elig).rank(axis=1, ascending=False)
    ent = (rank <= N).values; keep = (rank <= hyst * N).values & absig.notna().values; side = np.sign(sig.values)  # +1: fA > fB -> short A long B
    W = np.zeros(ent.shape); S = np.zeros(ent.shape); prev = np.zeros(ent.shape[1], bool); prevside = np.zeros(ent.shape[1])
    for i in range(len(ent)):
        cur = ent[i] | (prev & keep[i] & (side[i] == prevside)); W[i] = cur; S[i] = np.where(cur, np.where(prev & (side[i] == prevside), prevside, side[i]), 0); prev = cur.copy(); prevside = S[i]
    W = pd.DataFrame(W, index=s.index, columns=s.columns); S = pd.DataFrame(S, index=s.index, columns=s.columns)
    Wn = W.div(W.sum(1).replace(0, np.nan), axis=0).fillna(0)
    nxt = s.shift(-1)                                   # spread realised over the NEXT 8h
    pnl = (Wn * S * nxt).sum(1)                          # short the higher-funding venue receives +fA, long the lower pays fB  => S*(fA-fB)
    turn = (Wn - Wn.shift(1).fillna(0)).abs().sum(1); cost = turn * 2 * fee
    net = (pnl - cost)[s.index >= start]; gross = pnl[s.index >= start]
    daily = net.groupby(net.index.floor("D")).sum(); cum = (1 + net).cumprod(); yrs = max((net.index[-1] - net.index[0]).days, 1) / 365.25
    return dict(K=K, N=N, fee=fee, hyst=hyst, enter=enter_ann, ann=float(cum.iloc[-1] ** (1 / yrs) - 1) * 100, gross_ann=float(gross.mean() * 3 * 365) * 100, cost_ann=float((gross - net).mean() * 3 * 365) * 100,
                sharpe=float(daily.mean() / daily.std() * np.sqrt(365)) if daily.std() > 0 else np.nan, z=float(boot_z(daily.values)), turnover_day=float(turn[s.index >= start].mean() * 3),
                mdd=float((cum / cum.cummax() - 1).min()) * 100, n_avg=float((W[s.index >= start] > 0).sum(1).mean()), by_q={str(q): float(((1 + net[net.index.to_period("Q") == q]).prod() - 1) * 100) for q in sorted(set(net.index.to_period("Q")))})
HL, AS, BN = load_hl(), load_aster(), load_binance()
HL.columns = [norm(c) for c in HL.columns]; AS.columns = [norm(c) for c in AS.columns]; BN.columns = [norm(c) for c in BN.columns]
md = ["# T20 — cross-venue funding arbitrage (no borrow): long the lower-funding perp, short the higher, same coin (03.11.2026)\n",
      f"Data: Hyperliquid hourly funding {len(HL.columns)} coins (summed to 8h), Aster 8h funding {len(AS.columns)} symbols, Binance 8h (reference, not EU-accessible) {len(BN.columns)}. Fees per leg-side on turnover, 2 legs; price basis between the two perps ignored (both track the same index; see caveats).\n"]
AV = load_aster_vol()
for name, (A, B) in {"Hyperliquid vs Aster (both reachable from the EU with a wallet)": (HL, AS), "Hyperliquid vs Binance (reference)": (HL, BN), "Aster vs Binance (reference)": (AS, BN)}.items():
    common = sorted(set(A.columns) & set(B.columns)); idx = A.index.intersection(B.index)
    FA, FB = A.loc[idx, common], B.loc[idx, common]; both = FA.notna() & FB.notna(); FA, FB = FA.where(both), FB.where(both)
    sp = (FA - FB).abs() * 3 * 365 * 100
    md.append(f"\n## {name}: {len(common)} common coins, {idx.min().date()}..{idx.max().date()}, coin-periods with both rates {int(both.values.sum())}\n")
    md.append(f"Spread distribution (annualised |fA−fB|, per coin-period): median {np.nanmedian(sp.values):.1f} %/yr, 90th pct {np.nanpercentile(sp.values, 90):.1f}, 99th {np.nanpercentile(sp.values, 99):.1f}. Share of coin-periods with spread > 30 %/yr: {(sp > 30).values.sum() / both.values.sum() * 100:.1f} %.\n")
    md.append("| Aster vol ≥ | K | N | hyst | enter ≥ %/yr | fee | gross %/yr | cost %/yr | net ann % | Sharpe | z | turnover/day | maxDD % | avg positions | by quarter |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for mv in ([0, 1e6, 5e6] if "Aster" in name else [0]):
      for K in [3, 21]:
        for N in [5, 10, 20]:
            for hy, en in [(2, 0), (4, 20), (4, 40)]:
                for fee in [0.00035, 0.00015]:
                    r = run(FA, FB, K, N, fee, hy, en, minvol=mv, VOL=AV)
                    md.append(f"| {mv/1e6:.0f}M | {K} | {N} | {hy} | {en} | {fee*1e4:.1f}bp | {r['gross_ann']:+.1f} | {r['cost_ann']:.1f} | {r['ann']:+.1f} | {r['sharpe']:.2f} | {r['z']:.1f} | {r['turnover_day']:.2f} | {r['mdd']:.1f} | {r['n_avg']:.1f} | " + " ".join(f"{q[2:]}:{v:+.0f}" for q, v in r["by_q"].items()) + " |")
# diagnostics for HL vs Aster, K3 N10 hyst2 maker: PnL by coin, sign, Aster liquidity
common = sorted(set(HL.columns) & set(AS.columns)); idx = HL.index.intersection(AS.index); FA, FB = HL.loc[idx, common], AS.loc[idx, common]; both = FA.notna() & FB.notna(); FA, FB = FA.where(both), FB.where(both)
s_ = (FA - FB); sig = s_.rolling(3).mean(); rank = sig.abs().rank(axis=1, ascending=False); W = (rank <= 10).astype(float); W = W.div(W.sum(1).replace(0, np.nan), axis=0).fillna(0)
contrib = (W * np.sign(sig) * s_.shift(-1)).sum() * 100   # % of one-leg notional over the sample, per coin
sideA = (W * np.sign(sig)).sum()                             # >0: mostly SHORT on Hyperliquid (HL funding higher), <0: mostly LONG on HL
top = contrib.sort_values(ascending=False).head(15)
import subprocess
vol = {}
try:
    t24 = json.loads(subprocess.run(["curl", "-sS", "--max-time", "20", "https://fapi.asterdex.com/fapi/v1/ticker/24hr"], capture_output=True, text=True).stdout)
    vol = {norm(x["symbol"][:-4]): float(x.get("quoteVolume", 0)) for x in t24 if x["symbol"].endswith("USDT")}
except Exception: pass
md.append("\n## Diagnostics, HL vs Aster, K3 N10 hyst2 (no entry threshold): where the money comes from\n| coin | cum contribution % (of one-leg notional, whole sample) | share of basket-periods | avg side (+ = short HL / long Aster, − = long HL / short Aster) | mean |spread| when held %/yr | Aster 24h volume now USD |\n|---|---|---|---|---|---|")
for c in top.index:
    held = W[c] > 0
    md.append(f"| {c} | {top[c]:+.1f} | {held.mean()*100:.1f}% | {sideA[c]/max(held.sum(),1):+.2f} | {(s_[c].abs()[held].mean()*3*365*100) if held.any() else float('nan'):.0f} | {vol.get(c, float('nan')):,.0f} |")
md.append(f"Top-15 coins carry {top.sum()/contrib.sum()*100:.0f}% of total PnL; coins ever in basket: {(W.sum()>0).sum()}; Aster 24h volume median across basket coins: {np.nanmedian([vol.get(c, np.nan) for c in top.index]):,.0f} USD.")
# current cross-venue snapshot from Hyperliquid's predictedFundings
try:
    import subprocess
    pf = None
    for _ in range(3):
        try: pf = json.loads(subprocess.run(["curl", "-sS", "--max-time", "20", "-X", "POST", "-H", "Content-Type: application/json", "-d", '{"type":"predictedFundings"}', "https://api.hyperliquid.xyz/info"], capture_output=True, text=True).stdout); break
        except Exception: pass
    rows = []
    for coin, vs in pf:
        d = {v: float(x["fundingRate"]) * (8 / float(x.get("fundingIntervalHours", 8))) for v, x in vs}
        if "HlPerp" in d and "BinPerp" in d: rows.append((coin, (d["HlPerp"] - d["BinPerp"]) * 3 * 365 * 100, d["HlPerp"] * 3 * 365 * 100, d["BinPerp"] * 3 * 365 * 100, d.get("BybitPerp", np.nan) * 3 * 365 * 100))
    rows.sort(key=lambda r: -abs(r[1]))
    md.append("\n## Live snapshot (Hyperliquid predictedFundings, 8h-equivalent, %/yr): largest HL−Binance spreads right now\n| coin | HL − Binance | HL | Binance | Bybit |\n|---|---|---|---|---|")
    for r in rows[:12]: md.append(f"| {r[0]} | {r[1]:+.0f} | {r[2]:+.0f} | {r[3]:+.0f} | {r[4]:+.0f} |")
except Exception as e: md.append(f"\nlive snapshot failed: {e}")
md.append("\nCaveats: (1) the two perps' prices can diverge (venue basis); a long/short across venues carries that basis and needs margin on both sides, so capital ≈ 2× one-leg notional; (2) DEX taker fees 3.5 bp (HL 0.035 %/Aster 0.035 %), maker 1.5 bp or rebates, used on turnover only; (3) liquidity on small coins on Aster is thin; (4) Hyperliquid funding is hourly, so the 'next 8h' realisation assumes positions held across the 8 hourly payments; (5) no slippage.")
os.makedirs(RES, exist_ok=True); open(f"{RES}/T20_dex_carry.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
