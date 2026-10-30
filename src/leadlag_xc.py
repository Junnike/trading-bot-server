# Test 1 (TradFi->crypto xcorr, day-block bootstrap) and Test 4 (crypto-crypto lead-lag graph)
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/home/user/trading-bot-server/src')
from leadlag_common import *
rng=np.random.default_rng(1)
c,v,h,l=load(); idx=c.index
L=np.log(c.astype('float64')); R=L.diff(); R[v==0]=np.nan   # stale (zero-volume) bar returns dropped
REG=regimes(idx)
alts=[s for s in c.columns if s not in EQ+CM+MAJ and s not in ('XAUT','MKR','TON')]
print('alts',len(alts),alts)
ALT=R[alts].mean(axis=1,skipna=True)          # equal-weight alt basket return
R['ALT']=ALT
LAGS=list(range(-10,11)); B=1000
W=rng.multinomial(NDAY,[1/NDAY]*NDAY,size=B).astype(np.float64)   # day-resample counts
def xc(xs,Y,mask):
    """xs: (T,) ; Y: (T,N); returns corr[lag,N], lo, hi, n[lag,N] ; pairs (x_t, y_{t+k}); both bars in regime & valid."""
    ix=(~np.isnan(xs))&mask; Ym=Y.copy(); iy=(~np.isnan(Ym))&mask[:,None]
    mx=xs[ix].mean(); sx=xs[ix].std()
    zx=np.where(ix,(xs-mx)/sx,0.0)
    my=np.nanmean(np.where(iy,Ym,np.nan),axis=0); sy=np.nanstd(np.where(iy,Ym,np.nan),axis=0)
    zy=np.where(iy,(Ym-my)/sy,0.0); iyf=iy.astype(np.float64); ixf=ix.astype(np.float64)
    out=np.zeros((len(LAGS),Y.shape[1])); lo=out.copy(); hi=out.copy(); nn=out.copy()
    for a,k in enumerate(LAGS):
        T=len(xs)
        if k>=0: sl_x=slice(0,T-k); sl_y=slice(k,T)
        else: sl_x=slice(-k,T); sl_y=slice(0,T+k)
        P=zx[sl_x,None]*zy[sl_y]; Nn=ixf[sl_x,None]*iyf[sl_y]
        Tn=P.shape[0]; d=np.arange(Tn)//M
        num=np.zeros((NDAY,Y.shape[1])); cnt=np.zeros((NDAY,Y.shape[1]))
        # day sums (days are contiguous blocks; trailing partial block handled by padding)
        pad=NDAY*M-Tn
        if pad>0: P=np.vstack([P,np.zeros((pad,P.shape[1]))]); Nn=np.vstack([Nn,np.zeros((pad,Nn.shape[1]))])
        num=P.reshape(NDAY,M,-1).sum(1); cnt=Nn.reshape(NDAY,M,-1).sum(1)
        tot=num.sum(0)/np.maximum(cnt.sum(0),1)
        bs=(W@num)/np.maximum(W@cnt,1)
        out[a]=tot; lo[a]=np.percentile(bs,2.5,axis=0); hi[a]=np.percentile(bs,97.5,axis=0); nn[a]=cnt.sum(0)
    return out,lo,hi,nn
rows=[]
targets=MAJ+['ALT']
tradfi=[a for a in EQ+CM if a in R.columns]
for a in tradfi:
    for rg,mask in regs_for(a,REG).items():
        tg=targets+(alts if a in HEAD else [])
        co,lo,hi,nn=xc(R[a].values,R[tg].values,mask)
        for j,t in enumerate(tg):
            for i,k in enumerate(LAGS): rows.append((a,t,rg,k,co[i,j],lo[i,j],hi[i,j],int(nn[i,j])))
    print('done',a,flush=True)
