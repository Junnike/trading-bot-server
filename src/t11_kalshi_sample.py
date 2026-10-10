# Stage 1b: stratified-by-category series sample -> settled binary markets (live /markets + /historical/markets, <=2 hist pages).
import sys,json,random,os
sys.path.insert(0,'src')
from kcommon import get
from concurrent.futures import ThreadPoolExecutor
D='data/t11_kalshi/'
cat=json.load(open(D+'series_cat.json'))
PER=int(sys.argv[1]); K=int(sys.argv[2])   # series per category, markets kept per series
rng=random.Random(5)
bycat={}
for s,c in cat.items():
    if s.endswith('15M'): continue   # crypto 15m excluded per task
    bycat.setdefault(c,[]).append(s)
sel=[]
for c,l in sorted(bycat.items()):
    l.sort(); rng.shuffle(l); sel+= [(s,c) for s in l[:PER]]
done=set()
if os.path.exists(D+'sample.jsonl'):
    for l in open(D+'sample.jsonl'): done.add(json.loads(l)['s'])
KEEP=['ticker','event_ticker','open_time','close_time','result','volume_fp','market_type','open_interest_fp','yes_sub_title']
def pull(S):
    out=[];errs=0
    r=get('/markets',{'series_ticker':S,'status':'settled','limit':1000,'mve_filter':'exclude'})
    if r is None or '_err' in r: errs+=1
    else: out+=r['markets']
    cur=None
    for pg in range(2):
        p={'series_ticker':S,'limit':1000}
        if cur: p['cursor']=cur
        r=get('/historical/markets',p)
        if r is None or '_err' in r: errs+=1;break
        out+=r['markets'];cur=r.get('cursor')
        if not cur: break
    return out,errs
def work(a):
    S,c=a
    if S in done: return None
    out,errs=pull(S)
    seen={};
    for m in out: seen[m['ticker']]=m
    ms=[m for m in seen.values() if m.get('market_type')=='binary' and m.get('result') in('yes','no') and float(m.get('volume_fp') or 0)>=100]
    r2=random.Random(S); r2.shuffle(ms)
    return {'s':S,'c':c,'nraw':len(seen),'nelig':len(ms),'errs':errs,'m':[{k:m.get(k) for k in KEEP} for m in ms[:K]]}
with ThreadPoolExecutor(6) as ex, open(D+'sample.jsonl','a') as f:
    for i,x in enumerate(ex.map(work,sel)):
        if x: f.write(json.dumps(x)+'\n');f.flush()
        if i%100==0: print(i,len(sel),flush=True)
print('DONE')
