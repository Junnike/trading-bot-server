# T13: pull trade tape [S, S+62] for each T1b cell window (minute 7, yes_bid_close in [.7,.9)). Resume-safe checkpoint data/t13/tape.jsonl
import sys,json,os,threading
sys.path.insert(0,'src')
from an_common import *
from kcommon import get
from concurrent.futures import ThreadPoolExecutor
CUT=pd.Timestamp("2026-08-10",tz="UTC").timestamp()
OUT="data/t13/tape.jsonl"
def cells():
    mk=markets(['KXBTC15M']);mk=mk[~mk.thu_maint]
    c=candle_wide('KXBTC15M',mk)
    s=c[(c.m==7)&(c.yes_bid_close>=.7)&(c.yes_bid_close<.9)].merge(mk[["ticker","close_ts"]],on="ticker")
    return s
def fetch(ep,T,S):
    rows=[];cur=None
    while True:
        p={"ticker":T,"min_ts":S,"max_ts":S+62,"limit":1000}
        if cur:p["cursor"]=cur
        d=get(ep,p)
        if not d or "trades" not in d: return None
        rows+=d["trades"];cur=d.get("cursor")
        if not cur:break
    return rows
lock=threading.Lock()
def work(x):
    T=x.ticker;S=int(x.end_ts)
    first,second=("/historical/trades","/markets/trades") if x.close_ts<CUT else ("/markets/trades","/historical/trades")
    r=fetch(first,T,S);ep=first
    if r is not None and not r and abs(x.close_ts-CUT)<12*86400:
        r2=fetch(second,T,S)
        if r2: r,ep=r2,second
    if r is None: return
    with lock:
        with open(OUT,"a") as f: f.write(json.dumps({"ticker":T,"S":S,"ep":ep,"trades":r})+"\n")
if __name__=="__main__":
    s=cells();done=set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try: done.add(json.loads(l)["ticker"])
            except Exception: pass
    todo=[x for x in s.itertuples() if x.ticker not in done]
    print("cells",len(s),"todo",len(todo),flush=True)
    with ThreadPoolExecutor(8) as ex:
        for i,_ in enumerate(ex.map(work,todo)):
            if i%250==0:print(i,flush=True)
    print("DONE",flush=True)
