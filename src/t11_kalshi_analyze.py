import json,math,collections
import numpy as np,pandas as pd
from scipy.stats import norm
D='data/t11_kalshi/'
rows=[json.loads(l) for l in open(D+'entries.jsonl')]
skips=collections.Counter(r['skip'] for r in rows if 'skip' in r)
E=[r for r in rows if 'skip' not in r]
OTHER={'Culture','Education','Business','Exotics','Social','Transportation','Companies','Health'}
MAXAGE=6*3600; HOLD=pd.Timestamp('2026-08-10',tz='UTC').timestamp()
obs=[]
for r in E:
    cat='Other' if r['c'] in OTHER else r['c']
    for f in(10,50,90):
        a,b,ag=r[f'ask{f}'],r[f'bid{f}'],r[f'age{f}']
        if ag is None or ag>MAXAGE: continue
        for side,p,win in(('YES',a,r['res']=='yes'),('NO',None if b is None else 1-b,r['res']=='no')):
            if p is None or p<0.01 or p>0.99: continue
            p=round(p,4); fee=math.ceil(0.07*p*(1-p)*100-1e-9)/100
            obs.append((cat,r['c'],r['t'],f,side,p,int(win),fee,r['cl'],r['vol'],(a-b) if (a is not None and b is not None) else np.nan,(a+b)/2 if side=='YES' else 1-(a+b)/2))
df=pd.DataFrame(obs,columns=['cat','rawcat','t','f','side','p','win','fee','cl','vol','spr','mid'])
df['ev']=(df.win-df.p-df.fee)*100
df['date']=pd.to_datetime(df.cl,unit='s',utc=True).dt.strftime('%Y-%m-%d'); df['month']=df.date.str[:7]
df['hold']=df.cl>=HOLD
bk=[0,.05,.10,.20,.30,.50,.70,.90,.95,1.0001]; lab=['0-5','5-10','10-20','20-30','30-50','50-70','70-90','90-95','95-100']
df['b']=pd.cut(df.p,bk,labels=lab,right=False)
rng=np.random.default_rng(1)
def boot(g,B=2000):
    s=g.groupby('date').ev.agg(['sum','count']); S=s['sum'].values;N=s['count'].values
    if len(S)<3: return float('nan')
    idx=rng.integers(0,len(S),(B,len(S)));m=S[idx].sum(1)/N[idx].sum(1)
    return S.sum()/N.sum()/m.std() if m.std()>0 else float('nan')
df['z3']=pd.cut(df.p,[0,.2,.7,1.0001],labels=['L0-20','M20-70','F70-100'],right=False)
df['allc']='ALL'
res=[]
for col,cats in(('b',None),('z3',None)):
  for (cat,b),g in list(df.groupby(['cat',col],observed=True))+list(df.groupby(['allc',col],observed=True)):
    tr=g[~g.hold];ho=g[g.hold]
    if len(tr)==0: continue
    mo=tr.groupby('month').ev.agg(['mean','count']);mo=mo[mo['count']>=5]
    res.append(dict(cat=cat,bucket=b,n=tr.t.nunique(),nobs=len(tr),yesfrac=(tr.side=='YES').mean(),win=tr.win.mean(),price=tr.p.mean(),ev=tr.ev.mean(),z=boot(tr) if tr.t.nunique()>=200 else np.nan,
        mpos=int((mo['mean']>0).sum()),mtot=len(mo),n_hold=len(ho),ev_hold=ho.ev.mean() if len(ho) else np.nan,ndates=tr.date.nunique()))
R=pd.DataFrame(res); R.to_csv(D+'cells.csv',index=False)
T=R[R.n>=200]; NC=len(T); thr=norm.ppf(1-0.025/NC)
T=T.assign(alive=(T.z>=thr)&(T.mpos>=0.6*T.mtot)&(T.ev_hold>0)&(T.ev>=1.0)&(T.mtot>=3))
print('markets with candles',len(E),'skips',dict(skips),'obs',len(df),'cells all',len(R),'cells n>=200',NC,'bonf z thr',round(thr,2))
print('alive:',int(T.alive.sum()))
print('cats',df.groupby('cat').t.nunique().to_dict())
print('dates',df.date.min(),df.date.max(),'train obs',int((~df.hold).sum()),'hold obs',int(df.hold.sum()))
print('months',df.month.value_counts().sort_index().to_dict())
print('per-venue max z',round(T.z.max(),2),'min z',round(T.z.min(),2),'cells z>=2:',int((T.z>=2).sum()),'expected by chance at 2.0 ~',round(NC*0.0228,1))
pd.set_option('display.width',250)
cols=['cat','bucket','n','nobs','yesfrac','win','price','ev','z','mpos','mtot','ev_hold','n_hold']
print(T.sort_values('z',ascending=False).head(19)[cols].round(3).to_string(index=False))
print(T.sort_values('z').head(5)[cols].round(3).to_string(index=False))
# pooled bucket view (all categories, YES+NO, train)
tr=df[~df.hold]
pb=tr.groupby('b',observed=True).agg(n=('ev','size'),win=('win','mean'),price=('p','mean'),ev=('ev','mean'))
print(pb.round(3).to_string())
pc=tr.groupby(['cat']).agg(n=('ev','size'),ev=('ev','mean'),mk=('t','nunique'))
print(pc.round(2).to_string())
print('median quote age(h)',round(np.median([r[f'age{f}'] for r in E for f in(10,50,90) if r[f'age{f}'] is not None])/3600,2))
T.to_csv(D+'cells_tested.csv',index=False)

tr=df[~df.hold].copy(); ho=df[df.hold]
print('--- sensitivity (not counted as cells): by spread, train, pooled categories')
for lo,hi in((0,.03),(.03,.10),(.10,1.01)):
    g=tr[(tr.spr>=lo)&(tr.spr<hi)]
    print(f'spread[{lo},{hi}) markets={g.t.nunique()} obs={len(g)} EV={g.ev.mean():.2f}c z={boot(g):.1f} gross_vs_mid={((g.win-g.mid).mean()*100):.2f}c')
g=tr[tr.spr<.03]
for b,gg in g.groupby('z3',observed=True): print('tight',b,gg.t.nunique(),len(gg),round(gg.ev.mean(),2),round(boot(gg),1),'gross_mid',round((gg.win-gg.mid).mean()*100,2),'hold ev',round(ho[(ho.spr<.03)&(ho.z3==b)].ev.mean(),2),'nhold',int(((ho.spr<.03)&(ho.z3==b)).sum()))
for b,gg in g.groupby('b',observed=True): print('tight',b,gg.t.nunique(),len(gg),round(gg.ev.mean(),2),round(boot(gg),1),'gross_mid',round((gg.win-gg.mid).mean()*100,2))
print('by f (train, all):',{int(f):round(x.ev.mean(),2) for f,x in tr.groupby('f')}, 'by side',{k:round(x.ev.mean(),2) for k,x in tr.groupby('side')})
print('median spread',tr.spr.median())
