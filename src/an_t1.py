import sys,glob;sys.path.insert(0,'src')
from an_common import *
def vol_hour(mk):
    fs=sorted(glob.glob(D+"binance/BTCUSDT-1s-*.parquet"))
    if not fs: return None
    b=pd.concat([pd.read_parquet(f,columns=["t","c"]) for f in fs]).drop_duplicates("t").sort_values("t")
    t0=int(b.t.iloc[0]);n=int(b.t.iloc[-1])-t0+1
    px=np.full(n,np.nan);px[(b.t.values-t0)]=b.c.values
    px=pd.Series(px).ffill().values
    r2=np.zeros(n);r=np.diff(np.log(px));r2[1:]=r*r
    cs=np.concatenate([[0],np.cumsum(r2)])
    o=mk.open_ts.values-t0
    ok=(o-3600>=0)&(o<n)
    v=np.full(len(mk),np.nan);v[ok]=np.sqrt(cs[o[ok]]-cs[o[ok]-3600])
    return pd.Series(v,index=mk.ticker.values)
def run(coin_series="KXBTC15M",flips=None):
    mk=markets([coin_series]);mk0=mk
    wins=pd.read_parquet(D+"prints_win.parquet");cells=pd.read_parquet(D+"prints_cells.parquet")
    mk=mk[mk.ticker.isin(wins.ticker)]
    thu=int(mk.thu_maint.sum());mk=mk[~mk.thu_maint]
    cells=cells[cells.ticker.isin(mk.ticker)].merge(mk[["ticker","month","week","day"]],on="ticker")
    cells["num"]=cells.cw-cells.cp-cells.cf   # taker pnl (dollars)
    out=dict(nwin=len(mk),thu_excl=thu,months=sorted(mk.month.unique()),
             blk_share=float(wins.blk_ct.sum()/wins.ct.sum()) if wins.ct.sum() else np.nan)
    # per price bucket pooled and per age bucket (cells ab 0..4)
    def agg(g):
        pt=g.groupby("ticker").agg(num=("num","sum"),ct=("ct","sum"),mg=("cmg","sum"),n=("n","sum"))
        mean,z=boot_z(pt.num.values,pt.ct.values)
        mm,mz=boot_z(pt.mg.values,pt.ct.values)
        return pd.Series(dict(nwin=len(pt),n=int(pt.n.sum()),ct=pt.ct.sum(),taker_pnl_c=mean*100,z=z,maker_gross_c=mm*100,mk_z=mz))
    inr=cells[(cells.ab>=0)&(cells.ab<=4)]
    out["by_pb"]=inr.groupby("pb").apply(agg,include_groups=False)
    low=inr[inr.pb<=1]   # p<0.3
    out["low_by_ab"]=low.groupby("ab").apply(agg,include_groups=False)
    out["low_by_month"]=low.groupby("month").apply(agg,include_groups=False)
    out["low_all"]=agg(low)
    out["cells_month_pb_ab"]=inr.groupby(["month","pb","ab"]).apply(agg,include_groups=False)
    # weekly positivity of maker gross (low-p takers)
    wk=low.groupby("week").agg(mg=("cmg","sum"),ct=("ct","sum"),nw=("ticker","nunique"))
    wk["g"]=wk.mg/wk.ct*100;out["weeks"]=wk
    out["wk_pos"]=float((wk.g>0).mean());out["nweeks"]=len(wk)
    # FIFO scenarios, window-level realized, cap 200 ct/window
    pw=low.groupby("ticker").agg(mg=("cmg","sum"),ct=("ct","sum"))
    pw=pw.reindex(mk.ticker).fillna(0)
    ndays=mk0.day.nunique(); wpd=len(mk0[mk0.open_ts>=mk.open_ts.min()])/max(1,(mk0.open_ts.max()-mk.open_ts.min())/86400)
    out["fifo"]={}
    for sh in (0.238,0.10,0.05):
        f=np.minimum(1.0,200/np.maximum(pw.ct.values*sh,1e-9))*sh   # fraction of taker flow captured
        f=np.where(pw.ct.values*sh>0,f,0)
        pnl=(f*pw.mg.values)   # dollars per window (maker fee 0), mg=sum ct*(p-win)
        out["fifo"][sh]=dict(usd_day=float(pnl.mean()*wpd),usd_total_sample=float(pnl.sum()),wpd=float(wpd))
    # vol quartiles
    v=vol_hour(mk)
    if v is not None:
        mk=mk.assign(vol=mk.ticker.map(v));mk=mk[mk.vol.notna()]
        mk["vq"]=pd.qcut(mk.vol,4,labels=["Q1","Q2","Q3","Q4"])
        lw=low.merge(mk[["ticker","vq"]],on="ticker")
        out["low_by_vq"]=lw.groupby("vq",observed=True).apply(agg,include_groups=False)
    else: out["low_by_vq"]=None
    if flips is not None:
        fl=low.assign(flip=low.ticker.isin(flips))
        out["flip_n"]=int(len(flips&set(mk0.ticker[mk0.ticker.isin(wins.ticker)])))
        out["low_noflip"]=agg(fl[~fl.flip]);out["low_flip"]=agg(fl[fl.flip]) if fl.flip.any() else None
    return out
if __name__=="__main__":
    o=run()
    for k,v in o.items(): print(k);print(v)
