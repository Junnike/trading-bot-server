# T13 analysis: maker bid-cell fill replay. Inputs: data/t13/tape.jsonl, candle_parts/KXBTC15M_*, markets_KXBTC15M.jsonl
import sys,json
sys.path.insert(0,'src')
from t13_pull import cells
import numpy as np,pandas as pd
s=cells()
s["b"]=s.yes_bid_close
s["yes"]=s.yes.astype(int)
S2=s.set_index("ticker")
tape={}
for l in open("data/t13/tape.jsonl"):
    d=json.loads(l);tape[d["ticker"]]=d
s=s[s.ticker.isin(tape)].copy()
N_all=4703
LAT0,LAT1=2,62   # order live S+2, cancel S+62
def ts(x): return pd.Timestamp(x).timestamp()
mods={"A_any_le":lambda t,b:t["yp"]<=b+1e-9,
      "A2_takerNO_le":lambda t,b:(t["side"]=="no")&(t["yp"]<=b+1e-9),
      "B_takerNO_strict_lt":lambda t,b:(t["side"]=="no")&(t["yp"]<b-1e-9)}
Ks=[0,50,200,1000]
res=[]
ntr=[];
for r in s.itertuples():
    tr=tape[r.ticker]["trades"]
    t=pd.DataFrame({"t":[ts(x["created_time"])-r.end_ts for x in tr],"yp":[float(x["yes_price_dollars"]) for x in tr],
        "side":[x["taker_side"] for x in tr],"ct":[float(x["count_fp"]) for x in tr],"blk":[x["is_block_trade"] for x in tr]}) if tr else pd.DataFrame(columns=["t","yp","side","ct","blk"])
    t=t[(t.t>=LAT0)&(t.t<=LAT1)]
    ntr.append(len(t))
    row={"ticker":r.ticker,"b":r.b,"yes":r.yes,"day":pd.Timestamp(r.end_ts,unit="s",tz="UTC").strftime("%Y-%m-%d"),"month":r.month}
    for k,f in mods.items(): row[k]=bool(len(t) and f(t,r.b).any())
    # queue sensitivity: cumulative taker-NO volume at yes_price<=b exceeds K (depth ahead assumed K) -- ASSUMPTION, not measured
    q=t[(t.side=="no")&(t.yp<=r.b+1e-9)].sort_values("t")
    cum=q.ct.sum()
    for K in Ks: row[f"Q{K}"]=bool(cum>K)
    row["vol_at"]=cum
    res.append(row)
R=pd.DataFrame(res);R["pnl"]=(R.yes-R.b)*100
R.to_parquet("data/t13/replay.parquet")
def boot(R,m,B=2000,seed=1):
    days=R.day.values;ud=np.unique(days);idx={d:np.where(days==d)[0] for d in ud}
    f=R[m].values.astype(float);p=R.pnl.values*f
    sf=np.array([f[idx[d]].sum() for d in ud]);sp=np.array([p[idx[d]].sum() for d in ud]);sn=np.array([len(idx[d]) for d in ud])
    rng=np.random.default_rng(seed);ev_sig=[];ev_fil=[]
    for _ in range(B):
        k=rng.integers(0,len(ud),len(ud));nf=sf[k].sum()
        ev_sig.append(sp[k].sum()/sn[k].sum());ev_fil.append(sp[k].sum()/nf if nf else np.nan)
    ev_sig=np.array(ev_sig);ev_fil=np.array(ev_fil)
    a=sp.sum()/sn.sum();b=sp.sum()/sf.sum()
    return a,a/ev_sig.std(),b,b/np.nanstd(ev_fil)
out=[]
out.append(f"cells with tape {len(R)}/{N_all}; windows with >=1 trade in [S+2,S+62] {int((np.array(ntr)>0).sum())}; mean trades/window {np.mean(ntr):.1f}; frac bids non-integer cent {(abs(R.b*100-np.round(R.b*100))>1e-6).mean():.4f}")
out.append("model | fill_rate | n_fills | EV/filled c (z) | EV/signal c (z) | win filled | win unfilled | mean bid filled/unfilled | unfilled counterfactual EV c")
for m in list(mods)+[f"Q{K}" for K in Ks]:
    f=R[m];a,za,b,zb=boot(R,m)
    F=R[f];U=R[~f]
    out.append(f"{m} | {f.mean():.3f} | {len(F)} | {b:+.2f} ({zb:.1f}) | {a:+.2f} ({za:.1f}) | {F.yes.mean():.3f} | {U.yes.mean():.3f} | {F.b.mean():.3f}/{U.b.mean():.3f} | {U.pnl.mean():+.2f}")
out.append("Model B monthly: month n_sig fills EV/filled EV/signal")
mm=0;pos=0
for mo,g in R.groupby("month"):
    f=g["B_takerNO_strict_lt"];ev=(g.pnl*f).sum()/len(g);mm+=1;pos+=ev>0
    out.append(f"{mo} {len(g)} {int(f.sum())} {(g.pnl[f].mean() if f.sum() else float('nan')):+.2f} {ev:+.2f}")
out.append(f"B months positive per signal: {pos}/{mm}")
h=R[R.month.isin(sorted(R.month.unique())[-2:])]
a,za,b,zb=boot(h,"B_takerNO_strict_lt")
out.append(f"B holdout {sorted(R.month.unique())[-2:]}: n={len(h)} fills={int(h.B_takerNO_strict_lt.sum())} EV/signal {a:+.2f} (z {za:.1f}) EV/filled {b:+.2f} (z {zb:.1f})")
out.append(f"unconditional cell EV (all signals, fill at bid, no fill model) {R.pnl.mean():+.2f}c")
open("data/t13/analysis.txt","w").write("\n".join(out));print("\n".join(out))
