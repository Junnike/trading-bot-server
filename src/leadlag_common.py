import numpy as np, pandas as pd
D='/home/user/trading-bot-server/data/leadlag'
NDAY=183; M=1440; TRAIN_DAYS=122   # first 2/3 = 2026-04-28..2026-08-27 ; OOS = 2026-08-28..2026-10-27
EQ=['TSLA','NVDA','SPY','QQQ','AAPL','AMZN','COIN','MSTR','META','GOOGL','MSFT','HOOD','CRCL','PLTR','INTC','EWY']
CM=['XAU','XAG','CL','BZ','XPT','XPD','NATGAS','XAUT']
HEAD=['TSLA','NVDA','SPY','QQQ','XAU','XAG','CL','BZ']     # headline TradFi set (tested in full)
MAJ=['BTC','ETH','SOL']
HOL=['2026-05-25','2026-06-19','2026-07-03','2026-09-07']  # NYSE closed days in window
def load():
    c=pd.read_parquet(D+'/panel_c.parquet'); v=pd.read_parquet(D+'/panel_v.parquet')
    h=pd.read_parquet(D+'/panel_h.parquet'); l=pd.read_parquet(D+'/panel_l.parquet')
    for x in (c,v,h,l): x.columns=[s[:-4] for s in x.columns]
    return c,v,h,l
def regimes(idx):
    """bool arrays per regime name, by bar start time (UTC)."""
    dow=idx.dayofweek.values; tod=(idx.hour*60+idx.minute).values
    hol=np.isin(idx.strftime('%Y-%m-%d').values,HOL)
    wk=dow<5
    eq_open=wk&~hol&(tod>=13*60+30)&(tod<20*60)
    eq_weekend=dow>=5
    eq_closed=~eq_open&~eq_weekend
    cme_closed=((dow==4)&(tod>=21*60))|(dow==5)|((dow==6)&(tod<22*60))|((dow<4)&(tod>=21*60)&(tod<22*60))
    return {'EQ':{'open':eq_open,'weekend':eq_weekend,'closed_wk':eq_closed},
            'CM':{'open':~cme_closed,'closed':cme_closed},
            'ALL':{'all':np.ones(len(idx),bool)}}
def regs_for(a,R):
    return R['EQ'] if a in EQ else R['CM'] if a in CM else R['ALL']
def clmean(vals,days):
    """mean and day-cluster z (ratio estimator)."""
    n=len(vals)
    if n<3: return np.nan,np.nan,n
    S=np.bincount(days,weights=vals,minlength=NDAY); N=np.bincount(days,minlength=NDAY)
    mu=S.sum()/N.sum(); e=S-mu*N
    se=np.sqrt((e**2).sum())/N.sum()
    return mu,(mu/se if se>0 else np.nan),n
def winvalid(ok,lo,hi):
    """ok: bool per bar. True at t if ok[t+lo..t+hi] all True (lo<=0<=hi offsets)."""
    cs=np.concatenate([[0],np.cumsum(ok.astype(np.int32))]); T=len(ok); out=np.zeros(T,bool)
    a=np.arange(T)+lo; b=np.arange(T)+hi
    inb=(a>=0)&(b<T)
    out[inb]=(cs[b[inb]+1]-cs[a[inb]])==(hi-lo+1)
    return out
