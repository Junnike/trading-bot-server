import sys,json,time; sys.path.insert(0,'src')
import kcommon; pass
from kcommon import get
def fee(p): return 0.07*p*(1-p)
out=open("data/t4_poll.jsonl","a")
while True:
    t0=time.time()
    d=get("/markets",{"series_ticker":"KXBTCD","status":"open","limit":1000})
    rec={"ts":t0,"ok":bool(d and "markets" in d)}
    if rec["ok"]:
        ev={}
        for m in d["markets"]:
            try:
                ya=float(m["yes_ask_dollars"]);yb=float(m["yes_bid_dollars"])
                ys=float(m.get("yes_ask_size_fp") or 0);bs=float(m.get("yes_bid_size_fp") or 0)
                ev.setdefault(m["event_ticker"],[]).append((float(m["floor_strike"]),ya,ys,yb,bs,m["ticker"]))
            except Exception: pass
        best=None;ncross=0;npairs=0
        for e,L in ev.items():
            L.sort()
            for j,B in enumerate(L):
                if not(B[3]>0 and B[4]>0): continue   # need a no-ask: 1-yes_bid, requires a yes bid
                noask=1-B[3]
                for A in L[:j]:
                    if not(A[1]<1 and A[2]>0): continue
                    npairs+=1
                    gross=1-(A[1]+noask)
                    net=gross-fee(A[1])-fee(noask)
                    if net>0: ncross+=1
                    if best is None or net>best["net"]:
                        best={"net":net,"gross":gross,"A":A[5],"B":B[5],"yaA":A[1],"noB":noask,"szA":A[2],"szB":B[4]}
        rec.update(npairs=npairs,n_pos=ncross,best=best,nmk=len(d["markets"]))
        # confirm via orderbook when candidate
        if best and best["net"]>0:
            oa=get(f"/markets/{best['A']}/orderbook");ob=get(f"/markets/{best['B']}/orderbook")
            rec["ob"]=[oa,ob]
    out.write(json.dumps(rec)+"\n");out.flush()
    time.sleep(max(0,60-(time.time()-t0)))
