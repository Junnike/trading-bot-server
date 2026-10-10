# Stage 2: per sampled market, one candlestick call -> carried-forward yes_ask/yes_bid at 10/50/90% of life (last candle with end_ts<=t).
import sys,json,random,os
sys.path.insert(0,'src')
from kcommon import get
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
D='data/t11_kalshi/'
PERC=int(sys.argv[1])   # markets per category
CUT=pd.Timestamp('2026-08-10',tz='UTC').strftime('%Y-%m-%dT%H:%M:%SZ')
rng=random.Random(9)
bycat={}
for l in open(D+'sample.jsonl'):
    x=json.loads(l)
    for m in x['m']: m['c']=x['c'];m['s']=x['s'];bycat.setdefault(x['c'],[]).append(m)
todo=[]
for c,l in sorted(bycat.items()):
    l.sort(key=lambda m:m['ticker']); rng.shuffle(l); todo+=l[:PERC]
rng.shuffle(todo)
done=set()
if os.path.exists(D+'entries.jsonl'):
    for l in open(D+'entries.jsonl'): done.add(json.loads(l)['t'])
def v(x,k):
    if not x: return None
    y=x.get(k+'_dollars') if (k+'_dollars') in x else x.get(k)
    return float(y) if y not in(None,'') else None
def work(m):
    T=m['ticker']
    if T in done: return None
    o=int(pd.Timestamp(m['open_time']).timestamp());c=int(pd.Timestamp(m['close_time']).timestamp())
    life=c-o
    if life<=600: return {'t':T,'skip':'life<10min'}
    per=1 if life<=6*3600 else (60 if life<=150*86400 else 1440)
    eps=[f"/series/{m['s']}/markets/{T}/candlesticks",f"/historical/markets/{T}/candlesticks"]
    if m['close_time']<CUT: eps.reverse()
    cs=None
    for ep in eps:
        r=get(ep,{'start_ts':o,'end_ts':c,'period_interval':per})
        if r is None: return {'t':T,'skip':'fail'}
        if r.get('candlesticks'): cs=r['candlesticks'];break
    if not cs: return {'t':T,'skip':'nocandles'}
    rows=sorted((x['end_period_ts'],v(x.get('yes_ask'),'close'),v(x.get('yes_bid'),'close')) for x in cs)
    out={'t':T,'c':m['c'],'s':m['s'],'o':o,'cl':c,'res':m['result'],'vol':float(m['volume_fp']),'per':per,'nc':len(rows)}
    for f in(10,50,90):
        tp=o+life*f/100; last=None
        for e,a,b in rows:
            if e<=tp: last=(e,a,b)
            else: break
        out[f'ask{f}']=last[1] if last else None; out[f'bid{f}']=last[2] if last else None; out[f'age{f}']=(tp-last[0]) if last else None
    return out
with ThreadPoolExecutor(6) as ex, open(D+'entries.jsonl','a') as f:
    for i,x in enumerate(ex.map(work,todo)):
        if x: f.write(json.dumps(x)+'\n');f.flush()
        if i%200==0: print(i,len(todo),flush=True)
print('DONE')
