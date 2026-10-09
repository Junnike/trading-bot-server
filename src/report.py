import sys,subprocess,os,glob;sys.path.insert(0,'src')
import numpy as np,pandas as pd
from an_common import *
import an_t15,an_t1,an_t2,an_t4
out=sys.argv[1]
L=[]
def A(s): L.append(s)
sers=[os.path.basename(f)[8:-6] for f in glob.glob(D+"candle_parts/*_0000.parquet")]
sers=[s.split("_")[0] for s in map(lambda f:os.path.basename(f),glob.glob(D+"candle_parts/*_0000.parquet"))]
sers=sorted(set(x[:-5] for x in sers)) if sers else []
sers=sorted(set(os.path.basename(f).rsplit("_",1)[0] for f in glob.glob(D+"candle_parts/*.parquet")))
f2=lambda x:"nan" if x is None or (isinstance(x,float) and np.isnan(x)) else f"{x:.2f}"
A("# RESULTS_KALSHI (D1-D4,T1,T1b,T2,T4,T5,T6) 09.10.2026 -- PARTIAL if banner says so")
nw=len(pd.read_parquet(D+"prints_win.parquet")) if os.path.exists(D+"prints_win.parquet") else 0
mkb=markets(["KXBTC15M"])
A(f"Data: markets_*.jsonl 12 series (BTC {len(mkb)} windows {mkb.open_time.min()[:10]}..{mkb.open_time.max()[:10]}); candles: data/candle_parts/ {sers}; prints: data/prints/ ({nw} windows reduced -> data/prints_win.parquet, data/prints_cells.parquet); API: /historical/* used before 2026-08-10 cutoff (live /markets has only ~68d).")
# T1b/T5
r=an_t15.run(["KXBTC15M"],"btc")
cw=r["nwin"]
A(f"Confounders: candles BTC {cw} windows, months {r['months'][0]}..{r['months'][-1]} (data/candle_parts); Thursday 07-09 UTC windows excluded; no-candle windows dropped; prints are a RANDOM SAMPLE of BTC last-60d windows (rate-limit bound).")
t=r["t1b"];s=t[t.bidb=="[.7,.9)"].set_index("m")
A(f"## T1b BTC P(yes)-yes_bid_close, bucket [.7,.9) [data/candle_parts/KXBTC15M_*.parquet x markets_KXBTC15M.jsonl]")
mmo=r["t1b_month"];mmo=mmo[mmo.n>=30]
posm=mmo.groupby("m").apply(lambda g:pd.Series(dict(pos=(g.edge>0).mean(),k=len(g))),include_groups=False)
A("m:edge c (n win, z, %months+): "+" ".join(f"{m}:{s.edge[m]*100:+.1f}(n{int(s.n[m])},z{s.edge[m]/s.se[m]:.1f},{posm.pos.get(m,np.nan):.0%})" for m in s.index if 5<=m<=14))
oth=t[(t.m==7)&(t.bidb!="[.7,.9)")]
A("m=7 other buckets hit-bid c: "+" ".join(f"{b}:{e*100:+.1f}" for b,e in zip(oth.bidb,oth.edge)))
best=s.loc[5:14].edge.idxmax();bm=s.loc[5:13].edge.sub(0).idxmax()
z7=s.edge[7]/s.se[7]
A(f"T1b CAVEAT: edge assumes fill at the bid_close; no queue/adverse-selection model (use T1 print-level fills). Verdict T1b: "+("ALIVE" if (s.loc[5:14].edge>0.01).any() else "KILLED")+f" (hit-bid>0.01 at m=5-11; best m=7 {s.edge[7]*100:+.1f}c z={z7:.1f}, {posm.pos[7]:.0%} of {int(posm.k[7])} months positive -> T6 pass)")
t5=r["t5"];ev=t5[t5.n>=500]
tp=ev.sort_values("z",ascending=False).head(3)
A(f"## T5 taker at real ask (pooled yes@ask/no@1-bid), EV c/ct after fee [data/candle_parts/KXBTC15M_*]")
pbt=t5.groupby("pb",observed=True).apply(lambda g:pd.Series(dict(n=g.n.sum(),ev=(g.ev*g.n).sum()/g.n.sum()*100)),include_groups=False)
A("by price bucket (all m): "+"; ".join(f"{i} n={int(v.n)} ev={v.ev:+.2f}c" for i,v in pbt.iterrows()))
A("top z cells (n>=500): "+"; ".join(f"{x.pb} m={int(x.m)} n={int(x.n)} ev={x.ev*100:+.2f}c z={x.z:.1f}" for x in tp.itertuples()))
cand=ev[ev.z>2]
A(f"cells with z>2 & n>=500: {len(cand)} of {len(ev)}. Verdict T5: "+("ALIVE-candidate -> T6 below" if len(cand) else "KILLED (no cell z>2)"))
if len(cand):
    c5=r["t5_month"].merge(cand[["pb","m"]],on=["pb","m"])
    for x in cand.sort_values("z",ascending=False).head(2).itertuples():
        mm_=r["t5_month"][(r["t5_month"].pb==x.pb)&(r["t5_month"].m==x.m)]
        A(f"T6 cell {x.pb} m={x.m}: monthly EV c/ct "+" ".join(f"{a}:{b*100:+.1f}(n{int(n)})" for a,b,n in zip(mm_.month,mm_["mean"],mm_["size"]))+" [positive months "+f"{(mm_['mean']>0).mean():.0%}, months={len(mm_)}]")
