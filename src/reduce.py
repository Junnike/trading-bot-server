# reduce raw prints -> per-ticker cell aggregates (data/prints_cells.parquet) and window aggregates (data/prints_win.parquet). incremental.
import json,glob,os,gzip,sys
import numpy as np,pandas as pd
PB=[0,.1,.3,.5,.7,.9,1.0001]; AB=[0,60,120,300,600,900.0001]
res={}
for S in sorted(glob.glob("data/markets_*.jsonl")):
    for l in open(S):
        m=json.loads(l); res[m["ticker"]]=(m["result"],pd.Timestamp(m["open_time"]).timestamp(),pd.Timestamp(m["close_time"]).timestamp())
cells=pd.read_parquet("data/prints_cells.parquet") if os.path.exists("data/prints_cells.parquet") else pd.DataFrame()
wins=pd.read_parquet("data/prints_win.parquet") if os.path.exists("data/prints_win.parquet") else pd.DataFrame()
have=set(wins.ticker) if len(wins) else set()
newc=[];neww=[]
files=[f for f in glob.glob("data/prints/*.jsonl.gz")]
for f in files:
    T=os.path.basename(f)[:-9]
    if T in have or T not in res: continue
    r,o,c=res[T]
    try: d=pd.read_json(f,lines=True,dtype=False)
    except Exception as e: print("bad",T,e);continue
    if len(d)==0:
        neww.append(dict(ticker=T,n=0,ct=0.0));continue
    ct=d.count_fp.astype(float).values
    yes=(d.taker_side=="yes").values
    p=np.where(yes,d.yes_price_dollars.astype(float),d.no_price_dollars.astype(float))
    win=((yes&(r=="yes"))|(~yes&(r=="no"))).astype(float)
    t=((pd.to_datetime(d.created_time,format="ISO8601",utc=True)-pd.Timestamp(0,tz="UTC"))/pd.Timedelta(seconds=1)).values
    age=t-o
    fee=0.07*p*(1-p)
    blk=d.is_block_trade.astype(bool).values
    pb=np.digitize(p,PB)-1; ab=np.digitize(age,AB)-1   # ab -1 = before open, 5 = after close
    g=pd.DataFrame(dict(pb=pb,ab=ab,n=1,ct=ct,cp=ct*p,cw=ct*win,cf=ct*fee,cmg=ct*(p-win),blk=ct*blk,cpw=ct*p*p))
    g=g.groupby(["pb","ab"],as_index=False).sum();g.insert(0,"ticker",T);newc.append(g)
    sg=np.where(yes,1.0,-1.0)*ct
    w=dict(ticker=T,n=len(d),ct=ct.sum(),blk_ct=(ct*blk).sum(),first_age=age.min(),last_age=age.max())
    for a in (60,120,300,600): w[f"S{a}"]=sg[(age<=a)].sum(); w[f"ct{a}"]=ct[age<=a].sum()
    neww.append(w)
if neww:
    wins=pd.concat([wins,pd.DataFrame(neww)],ignore_index=True);wins.to_parquet("data/prints_win.parquet")
    cells=pd.concat([cells]+newc,ignore_index=True);cells.to_parquet("data/prints_cells.parquet")
print("windows",len(wins),"cells",len(cells))
