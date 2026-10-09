# T1b and T5 from candles; also flips.
import sys;sys.path.insert(0,'src')
from an_common import *
def run(series_list,label):
    mk=markets(series_list);mk=mk[~mk.thu_maint]
    out={}
    allc=[]
    for S in series_list:
        c=candle_wide(S,mk)
        allc.append(c)
    c=pd.concat(allc,ignore_index=True).merge(mk[["ticker","yes","month","coin"]],on="ticker")
    nwin=c.ticker.nunique()
    res=dict(nwin=nwin,months=sorted(c.month.unique()))
    # T1b: bid close bucket
    rows=[]
    edges=[0,.1,.3,.5,.7,.9,1.0001]
    c["bidb"]=pd.cut(c.yes_bid_close,edges,right=False,labels=PBN)
    t1b=c[c.yes_bid_close>0].groupby(["m","bidb"],observed=True).agg(n=("yes","size"),hit=("yes","mean"),bid=("yes_bid_close","mean")).reset_index()
    t1b["edge"]=t1b.hit-t1b.bid
    t1b["se"]=np.sqrt(t1b.hit*(1-t1b.hit)/t1b.n)
    res["t1b"]=t1b
    # monthly sign of edge for 0.7-.9 per m>=5
    sub=c[(c.yes_bid_close>=.7)&(c.yes_bid_close<.9)&(c.m>=5)&(c.m<=14)]
    mon=sub.assign(e=sub.yes-sub.yes_bid_close).groupby(["m","month"]).agg(n=("e","size"),edge=("e","mean")).reset_index()
    res["t1b_month"]=mon
    # T5: buy at ask: yes at yes_ask_close, no at 1-yes_bid_close
    y=c[(c.yes_ask_close>0)&(c.yes_ask_close<1)].copy()
    y["p"]=y.yes_ask_close;y["win"]=y.yes;y["side"]="yes"
    n=c[(c.yes_bid_close>0)&(c.yes_bid_close<1)].copy()
    n["p"]=1-n.yes_bid_close;n["win"]=1-n.yes;n["side"]="no"
    b=pd.concat([y[["ticker","m","p","win","month","side"]],n[["ticker","m","p","win","month","side"]]])
    b=b[b.m<=14]
    b["ev"]=b.win-b.p-fee(b.p)
    b["pb"]=pd.cut(b.p,edges,right=False,labels=PBN)
    t5=b.groupby(["pb","m"],observed=True).agg(n=("ev","size"),ev=("ev","mean"),sd=("ev","std")).reset_index()
    t5["z"]=t5.ev/(t5.sd/np.sqrt(t5.n))
    res["t5"]=t5
    res["t5_month"]=b.groupby(["pb","m","month"],observed=True).ev.agg(["size","mean"]).reset_index()
    # flips (minute 14 yes_ask_close)
    f=c[c.m==14]
    flip=((f.yes_ask_close>=.9)&(f.yes==0))|((f.yes_ask_close<=.1)&(f.yes==1))
    res["flips"]=int(flip.sum());res["flip_den"]=int(len(f))
    res["flip_by_ticker"]=set(f.ticker[flip])
    return res
if __name__=="__main__":
    r=run(["KXBTC15M"],"btc")
    print(r["nwin"],r["months"],r["flips"]);print(r["t1b"][r["t1b"].bidb=="[.7,.9)"].round(4).to_string())