for S2 in ("KXETH15M","KXSOL15M"):
    if not glob.glob(D+f"candle_parts/{S2}_*.parquet"): continue
    try: r2=an_t15.run([S2],"x")
    except Exception as e: continue
    if r2["nwin"]<300: continue
    t2b=r2["t1b"];s2=t2b[t2b.bidb=="[.7,.9)"].set_index("m")
    mo2=r2["t1b_month"];mo2=mo2[(mo2.n>=30)]
    p2=mo2.groupby("m").apply(lambda g:pd.Series(dict(pos=(g.edge>0).mean(),k=len(g))),include_groups=False)
    ev2=r2["t5"][r2["t5"].n>=500]
    A(f"{S2[2:-3]} (candles only, {r2['nwin']} windows {r2['months'][0]}..{r2['months'][-1]}, data/candle_parts/{S2}_*): T1b [.7,.9) hit-bid c m5-9: "+" ".join(f"{m}:{s2.edge[m]*100:+.1f}(z{s2.edge[m]/s2.se[m]:.1f},{p2.pos.get(m,np.nan):.0%}of{int(p2.k.get(m,0))}mo)" for m in range(5,10) if m in s2.index)+f"; T5 max z (n>=500)={ev2.z.max():.1f}, cells z>2: {(ev2.z>2).sum()}/{len(ev2)}; flips {r2['flips']}/{r2['flip_den']}")
