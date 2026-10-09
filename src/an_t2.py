import sys;sys.path.insert(0,'src')
from an_common import *
from an_t15 import candle_wide
def run(S="KXBTC15M"):
    mk=markets([S]);wins=pd.read_parquet(D+"prints_win.parquet")
    mk=mk[mk.ticker.isin(wins.ticker)&~mk.thu_maint]
    c=candle_wide(S,mk)
    # row starting at minute m (ends m+1): ask_open / bid_open
    piv=lambda col:c.pivot(index="ticker",columns="m",values=col)
    ask_o=piv("yes_ask_open");bid_o=piv("yes_bid_open");ask_c=piv("yes_ask_close");bid_c=piv("yes_bid_close")
    w=wins.merge(mk[["ticker","yes","month"]],on="ticker").set_index("ticker")
    w=w[w.index.isin(ask_o.index)]
    rows=[];best=None
    for a in (60,120,300,600):
        m=a//60+1   # candle row spanning [a, a+60]
        S_=w[f"S{a}"]/w.ct.replace(0,np.nan)
        for q in (0.10,0.20,0.30):
            thr=S_.abs().quantile(1-q);sel=w[(S_.abs()>=thr)&(S_!=0)]
            s=np.sign(S_[sel.index])
            win_side=np.where(s>0,sel.yes==1,sel.yes==0).astype(float)
            o1=win_side.mean();n=len(sel)
            # price: buy flow side at next-minute quote (open of row m)
            pr=np.where(s>0,ask_o.loc[sel.index,m],1-bid_o.loc[sel.index,m])
            pc=np.where(s>0,ask_c.loc[sel.index,m],1-bid_c.loc[sel.index,m])  # conservative: close of that minute
            ok=~np.isnan(pr)&(pr>0)&(pr<1)
            ev=(win_side-pr-fee(pr))[ok];evc=(win_side-pc-fee(pc))[ok&~np.isnan(pc)]
            z=ev.mean()/(ev.std()/np.sqrt(len(ev))) if len(ev)>2 else np.nan
            zc=evc.mean()/(evc.std()/np.sqrt(len(evc))) if len(evc)>2 else np.nan
            mon=pd.DataFrame(dict(m=sel.month.values[ok],e=ev)).groupby("m").e.agg(["size","mean"])
            rows.append(dict(a=a,q=q,n=n,hit=o1,hit_z=(o1-.5)/np.sqrt(.25/n) if n else np.nan,ev_c=ev.mean()*100 if len(ev) else np.nan,z=z,ev_close_c=evc.mean()*100 if len(evc) else np.nan,z_close=zc,mon=mon))
    return pd.DataFrame(rows)
if __name__=="__main__":
    r=run();print(r.drop(columns="mon").round(3).to_string())
