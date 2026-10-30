# Build aligned 1-minute panels (UTC grid) from data/leadlag/k1m -> data/leadlag/panel_{c,h,l,v}.parquet
import pandas as pd, numpy as np, glob, os
D='/home/user/trading-bot-server/data/leadlag'
T0=pd.Timestamp('2026-04-28',tz='UTC'); T1=pd.Timestamp('2026-10-28',tz='UTC')
idx=pd.date_range(T0,T1,freq='1min',inclusive='left')
P={k:{} for k in 'chlv'}
for f in sorted(glob.glob(D+'/k1m/*.parquet')):
    s=os.path.basename(f)[:-8]; df=pd.read_parquet(f)
    # timestamps: ms (spot 2025+ may be us) -> normalise
    t=df['t'].values; 
    if t.max()>1e14: t=t//1000
    df.index=pd.to_datetime(t,unit='ms',utc=True)
    df=df[~df.index.duplicated()].reindex(idx)
    for k,col in zip('chlv',['c','h','l','qv']): P[k][s]=df[col]
for k in 'chlv': pd.DataFrame(P[k]).to_parquet(f'{D}/panel_{k}.parquet')
c=pd.DataFrame(P['c']); v=pd.DataFrame(P['v'])
print(c.shape, 'nan close frac', c.isna().mean().round(4).to_dict() if c.isna().mean().max()>0 else 0)
tr=['TSLAUSDT','NVDAUSDT','XAUUSDT','XAGUSDT','CLUSDT','BZUSDT','SPYUSDT','QQQUSDT','XAUTUSDT']
r=np.log(c).diff()
for s in tr+['BTCUSDT','ETHUSDT']:
    print(s,'zero-vol',round((v[s]==0).mean(),4),'zero-ret',round((r[s]==0).mean(),3),'med qvol/min',round(v[s].median()))
