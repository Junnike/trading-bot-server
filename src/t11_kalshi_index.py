# Stage 1: series->category map, then random close-time windows of settled non-MVE markets (live + /historical).
import sys,json,random,os,time
sys.path.insert(0,'src')
from kcommon import get
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
D='data/t11_kalshi/'
if not os.path.exists(D+'series_cat.json'):
    r=get('/series',{'limit':1000,'include_volume':'true'})
    cat={s['ticker']:(s['category'] if isinstance(s['category'],str) else 'UNK') for s in r['series']}
    json.dump(cat,open(D+'series_cat.json','w'))
NW=int(sys.argv[1]); WMIN=20
rng=random.Random(11)
start=pd.Timestamp('2025-01-01',tz='UTC').timestamp(); end=pd.Timestamp('2026-10-08',tz='UTC').timestamp()
wins=sorted(rng.uniform(start,end) for _ in range(NW))
wins=[int(w) for w in wins]
CUT=pd.Timestamp('2026-08-10',tz='UTC').timestamp()
done=set()
if os.path.exists(D+'index.jsonl'):
    for l in open(D+'index.jsonl'): done.add(json.loads(l)['w'])
KEEP=['ticker','event_ticker','open_time','close_time','result','volume_fp','status','market_type','open_interest_fp','price_level_structure']
def work(w):
    if w in done: return None
    ep='/historical/markets' if w+WMIN*60<CUT else '/markets'
    p={'limit':1000,'mve_filter':'exclude','min_close_ts':w,'max_close_ts':w+WMIN*60}
    if ep=='/markets': p['status']='settled'
    r=get(ep,p)
    if not r or '_err' in r: return {'w':w,'err':1,'m':[]}
    ms=[{k:m.get(k) for k in KEEP} for m in r['markets']]
    return {'w':w,'n':len(ms),'more':bool(r.get('cursor')) and len(ms)>=1000,'m':ms}
with ThreadPoolExecutor(6) as ex, open(D+'index.jsonl','a') as f:
    for i,x in enumerate(ex.map(work,wins)):
        if x:
            f.write(json.dumps(x)+'\n'); f.flush()
        if i%50==0: print(i,flush=True)
