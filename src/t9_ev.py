import pandas as pd, numpy as np, json, glob
O='data/t9/'; rng=np.random.default_rng(5)
M=[json.loads(l) for l in open('data/markets_KXBTC15M.jsonl')]
M=pd.DataFrame([{k:m[k] for k in('ticker','open_time','result')} for m in M]); M['open']=pd.to_datetime(M.open_time,utc=True).dt.as_unit('ns')
M=M[M.result.isin(['yes','no'])].drop_duplicates('ticker')
C=pd.concat([pd.read_parquet(f) for f in glob.glob('data/candle_parts/KXBTC15M_*.parquet')])
C=C.merge(M,on='ticker'); C['off']=C.end_ts-(C.open.dt.as_unit('s').astype('int64'))
print('candle windows',C.ticker.nunique(),'offset values',sorted(C.off.unique())[:4])
c1=C[C.off==60].set_index('open')[['yes_bid_close','yes_ask_close']]
D=pd.read_parquet(O+'D_CL_15m.parquet'); D.index=D.index.as_unit('ns'); D['sd']=-np.sign(D.oret1)
D=D.join(M.set_index('open')[['result']],how='left')
print('oil-span usable',len(D),'with Kalshi result',D.result.notna().sum(),'with minute1 candle',D.index.isin(c1.index).sum())
def z_ev(day,ev,B=2000):
    g=pd.DataFrame({'d':day,'e':ev}).groupby('d').e.agg(['sum','count']).values
    idx=rng.integers(0,len(g),(B,len(g))); s=g[idx,0].sum(1)/g[idx,1].sum(1); return ev.mean()/s.std() if s.std()>0 else np.nan
def ev_tab(S,label):
    S=S.copy(); S['win']=((S.sd>0)==(S.result=='yes')).astype(int)
    thu=(S.index.dayofweek==3)&(S.index.hour>=7)&(S.index.hour<9); S=S[~thu]
    rows=[]
    for bk in ['all','0-.5','.5-1','1-2','2+']:
        s=S if bk=='all' else S[S.bk==bk]
        if len(s)<30: continue
        ev=(s.win-s.p-0.07*s.p*(1-s.p))*100
        mo=ev.groupby(ev.index.strftime('%Y-%m')).mean()
        rows.append(dict(src=label,bk=bk,n=len(s),hit=round(s.win.mean(),3),ev=round(ev.mean(),2),z=round(z_ev(s.day,ev.values),2),months=len(mo),pos_months=int((mo>0).sum()),mo=' '.join(f'{k}:{v:+.1f}' for k,v in mo.items())))
    return pd.DataFrame(rows)
D['day']=D.index.floor('D'); D['bk']=D.bk.astype(str)
R=D[D.result.notna()].copy()
R['p']=0.52
t=ev_tab(R,'ASSUMED p=.52 all oil-span windows')
A=R[R.index.isin(c1.index)].copy()
A=A.join(c1)
A['p']=np.where(A.sd>0,A.yes_ask_close,1-A.yes_bid_close)
print('real-ask windows',len(A),'ask>=.99 excluded',(A.p>=.99).sum(), 'mean p',A.p.mean())
A=A[A.p<0.99]
t2=ev_tab(A,'REAL minute-1 ask')
pd.set_option('display.width',250); print(pd.concat([t,t2]).to_string())
pd.concat([t,t2]).to_csv(O+'t3.csv')
