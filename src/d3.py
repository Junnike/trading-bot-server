import json,sys,os,gzip,threading,glob
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'src')
import kcommon; pass
from kcommon import get
import pandas as pd
CUT="2026-08-10T00:00:00Z"
order=sys.argv[1:]   # list of "SERIES:days" ; days=0 means all
def load(S):
    return [json.loads(l) for l in open(f"data/markets_{S}.jsonl")]
jobs=[];queued=set()
for spec in order:
    S,days=spec.split(":");days=int(days)
    ms=load(S)
    if days:
        cutoff="2026-08-10T00:00:00Z" if days==60 else (pd.Timestamp("2026-10-09",tz="UTC")-pd.Timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        ms=[m for m in ms if m["open_time"]>=cutoff]
    import random; random.Random(0).shuffle(ms)   # random sample order so any prefix is representative
    for m in ms:
        if m["ticker"] not in queued: queued.add(m["ticker"]);jobs.append(m)
print("jobs",len(jobs),flush=True)
agglock=threading.Lock()
def work(m):
    T=m["ticker"];fn=f"data/prints/{T}.jsonl.gz"
    if os.path.exists(fn): return
    ep="/historical/trades" if m["close_time"]<CUT else "/markets/trades"
    rows=[];cur=None
    while True:
        p={"ticker":T,"limit":1000}
        if cur:p["cursor"]=cur
        d=get(ep,p)
        if not d or "trades" not in d:
            with open("data/d3_fail.log","a") as f:f.write(T+"\n")
            return
        rows+=d["trades"];cur=d.get("cursor")
        if not cur:break
    tmp=fn+".tmp"
    with gzip.open(tmp,"wt") as f:
        for r in rows:f.write(json.dumps(r)+"\n")
    os.rename(tmp,fn)
    # per-ticker aggregate
    with agglock:
        a={"ticker":T,"n":len(rows),"contracts":sum(float(r["count_fp"]) for r in rows)}
        open("data/prints_agg.jsonl","a").write(json.dumps(a)+"\n")
done=0
with ThreadPoolExecutor(12) as ex:
    for i,_ in enumerate(ex.map(work,jobs)):
        if i%500==0:print(i,flush=True)
print("DONE",flush=True)