df=pd.DataFrame(rows,columns=['tradfi','target','regime','lag','corr','lo','hi','n']); df.to_csv(D+'/xc_tradfi_to_crypto.csv',index=False)
# ---- Test 4: crypto-crypto
coins=MAJ+alts
Z=R[coins].values.astype(np.float64); okc=~np.isnan(Z); mu=np.nanmean(Z,0); sd=np.nanstd(Z,0)
Z=np.where(okc,(Z-mu)/sd,0.0); Zr=Z.reshape(NDAY,M,-1); Or=okc.astype(np.float64).reshape(NDAY,M,-1)
NC=len(coins); K=list(range(-10,11)); num={}; cnt={}
for k in K:
    n_=np.zeros((NDAY,NC,NC)); c_=np.zeros((NDAY,NC,NC))
    for d in range(NDAY):
        z=Zr[d]; o=Or[d]
        if k>=0: a_,b_=z[:M-k],z[k:]; oa,ob=o[:M-k],o[k:]
        else: a_,b_=z[-k:],z[:M+k]; oa,ob=o[-k:],o[:M+k]
        n_[d]=a_.T@b_; c_[d]=oa.T@ob     # [i,j] = sum z_i[t] z_j[t+k]
    num[k]=n_; cnt[k]=c_
CK=np.stack([num[k].sum(0)/cnt[k].sum(0) for k in K])           # (lag,i,j) corr(i_t, j_{t+k})
np.save(D+'/cc_corr_lags.npy',CK)
pk=np.argmax(CK,axis=0); peaklag=np.array(K)[pk]
iu=np.triu_indices(NC,1)
print('pairs',len(iu[0]),'peak at lag0 frac',(peaklag[iu]==0).mean().round(3))
def asym(dsel,Wd):
    """lead strength of i over j = mean_{k=1..3} C_k[i,j] - mean_{k=1..3} C_k[j,i], with day weights Wd (B,D) or (D,)"""
    s=0
    for k in (1,2,3):
        nk=np.tensordot(Wd,num[k][dsel],axes=(-1,0)); ck=np.tensordot(Wd,cnt[k][dsel],axes=(-1,0))
        Ck=nk/np.maximum(ck,1); s=s+(Ck-np.swapaxes(Ck,-1,-2))/3
    return s
def full(dsel):
    Wd=np.ones(len(dsel)); return asym(dsel,Wd)
dall=np.arange(NDAY); dtr=dall[:TRAIN_DAYS]; doo=dall[TRAIN_DAYS:]
Bw=rng.multinomial(NDAY,[1/NDAY]*NDAY,size=300).astype(np.float64)
A_all=full(dall); A_b=np.stack([asym(dall,Bw[b]) for b in range(300)])
lo=np.percentile(A_b,2.5,axis=0); hi=np.percentile(A_b,97.5,axis=0)
A_tr=full(dtr); A_oo=full(doo)
# train-only bootstrap for edge selection
Bt=rng.multinomial(TRAIN_DAYS,[1/TRAIN_DAYS]*TRAIN_DAYS,size=300).astype(np.float64)
At_b=np.stack([asym(dtr,Bt[b]) for b in range(300)]); lot=np.percentile(At_b,2.5,axis=0); hit=np.percentile(At_b,97.5,axis=0)
edges=[]
for i in range(NC):
    for j in range(NC):
        if i==j: continue
        edges.append((coins[i],coins[j],A_all[i,j],lo[i,j],hi[i,j],A_tr[i,j],lot[i,j],hit[i,j],A_oo[i,j],peaklag[i,j]))
E=pd.DataFrame(edges,columns=['lead','lag','A_all','lo','hi','A_train','lo_tr','hi_tr','A_oos','peaklag_ij'])
E.to_csv(D+'/cc_edges.csv',index=False)
sig=E[(E.lo>0)]; sigtr=E[E.lo_tr>0]
print('edges ordered',len(E),'sig(all, CI>0)',len(sig),'sig train',len(sigtr))
print('train-sig edges with OOS A>0:',(sigtr.A_oos>0).mean().round(3),'n',len(sigtr))
sc=E.assign(s=(E.lo>0).astype(int)-(E.hi<0).astype(int)).groupby('lead').s.sum()
sc2=E.groupby('lead').A_all.mean()
Rk=pd.DataFrame({'net_edges':sc,'mean_A':sc2}).sort_values('net_edges',ascending=False)
Rk.to_csv(D+'/cc_leader_rank.csv'); print(Rk.head(12)); print(Rk.tail(6))
# peak lag among nonzero: pair summary for majors
pl=[(coins[i],coins[j],int(peaklag[i,j])) for i in range(3) for j in range(NC) if i!=j]
pd.DataFrame(pl,columns=['i','j','peak_lag']).to_csv(D+'/cc_peaklag_majors.csv',index=False)
print(pd.Series([p[2] for p in pl]).value_counts().sort_index().to_dict())
