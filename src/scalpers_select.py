"""Select ~200 candidate wallets from the public HL leaderboard (data/scalpers/lb.json)."""
import json, sys
D='data/scalpers/'
rows=json.load(open(D+'lb.json'))['leaderboardRows']
c=[]
for r in rows:
    w={k:{a:float(b) for a,b in v.items()} for k,v in r['windowPerformances']}
    av=float(r['accountValue'])
    if not(w['week']['pnl']>0 and w['month']['pnl']>=50e3 and w["allTime"]["pnl"]>=150e3 and w['month']['roi']>=0.05 and w['allTime']['roi']>0): continue
    if w['month']['vlm']<max(av,1e5)*10: continue   # turnover filter: scalper-like
    c.append(dict(addr=r['ethAddress'],name=r['displayName'],av=av,w=w))
def rk(key):
    s=sorted(c,key=key); 
    for i,x in enumerate(s): x.setdefault('r',[]).append(i/len(s))
rk(lambda x:x['w']['month']['pnl']); rk(lambda x:x['w']['allTime']['pnl']); rk(lambda x:x['w']['month']['roi']); rk(lambda x:x['w']['week']['roi']); rk(lambda x:x['w']['allTime']['roi'])
for x in c: x['score']=sum(x['r'])/len(x['r'])
c.sort(key=lambda x:-x['score'])
print(len(c),'passed filter')
json.dump(c[:200],open(D+'candidates.json','w'))
print(len(c[:200]))
