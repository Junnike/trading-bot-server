# Monthly signs / event days for chosen rules (same event logic as leadlag_rules.py)
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/home/user/trading-bot-server/src')
from leadlag_common import *
c,v,hh,ll=load(); idx=c.index; T=len(idx)
L=np.log(c.astype('float64')); R=L.diff(); R[v==0]=np.nan
REG=regimes(idx); day=(np.arange(T)//M).astype(int); trainT=day<TRAIN_DAYS
SPECS=[('CL','closed','ETH',5,99,15,-1),('CL','closed','SOL',5,99,15,-1),('TSLA','open','ETH',1,99,15,-1),('TSLA','open','SOL',1,99,15,-1),('BZ','closed','SOL',5,99,5,-1),('BTC','all','IMX',1,95,1,1)]
out=[]
for a,rg,tg,w,q,h,s_ in SPECS:
    mask=regs_for(a,REG)[rg]; xr=R[a].values; okx=(~np.isnan(xr))&mask
    cs=np.concatenate([[0],np.cumsum(np.where(okx,xr,0))]); xw=np.full(T,np.nan); xw[w:]=cs[w+1:]-cs[1:T+1-w]
    vs=winvalid(okx,-(w-1),h)&~np.isnan(xw); thr=np.quantile(np.abs(xw[vs&trainT]),q/100)
    ev0=vs&(np.abs(xw)>thr); prev=np.zeros(T,bool)
    for k in range(1,6): prev[k:]|=ev0[:T-k]
    ti=np.nonzero(ev0&~prev)[0]; ti=ti[ti+h+2<T]; sg=np.sign(xw[ti]); pos=s_*sg
    C=c[tg].values; g=pos*np.log(C[ti+h]/C[ti])*1e4
    fill=np.where(pos>0,ll[tg].values[ti+1]<C[ti],hh[tg].values[ti+1]>C[ti]); mk=np.where(fill,g-2,0)
    df=pd.DataFrame({'m':idx[ti].strftime('%Y-%m'),'d':day[ti],'gross':g,'taker':g-9,'maker':mk})
    mm=df.groupby('m').agg(n=('gross','size'),days=('d','nunique'),gross=('gross','mean'),taker=('taker','mean'),maker=('maker','mean')).round(1)
    print(a,rg,tg,w,q,h,s_,'thr_bp',round(thr*1e4,1),'events',len(df),'days',df.d.nunique()); print(mm.to_string())
    mm['spec']=f'{a}-{rg}-{tg}-w{w}-q{q}-h{h}'; out.append(mm.reset_index())
pd.concat(out).to_csv(D+'/best_monthly.csv',index=False)
