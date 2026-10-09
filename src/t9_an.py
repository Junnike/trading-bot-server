import pandas as pd, numpy as np, json, glob
O='data/t9/'; rng=np.random.default_rng(9)
btc={i:pd.read_parquet(O+f'btc_{i}.parquet').set_index('t') for i in ['15m','1h']}
oil={(a,i):pd.read_parquet(O+f'oil_{a}_{i}.parquet')['Close'].dropna() for a in ['CL','BZ'] for i in ['15m','1h']}
FREQ={'15m':'15min','1h':'1h'}
def boot_hit(day,hit,B=2000):
    g=pd.DataFrame({'d':day,'h':hit}).groupby('d').h.agg(['sum','count']).values
    idx=rng.integers(0,len(g),(B,len(g)))
    s=g[idx,0].sum(1)/g[idx,1].sum(1)
    return s.std()
def zhit(day,hit,base=0.5):
    sd=boot_hit(day,hit); m=np.mean(hit); return m,(m-base)/sd if sd>0 else np.nan
def build(a,i):
    f=FREQ[i]; b=btc[i]; o=oil[(a,i)]
    o=o[~o.index.duplicated()]
    start=max(b.index.min(),o.index.min()); 
    grid=pd.date_range(start.ceil(f),min(b.index.max(),o.index.max()),freq=f,tz='UTC')
    og=o.reindex(grid)  # oil candle opened at t, closed at t+I; exact grid stamps only
    r1=np.log(og/og.shift(1))   # return of candle t (needs candle t-1 too)
    D=pd.DataFrame(index=grid); D['bo']=b.o.reindex(grid); D['bc']=b.c.reindex(grid)
    D['bret']=D.bc/D.bo-1
    D['bprev']=np.sign(D.bret.shift(1))
    D['oret1']=r1.shift(1)          # oil candle opened T-I, closed at T
    sig=r1.dropna().rolling(100).std()
    D['sig']=sig.reindex(grid).shift(1)  # sigma at candle T-I over last 100 candles (contiguous series)
    D['z']=D.oret1/D.sig
    ks=[1,2,4] if i=='15m' else [1,2]
    for k in ks: D[f'cum{k}']=np.log(og.shift(1)/og.shift(k+1))
    D['y']=np.sign(D.bret)
    tot=len(D.dropna(subset=['bo','bc']))
    D=D.dropna(subset=['bo','bc','oret1','bprev']); D=D[(D.y!=0)]
    return D,tot
bucket=lambda z: pd.cut(z.abs(),[0,.5,1,2,np.inf],right=False,labels=['0-.5','.5-1','1-2','2+'])
out=[];res={}
# Table1
def xc(a):
    rows=[]
    for iv,fr in [('15m','15min'),('1h','1h'),('4h','4h'),('1d','1D')]:
        src='15m' if iv=='15m' else '1h'
        b=btc[src].c; o=oil[(a,src)]; o=o[~o.index.duplicated()]
        rb=b.resample(fr,closed='left',label='left').last(); 
        ro=o.resample(fr,closed='left',label='left').last()
        if iv!='15m' and iv!='1h':
            idx=pd.date_range(max(rb.index.min(),ro.index.min()),min(rb.index.max(),ro.index.max()),freq=fr,tz='UTC')
        else: idx=pd.date_range(max(rb.index.min(),ro.index.min()).ceil(fr),min(rb.index.max(),ro.index.max()),freq=fr,tz='UTC')
        rb=np.log(rb.reindex(idx)).diff(); ro=np.log(ro.reindex(idx)).diff()
        row={'iv':iv,'oil':a}
        for k in range(-4,5):
            x=pd.concat([rb,ro.shift(k)],axis=1).dropna()   # k>0: oil k candles earlier leads
            row[k]=round(x.corr().iloc[0,1],3); row['n']=len(x)
        rows.append(row)
    return rows
T1=pd.DataFrame(xc('CL')+xc('BZ')); print(T1.to_string())
T1.to_csv(O+'t1.csv')
# Hit tables
cells=[]
for a in ['CL','BZ']:
  for i in ['15m','1h']:
    D,tot=build(a,i); excl=1-len(D)/tot
    print(a,i,'btc candles in oil span',tot,'usable',len(D),'excluded share %.3f'%excl)
    D['day']=D.index.floor('D'); D['bk']=bucket(D.z)
    D['sig_dir']=-np.sign(D.oret1); D=D[D.sig_dir!=0]
    D['hit']=(D.sig_dir==D.y).astype(int)
    for pv,name in [(None,'all'),(1,'prev+'),(-1,'prev-')]:
      for bk in [None]+list(D.bk.cat.categories):
        s=D
        if pv is not None: s=s[s.bprev==pv]
        if bk is not None: s=s[s.bk==bk]
        if len(s)<30: continue
        h,z=zhit(s.day,s.hit.values)
        base=(s.bprev==s.y).mean()
        pu_ou=(s[s.oret1>0].y>0).mean(); pu_od=(s[s.oret1<0].y>0).mean()
        cells.append(dict(oil=a,iv=i,kind='S2',bk=bk or 'all',prev=name,n=len(s),days=s.day.nunique(),hit_neg=h,z_neg=z,hit_opp=1-h,z_opp=-z,base_prev=base,P_up_oilup=pu_ou,P_up_oildn=pu_od))
    for k in ([1,2,4] if i=='15m' else [1,2]):
      s=D.copy(); s['sd']=-np.sign(s[f'cum{k}']); s=s.dropna(subset=['sd']); s=s[s.sd!=0]; s['h']=(s.sd==s.y).astype(int)
      for pv,name in [(None,'all'),(1,'prev+'),(-1,'prev-')]:
        t=s if pv is None else s[s.bprev==pv]
        h,z=zhit(t.day,t.h.values)
        cells.append(dict(oil=a,iv=i,kind=f'S3k{k}',bk='all',prev=name,n=len(t),days=t.day.nunique(),hit_neg=h,z_neg=z,hit_opp=1-h,z_opp=-z))
    D.to_parquet(O+f'D_{a}_{i}.parquet')
    res[f'{a}_{i}']=dict(tot=tot,usable=len(D),excl=excl)
C=pd.DataFrame(cells); C.to_csv(O+'t2.csv'); 
pd.set_option('display.width',250)
print(C[C.oil=='CL'].round(3).to_string())
json.dump(res,open(O+'excl.json','w'))