A(f"Flips (ask_close m14 >=.9 & no / <=.1 & yes): {r['flips']} of {r['flip_den']} windows ({r['flips']/max(1,r['flip_den'])*100:.1f}%) [candles]")
# T1
if nw>=5:
    o=an_t1.run("KXBTC15M",flips=r["flip_by_ticker"])
    A(f"## T1 BTC maker vs p<0.3 takers: {o['nwin']} sampled windows, months {o['months']}, block share {o['blk_share']:.3f} [data/prints_cells.parquet]")
    la=o["low_all"]
    A(f"p<.3 all: ct={la.ct:.3g} taker_pnl={la.taker_pnl_c:+.2f}c/ct (z={la.z:.1f}) maker_gross={la.maker_gross_c:+.2f}c/ct (z={la.mk_z:.1f})")
    A("by p-bucket [taker pnl c/ct (z) | maker gross c/ct]: "+"; ".join(f"{PBN[int(i)]} {v.taker_pnl_c:+.1f}({v.z:.1f})|{v.maker_gross_c:+.1f}" for i,v in o["by_pb"].iterrows()))
    A("p<.3 by age: "+"; ".join(f"{ABN[int(i)]} n={int(v.nwin)}w maker={v.maker_gross_c:+.1f}(z{v.mk_z:.1f})" for i,v in o["low_by_ab"].iterrows()))
    A("p<.3 by month: "+"; ".join(f"{i} {int(v.nwin)}w maker={v.maker_gross_c:+.1f}(z{v.mk_z:.1f})" for i,v in o["low_by_month"].iterrows()))
    A(f"weeks with maker gross>0: {o['wk_pos']:.0%} of {o['nweeks']} weeks (weekly windows: "+",".join(str(int(x)) for x in o['weeks'].nw)+")")
    if o["low_by_vq"] is not None: A("p<.3 by 1h-vol quartile (data/binance): "+"; ".join(f"{i} {int(v.nwin)}w {v.maker_gross_c:+.1f}c" for i,v in o["low_by_vq"].iterrows()))
    else: A("vol quartile split: UNMEASURED (data/binance missing)")
    if o.get("low_flip") is not None: A(f"flip windows ({o['flip_n']}): maker {o['low_flip'].maker_gross_c:+.1f}c vs non-flip {o['low_noflip'].maker_gross_c:+.1f}c")
    fi=o["fifo"]
    A("FIFO (cap 200ct/window binds at all shares since taker ct/window >> 200): "+"; ".join(f"share {k}: {v['usd_day']:.0f} USD/day" for k,v in fi.items())+f" ({fi[0.05]['wpd']:.0f} win/day)")
    full=(o['nwin']>=1500)
    A("Verdict T1: "+("KILLED" if (la.maker_gross_c<=1.0 or o['wk_pos']<.6 or fi[0.05]['usd_day']<5) else "ALIVE (sample-limited, see n windows)")+f" -- sample {o['nwin']} windows")
else: A("T1: pending prints")
# T2
if nw>=20:
    t2=an_t2.run();A("## T2 signed flow BTC [data/prints_win.parquet + candles]; EV c/ct buy flow side at ask_open of next minute")
    A("a,q,n | hit | EV(z) | EV@close-of-minute(z): "+" ; ".join(f"{int(x.a)},{x.q:.1f},{x.n} {x.hit:.3f} {x.ev_c:+.1f}({x.z:.1f}) {x.ev_close_c:+.1f}({x.z_close:.1f})" for x in t2.itertuples()))
    b=t2.sort_values("z",ascending=False).iloc[0]
    A(f"best cell a={int(b.a)} q={b.q}: n={b.n} EV={b.ev_c:+.1f}c z={b.z:.1f}; months: "+" ".join(f"{i}:{v['mean']*100:+.1f}(n{int(v['size'])})" for i,v in b.mon.iterrows()))
    A("Verdict T2: "+("KILLED" if ((t2.ev_c<=0).all() or (b.z<2 and b.n>=500)) else ("ALIVE-candidate" if b.z>=2 else "UNMEASURED (n<500 windows, best z<2)")))
# T4
a=an_t4.analyze()
if a: A(f"## T4 KXBTCD ladder [data/t4_poll.jsonl]: {a['snaps']} snapshots over {a['hours']:.1f} h (fails {a['fail']}), mean pairs {a['pairs_mean']:.0f}; max net edge {a['max_net']:+.4f} (gross {a['max_gross']:+.4f}); snapshots net>0: {a['n_pos']}, net>=1c: {a['n_ge1c']}; Verdict T4: "+("KILLED" if a['n_ge1c']==0 and a['hours']>=3 else ("UNMEASURED (<3 h)" if a['hours']<3 else "ALIVE-candidate")))
open(out,"w").write("\n".join(L)+"\n")
print("\n".join(L))
