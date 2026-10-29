"""Scalper metrics from cached fills/portfolio -> data/scalpers/metrics.json (one record per wallet)."""
import json, gzip, os, glob, bisect, statistics as st, collections, sys
D='data/scalpers/'; TAKER=0.00045
cand={c['addr']:c for c in json.load(open(D+'candidates.json'))}

def is_perp(c): return not (c.startswith('@') or '/' in c)

def wmedian(vals):  # vals: (x, w)
    vals=sorted(vals); tot=sum(w for _,w in vals); a=0
    for x,w in vals:
        a+=w
        if a>=tot/2: return x
    return None

def lots(fills):
    """FIFO round trips per coin. returns list of (coin,open_t,close_t,open_px,close_px,size,dir(+1 long))."""
    pos=collections.defaultdict(collections.deque); out=[]; seen=set()
    for f in fills:
        c=f['coin']; q=float(f['sz'])*(1 if f['side']=='B' else -1); px=float(f['px']); t=f['time']
        dq=pos[c]
        if c not in seen:
            seen.add(c); sp=float(f['startPosition'])
            if sp!=0: dq.append([None,px,sp])
        while q!=0 and dq and (dq[0][2]>0)!=(q>0):
            l=dq[0]; m=min(abs(l[2]),abs(q))
            if l[0] is not None: out.append((c,l[0],t,l[1],px,m,1 if l[2]>0 else -1))
            l[2]-= m if l[2]>0 else -m
            q-= m if q>0 else -m
            if abs(l[2])<1e-12: dq.popleft()
        if abs(q)>1e-12: dq.append([t,px,q])
    return out

def dd(series):
    pk=-1e18; m=0
    for v in series:
        pk=max(pk,v); m=max(m,pk-v)
    return m

