"""Filter/rank/OOS from data/scalpers/metrics.json -> data/scalpers/ranking.json + printed tables."""
import json, time, statistics as st
D='data/scalpers/'
M=[m for m in json.load(open(D+'metrics.json')) if 'skip' not in m]
now=time.time()*1000
def bps(p,m): return p['net']/m['notional']*1e4 if m['notional'] else 0
def style(m):
    if m['maker_share_notional']>=0.8 and (m['med_hold_s'] or 1e9)<120: return 'MM/HFT-bot'
    if m['fills_day']>3000: return 'HFT-bot'
    if m['maker_share_notional']>=0.5: return 'maker-scalper'
    return 'taker-scalper'
rows=[]
for m in M:
    r=dict(addr=m['addr'],active=(now-m['last'])/86400e3<=3,days=m['days'])
    pw=[x for x in (m['pos_weeks_fills'] if m['nweeks_fills']>=2 else None, m['port']['pos_share'] if m['port'] and m['port']['weeks']>=4 else None) if x is not None]
    r['posw']=min(pw) if pw else None
    r['ok_hold']=m['med_hold_s'] is not None and m['med_hold_s']<1800
    r['ok_trades']=m['fills_day']>=20
    r['ok_net']=m['full']['net']>0
    r['ok_week']=r['posw'] is not None and r['posw']>=0.6
    r['ok_conc']=m['top3_share'] is not None and m['top3_share']<=0.4
    r['style']=style(m); r['m']=m
    r['pass']=all(r[k] for k in ('active','ok_hold','ok_trades','ok_net','ok_week','ok_conc'))
    rows.append(r)
print('wallets',len(rows))
for k in ('active','ok_hold','ok_trades','ok_net','ok_week','ok_conc','pass'): print(k,sum(1 for r in rows if r[k]))
def score(r):
    m=r['m']; c={x['shift']:x for x in m['copy']}
    sv=1 if c[5000]['n']>=30 and c[5000]['pnl']>0 else 0
    return r['posw']+min(m['full']['pf'] or 0,3)/3+min(bps(m['full'],m),5)/5+sv
P=sorted([r for r in rows if r['pass']],key=lambda r:-score(r))
for r in P[:15]:
    m=r['m']; print(r['addr'],r['style'],round(m['fills_day']),m['med_hold_s'],round(m['maker_share_notional'],2),round(m['full']['net']),round(m['full']['pf'] or 0,2),round(r['posw'],2),round(m['top3_share'],2),round(score(r),2))
# OOS: universe = activity-filtered wallets (hold/trades/active), rank on older half only
U=[r for r in rows if r['active'] and r['ok_hold'] and r['ok_trades'] and r['m']['old'] and r['m']['new'] and r['m']['old']['ndays']>=3 and r['m']['new']['ndays']>=3]
def old_key(r): m=r['m']; return (bps(m['old'],m), )
Us=sorted(U,key=lambda r:-bps(r['m']['old'],r['m']))
oos=dict(universe=len(U))
oos['old_pos']=sum(1 for r in U if r['m']['old']['net']>0)
oos['old_pos_new_pos']=sum(1 for r in U if r['m']['old']['net']>0 and r['m']['new']['net']>0)
oos['top5_old']=[(r['addr'],round(r['m']['old']['net']),round(r['m']['new']['net']),round(bps(r['m']['old'],r['m']),2),round(bps(r['m']['new'],r['m']),2)) for r in Us[:5]]
oos['top10_new_net']=sum(r['m']['new']['net'] for r in Us[:10]); oos['top10_new_pos']=sum(1 for r in Us[:10] if r['m']['new']['net']>0)
# Spearman
def rank(v): 
    o=sorted(range(len(v)),key=lambda i:v[i]); rk=[0]*len(v)
    for i,j in enumerate(o): rk[j]=i
    return rk
if len(U)>3:
    a=rank([bps(r['m']['old'],r['m']) for r in U]); b=rank([bps(r['m']['new'],r['m']) for r in U]); n=len(U)
    ma=st.mean(a); mb=st.mean(b)
    oos['spearman']=sum((x-ma)*(y-mb) for x,y in zip(a,b))/ (st.pstdev(a)*st.pstdev(b)*n)
# same for passing top picks
oos['picks_old_new']=[(r['addr'],round(r['m']['old']['net']),round(r['m']['new']['net'])) for r in P[:5]]
print(json.dumps(oos,indent=0))
json.dump(dict(picks=[dict(addr=r['addr'],style=r['style'],score=score(r)) for r in P],oos=oos,counts={k:sum(1 for r in rows if r[k]) for k in ('active','ok_hold','ok_trades','ok_net','ok_week','ok_conc','pass')},n=len(rows)),open(D+'ranking.json','w'),default=str)
