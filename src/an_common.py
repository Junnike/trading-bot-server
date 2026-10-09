import json,glob,os
import numpy as np,pandas as pd
D="data/"
def markets(series=None):
    rows=[]
    for f in sorted(glob.glob(D+"markets_*.jsonl")):
        S=f.split("markets_")[1][:-6]
        if series and S not in series: continue
        for l in open(f):
            m=json.loads(l)
            rows.append((m["ticker"],S,m["open_time"],m["close_time"],m["result"],m.get("floor_strike")))
    d=pd.DataFrame(rows,columns=["ticker","series","open_time","close_time","result","strike"])
    d["open_ts"]=(pd.to_datetime(d.open_time,utc=True)-pd.Timestamp(0,tz="UTC"))//pd.Timedelta(seconds=1)
    d["close_ts"]=(pd.to_datetime(d.close_time,utc=True)-pd.Timestamp(0,tz="UTC"))//pd.Timedelta(seconds=1)
    dt=pd.to_datetime(d.open_ts,unit="s",utc=True)
    d["month"]=dt.dt.strftime("%Y-%m");d["week"]=dt.dt.strftime("%G-W%V");d["day"]=dt.dt.strftime("%Y-%m-%d")
    d["thu_maint"]=(dt.dt.weekday==3)&(dt.dt.hour>=7)&(dt.dt.hour<9)
    d["yes"]=(d.result=="yes").astype(int)
    d["coin"]=d.series.str[2:-3]
    return d
def candles(S):
    fs=sorted(glob.glob(D+f"candle_parts/{S}_*.parquet"))
    if not fs: return pd.DataFrame()
    c=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True)
    return c
def candle_wide(S,mk):
    """per-ticker x minute(1..15) arrays"""
    c=candles(S);c=c[c.end_ts.notna()].drop_duplicates(["ticker","end_ts"])
    c=c.merge(mk[["ticker","open_ts"]],on="ticker")
    c["m"]=((c.end_ts-c.open_ts)//60).astype(int)
    c=c[(c.m>=1)&(c.m<=15)]
    return c
def boot_z(num,ct,B=2000,seed=1):
    """cluster bootstrap over windows: stat = sum(num)/sum(ct)."""
    n=len(num)
    if n<2 or ct.sum()==0: return np.nan,np.nan
    rng=np.random.default_rng(seed);st=np.empty(B)
    for i in range(B):
        w=np.bincount(rng.integers(0,n,n),minlength=n)
        den=w@ct;st[i]=(w@num)/den if den>0 else np.nan
    mean=num.sum()/ct.sum();sd=np.nanstd(st)
    return mean,(mean/sd if sd>0 else np.nan)
def fee(p): return 0.07*p*(1-p)
PBN=["[0,.1)","[.1,.3)","[.3,.5)","[.5,.7)","[.7,.9)","[.9,1]"];ABN=["[0,60)","[60,120)","[120,300)","[300,600)","[600,900]"]