def weekly_from_port(port,key='perpAllTime'):
    d=dict(port).get(key) or {}
    pts=[(int(t),float(v)) for t,v in d.get('pnlHistory',[])]
    av=[(int(t),float(v)) for t,v in d.get('accountValueHistory',[])]
    if len(pts)<3: return None
    wk=7*86400e3; t0=pts[0][0]; last={}
    for t,v in pts: last[int((t-t0)//wk)]=v
    ks=sorted(last); prev=0; ch=[]
    for k in ks:
        ch.append(last[k]-prev); prev=last[k]
    return dict(weeks=len(ch),pos_share=sum(1 for x in ch if x>0)/len(ch),dd=dd([v for _,v in pts]),
                pnl=pts[-1][1]-pts[0][1],avg_av=sum(v for _,v in av)/max(len(av),1),peak_av=max([v for _,v in av] or [0]),
                weekly=ch[-26:])

def period_stats(fills,evs):
    """fills in period (perp), evs = closing events (t, pnl_net) in period"""
    if not fills: return None
    g=sum(float(f['closedPnl']) for f in fills); fee=sum(float(f['fee']) for f in fills)
    net=g-fee; days=max((fills[-1]['time']-fills[0]['time'])/86400e3,1/24)
    dp=collections.defaultdict(float)
    for t,p in evs: dp[int(t//86400e3)]+=p
    wins=[p for _,p in evs if p>0]; loss=[-p for _,p in evs if p<0]
    return dict(net=net,gross=g,fee=fee,days=days,pos_days=sum(1 for v in dp.values() if v>0)/max(len(dp),1),ndays=len(dp),
                pf=sum(wins)/sum(loss) if loss else None, win=len(wins)/max(len(evs),1),
                avg_win=st.mean(wins) if wins else 0,avg_loss=-st.mean(loss) if loss else 0)

def closing_events(fills):
    """aggregate closing fills by (coin,oid) -> net pnl after fee"""
    a=collections.OrderedDict()
    for f in fills:
        cp=float(f['closedPnl'])
        if cp==0 and not f['dir'].startswith('Close'): continue
        k=(f['coin'],f['oid']); r=a.setdefault(k,[f['time'],0.0]); r[1]+=cp-float(f['fee'])
    return list(a.values())

def copy_sim(fills,lt,shift_ms):
    px=collections.defaultdict(lambda:([],[]))
    for f in fills:
        a,b=px[f['coin']]; a.append(f['time']); b.append(float(f['px']))
    def at(c,t):
        a,b=px[c]; i=bisect.bisect_left(a,t)
        if i>=len(a): return None
        return b[i] if a[i]-t<=30000 else None
    pnl=0.0; notl=0.0; n=0; miss=0
    for c,o,cl,op,cp,sz,d in lt:
        po=at(c,o+shift_ms); pc=at(c,cl+shift_ms)
        if po is None or pc is None: miss+=1; continue
        pnl+=d*(pc-po)*sz - TAKER*sz*(po+pc); notl+=sz*po; n+=1
    return dict(pnl=pnl,notional=notl,n=n,miss=miss)

def analyze(path):
    d=json.load(gzip.open(path,'rt')); a=d['addr']
    fills=sorted([f for f in d['fills'] if is_perp(f['coin'])],key=lambda f:f['time'])
    if len(fills)<200: return dict(addr=a,skip='few_fills',n=len(fills))
    t0,t1=fills[0]['time'],fills[-1]['time']; days=max((t1-t0)/86400e3,1e-3)
    lt=lots(fills)
    hold=[((c-o)/1000,sz*op) for _,o,c,op,_,sz,_ in lt]
    orders=len({(f['coin'],f['oid']) for f in fills})
    notional=sum(float(f['px'])*float(f['sz']) for f in fills)
    mk=sum(float(f['px'])*float(f['sz']) for f in fills if not f['crossed'])
    mk_n=sum(1 for f in fills if not f['crossed'])
    evs=closing_events(fills)
    tm=(t0+t1)/2
    full=period_stats(fills,evs)
    old=period_stats([f for f in fills if f['time']<tm],[e for e in evs if e[0]<tm])
    new=period_stats([f for f in fills if f['time']>=tm],[e for e in evs if e[0]>=tm])
    pnls=sorted([p for _,p in evs],reverse=True)
    top3=sum(pnls[:3])/full['net'] if full['net']>0 else None
    # weeks from fills
    wk=collections.defaultdict(float)
    for t,p in evs: wk[int((t-t0)//(7*86400e3))]+=p
    wv=list(wk.values())
    coin_pnl=collections.defaultdict(float); coin_n=collections.Counter()
    for f in fills:
        coin_pnl[f['coin']]+=float(f['closedPnl'])-float(f['fee']); coin_n[f['coin']]+=1
    cs=[]
    for sh in (0,1000,5000):
        cs.append(dict(shift=sh,**copy_sim(fills,lt,sh)))
    port=weekly_from_port(d['portfolio']) if d['portfolio'] else None
    # drawdown of fills-based cumulative net pnl
    cum=0; ser=[]
    for t,p in evs: cum+=p; ser.append(cum)
    top=sorted(coin_n.items(),key=lambda x:-x[1])[:3]
    return dict(addr=a,n_fills=len(fills),days=days,fills_day=len(fills)/days,orders_day=orders/days,
        med_hold_s=wmedian(hold) if hold else None,n_lots=len(lt),
        maker_share_fills=mk_n/len(fills),maker_share_notional=mk/notional if notional else None,
        fee_total=full['fee'],avg_fee_bps=full['fee']/notional*1e4 if notional else None,notional=notional,
        full=full,old=old,new=new,top3_share=top3,pos_weeks_fills=sum(1 for x in wv if x>0)/len(wv),nweeks_fills=len(wv),
        port=port,fill_dd=dd(ser) if ser else None,
        coins=[(c,n,coin_pnl[c]) for c,n in top],btceth_pnl_share=(coin_pnl['BTC']+coin_pnl['ETH'])/full['net'] if full['net']>0 else None,
        btceth_fill_share=(coin_n['BTC']+coin_n['ETH'])/len(fills),copy=cs,first=t0,last=t1,
        lb={k:v for k,v in cand[a]['w'].items()},name=cand[a]['name'],av=cand[a]['av'])

if __name__=='__main__':
    res=[]
    for p in sorted(glob.glob(D+'raw/*.json.gz')):
        try: res.append(analyze(p))
        except Exception as e: res.append(dict(addr=os.path.basename(p)[:42],skip='err:'+repr(e)))
    json.dump(res,open(D+'metrics.json','w'),default=str)
    print(len(res),sum(1 for r in res if 'skip' not in r))
