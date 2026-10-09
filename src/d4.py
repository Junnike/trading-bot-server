import json,sys,os,glob,threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'src')
import kcommon; kcommon.GAP=float(os.environ.get("GAP","0.4"))
from kcommon import get
import pandas as pd
CUT="2026-08-10T00:00:00Z"
S=sys.argv[1];days=int(sys.argv[2])
ms=[json.loads(l) for l in open(f"data/markets_{S}.jsonl")]
if days:
    c="2026-08-10T00:00:00Z" if days==60 else (pd.Timestamp("2026-10-09",tz="UTC")-pd.Timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ms=[m for m in ms if m["open_time"]>=c]
import random; random.Random(0).shuffle(ms)  # same order as d3
doneset=set()
for f in glob.glob(f"data/candle_parts/{S}_*.parquet"):
    doneset|=set(pd.read_parquet(f,columns=["ticker"]).ticker)
todo=[m for m in ms if m["ticker"] not in doneset]
print(S,"todo",len(todo),flush=True)
def f(x,k):
    if not x: return None
    v=x.get(k+"_dollars") if (k+"_dollars") in x else x.get(k)
    return float(v) if v not in (None,"") else None
def work(m):
    T=m["ticker"];o=int(pd.Timestamp(m["open_time"]).timestamp());c=int(pd.Timestamp(m["close_time"]).timestamp())
    eps=[f"/series/{S}/markets/{T}/candlesticks",f"/historical/markets/{T}/candlesticks"]
    if m["close_time"]<CUT: eps.reverse()
    cs=None
    for ep in eps:
        r=get(ep,{"start_ts":o,"end_ts":c,"period_interval":1})
        if r is None: return None
        if r.get("candlesticks"): cs=r["candlesticks"];break
    rows=[]
    for x in cs or []:
        row={"ticker":T,"end_ts":x["end_period_ts"],"vol":f(x,"volume_fp") if "volume_fp" in x else f(x,"volume"),"oi":f(x,"open_interest_fp") if "open_interest_fp" in x else f(x,"open_interest")}
        for side in("yes_bid","yes_ask","price"):
            for k in("open","high","low","close"):
                row[f"{side}_{k}"]=f(x.get(side),k)
        rows.append(row)
    if not rows: rows=[{"ticker":T,"end_ts":None}]   # marker: no data
    return rows
buf=[];part=len(glob.glob(f"data/candle_parts/{S}_*.parquet"))
def flush():
    global buf,part
    if buf:
        pd.DataFrame(buf).to_parquet(f"data/candle_parts/{S}_{part:04d}.parquet");part+=1;buf=[]
with ThreadPoolExecutor(6) as ex:
    for i,r in enumerate(ex.map(work,todo)):
        if r: buf+=r
        if (i+1)%100==0: flush();print(i+1,flush=True)
flush();print("DONE",S,flush=True)
