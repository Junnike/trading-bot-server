# Tests 2 (predictive regression), 3 (event study), 5 (tradability, OOS). Train = first 122 days, OOS = last 61.
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/home/user/trading-bot-server/src')
from leadlag_common import *
c,v,hh,ll=load(); idx=c.index; T=len(idx)
L=np.log(c.astype('float64')); R=L.diff(); R[v==0]=np.nan
REG=regimes(idx); day=(np.arange(T)//M).astype(int); trainT=day<TRAIN_DAYS
alts=[s for s in c.columns if s not in EQ+CM+MAJ and s not in ('MKR','TON')]
coins=MAJ+alts
Lv={s:L[s].values for s in c.columns}; Hv={s:hh[s].values for s in c.columns}; Lo={s:ll[s].values for s in c.columns}; Cv={s:c[s].values for s in c.columns}
def sh(a,k):  # a[t+k] aligned at t (NaN beyond end)
    o=np.full(T,np.nan); 
    if k>=0: o[:T-k]=a[k:]
    else: o[-k:]=a[:T+k]
    return o
TAKER=9.0; MAKER_EXIT=2.0   # bp round trip (0.045%x2) ; maker entry 0 + taker exit 0.02%
regrows=[]; rulerows=[]
leaders=[(a,rg,m) for a in HEAD for rg,m in regs_for(a,REG).items()]+[(a,'all',REG['ALL']['all']) for a in MAJ]
for a,rg,mask in leaders:
    xr=R[a].values; okx=(~np.isnan(xr))&mask
    xz=np.where(okx,xr,0.0); cs=np.concatenate([[0],np.cumsum(xz)])
    targets=(MAJ if a in HEAD else [s for s in coins if s!=a])
    for w in (1,3,5):
        xw=np.full(T,np.nan); xw[w:]=cs[w+1:]-cs[1:T+1-w]   # sum r[t-w+1..t]
        for h in (1,3,5,15):
            vs=winvalid(okx,-(w-1),h)
            if h<15 and True:
                pass
            for tg in targets:
                y=sh(Lv[tg],h)-Lv[tg]            # log ret c[t]->c[t+h] (bar closes)
                ok=vs&~np.isnan(y)&~np.isnan(xw)
                # ---- regression (h in 1,3,5 ; w in 1,3,5)
                if h<=5:
                    for part,pm in (('train',trainT),('oos',~trainT)):
                        s=ok&pm; xs=xw[s]*1e4; ys=y[s]*1e4; d=day[s]
                        if len(xs)<500: continue
                        xm=xs-xs.mean(); ym=ys-ys.mean(); sxx=np.bincount(d,xm*xm,NDAY).sum(); b=(xm*ym).sum()/sxx
                        u=np.bincount(d,xm*(ym-b*xm),NDAY); se=np.sqrt((u**2).sum())/sxx
                        agree=(np.sign(xs)==np.sign(ys))[(xs!=0)&(ys!=0)]; dd=d[(xs!=0)&(ys!=0)]
                        hm,hz,hn=clmean(agree.astype(float)-0.5,dd)
                        regrows.append((a,rg,tg,w,h,part,len(xs),b,b/se,0.5+hm,hz))
    # ---- events/rules (w in 1,5 ; q 95,99 ; h 1,3,5,15)
    for w in (1,5):
        xw=np.full(T,np.nan); xw[w:]=cs[w+1:]-cs[1:T+1-w]
        for h in (1,3,5,15):
            vs=winvalid(okx,-(w-1),h)&~np.isnan(xw)
            for q in (95,99):
                thr=np.quantile(np.abs(xw[vs&trainT]),q/100)
                ev0=vs&(np.abs(xw)>thr)
                prev=np.zeros(T,bool)
                for k in range(1,6): prev[k:]|=ev0[:T-k]
                ev=ev0&~prev; ti=np.nonzero(ev)[0]; ti=ti[ti+h+2<T]
                sg=np.sign(xw[ti]); dti=day[ti]
                for tg in targets:
                    Ct=Cv[tg]; gross=sg*(np.log(Ct[ti+h]/Ct[ti]))*1e4
                    tr=dti<TRAIN_DAYS; 
                    if tr.sum()<20 or (~tr).sum()<5: continue
                    mu_tr=gross[tr].mean(); s_=1.0 if mu_tr>=0 else -1.0
                    g=s_*gross
                    pos=s_*sg                                    # +1 long target
                    fill=np.where(pos>0,Lo[tg][ti+1]<Ct[ti],Hv[tg][ti+1]>Ct[ti])
                    mk=np.where(fill,g-MAKER_EXIT,0.0)
                    gd=pos*np.log(Ct[ti+1+h]/Ct[ti+1])*1e4 if (ti+1+h<T).all() else np.full(len(ti),np.nan)
                    rec=[a,rg,tg,w,q,h,int(s_)]
                    for part,pm in (('train',tr),('oos',~tr)):
                        m1,z1,n1=clmean(g[pm],dti[pm]); m2,z2,_=clmean((g-TAKER)[pm],dti[pm]); m3,z3,_=clmean(mk[pm],dti[pm])
                        m4,_,_=clmean(gd[pm][~np.isnan(gd[pm])],dti[pm][~np.isnan(gd[pm])])
                        rec+= [n1,m1,z1,m2,z2,m3,z3,fill[pm].mean(),m4]
                    rulerows.append(rec)
    print('done',a,rg,flush=True)
RG=pd.DataFrame(regrows,columns=['lead','regime','target','w','h','part','n','beta','z','hit','hit_z']); RG.to_csv(D+'/reg_results.csv',index=False)
cols=['lead','regime','target','w','q','h','side']
for p in ('tr','oo'): cols+=[f'n_{p}',f'gross_{p}',f'z_{p}',f'taker_{p}',f'tz_{p}',f'maker_{p}',f'mz_{p}',f'fill_{p}',f'delay1_{p}']
RL=pd.DataFrame(rulerows,columns=cols); RL.to_csv(D+'/rule_results.csv',index=False)
print(len(RG),len(RL))
